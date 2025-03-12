import base64
import os
import shutil
import uuid
from functools import wraps
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
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
from schemas.errors import Error404Response
from schemas.product import ProductCreate, ProductList, ProductOut

response = {
    404: {"description": "product not found", "model": Error404Response},
    302: {"description": "The product was moved"},
    403: {"description": "Not enough privileges"},
}


router = APIRouter(
    prefix="/products", tags=["products"], dependencies=[Depends(get_current_user)]
)


def encode_to_base64(image_path: str, image_type: str = "png") -> str:
    # Check if the file exists
    try:
        with open(image_path, "rb") as image_file:  # noqa: PTH123
            image_data = image_file.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading image: {e}")

    base64_encoded = base64.b64encode(image_data).decode("utf-8")
    return f"data:image/{image_type};base64,{base64_encoded}"

# Product List
@router.get(
    "/",
    response_model=ProductList,
    responses={
        403: {"detail": "user not authenticated", "model": Error404Response},
        404: {"detail": "No product exist"},
    },
)
def read_products(
    db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 10
):
    products = get_products(db, skip=skip, limit=limit)
    if not products:
        return JSONResponse(status_code=404, content={"detail": "No product found"})

    for product in products:
        image_path = product.image.lstrip("/")

        if not os.path.exists(image_path):  # noqa: PTH110
            raise HTTPException(
                status_code=404,
                detail=f"Error reading image: file not found at '{image_path}'"
            )
        product.image = encode_to_base64(image_path)  # type: ignore

    return {"products": products}

# Product By ID
@router.get(
    "/{product_id}",
    response_model=ProductOut,
)
def read_product_by_id(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    image_path = product.image.lstrip("/")

    if not os.path.exists(image_path):  # noqa: PTH110
        raise HTTPException(
            status_code=404,
            detail=f"Error reading image: file not found at '{image_path}'"
        )

    product.image = encode_to_base64(image_path)  # type: ignore
    return product


# Create Product
@router.post("/create", response_model=ProductOut)
async def create_products(
    name: Annotated[str, Form()] = ..., # type: ignore
    price: Annotated[float, Form()] = ..., # type: ignore
    image: Annotated[UploadFile, File()] = ..., # type: ignore
    db: Session = Depends(get_db)  # noqa: FAST002
):
    static_images_dir = os.path.join("static", "images")  # noqa: PTH118
    os.makedirs(static_images_dir, exist_ok=True)  # noqa: PTH103

    original_filename = image.filename
    _, file_extension = os.path.splitext(original_filename)  # type: ignore # noqa: PTH122
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    # Save the file using the unique filename
    file_location = os.path.join(static_images_dir, unique_filename)  # noqa: PTH118
    with open(file_location, "wb") as buffer:  # noqa: PTH123
        shutil.copyfileobj(image.file, buffer)

    # Build a URL that points to the uploaded image
    image_url = f"/static/images/{unique_filename}"

    # Create product using the CRUD function; store the image URL in the database
    product_create = ProductCreate(name=name, price=price)
    product = create_product(db, product_create, image_path=image_url)
    return product

# Update Product
@router.put("/update/{product_id}", response_model=ProductOut)
def update_existing_product(
    product_id: int, product: ProductCreate, db: Annotated[Session, Depends(get_db)]
):
    db_product = update_product(db, product_id, product)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


# Delete Product
@router.delete("/delete/{product_id}")
def delete_existing_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    db_product = delete_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}
