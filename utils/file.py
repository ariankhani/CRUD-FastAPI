import magic
from fastapi import UploadFile

from core.config import settings


async def verify_file_type(file: UploadFile) -> bool:
    header = await file.read(1024)
    file.file.seek(0)

    mime = magic.from_buffer(header, mime=True)
    return mime in settings.ALLOWED_CONTENT_TYPES


async def verify_file_size(image: UploadFile) -> bool:
    image.file.seek(0, 2)
    file_size = image.file.tell()
    image.file.seek(0)
    return file_size <= settings.MAX_FILE_SIZE

