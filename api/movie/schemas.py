from pydantic import BaseModel
from typing import Optional, List, Annotated
from fastapi import File, UploadFile


class Movie(BaseModel):
    genreId: int
    langueId: int
    title: str
    cover_image: Annotated[UploadFile, File(...)]
    description: Optional[str] = None
    release_year: Optional[str] = None
    running_time: Optional[str] = None
    age_limit: Optional[str] = None
    videos_list: List[Annotated[UploadFile, File(...)]]
    movie_type: str
    
    
class DownloadLink(BaseModel):
    movieId: int
    advertisement: Optional[str] = ''
    link: str