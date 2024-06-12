from fastapi import APIRouter, status, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.security import oauth2_scheme, get_current_user
from core.database import get_db
from user import services, schemas, responses

from typing import List


router = APIRouter(
    prefix='/users',
    tags=['Users Router'],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(oauth2_scheme)]
)


@router.get('/me', status_code=status.HTTP_200_OK)
async def get_me(request: Request):
    if not request.user:
        return {"detail": "Not authenticated"}
    return request.user


@router.get('/', response_model=List[responses.User], status_code=status.HTTP_200_OK)
async def get_users(request: Request, db: Session = Depends(get_db)):
    return await services.get_users(request, db)


@router.get('/{id}/', response_model=responses.User, status_code=status.HTTP_200_OK)
async def get_user(id: int, db: Session = Depends(get_db)):
    return await services.get_user(id, db)


@router.put('/{id}/', status_code=status.HTTP_200_OK)
async def update_user(id: int, request: schemas.User, db: Session = Depends(get_db)):
    return await services.update_user(id, request, db)


@router.get('/{id}/activate/', status_code=status.HTTP_200_OK)
async def activate_user(id: int, db: Session = Depends(get_db)):
    return await services.activate_user(id, db)


@router.get('/{id}/promote/', status_code=status.HTTP_200_OK)
async def promote_user(id: int, db: Session = Depends(get_db)):
    return await services.promote_user(id, db)


@router.delete('/{id}/', status_code=status.HTTP_202_ACCEPTED)
async def delete_user(id: int, db: Session = Depends(get_db)):
    return await services.delete_user(id, db)


