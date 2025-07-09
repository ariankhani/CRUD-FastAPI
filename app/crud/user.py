import uuid

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