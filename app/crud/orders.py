from sqlalchemy.orm import Session, joinedload

from app.models.orders import Order, OrderItem
from app.models.product import Product
from app.schemas.order import (
    OrderCreate,
    OrderItemResponse,
    OrderResponse,
    ProductResponse,
)


def _get_order_model(db: Session, order_id: int) -> Order | None:
    """Return the ORM Order model (used for updates/deletes)."""
    return db.query(Order).filter(Order.id == order_id).first()


def get_order(db: Session, order_id: int) -> OrderResponse | None:
    order = (
        db.query(Order)
        .options(joinedload(Order.items).joinedload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        return None

    items = []
    for oi in order.items:
        product = oi.product
        if product is None:
            continue
        items.append(
            OrderItemResponse(
                product=ProductResponse(
                    id=product.id, name=product.name, price=product.price
                ),
                quantity=oi.quantity,
            )
        )

    return OrderResponse(id=order.id, user_id=order.user_id, items=items) # type: ignore


def create_order(db: Session, order_data: OrderCreate) -> OrderResponse:
    # Create the order
    new_order = Order(user_id=order_data.user_id)
    db.add(new_order)

    order_items = []

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise ValueError(f"Product with id {item.product_id} not found")

        order_item = OrderItem(order=new_order, product_id=item.product_id, quantity=item.quantity)
        db.add(order_item)
        order_items.append(
            OrderItemResponse(
                product=ProductResponse(id=product.id, name=product.name, price=product.price), # type: ignore
                quantity=item.quantity,
            )
        )
    db.commit()
    db.refresh(new_order)

    return OrderResponse(id=new_order.id, user_id=new_order.user_id, items=order_items) # type: ignore


def delete_order(db: Session, order_id: int) -> OrderResponse | None:
    order_model = _get_order_model(db, order_id)
    if not order_model:
        return None

    resp = get_order(db, order_id)
    db.delete(order_model)
    db.commit()
    return resp
