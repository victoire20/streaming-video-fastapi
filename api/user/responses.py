from pydantic import BaseModel, EmailStr
from pydantic.generics import GenericModel
from typing import Optional, List, TypeVar, Generic
    
from datetime import datetime

T = TypeVar('T')


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
    first_connection: Optional[datetime] = None
    last_connection: Optional[datetime] = None
    registered_at: Optional[datetime] = None
    comments_count: int
    favorites_count: int
    comments: Optional[List[Comment]] = []
    favorites: Optional[List[Favorite]] = []
    
    
class PaginatedResponse(GenericModel, Generic[T]):
    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    contents: List[T]