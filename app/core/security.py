from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Generate a JWT token
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    if settings.jwt_expiration_minutes is not None:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_expiration_minutes
        )
        to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# Decode and validate a JWT token
def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        return None
