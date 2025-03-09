from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud.user import create_user
from database.db import get_db
from schemas.user import UserBase

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/new-user", response_model=UserBase)
def create_new_user(user: UserBase, db: Annotated[Session, Depends(get_db)]):
    return create_user(db=db, username=user.username, password=user.password)
    # return {"message": "User registered successfully"}
