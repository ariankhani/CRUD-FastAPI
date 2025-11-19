import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext for password hashing (no changes needed here)
pwd_context = CryptContext(schemes=["argon2", "bcrypt", "bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


# --- START OF CHANGES ---

def create_access_token(data: dict, jti: str | None = None) -> str:
    """Create a JWT access token. If `jti` is not provided, generate one."""
    to_encode = data.copy()

    # Ensure a JTI exists for revocation/rotation
    if not jti:
        jti = str(uuid.uuid4())

    # Add expiry if configured (None means no expiry)
    if settings.jwt_expiration_minutes is not None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiration_minutes)
        to_encode["exp"] = expire

    to_encode.update({"jti": jti, "type": "access"})

    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict, jti: str | None = None) -> str:
    """Create a JWT refresh token. If `jti` is not provided, generate one."""
    to_encode = data.copy()

    if not jti:
        jti = str(uuid.uuid4())

    # Use configured refresh expiration (minutes) if set
    if settings.jwt_refresh_expiration_minutes is not None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_refresh_expiration_minutes)
        to_encode["exp"] = expire

    to_encode.update({"jti": jti, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """
    Decodes any JWT token. Renamed for clarity as it decodes both types.
    (No functional change needed here, just ensuring it's correct)
    """
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except jwt.PyJWTError:
        return None

# --- END OF CHANGES ---
