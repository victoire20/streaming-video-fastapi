from pydantic import BaseModel
from typing import Optional, List, Annotated
from fastapi import File, UploadFile
    
    
class DownloadLink(BaseModel):
    movieId: int
    advertisement: Optional[str] = ''
    link: str