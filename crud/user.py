from sqlalchemy.orm import Session

from core.security import hash_password
from models.users import User


def create_user(db: Session, username: str, password: str) -> User:
    hashed_pass = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


