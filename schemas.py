from pydantic import BaseModel, HttpUrl, EmailStr
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
    
    
class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True # Replaces orm_mode in Pydantic v2

# For creating a new user (request body)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# --- Schemas for Token Handling (we'll use these in the next step) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None
    
    
class TrackedProductInfo(BaseModel):
    name: Optional[str] = "Not Found"
    brand: Optional[str] = "Not Found"
    image_urls: List[HttpUrl] = []

    class Config:
        from_attributes = True

# The main response schema for a single tracked product
class TrackedProductResponse(BaseModel):
    id: int
    url: HttpUrl
    initial_price: Optional[float] = None
    current_price: Optional[float] = None
    product: TrackedProductInfo # Nest the product info

    class Config:
        from_attributes = True