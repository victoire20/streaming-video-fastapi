from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from user import responses
from core.security import get_password_hash
from core.models import User, Comment, Favorite


async def get_users(request: dict, db: Session) -> List[responses.User]:
    all_users = db.query(User).filter(User.id != request.user.id).all()
    
    results = []
    for user in all_users:
        comments = db.query(Comment).filter(Comment.userId == user.id).all()
        favorites = db.query(Favorite).filter(Favorite.userId == user.id).all()
        
        user_data = responses.User(
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
        results.append(user_data)
    
    return results


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
