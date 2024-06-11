from pydantic import BaseModel
from typing import Optional


class Genre(BaseModel):
    libelle: str