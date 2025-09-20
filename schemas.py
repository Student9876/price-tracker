from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict

class ScrapeRequest(BaseModel):
    urls: List[HttpUrl]

class ListingDetails(BaseModel):
    """Details specific to a single URL/listing."""
    url: HttpUrl
    price: Optional[float] = None
    mrp: Optional[float] = None
    currency: Optional[str] = "INR"
    stock_status: Optional[str] = "Not Found"
    seller_name: Optional[str] = "Not Found"
    average_rating: Optional[float] = None
    num_ratings: Optional[int] = 0
    offers: List[str] = []

class ProductDetails(BaseModel):
    """Canonical details of a product, gathered from one or more listings."""
    signature: str # The unique fingerprint we generate
    name: Optional[str] = "Not Found"
    brand: Optional[str] = "Not Found"
    category_path: List[str] = []
    image_urls: List[HttpUrl] = []
    key_features: List[str] = []
    specifications: Dict[str, str] = {}
    listing: ListingDetails # For this simple version, each product has one listing

class ErrorResponse(BaseModel):
    url: str
    error: str