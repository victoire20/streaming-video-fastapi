from fastapi import HTTPException, status, Request
from sqlalchemy import select, func, text, or_
from sqlalchemy.orm import Session
from typing import List, Optional

from core.models import Genre, GenreMovie


async def create_genre(request: dict, db: Session) -> str:
    if db.query(Genre).filter(Genre.libelle == request.libelle.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This genre already exist.'
        )
        
    new_genre = Genre(libelle=request.libelle.lower())
    
    db.add(new_genre)
    db.commit()
    return 'Genre Added successfully.'


async def get_genres(request: Request, db: Session):
    return db.query(Genre).all()


async def get_genre(id: int, db: Session) -> Genre:
    genre = db.query(Genre).filter(Genre.id == id).first()
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This genre don\'t exist.'
        )
        
    return genre


async def update_genre(id: int, request: dict, db: Session) -> str:
    genre = await get_genre(id, db)
    
    genre.libelle = request.libelle.lower()
    db.commit()
    
    return 'Genre updated successfully.'


async def activate_genre(id: int, db: Session) -> str:
    genre = await get_genre(id, db)
    
    genre.is_active = not genre.is_active
    db.commit()
    db.refresh(genre)
    
    if genre.is_active:
        return 'Genre activated successfully.'
    return 'Genre deactivated successfully.'


async def delete_genre(id: int, db: Session) -> str:
    genre = await get_genre(id, db)
    
    if db.query(GenreMovie).filter(GenreMovie.genreId == genre.id).count() > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This genre contains movies! Please delete them first!'
        )
    
    db.delete(genre)
    db.commit()
    
    return 'Genre deleted successfully.'
    