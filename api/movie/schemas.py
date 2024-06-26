from pydantic import BaseModel
from typing import Optional, List, Annotated
    
    
class DownloadLink(BaseModel):
    advertisement: Optional[str] = ''
    link: str