from pydantic import BaseModel, ConfigDict


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
    model_config = ConfigDict(from_attributes=True)