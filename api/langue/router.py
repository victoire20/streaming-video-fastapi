from fastapi import APIRouter, status, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from langue import services, schemas


router = APIRouter(
    prefix='/languages',
    tags=['Languages Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_language(request: schemas.Language, db: Session = Depends(get_db)):
    return await services.create_language(request, db)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_languages(db: Session = Depends(get_db)):
    return await services.get_languages(db)


@router.get('/{id}/', status_code=status.HTTP_200_OK)
async def get_language(id: int, db: Session = Depends(get_db)):
    return await services.get_language(id, db)


@router.put('/{id}/', status_code=status.HTTP_200_OK)
async def update_language(id: int, request: schemas.Language, db: Session = Depends(get_db)):
    return await services.update_language(id, request, db)


@router.get('/{id}/activate/', status_code=status.HTTP_200_OK)
async def activate_language(id: int, db: Session = Depends(get_db)):
    return await services.activate_language(id, db)


@router.delete('/{id}/', status_code=status.HTTP_202_ACCEPTED)
async def delete_language(id: int, db: Session = Depends(get_db)):
    return await services.delete_language(id, db)