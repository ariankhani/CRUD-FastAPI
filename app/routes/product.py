import base64
import os
from typing import Annotated, Optional

# import magic
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
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
    products = get_products(db)
    if not products:
        return {"products": []} #TODO: show empty dict
    for product in products:
        image_path = product.image.lstrip("/")

        if not os.path.exists(image_path):  # noqa: PTH110
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
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


# Update Product
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_existing_product(
    product_id: int,
    product: Annotated[ProductUpdateForm, Depends(ProductUpdateForm.as_form)],
    db: Annotated[Session, Depends(get_db)],
    image: Annotated[Optional[UploadFile], File()] = None
):
    # Retrieve the existing product
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update the product fields from the form data
    db_product.name = product.name # type: ignore
    db_product.price = product.price # type: ignore

    # If a new image file is provided, validate and save it
    if image:
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

        if not await verify_file_extension(image):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. File most be .png or .jpg"
            )
        image_url = save_uploaded_image(image)
        db_product.image = image_url # type: ignore

    db.commit()
    db.refresh(db_product)
    return db_product


# Delete Product
@router.delete("/delete/{product_id}")
def delete_existing_product(product_id: int, db: Annotated[Session, Depends(get_db)]):
    db_product = delete_product(db, product_id)
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

    if not await verify_file_extension(image):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. File most be .png or .jpg"
        )

    image_url = save_uploaded_image(image)

    product_create = ProductCreate(name=product.name, price=product.price)
    created_product = create_product(db, product_create, image_path=image_url)
    return created_product
