from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_user_from_refresh_token
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user import create_user, get_user_by_username, update_user_jti
from app.database.db import get_db
from app.schemas.user import RefreshTokenRequest, Token, UserBase

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/new-user", response_model=dict)
async def create_new_user(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    # Check if a user already exists using run_in_threadpool since it's a synchronous DB call
    existing_user = await run_in_threadpool(get_user_by_username, db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    # Create the user in the database through a thread pool (since it's a synchronous operation)
    await run_in_threadpool(create_user, db, user.username, user.password)

    return {"message": "User registered successfully"}


@router.post("/login", response_model=Token)
async def login(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    # Retrieve the user from the database (wrapped in a threadpool)
    db_user = await run_in_threadpool(get_user_by_username, db, user.username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong Username or Password",
        )

    # Verify the password (using a threadpool to offload blocking call)
    password_valid = await run_in_threadpool(
        verify_password,
        user.password,
        db_user.hashed_password,  # type: ignore
    )
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong Username or Password",
        )
    
    jti = await run_in_threadpool(update_user_jti, db, db_user.username) # type: ignore
    if not jti:
        raise HTTPException(status_code=500, detail="Could not update user session")


    # Create JWT tokens
    access_token = await run_in_threadpool(create_access_token, {"sub": db_user.username}, jti)
    refresh_token = await run_in_threadpool(create_refresh_token, {"sub": db_user.username}, jti)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }




@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    token_request: RefreshTokenRequest, db: Annotated[Session, Depends(get_db)]
):
    """
    Implements Refresh Token Rotation.
    Validates the refresh token and issues a new pair of access and refresh tokens.
    """
    token = token_request.refresh_token
    
    # 1. Decode the incoming refresh token
    payload = await run_in_threadpool(decode_token, token)
    # --- START OF DEBUGGING STEP ---
    # Add this print statement to see the decoded payload in your console
    print("--- DECODED REFRESH TOKEN PAYLOAD ---")
    print(payload)
    print("-------------------------------------")
    # --- END OF DEBUGGING STEP ---
    
    # 2. Check if the token is valid and is a 'refresh' token
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    username = payload.get("sub")
    jti = payload.get("jti")
    if not username or not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # 3. Check if the token has been revoked
    # We fetch the user and compare the token's jti with the one in the database
    user = await run_in_threadpool(get_user_by_username, db, username)
    if not user or user.jti != jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked. Please log in again.",
        )

    # 4. Invalidate the old token by generating and storing a NEW jti (The Rotation)
    new_jti = await run_in_threadpool(update_user_jti, db, user.username) # type: ignore
    if not new_jti:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update user session. Please try again.",
        )

    # 5. Issue a new pair of tokens with the new jti
    new_access_token = await run_in_threadpool(
        create_access_token, {"sub": user.username}, new_jti# type: ignore
    )
    new_refresh_token = await run_in_threadpool(
        create_refresh_token, {"sub": user.username}, new_jti# type: ignore
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }