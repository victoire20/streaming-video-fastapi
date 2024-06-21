from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, List, TypeVar, Generic
    
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        
        
class PaginatedResponse(GenericModel, Generic[T]):
    page_number: int
    page_size: int
    total_pages: int
    total_record: int
    contents: List[T]