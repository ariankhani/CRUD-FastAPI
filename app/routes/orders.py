from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
<<<<<<< HEAD
=======
from fastapi.concurrency import run_in_threadpool
>>>>>>> origin/main
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.orders import create_order, get_order
from app.database.db import get_db
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_user)])


@router.post("/create/", response_model=OrderResponse)
async def create_order_api(
    order: OrderCreate, db: Annotated[Session, Depends(get_db)]
):
    new_order = await run_in_threadpool(create_order, db, order)
    return new_order


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"detail": "Order not found"}},
)
<<<<<<< HEAD
def read_order(order_id: int, db: Annotated[Session, Depends(get_db)], current_user: dict = Depends(get_current_user)):
    order = get_order(db, order_id)
=======
async def read_order(
    order_id: int, db: Annotated[Session, Depends(get_db)]
):
    order = await run_in_threadpool(get_order, db, order_id)
>>>>>>> origin/main
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
            for item in order.items if item.product is not None
        ],
    }
    return order_data
