from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.crud.user import create_user, get_user_by_username
from app.database.db import get_db
from app.schemas.user import Token, UserBase

router = APIRouter(prefix="/accounts", tags=["accounts"])


<<<<<<< HEAD
@router.post("/new-user", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    existing_user = get_user_by_username(db, user.username)
=======
@router.post("/new-user", response_model=dict)
async def create_new_user(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    # Check if a user already exists using run_in_threadpool since it's a synchronous DB call
    existing_user = await run_in_threadpool(get_user_by_username, db, user.username)
>>>>>>> origin/main
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
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong Username or Password"
        )

    # Verify the password (using a threadpool to offload blocking call)
    password_valid = await run_in_threadpool(
        verify_password,
        user.password,
        db_user.hashed_password,  # type: ignore
    )
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong Username or Password"
        )

    # Create JWT token in a thread pool as needed
    token = await run_in_threadpool(create_access_token, {"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
