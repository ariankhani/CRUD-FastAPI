from typing import Optional

from fastapi import File, UploadFile
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    image: Optional[UploadFile] = File(None)


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None

    class Config:
        orm_mode = True


class ProductList(BaseModel):
    products: list[ProductOut]
