from pydantic import BaseModel, EmailStr
from typing import Optional


class User(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None