from sqlalchemy.orm import Session

from app.models.orders import Order, OrderItem
from app.models.product import Product
from app.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    ProductResponse,
)


def get_order(db: Session, order_id: int) -> OrderResponse | None:
    return db.query(Order).filter(Order.id == order_id).first()

def create_order(db: Session, order_data: OrderCreate) -> OrderResponse:
    # Create the order
    new_order = Order(user_id=order_data.user_id)
    db.add(new_order)
    # db.commit()
    # db.refresh(new_order)

    order_items = []
    

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product with id {item.product_id} not found")

        order_item = OrderItem(
            order_id=new_order.id, product_id=item.product_id, quantity=item.quantity
        )
        db.add(order_item)
        order_items.append(
            OrderItemResponse(
                product=ProductResponse(
                    id=product.id, name=product.name, price=product.price # type: ignore
                ),  # type: ignore
                quantity=item.quantity,
            )
        )
    db.commit()
    db.refresh(new_order)

    return OrderResponse(id=new_order.id, user_id=new_order.user_id, items=order_items)  # type: ignore


async def update_order(db: Session, order_id: int, order: OrderCreate):
    order_update = get_order(db, order_id)
    if not order_update:
        return None



def delete_order(db: Session, order_id: int) -> OrderResponse | None:
    order = get_order(db, order_id)
    if order:
        db.delete(order)
        db.commit()
        return order
    return None