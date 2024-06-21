from fastapi import HTTPException, status, Request
from sqlalchemy import select, func, text, or_
from sqlalchemy.orm import Session
from typing import List, Optional

from core.models import Langue, Movie
from langue import responses
import math


def convert_sort(sort: str) -> str:
    return ','.join(sort.split('-'))


def convert_columns(columns: str) -> List:
    return list(map(lambda x: getattr(Langue, x), columns.split('-')))


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


async def get_languages(
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
        Langue.id, 
        Langue.libelle, 
        Langue.is_active,
        Langue.created_at,
        Langue.updated_at
    ]

    if columns and columns != "all":
        selected_columns = convert_columns(columns)
        if not selected_columns:
            selected_columns = default_columns
    else:
        selected_columns = default_columns

    query = select(*selected_columns).select_from(Langue)

    if filter and filter != "null":
        criteria = dict(x.split("*") for x in filter.split('-'))
        for attr, value in criteria.items():
            _attr = getattr(Langue, attr)
            search = "%{}%".format(value)
            criteria_list.append(_attr.like(search))
        query = query.where(or_(*criteria_list))
    
    if sort and sort != "null":
        query = query.order_by(text(convert_sort(sort)))

    count_query = select(func.count()).select_from(Langue).where(
        or_(*criteria_list) if criteria_list else True
    )
    total_record = (db.execute(count_query)).scalar() or 0

    total_page = math.ceil(total_record / limit)
    offset_page = (page - 1) * limit

    query = query.offset(offset_page).limit(limit)
    
    result = db.execute(query)
    all_languages = result.fetchall()

    results = []
    for row in all_languages:
        language_data = {}
        for col in selected_columns:
            language_data[col.name] = getattr(row, col.name)
        
        results.append(language_data)
        
    return responses.PaginatedResponse(
        page_number=page,
        page_size=limit,
        total_pages=total_page,
        total_record=total_record,
        contents=results
    )


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