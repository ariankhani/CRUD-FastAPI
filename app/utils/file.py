import shutil
import uuid
from pathlib import Path

import magic
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


async def verify_file_type(file: UploadFile) -> bool:
    """
    Verify that the uploaded file's MIME type is allowed.

    This function reads the first 1024 bytes of the file to determine its MIME type using the magic library,
    then resets the file pointer so that further operations on the file work correctly.

    Args:
        file (UploadFile): The uploaded file to check.

    Returns:
        bool: True if the file's MIME type is included in settings.ALLOWED_CONTENT_TYPES; otherwise, False.
    """
    header = await file.read(1024)
    file.file.seek(0)

    mime = magic.from_buffer(header, mime=True)
    return mime in settings.ALLOWED_CONTENT_TYPES


async def verify_file_size(image: UploadFile) -> bool:
    """
    Verify that the uploaded file's size does not exceed the maximum allowed size.

    This function seeks to the end of the file to determine its size, then resets the file pointer so that the file
    can be used in subsequent operations.

    Args:
        image (UploadFile): The uploaded file to check.

    Returns:
        bool: True if the file size is less than or equal to settings.MAX_FILE_SIZE; otherwise, False.
    """
    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)
    return file_size <= settings.MAX_FILE_SIZE


async def verify_file_extension(image: UploadFile) -> bool:
    """
    Verify that the uploaded file has an allowed extension.

    Args:
        image (UploadFile): The uploaded file to be checked for a valid file extension.

    Raises:
        HTTPException: If the uploaded file does not have a filename.

    Returns:
        bool: True if the file extension is in the allowed extensions set, otherwise False.
    """
    if image.filename is None:
        raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Uploaded file does not have a filename."
    )
    file_extension = Path(image.filename).suffix.lower()
    return file_extension in settings.ALLOWED_EXTENSIONS


def save_uploaded_image(image: UploadFile) -> str:
    """
    Save an uploaded image file to the static/images directory and return its public URL.

    This function creates the static images directory if it does not exist. It then checks that the file has a valid filename,
    generates a unique filename using a UUID (preserving the original file extension), and saves the file to disk. Finally,
    it returns the URL that can be used to access the saved image (assuming that the static directory is mounted correctly in your app).

    Args:
        image (UploadFile): The uploaded image file to be saved.

    Raises:
        HTTPException: If the uploaded file does not have a filename.

    Returns:
        str: The URL for accessing the saved image, e.g., "/static/images/{unique_filename}".
    """
    static_images_dir = Path("static") / "images"
    static_images_dir.mkdir(parents=True, exist_ok=True)

    if image.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file does not have a filename."
        )
    original_filename = image.filename
    file_extension = Path(original_filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = static_images_dir / unique_filename

    with file_location.open("wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Return the URL to access the image (assuming your app mounts "/static")
    return f"/static/images/{unique_filename}"
