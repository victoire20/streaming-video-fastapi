from fastapi import HTTPException, status, Request
from sqlalchemy import select, func, text, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.orm.attributes import InstrumentedAttribute
from typing import List, Optional

from user import responses
from core.security import get_password_hash
from core.models import User, Comment, Favorite

import math


# Fonction pour convertir le tri
def convert_sort(sort: str) -> str:
    return ','.join(sort.split('-'))


# Function to convert columns
def convert_columns(columns: str) -> List:
    return list(map(lambda x: getattr(User, x), columns.split('-')))


async def get_users(
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
        User.id, 
        User.email, 
        User.username,
        User.is_admin,
        User.is_active,
        User.first_connection,
        User.last_connection,
        User.registered_at
    ]

    if columns and columns != "all":
        selected_columns = convert_columns(columns)
        if not selected_columns:
            selected_columns = default_columns
    else:
        selected_columns = default_columns

    query = select(*selected_columns).select_from(User)

    if filter and filter != "null":
        criteria = dict(x.split("*") for x in filter.split('-'))
        for attr, value in criteria.items():
            _attr = getattr(User, attr)
            search = "%{}%".format(value)
            criteria_list.append(_attr.like(search))
        query = query.where(or_(*criteria_list))
    
    if sort and sort != "null":
        query = query.order_by(text(convert_sort(sort)))

    count_query = select(func.count()).select_from(User).where(
        or_(*criteria_list) if criteria_list else True
    )
    total_record = (db.execute(count_query)).scalar() or 0

    total_page = math.ceil(total_record / limit)
    offset_page = (page - 1) * limit

    query = query.offset(offset_page).limit(limit)
    
    result = db.execute(query)
    all_users = result.fetchall()

    results = []
    for row in all_users:
        user_data = {}
        for col in selected_columns:
            # Accéder directement à l'attribut de la ligne
            user_data[col.name] = getattr(row, col.name)
        
        comments = db.query(Comment).filter(Comment.userId == row.id).all()
        user_data['comments_count'] = len(comments)
        
        favorites = db.query(Favorite).filter(Favorite.userId == row.id).all()
        user_data['favorites_count'] = len(favorites)
        
        user_data['comments'] = comments
        user_data['favorites'] = favorites
        
        results.append(user_data)

    return responses.PaginatedResponse(
        page_number=page,
        page_size=limit,
        total_pages=total_page,
        total_record=total_record,
        contents=results
    )

async def get_user(id: int, db: Session) -> responses.User:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    comments = db.query(Comment).filter(Comment.userId == user.id).all()
    favorites = db.query(Favorite).filter(Favorite.userId == user.id).all()
    
    result = responses.User(
        id=user.id,
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
        is_active=user.is_active,
        is_verified=user.is_verified,
        first_connection=user.first_connection,
        last_connection=user.last_connection,
        registered_at=user.registered_at,
        comments_count=len(comments),
        favorites_count=len(favorites),
        comments=comments,
        favorites=favorites,
    )
    return result


async def update_user(id: int, request: dict, db: Session) -> str:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    
    if request.email:
        user.email = request.email.lower()

    if request.username:
        user.username = request.username.lower()

    if request.password:
        user.password = get_password_hash(request.password)
        
    db.commit()
    return 'User Updated successfully'


async def activate_user(id: int, db: Session) -> str:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    if user.is_active:
        return 'User is activated successfully.'
    return 'User is deactivated successfully.'


async def promote_user(id: int, db: Session) -> str:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    
    if user.is_admin:
        return 'User became a director successfully.'
    return 'User no longer a director successfully.'


async def delete_user(id: int, db: Session) -> str:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    
    db.delete(user)
    db.commit()
    
    return 'User deleted successfully.'
