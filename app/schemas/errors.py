from pydantic import BaseModel


class Error404Response(BaseModel):
    message: str
    detail: str | None


class Error403Forbiden(BaseModel):
    pass
