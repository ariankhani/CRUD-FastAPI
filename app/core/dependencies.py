from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.crud.user import get_user_by_username
from app.database.db import get_db

# Create a single, reusable auth scheme instance
auth_scheme = HTTPBearer()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> dict:
    """
    Strict: validates access token AND ensures token.jti matches DB user.jti.
    Returns the payload (you can switch to returning ORM User if you prefer).
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    token_jti = payload.get("jti")
    if not username or not token_jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_username(db, username) # type: ignore
    if not user or getattr(user, "jti", None) != token_jti:
        # jti mismatch => token revoked by logout/rotation
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Expire",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def get_user_from_refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> dict:
    """
    Dependency to get the current user from a REFRESH token.
    Used ONLY for the token refresh endpoint.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
