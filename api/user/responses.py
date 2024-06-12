from pydantic import BaseModel, EmailStr
from typing import Optional, List
    
from datetime import datetime


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        

class Comment(BaseModel):
    id: int
    movieId: int
    content: str
    created_at: datetime
        

class Favorite(BaseModel):
    id: int
    movieId: int
    created_at: datetime
        

class User(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool
    is_active: bool
    is_verified: bool
    first_connection: Optional[datetime]
    last_connection: Optional[datetime]
    registered_at: Optional[datetime]
    comments_count: int
    favorites_count: int
    comments: Optional[List[Comment]] = []
    favorites: Optional[List[Favorite]] = []