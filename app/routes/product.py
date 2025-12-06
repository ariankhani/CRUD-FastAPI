import base64
import os
from typing import Annotated, Optional

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.logger import product_logger
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
async def read_products(db: Annotated[Session, Depends(get_db)]):
    try:
        products = await run_in_threadpool(get_products, db)
        if not products:
            product_logger.warning("product not found")
            return {"products": []}  # TODO: show empty dict
        product_logger.info(f"found {len(products)} Products in Database")

        # Process each product: check file existence and encode image asynchronously.
        for product in products:
            image_path = product.image.lstrip("/")
            # Use run_in_threadpool to avoid blocking the event loop
            exists = await run_in_threadpool(os.path.exists, image_path)
            if not exists:
                product_logger.error(
                    f"product image not found: ID:{product.id} PATH:{image_path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Error reading image: file not found at '{image_path}'",
                )
            # Encode the image asynchronously
            product.image = await encode_to_base64(image_path)  # type: ignore
        product_logger.info("All products were processed successfully.")
        return {"products": products}
    except Exception as e:
        product_logger.error(f"Unexpected error in receiving products: {e}")


# Product By ID
@router.get(
    "/{product_id}",
    response_model=ProductOut,
)
async def read_product_by_id(product_id: int, db: Annotated[Session, Depends(get_db)]):
    product = await run_in_threadpool(get_product, db, product_id)
    if not product:
        product_logger.error("Product with this id not in database")
        raise HTTPException(status_code=404, detail="Product not found")
    product_logger.info(f"product found. ID={product.id}, NAME={product.name}")

    image_path = product.image.lstrip("/")
    exists = await run_in_threadpool(os.path.exists, image_path)
    if not exists:
        product_logger.error(
            f"product image not found: ID:{product.name} PATH:{image_path}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Error reading image: file not found at '{image_path}'",
        )

    product.image = await encode_to_base64(image_path)  # type: ignore
    return product


# Update Product
@router.put("/update/{product_id}", response_model=ProductOut)
async def update_existing_product(
    product_id: int,
    product_payload: Annotated[ProductUpdateForm, Depends(ProductUpdateForm.as_form)],
    db: Annotated[Session, Depends(get_db)],
    image: Annotated[Optional[UploadFile], File()] = None,
):
    try:
        # Retrieve the existing product in a threadpool call
        product = await run_in_threadpool(get_product, db, product_id)
        if not product:
            product_logger.error(f"product with id:{product.id} not found")  # type: ignore
            raise HTTPException(status_code=404, detail="Product not found")

        # Update product fields from form data
        product.name = product_payload.name  # type: ignore
        product.price = product_payload.price  # type: ignore

        # If a new image file is provided, validate and save it asynchronously
        if image:
            if not await verify_file_type(image):
                product_logger.error(
                    f"File Type Error. MESSAGE=Invalid file type. Only JPEG and PNG images are allowed. ID={product.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Only JPEG and PNG images are allowed.",
                )

            if not await verify_file_size(image):
                product_logger.error(
                    f"File Size Error. MESSAGE=File too large. Maximum allowed size is 2 MB. ID={product.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File too large. Maximum allowed size is 2 MB.",
                )

            if not await verify_file_extension(image):
                product_logger.error(
                    f"File Extension Error. MESSAGE=Invalid file type. File must be .png or .jpg. ID={product.id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. File must be .png or .jpg.",
                )
            image_url = save_uploaded_image(image)
            product.image = image_url  # type: ignore

        await run_in_threadpool(db.commit)
        await run_in_threadpool(db.refresh, product)
        product_logger.info(
            f"Product Update Successful. ID={product.id}, NAME={product.name}"
        )
        return product
    except Exception as e:
        product_logger.exception(f"Can't update Product. MESSAGE={e}")


# Delete Product
@router.delete("/delete/{product_id}")
async def delete_existing_product(
    product_id: int, db: Annotated[Session, Depends(get_db)]
):
    db_product = await run_in_threadpool(delete_product, db, product_id)
    if not db_product:
        product_logger.error(f"Product not found with this ID. ID={product_id}")
        raise HTTPException(status_code=404, detail="Product not found")

    product_logger.info(f"Product deleted: {db_product}")
    return {"detail": "Product deleted"}


# Create Product
@router.post("/create", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_products(
    product: Annotated[ProductCreateForm, Depends(ProductCreateForm.as_form)],
    image: Annotated[UploadFile, File()],
    db: Annotated[Session, Depends(get_db)],
):
    # --- validations ---
    if not await verify_file_type(image):
        product_logger.error("File Type Error. Only JPEG and PNG allowed")
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only JPEG and PNG images are allowed.",
        )

    if not await verify_file_size(image):
        product_logger.error("File Size Error. Max 2 MB")
        raise HTTPException(
            status_code=400, detail="File too large. Maximum allowed size is 2 MB."
        )

    if not await verify_file_extension(image):
        product_logger.error("File Extension Error. Must be .png or .jpg")
        raise HTTPException(
            status_code=400, detail="Invalid file type. File must be .png or .jpg."
        )

    image_url = save_uploaded_image(image)

    # --- convert to real filesystem path ---
    # If your project root is the working directory
    file_path = "." + image_url  # "./static/images/xxx.jpg"

    # --- create product in DB ---
    product_create = ProductCreate(name=product.name, price=product.price)
    created_product = await run_in_threadpool(
        create_product, db, product_create, image_path=image_url
    )

    image_ext = os.path.splitext(file_path)[1][1:].lower()  # noqa: PTH122
    created_product.image = await encode_to_base64(file_path, image_type=image_ext)  # type: ignore

    product_logger.info(
        f"Product Created: name:{product_create.name}, ID={created_product.id}"
    )
    return created_product
