from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_token

# Create a single, reusable auth scheme instance
auth_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)],
) -> dict:
    """
    Dependency to get the current user from an ACCESS token.
    Used for protecting data endpoints.
    """
    token = credentials.credentials
    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
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