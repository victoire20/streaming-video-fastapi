from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.models import User


async def get_users(db: Session) -> List[User]:
    return db.query(User).all()


async def get_user(id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This user don\'t exist.'
        )
    
    return user


async def update_user(id: int, request: dict, db: Session) -> str:
    user = await get_user(id, db)
    
    if request.email:
        user.email = request.email.lower()

    if request.username:
        user.username = request.username.lower()

    if request.password:
        user.password = request.password
        
    db.commit()
    return 'User Updated successfully'


async def activate_user(id: int, db: Session) -> str:
    user = await get_user(id, db)
    
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    if user.is_active:
        return 'User is activated successfully.'
    return 'User is deactivated successfully.'


async def promote_user(id: int, db: Session) -> str:
    user = await get_user(id, db)
    
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    
    if user.is_admin:
        return 'User became a director successfully.'
    return 'User no longer a director successfully.'


async def delete_user(id: int, db: Session) -> str:
    user = await get_user(id, db)
    
    db.delete(user)
    db.commit()
    
    return 'User deleted successfully.'
