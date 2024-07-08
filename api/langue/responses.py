from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Optional, List, TypeVar, Generic
    
from datetime import datetime

T = TypeVar('T')


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True