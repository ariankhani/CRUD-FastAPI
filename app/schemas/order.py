from typing import List

from pydantic import BaseModel, ConfigDict


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)

class OrderItemResponse(BaseModel):
    product: ProductResponse
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
