from fastapi import HTTPException, status, Request
from sqlalchemy import select, func, text, or_
from sqlalchemy.orm import Session
from typing import List, Optional

from core.models import Genre, GenreMovie
from genre import responses
import math


def convert_sort(sort: str) -> str:
    return ','.join(sort.split('-'))


def convert_columns(columns: str) -> List:
    return list(map(lambda x: getattr(Genre, x), columns.split('-')))


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


async def get_genres(
    request: Request,
    page: int, 
    limit: int, 
    db: Session, 
    columns: Optional[str] = None, 
    sort: Optional[str] = None, 
    filter: Optional[str] = None
):
    criteria_list = []

    default_columns = [
        Genre.id, 
        Genre.libelle, 
        Genre.is_active,
        Genre.created_at,
        Genre.updated_at
    ]

    if columns and columns != "all":
        selected_columns = convert_columns(columns)
        if not selected_columns:
            selected_columns = default_columns
    else:
        selected_columns = default_columns

    query = select(*selected_columns).select_from(Genre)

    if filter and filter != "null":
        criteria = dict(x.split("*") for x in filter.split('-'))
        for attr, value in criteria.items():
            _attr = getattr(Genre, attr)
            search = "%{}%".format(value)
            criteria_list.append(_attr.like(search))
        query = query.where(or_(*criteria_list))
    
    if sort and sort != "null":
        query = query.order_by(text(convert_sort(sort)))

    count_query = select(func.count()).select_from(Genre).where(
        or_(*criteria_list) if criteria_list else True
    )
    total_record = (db.execute(count_query)).scalar() or 0

    total_page = math.ceil(total_record / limit)
    offset_page = (page - 1) * limit

    query = query.offset(offset_page).limit(limit)
    
    result = db.execute(query)
    all_genres = result.fetchall()

    results = []
    for row in all_genres:
        genre_data = {}
        for col in selected_columns:
            # Accéder directement à l'attribut de la ligne
            genre_data[col.name] = getattr(row, col.name)
        
        results.append(genre_data)
        
    return responses.PaginatedResponse(
        page_number=page,
        page_size=limit,
        total_pages=total_page,
        total_record=total_record,
        contents=results
    )


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
    