from pydantic import BaseModel


class Language(BaseModel):
    libelle: str