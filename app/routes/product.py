import base64
import os
from typing import Annotated, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.product import (
    create_product,
    delete_product,
    get_product,
    get_products,
)
from app.database.db import get_db
from app.schemas.errors import Error404Response
from app.schemas.product import (
    ProductCreate,
    ProductCreateForm,
    ProductList,
    ProductOut,
    ProductUpdateForm,
)
from app.utils.file import (
    save_uploaded_image,
    verify_file_extension,
    verify_file_size,
    verify_file_type,
)

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


async def encode_to_base64(image_path: str, image_type: str = "png") -> str:
    """Read an image asynchronously and convert it to a base64 encoded data URI."""
    try:
        async with aiofiles.open(image_path, "rb") as image_file:
            image_data = await image_file.read()
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
async def read_products(
    db: Annotated[Session, Depends(get_db)], skip: int = 0, limit: int = 10
):
    products = await run_in_threadpool(get_products, db, skip, limit)
    if not products:
        return JSONResponse(status_code=404, content={"detail": "No product found"})

    # Process each product: check file existence and encode image asynchronously.
    for product in products:
        image_path = product.image.lstrip("/")
        # Use run_in_threadpool to avoid blocking the event loop
        exists = await run_in_threadpool(os.path.exists, image_path)
        if not exists:
            raise HTTPException(
                status_code=404,
                detail=f"Error reading image: file not found at '{image_path}'",
            )
        # Encode the image asynchronously
        product.image = await encode_to_base64(image_path) # type: ignore

    return {"products": products}


# Product By ID
@router.get(
    "/{product_id}",
    response_model=ProductOut,
)
async def read_product_by_id(
    product_id: int, db: Annotated[Session, Depends(get_db)]
):
    product = await run_in_threadpool(get_product, db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    image_path = product.image.lstrip("/")
    exists = await run_in_threadpool(os.path.exists, image_path)
    if not exists:
        raise HTTPException(
            status_code=404,
            detail=f"Error reading image: file not found at '{image_path}'",
        )
    product.image = await encode_to_base64(image_path) # type: ignore
    return product


# Update Product
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_existing_product(
    product_id: int,
    product: Annotated[ProductUpdateForm, Depends(ProductUpdateForm.as_form)],
    db: Annotated[Session, Depends(get_db)],
    image: Annotated[Optional[UploadFile], File()] = None
):
    # Retrieve the existing product in a threadpool call
    db_product = await run_in_threadpool(get_product, db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update product fields from form data
    db_product.name = product.name  # type: ignore
    db_product.price = product.price  # type: ignore

    # If a new image file is provided, validate and save it asynchronously
    if image:
        if not await verify_file_type(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG and PNG images are allowed.",
            )

        if not await verify_file_size(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum allowed size is 2 MB."
            )

        if not await verify_file_extension(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. File must be .png or .jpg."
            )
        image_url = save_uploaded_image(image)
        db_product.image = image_url  # type: ignore

    await run_in_threadpool(db.commit)
    await run_in_threadpool(db.refresh, db_product)
    return db_product


# Delete Product
@router.delete("/delete/{product_id}")
async def delete_existing_product(
    product_id: int, db: Annotated[Session, Depends(get_db)]
):
    db_product = await run_in_threadpool(delete_product, db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"detail": "Product deleted"}


# Create Product
@router.post("/create", response_model=ProductOut)
async def create_products(
    product: Annotated[ProductCreateForm, Depends(ProductCreateForm.as_form)],
    image: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
):
    if not await verify_file_type(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only JPEG and PNG images are allowed.",
        )

    if not await verify_file_size(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum allowed size is 2 MB."
        )

    if not await verify_file_extension(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. File must be .png or .jpg."
        )

    image_url = save_uploaded_image(image)
    product_create = ProductCreate(name=product.name, price=product.price)
    created_product = await run_in_threadpool(create_product, db, product_create, image_path=image_url)
    return created_product
