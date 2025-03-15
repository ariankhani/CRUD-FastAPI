from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True
