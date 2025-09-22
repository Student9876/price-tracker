import re
from typing import Optional
from bs4 import BeautifulSoup
from schemas import ProductDetails, ListingDetails

class AmazonScraper:
    def _parse_price(self, text: str) -> Optional[float]:
        if not text: return None
        price = re.search(r'[\d,.]+', text)
        return float(price.group(0).replace(',', '')) if price else None

    def scrape(self, soup: BeautifulSoup, url: str) -> ProductDetails:
        # --- Listing-specific Details ---
        title = soup.select_one("#productTitle")
        mrp_element = soup.select_one("span.a-text-price span.a-offscreen")
        price_element = soup.select_one(".a-price-whole")
        currency_element = soup.select_one(".a-price-symbol")
        rating_text_element = soup.select_one("#acrPopover .a-icon-alt")
        num_ratings_element = soup.select_one("#acrCustomerReviewText")
        availability_element = soup.select_one("#availability")
        seller_element = soup.select_one("#merchant-info")

        # --- Canonical Product Details ---
        brand_element = soup.select_one("#bylineInfo")
        feature_bullets_elements = soup.select("#feature-bullets li .a-list-item")
        image_gallery_elements = soup.select("#altImages .a-button-thumbnail img")
        breadcrumbs_elements = soup.select("#wayfinding-breadcrumbs ul li .a-link-normal")
        spec_table_rows = soup.select("#productDetails_techSpec_section_1 tr")

        # --- Process Listing Details ---
        price = self._parse_price(price_element.get_text()) if price_element else None
        mrp = self._parse_price(mrp_element.get_text()) if mrp_element else price
        
        avg_rating = 0.0
        if rating_text_element:
            rating_match = re.search(r'[\d.]+', rating_text_element.text)
            if rating_match:
                avg_rating = float(rating_match.group(0))

        num_ratings = 0
        if num_ratings_element:
            ratings_match = re.search(r'[\d,]+', num_ratings_element.text)
            if ratings_match:
                num_ratings = int(ratings_match.group(0).replace(',', ''))
        
        listing = ListingDetails(
            url=url,
            price=price,
            mrp=mrp,
            currency=currency_element.text if currency_element else "₹",
            stock_status=availability_element.get_text(strip=True) if availability_element else "Not Found",
            seller_name=seller_element.get_text(strip=True) if seller_element else "Amazon",
            average_rating=avg_rating,
            num_ratings=num_ratings,
        )

        # --- Process Canonical Details ---
        name = title.get_text(strip=True) if title else "Not Found"
        brand = brand_element.get_text(strip=True).replace('Visit the ', '').replace(' Store', '') if brand_element else "Not Found"
        
        key_features = [feat.get_text(strip=True) for feat in feature_bullets_elements]
        
        image_urls = [img.get('src').replace('_AC_US40_', '_AC_SL1500_') for img in image_gallery_elements]
        if not image_urls:
            main_image = soup.select_one("#landingImage")
            if main_image:
                image_urls.append(main_image.get('src'))

        category_path = [crumb.get_text(strip=True) for crumb in breadcrumbs_elements]
        
        specifications = {row.th.get_text(strip=True): row.td.get_text(strip=True) for row in spec_table_rows}
        if 'Brand' in specifications:
            brand = specifications['Brand']

        # Generate signature
        signature_str = f"{brand} {name}".lower().strip()
        signature = re.sub(r'\s+', ' ', signature_str)

        product = ProductDetails(
            signature=signature,
            name=name,
            brand=brand,
            category_path=category_path,
            image_urls=image_urls,
            key_features=key_features,
            specifications=specifications,
            listing=listing
        )

        return product