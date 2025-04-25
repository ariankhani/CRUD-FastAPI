from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.orders import create_order, delete_order, get_order
from app.database.db import get_db
from app.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["orders"], dependencies=[Depends(get_current_user)])

# Order Create
@router.post("/create/", response_model=OrderResponse)
async def create_order_api(
    order: OrderCreate, db: Annotated[Session, Depends(get_db)]
):
    new_order = await run_in_threadpool(create_order, db, order)
    return new_order

# Order Read
@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    responses={404: {"detail": "Order not found"}},
)
async def read_order(order_id: int, db: Annotated[Session, Depends(get_db)], current_user: dict = Depends(get_current_user)):
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Order Delete
@router.delete("/delete/{order_id}")
async def order_delete(order_id: int, db: Annotated[Session, Depends(get_db)], current_user: dict = Depends(get_current_user)):
    order = delete_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"detail": "Order deleted"}
