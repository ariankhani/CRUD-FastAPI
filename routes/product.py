import base64
import os
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.dependencies import get_current_user
from crud.product import (
    create_product,
    delete_product,
    get_product,
    get_products,
    update_product,
)
from database.db import SessionLocal, get_db
from schemas.product import ProductCreate, ProductList, ProductOut

router = APIRouter(prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)])

def encode_to_base64(image_path: str, image_type: str = "png") -> str:
    # Check if the file exists
    try:
        with open(image_path, "rb") as image_file:  # noqa: PTH123
            image_data = image_file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading image: {e}")

    base64_encoded = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/{image_type};base64,{base64_encoded}"


@router.get("/", response_model=ProductList)
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):  # noqa: FAST002
    products = get_products(db, skip=skip, limit=limit)
    for product in products:
        product.image = encode_to_base64(product.image) # type: ignore
    return {"products": products}

@router.get("/{product_id}", response_model=ProductOut)
def read_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.image = encode_to_base64(product.image) # type: ignore
    return product

@router.post("/create", response_model=ProductOut)
def create_new_product(product: ProductCreate, db: Annotated[Session, Depends(get_db)]):
    return create_product(db, product)

@router.put("/update/{product_id}", response_model=ProductOut)
def update_existing_product(product_id: int, product: ProductCreate, db: Annotated[Session, Depends(get_db)]):
    db_product = update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.delete("/delete/{product_id}")
def delete_existing_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    db_product = delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}
