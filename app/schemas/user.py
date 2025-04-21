<<<<<<< HEAD
from pydantic import BaseModel, ConfigDict
=======
from typing import List

from pydantic import BaseModel, Field, field_validator
>>>>>>> origin/main


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        errors: List[str] = []

        if not any(char.isupper() for char in value):
            errors.append("Password must include at least one uppercase letter.")
        if not any(char.islower() for char in value):
            errors.append("Password must include at least one lowercase letter.")
        if not any(char.isdigit() for char in value):
            errors.append("Password must include at least one digit.")
        if not any(not char.isalnum() for char in value):
            errors.append("Password must include at least one special character.")

        if errors:
            # Raise a single error with all messages joined
            raise ValueError(" ".join(errors))
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
<<<<<<< HEAD


class UserResponse(BaseModel):
    id: int
    username: str
    password: str
    model_config = ConfigDict(from_attributes=True)
=======
>>>>>>> origin/main
