from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from db.base import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    tracked_product_id = Column(Integer, ForeignKey("tracked_products.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

    tracked_product = relationship("TrackedProduct", back_populates="price_history")