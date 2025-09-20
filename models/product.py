# models/product.py

from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB  # Import JSONB for Postgres
from db.base import Base

class Product(Base):
    """Stores the canonical, user-independent details of a product."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    signature = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    brand = Column(String)
    
    # --- NEW FIELDS ---
    # Use JSONB to store lists and dictionaries efficiently
    category_path = Column(JSONB)  # For ["Electronics", "Mobiles"]
    image_urls = Column(JSONB)     # For ["url1", "url2", ...]
    key_features = Column(JSONB)   # For ["Feature 1", "Feature 2", ...]
    specifications = Column(JSONB) # For {"OS": "Android", "RAM": "12 GB"}

class TrackedProduct(Base):
    """Links a User to a specific Product URL they are tracking."""
    __tablename__ = "tracked_products"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    initial_price = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    # --- NEW FIELDS ---
    mrp = Column(Numeric(10, 2))
    currency = Column(String(10))
    stock_status = Column(String)
    seller_name = Column(String)
    average_rating = Column(Numeric(3, 2))
    num_ratings = Column(Integer)
    offers = Column(JSONB)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))

    owner = relationship("User", back_populates="tracked_products")
    product = relationship("Product")