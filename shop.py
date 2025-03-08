from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from pydantic import BaseModel


DATABASE_URL = "sqlite:///./test.db"  # using SQLite for simplicity

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    image = Column(String)


Base.metadata.create_all(bind=engine)



class ProductCreate(BaseModel):
    name: str
    price: float
    image: str

class ProductOut(ProductCreate):
    id: int

    class Config:
        orm_mode = True
