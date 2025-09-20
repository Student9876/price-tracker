import json
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Optional, List, Tuple, Dict, Any

from bs4 import BeautifulSoup

from schemas import ProductDetails, ListingDetails

# Tunables
SELECTORS_PATH = Path("selectors/flipkart.json")
CANDIDATE_PATH = Path("selectors/flipkart.candidate.json")
CONFIDENCE_THRESHOLD = 0.6   # if top selector appears in >=60% of pages -> promote


class FlipkartScraper:
    def __init__(self, selectors_file: str = str(SELECTORS_PATH)):
        self.selector_file = Path(selectors_file)
        self.selectors = {}
        if self.selector_file.exists():
            try:
                self.selectors = json.loads(self.selector_file.read_text())
            except Exception:
                self.selectors = {}

    # ----------------------------
    # Existing scrape logic (unchanged behavior)
    # ----------------------------
    def _try_selectors(self, soup: BeautifulSoup, key: str):
        sel_list = self.selectors.get(key, [])
        for sel in sel_list:
            elems = soup.select(sel)
            if not elems:
                continue
            if key == "images":
                urls = []
                for el in elems:
                    src = el.get("src") or el.get("data-src") or el.get("data-image")
                    if src:
                        urls.append(src)
                if urls:
                    return urls
            else:
                text = elems[0].get_text(separator=" ", strip=True)
                if text:
                    return text
        return None

    def _heuristic_name(self, soup: BeautifulSoup):
        meta = soup.select_one('meta[property="og:title"], meta[name="og:title"]')
        if meta and meta.get("content"):
            return meta["content"].strip()
        t = soup.title.string if soup.title else None
        if t:
            return t.strip()
        for tag in ("h1", "h2"):
            el = soup.select_one(tag)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return "Not Found"

    def _parse_price(self, text: str) -> Optional[float]:
        if not text:
            return None
        # strip currency symbols and words
        cleaned = text.replace("₹", "").replace("Rs.", "").replace("INR", "")
        price = re.search(r'[\d,]+', cleaned)
        return float(price.group(0).replace(',', '')) if price else None

    def scrape(self, soup: BeautifulSoup, url: str) -> ProductDetails:
        # JSON-LD attempt
        product_data = {}
        script_tag = soup.find("script", {"id": "jsonLD"})
        if script_tag:
            try:
                json_data_list = json.loads(script_tag.string)
                for item in json_data_list:
                    if item.get("@type") == "Product":
                        product_data = item
                        break
            except Exception:
                product_data = {}

        # Name
        name = product_data.get("name") if product_data else None
        if not name:
            name = self._try_selectors(soup, "name")
        if not name:
            name = self._heuristic_name(soup)

        brand = product_data.get("brand", {}).get("name", name.split()[0]) if product_data else name.split()[0]

        # Price
        price = None
        if product_data:
            offer = product_data.get("offers", [{}])
            if isinstance(offer, list):
                offer = offer[0] if offer else {}
            try:
                price = float(offer.get("price", 0.0))
            except Exception:
                price = None

        if not price:
            price_text = self._try_selectors(soup, "price")
            price = self._parse_price(price_text) if price_text else None

        mrp_text = self._try_selectors(soup, "mrp")
        mrp = self._parse_price(mrp_text) if mrp_text else price

        # Images
        image_urls = product_data.get("image", []) if product_data else []
        if not image_urls:
            imgs = self._try_selectors(soup, "images")
            image_urls = imgs if imgs else []

        # Seller & rating
        seller_name = self._try_selectors(soup, "seller") or "Not Found"
        rating_text = self._try_selectors(soup, "rating") or ""
        avg_rating = 0.0
        if rating_text:
            m = re.search(r'[\d.]+', rating_text)
            if m:
                avg_rating = float(m.group(0))

        listing = ListingDetails(
            url=url,
            price=price or 0.0,
            mrp=mrp or (price or 0.0),
            currency="INR",
            stock_status="In Stock",
            seller_name=seller_name,
            average_rating=avg_rating,
            num_ratings=0
        )

        signature_str = f"{brand} {name}".lower().strip()
        signature = re.sub(r'\s+', ' ', signature_str)

        product = ProductDetails(
            signature=signature,
            name=name,
            brand=brand,
            key_features=product_data.get("description", "").split(", ") if product_data.get("description") else [],
            listing=listing,
            image_urls=image_urls,
            category_path=[],
            specifications={}
        )
        return product

    # ----------------------------
    # Discovery & auto-update functionality
    # ----------------------------
    @staticmethod
    def _gather_candidates_from_soup(soup: BeautifulSoup) -> Dict[str, List[str]]:
        """
        Return candidate selectors per key for one BeautifulSoup document.
        The output maps field -> list of selector strings seen in that document.
        """
        candidates = defaultdict(list)

        # Price-like text nodes -> prefer parent classes
        PRICE_RE = re.compile(r'₹?\s*[\d,]{3,}')
        for el in soup.find_all(text=True):
            if el.parent is None:
                continue
            text = el.strip()
            if not text:
                continue
            if PRICE_RE.search(text):
                parent = el.parent
                if parent.get("class"):
                    sel = ".".join(parent.get("class"))
                    candidates["price"].append(f"{parent.name}.{sel}")
                else:
                    candidates["price"].append(parent.name)

        # Names: meta og:title, h1/h2 with classes
        meta = soup.select_one('meta[property="og:title"], meta[name="og:title"]')
        if meta and meta.get("content"):
            candidates["name"].append("meta[property='og:title']")
        for tag in ("h1", "h2"):
            el = soup.select_one(tag)
            if el and el.get_text(strip=True):
                if el.get("class"):
                    candidates["name"].append(f"{tag}.{'.'.join(el.get('class'))}")
                else:
                    candidates["name"].append(tag)

        # images: img tags with classes
        for img in soup.find_all("img"):
            src = img.get("src") or img.get("data-src") or img.get("data-image")
            if not src or not src.startswith("http"):
                continue
            if img.get("class"):
                candidates["images"].append(f"img.{'.'.join(img.get('class'))}")
            else:
                candidates["images"].append("img")

        # seller: #sellerName or class hints
        seller_el = soup.select_one("#sellerName")
        if seller_el:
            candidates["seller"].append("#sellerName")
        else:
            # scan for text "seller" near spans
            for span in soup.find_all("span"):
                txt = span.get_text(strip=True).lower()
                if "seller" in txt or "sold by" in txt:
                    if span.get("class"):
                        candidates["seller"].append(f"span.{'.'.join(span.get('class'))}")

        # rating
        for rating_class in ("_3LWZlK", "_2d4LTz", "div._3LWZlK"):
            if soup.select_one(f".{rating_class.strip(' .')}"):
                candidates["rating"].append(f".{rating_class.strip(' .')}")

        # return as lists
        return {k: list(v) for k, v in candidates.items()}

    @staticmethod
    def _rank_candidates(all_candidates: List[Dict[str, List[str]]]) -> Dict[str, List[str]]:
        """
        all_candidates is a list of per-page candidate dicts.
        We compute frequency of each selector string and return
        lists sorted by descending frequency for each key.
        """
        counters = defaultdict(Counter)
        pages = len(all_candidates) or 1
        for cand in all_candidates:
            for k, sels in cand.items():
                for s in sels:
                    counters[k][s] += 1

        ranked = {}
        for k, counter in counters.items():
            # sort by frequency desc, selector uniqueness maintained
            ranked[k] = [sel for sel, _ in counter.most_common()]
        return ranked

    async def auto_update_selectors(
        self,
        seed_urls: List[str],
        fetcher=None,
        replace_if_confident: bool = True
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Fetches the seed_urls (async) using the provided fetcher or httpx,
        runs selector-discovery across them, writes a candidate JSON, and
        optionally promotes to active selectors file if confidence threshold met.

        - fetcher: optional async function signature (url) -> (status_code, html)
                   If not provided, this method uses httpx.AsyncClient internally.
        - returns: (updated_bool, report_dict)
        """
        import httpx  # local import so module stays importable if user doesn't have httpx

        htmls = []
        # use provided fetcher if given
        if fetcher is None:
            async with httpx.AsyncClient(http2=True, trust_env=False, timeout=20.0) as client:
                for u in seed_urls:
                    try:
                        resp = await client.get(u, follow_redirects=True)
                        if resp.status_code == 200:
                            htmls.append(resp.text)
                    except Exception:
                        continue
        else:
            for u in seed_urls:
                try:
                    status, html = await fetcher(u)
                    if status == 200 and html:
                        htmls.append(html)
                except Exception:
                    continue

        if not htmls:
            return False, {"reason": "no_html_fetched", "fetched": 0}

        all_candidates = []
        for h in htmls:
            soup = BeautifulSoup(h, "html.parser")
            cands = self._gather_candidates_from_soup(soup)
            all_candidates.append(cands)

        ranked = self._rank_candidates(all_candidates)

        # Write candidate JSON for human review
        candidate_obj = {"ranked": ranked, "sample_pages": len(htmls)}
        try:
            CANDIDATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            CANDIDATE_PATH.write_text(json.dumps(candidate_obj, indent=2))
        except Exception:
            pass

        report = {"sample_pages": len(htmls), "ranked": ranked}

        # Decision to promote: for each required key, if top selector appears in >= threshold of pages
        promote = True
        required_keys = ["name", "price", "images"]
        for k in required_keys:
            top = ranked.get(k, [])
            if not top:
                promote = False
                report.setdefault("confidence", {})[k] = 0.0
                continue
            top_sel = top[0]
            # compute frequency across pages
            freq = sum(1 for page in all_candidates if top_sel in sum([v for v in page.values()], []))
            confidence = freq / len(all_candidates)
            report["confidence"][k] = confidence
            if confidence < CONFIDENCE_THRESHOLD:
                promote = False

        if promote and replace_if_confident:
            # Build new selectors dict ordered by ranked suggestions (top n per key)
            new_selectors = {}
            for k, arr in ranked.items():
                new_selectors[k] = arr  # keep full ordered list; the scrape uses first match
            try:
                SELECTORS_PATH.write_text(json.dumps(new_selectors, indent=2))
                # reload
                self.selectors = new_selectors
                report["promoted"] = True
                return True, report
            except Exception as e:
                report["promoted"] = False
                report["error"] = str(e)
                return False, report

        report["promoted"] = False
        return False, report
