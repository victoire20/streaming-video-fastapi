from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, List, TypeVar, Generic
    
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        

class Genre(BaseModel):
    id: int
    libelle: str
        
        
class GenreMovie(BaseModel):
    genre: List[Genre]
        
        
class Langue(BaseModel):
    libelle: str
    
    
class DowloadLinks(BaseModel):
    id: int
    advertisement: Optional[str] = None
    link: str
    is_active: bool


class Comments(BaseModel):
    id: int
    parentId: Optional[int] = None
    userId: int
    content: str
        
        
class MovieResponse(BaseModel):
    id: int
    title: str
    langue: Langue
    cover_image: Optional[str] = None
    meta_keywords: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[str] = None
    running_time: Optional[str] = None
    age_limit: Optional[str] = None
    movie_type: str
    rate: Optional[float] = None
    views: int
    is_active: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    # genre_movie: GenreMovie
    download_links: Optional[List[DowloadLinks]] = None
    comments: Optional[List[Comments]] = None
        
        
class PaginatedResponse(GenericModel, Generic[T]):
    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    contents: List[T]