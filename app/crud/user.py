import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.users import User


def create_user(db: Session, username: str, password: str) -> User:
    hashed_pass = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user_jti(db: Session, username: str) -> str:
    """
    Generates a new JTI, updates it for the user, and returns it.
    This action effectively revokes all previous tokens for that user.
    """
    # Step 1: Find the user in the database.
    user = get_user_by_username(db, username)
    if not user:
        # If the user doesn't exist, we can't proceed.
        return None # type: ignore

    # Step 2: Create a new, completely random, and unique ID.
    new_jti = str(uuid.uuid4())

    # Step 3: Update the user's 'jti' field in the database with the new ID.
    user.jti = new_jti # type: ignore

    # Step 4: Save the change permanently.
    db.commit()

    # Step 5: Return the new ID so it can be used to create the new tokens.
    return new_jti


def rotate_jti_if_matches(db: Session, *, username: str, expected_jti: str) -> bool:
    """
    Logout helper: rotate user's JTI **only if** current DB JTI equals `expected_jti`.
    Returns True if rotated (logged out), False otherwise.
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if getattr(user, "jti", None) != expected_jti:
        # token already revoked / mismatch -> treat as not logged in
        return False
    user.jti = str(uuid.uuid4())  # type: ignore[attr-defined]
    db.commit()
    return True
