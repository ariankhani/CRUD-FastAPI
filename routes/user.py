from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session

from core.security import create_access_token, verify_password
from crud.user import create_user, get_user_by_username
from database.db import get_db
from models.users import User
from schemas.user import Token, UserBase

router = APIRouter(prefix="/accounts", tags=["accounts"])



@router.post("/new-user", response_model=dict)
def create_new_user(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    create_user(db, user.username, user.password)
    return {"message": "User registered successfully"}



@router.post("/token", response_model=Token)
def login(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    db_user = get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password): # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{db_user.hashed_password}" # type: ignore
        )
    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
