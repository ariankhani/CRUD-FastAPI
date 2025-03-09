from pydantic import BaseModel


class ProductCreate(BaseModel):
    name: str
    price: float
    image: str

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    image: str

    class Config:
        orm_mode = True


class ProductList(BaseModel):
    products: list[ProductOut]
