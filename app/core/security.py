import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext for password hashing (no changes needed here)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


# --- START OF CHANGES ---

def create_access_token(data: dict, jti: str) -> str:
    """
    Creates a new JWT access token.
    Accepts a 'jti' and includes it in the token payload.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expiration_minutes or 15
    )
    # Add all required claims to the payload
    to_encode.update(
        {
            "exp": expire,
            "jti": jti,  # <-- Add the JTI here
            "type": "access",
        }
    )
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict, jti: str) -> str:
    """
    Creates a new JWT refresh token.
    Accepts a 'jti' and includes it in the token payload.
    """
    to_encode = data.copy()
    # Refresh tokens typically have a longer expiry time
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    # Add all required claims to the payload
    to_encode.update(
        {
            "exp": expire,
            "jti": jti,  # <-- Add the JTI here
            "type": "refresh",
        }
    )
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
