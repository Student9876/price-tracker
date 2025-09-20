from fastapi import FastAPI, HTTPException
from typing import List, Union
import asyncio


from scraper import scrape_url # The coordinator
from schemas import ScrapeRequest, ProductDetails, ErrorResponse # The data models

app = FastAPI(
    title="Modular Product Scraper API",
    description="An API that scrapes detailed product information from a list of URLs."
)

# ... THE REST OF YOUR main.py REMAINS UNCHANGED ...
@app.post("/scrape", response_model=List[Union[ProductDetails, ErrorResponse]])
async def scrape_products(request: ScrapeRequest):
    if not request.urls:
        raise HTTPException(status_code=400, detail="URL list cannot be empty.")
    
    tasks = [scrape_url(str(url)) for url in request.urls]
    results = await asyncio.gather(*tasks)
    
    return results