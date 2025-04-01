from sqlalchemy import Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String, index=True)

    order_items = relationship("OrderItem", back_populates="product")  # Link back to OrderItem