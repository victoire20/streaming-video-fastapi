from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.models import Langue, Movie


async def create_language(request: dict, db: Session) -> str:
    if db.query(Langue).filter(Langue.libelle == request.libelle.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This language already exist.'
        )
        
    new_language = Langue(libelle=request.libelle.lower())
    
    db.add(new_language)
    db.commit()
    return 'Language added successfully.'


async def get_languages(db: Session) -> List[Langue]:
    return db.query(Langue).all()


async def get_language(id: int, db: Session) -> Langue:
    language = db.query(Langue).filter(Langue.id == id).first()
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This language does not exist.'
        )
        
    return language


async def update_language(id: int, request: dict, db: Session) -> str:
    language = await get_language(id, db)
    
    language.libelle = request.libelle.lower()
    db.commit()
    return 'Language updated successfully.'


async def activate_language(id: int, db: Session) -> str:
    language = await get_language(id, db)
    
    language.is_active = not language.is_active
    
    db.commit()
    db.refresh(language)
    
    if language.is_active:
        return 'Language activated successfully.'
    return 'Language deactivated successfully.'


async def delete_language(id: int, db: Session) -> str:
    language = await get_language(id, db)
    
    if db.query(Movie).filter(Movie.langueId == language.id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This language has several films. Please delete them first!'
        )
        
    db.delete(language)
    db.commit()
    return 'Language deleted successfully.'