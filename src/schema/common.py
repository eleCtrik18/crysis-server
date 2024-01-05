from pydantic import BaseModel
from typing import Dict, Any


class APIResponse(BaseModel):
    success: bool
    message: str = ""
    error: str = ""
    data: Dict[Any, Any] = {"": ""}


class TokenPayload(BaseModel):
    sub: str
    exp: int
