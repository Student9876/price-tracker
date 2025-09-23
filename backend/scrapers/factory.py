import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from schemas import ErrorResponse
# Import the new, modular scraper classes
from .amazon import AmazonScraper

class ScraperFactory:
    def __init__(self):
        self._scrapers = {
            "www.amazon.in": AmazonScraper(),
            "www.amazon.com": AmazonScraper(),
        }

    def get_scraper(self, url: str):
        domain = urlparse(url).netloc
        return self._scrapers.get(domain)

# The single entry point for all scraping tasks
async def scrape_url(url: str):
    factory = ScraperFactory()
    scraper = factory.get_scraper(url)
    
    if not scraper:
        return ErrorResponse(url=url, error="No scraper available for this website.")

    headers = {
        'authority': urlparse(url).netloc,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    try:
        async with httpx.AsyncClient(http2=True, trust_env=False) as client:
            resp = await client.get(url, headers=headers, follow_redirects=True, timeout=20.0)
            resp.raise_for_status()
            
            if resp.status_code != 200:
                return ErrorResponse(url=url, error=f"Blocked (possible captcha/bot challenge). Status: {resp.status_code}")

            soup = BeautifulSoup(resp.text, "html.parser")
            product = scraper.scrape(soup, url)

            # If essential fields are missing, you can implement discovery logic per-scraper if/when needed.

            return product

    except Exception as e:
        return ErrorResponse(url=url, error=f"Failed to scrape. Reason: {str(e)}")