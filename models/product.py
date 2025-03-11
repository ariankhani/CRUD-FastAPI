from sqlalchemy import Column, Float, Integer, String

from database.db import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String, index=True)
