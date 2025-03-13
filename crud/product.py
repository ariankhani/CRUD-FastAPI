from sqlalchemy.orm import Session

from models.product import Product
from schemas.product import ProductCreate


def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Product).offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate, image_path: str):
    db_product = Product(name=product.name, price=product.price, image=image_path)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductCreate):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    if product.name is not None:
        db_product.name = product.name # type: ignore
    if product.price is not None:
        db_product.price = product.price # type: ignore
    if product.image is not None:
        db_product.image = product.image # type: ignore
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int):
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    db.delete(db_product)
    db.commit()
    return db_product
