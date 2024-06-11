from fastapi import APIRouter, status, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from genre import services, schemas


router = APIRouter(
    prefix='/genres',
    tags=['Genre Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_genre(request: schemas.Genre, db: Session = Depends(get_db)):
    return await services.create_genre(request, db)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_genres(db: Session = Depends(get_db)):
    return await services.get_genres(db)


@router.get('/{id}/', status_code=status.HTTP_200_OK)
async def get_genre(id: int, db: Session = Depends(get_db)):
    return await services.get_genre(id, db)


@router.put('/{id}/', status_code=status.HTTP_200_OK)
async def update_genre(id: int, request: schemas.Genre, db: Session = Depends(get_db)):
    return await services.update_genre(id, request, db)


@router.get('/{id}/activate/', status_code=status.HTTP_200_OK)
async def activate_genre(id: int, db: Session = Depends(get_db)):
    return await services.activate_genre(id, db)


@router.delete('/{id}/', status_code=status.HTTP_202_ACCEPTED)
async def delete_genre(id: int, db: Session = Depends(get_db)):
    return await services.delete_genre(id, db)