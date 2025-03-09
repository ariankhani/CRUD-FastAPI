from sqlalchemy.orm import Session

from core.security import hash_password
from models.users import User


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username)


def create_user(db: Session, username: str, password: str) -> User:
    hashed_pass = hash_password(password)
    new_user = User(username=username, password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # print(f'---------------------------------------------{new_user}---------------------')
    return new_user
