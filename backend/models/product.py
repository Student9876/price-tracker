from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from db.base import Base

class Product(Base):
    """Stores the canonical, user-independent details of a product."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    signature = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    brand = Column(String)
    category_path = Column(JSONB)
    image_urls = Column(JSONB)
    key_features = Column(JSONB)
    specifications = Column(JSONB)
    # The relationship that was here has been moved to TrackedProduct

class TrackedProduct(Base):
    """Links a User to a specific Product URL they are tracking."""
    __tablename__ = "tracked_products"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    initial_price = Column(Numeric(10, 2))
    current_price = Column(Numeric(10, 2))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
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
    
    # --- MOVED HERE ---
    # This correctly links a TrackedProduct to its many PriceHistory entries.
    price_history = relationship("PriceHistory", back_populates="tracked_product", cascade="all, delete-orphan")