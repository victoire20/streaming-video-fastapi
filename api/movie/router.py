from fastapi import APIRouter, status, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from core.database import get_db
from movie import services, schemas
from typing import Optional


router = APIRouter(
    prefix='/movies',
    tags=['Movies Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_movie(request: schemas.Movie, db: Session = Depends(get_db)):
    return await services.create_movie(request, db)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_movies(db: Session = Depends(get_db)):
    return await services.get_movies(db)


@router.get('/{id}/', status_code=status.HTTP_200_OK)
async def get_movie(id: int, db: Session = Depends(get_db)):
    return await services.get_movie(id, db)


@router.put('/{id}/', status_code=status.HTTP_200_OK)
async def update_movie(id: int, request: schemas.Movie, db: Session = Depends(get_db)):
    return await services.update_movie(id, request, db)


@router.get('/{id}/activate/', status_code=status.HTTP_200_OK)
async def activate_movie(id: int, db: Session = Depends(get_db)):
    return await services.activate_movie(id, db)


@router.delete('/{id}/', status_code=status.HTTP_202_ACCEPTED)
async def delete_movie(id: int, db: Session = Depends(get_db)):
    return await services.delete_movie(id, db)


@router.get('/{id}/comments/', status_code=status.HTTP_200_OK)
async def get_comments(id: int, idComment: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.get_comments(id, idComment, db)


@router.delete('/{id}/comments/', status_code=status.HTTP_200_OK)
async def delete_comments(id: int, idComment: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.delete_comments(id, idComment, db)


@router.post('/download-links/', status_code=status.HTTP_200_OK)
async def create_links(request: schemas.DownloadLink, db: Session = Depends(get_db)):
    return await services.create_links(request, db)


@router.get('/{id}/download-links/', status_code=status.HTTP_200_OK)
async def get_links(id: int, idlink: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.get_links(id, idlink, db)


@router.get('/{id}/download-links/{idlink}/activate/', status_code=status.HTTP_200_OK)
async def activate_links(id: int, idlink: int, db: Session = Depends(get_db)):
    return await services.activate_links(id, idlink, db)


@router.delete('/{id}/download-links/', status_code=status.HTTP_200_OK)
async def delete_links(id: int, idlink: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.delete_links(id, idlink, db)