from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud.orders import create_order, get_order
from app.database.db import get_db
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/create/", response_model=OrderResponse)
def create_order_api(order: OrderCreate, db: Annotated[Session, Depends(get_db)]):
    return create_order(db, order)


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={
        404: {"detail": "Order not found"},
    },
)
def read_order(order_id: int, db: Annotated[Session, Depends(get_db)]):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order_data = {
        "id": order.id,
        "user_id": order.user_id,
        "items": [
            {
                "quantity": item.quantity,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": item.product.price,
                },
            }
            for item in order.items
            if item.product is not None  # Ensure product exists
        ],
    }
    return order_data
