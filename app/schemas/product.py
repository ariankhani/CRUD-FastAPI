from typing import Optional

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    price: float
    image: Optional[UploadFile] = File(None)


class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    image: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProductList(BaseModel):
    products: list[ProductOut]


class ProductCreateForm(BaseModel):
    name: str
    price: float

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        price: float = Form(...),
    ) -> "ProductCreateForm":
        return cls(name=name, price=price)

class ProductUpdateForm(BaseModel):
    name: str
    price: float

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        price: float = Form(...),
    ) -> "ProductUpdateForm":
        return cls(name=name, price=price)
