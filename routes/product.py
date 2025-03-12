import base64
import os
import shutil
import uuid
from pathlib import Path
from typing import Annotated, cast

# import magic
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
from database.db import get_db
from schemas.errors import Error404Response
from schemas.product import ProductCreate, ProductList, ProductOut
from utils.file import verify_file_size, verify_file_type

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB in bytes
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}


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
                detail=f"Error reading image: file not found at '{image_path}'",
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
            detail=f"Error reading image: file not found at '{image_path}'",
        )

    product.image = encode_to_base64(image_path)  # type: ignore
    return product


# Create Product
@router.post("/create", response_model=ProductOut)
async def create_products(
    name: Annotated[str, Form()],
    price: Annotated[float, Form()],
    image: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
):
    # Validate image format
    if not await verify_file_type(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are allowed.",
        )

    # Validate image size
    if not await verify_file_size(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum allowed size is 2 MB."
        )

    static_images_dir = Path("static") / "images"
    static_images_dir.mkdir(parents=True, exist_ok=True)

    original_filename = cast(str, image.filename)
    file_extension = Path(original_filename).suffix

    unique_filename = f"{uuid.uuid4()}{file_extension}"

    file_location = static_images_dir / unique_filename

    with file_location.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = f"/static/images/{unique_filename}"

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
