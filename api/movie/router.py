from fastapi import APIRouter, status, Depends, Request, HTTPException, Header, Form, File, UploadFile
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from movie import services, schemas, responses
from typing import Optional, List
from datetime import datetime


router = APIRouter(
    prefix='/movies',
    tags=['Movies Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_movie(
    background: BackgroundTasks,
    cover_player: UploadFile = Form(...),
    genreId: List[int] = Form(...),
    # langueId: int = Form(...),
    langueId: List[int] = Form(...),
    title: str = Form(...),
    cover_image: UploadFile = Form(...),
    description: Optional[str] = Form(None),
    publication_date: Optional[datetime] = Form(None),
    trailer_url: Optional[str] = Form(...),
    release_year: Optional[str] = Form(None),
    running_time: Optional[str] = Form(None),
    age_limit: Optional[str] = Form(None),
    # zip_file: UploadFile = Form(...),
    zip_files: List[UploadFile] = Form(...),
    movie_type: str = Form(...),
    meta_keywords: str = Form(...),
    seo_title: Optional[str] = Form(None),
    seo_description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Make for each for zip_files"""
    
    return await services.create_movie(
        cover_player=cover_player,
        genreId=genreId,
        langueId=langueId,
        title=title,
        cover_image=cover_image,
        description=description,
        publication_date=publication_date,
        trailer_url=trailer_url,
        release_year=release_year,
        running_time=running_time,
        age_limit=age_limit,
        # zip_file=zip_file,
        zip_files=zip_files,
        movie_type=movie_type, 
        meta_keywords=meta_keywords,
        seo_title=seo_title,
        seo_description=seo_description,
        background=background,
        db=db
    )


@router.get('/', response_model=List[responses.MovieResponse], status_code=status.HTTP_200_OK)
async def get_movies(request: Request, db: Session = Depends(get_db)):
    return await services.get_movies(request=request, db=db)


@router.get('/{id}/', response_model=responses.MovieResponse, status_code=status.HTTP_200_OK)
async def get_movie(id: int, db: Session = Depends(get_db)):
    return await services.get_movie(id, db)


@router.put('/{id}/', status_code=status.HTTP_200_OK)
async def update_movie(
    id: int, 
    background: BackgroundTasks,
    cover_player: Optional[UploadFile] = Form(...),
    genreId: Optional[List[int]] = Form(...),
    langueId: Optional[int] = Form(...),
    title: Optional[str] = Form(...),
    cover_image: Optional[UploadFile] = Form(...),
    description: Optional[str] = Form(None),
    release_year: Optional[str] = Form(None),
    running_time: Optional[str] = Form(None),
    age_limit: Optional[str] = Form(None),
    zip_file: Optional[UploadFile] = Form(...),
    movie_type: Optional[str] = Form(...),
    meta_keywords: Optional[str] = Form(...),
    db: Session = Depends(get_db)
):
    return await services.update_movie(
        id,
        cover_player=cover_player,
        genreId=genreId,
        langueId=langueId,
        title=title,
        cover_image=cover_image,
        description=description,
        release_year=release_year,
        running_time=running_time,
        age_limit=age_limit,
        zip_file=zip_file,
        movie_type=movie_type, 
        meta_keywords=meta_keywords,
        background=background,
        db=db
    )


@router.put('/{id}/add-episodes/', status_code=status.HTTP_200_OK)
async def add_episodes(
    id: int, 
    episodes: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    return await services.add_episodes(id=id, episodes=episodes, db=db)


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
async def create_links(
    request: schemas.DownloadLink, 
    movieId: int = Header(...), 
    db: Session = Depends(get_db)
):
    return await services.create_links(request, movieId, db)


@router.put('/{id}/download-links/', status_code=status.HTTP_200_OK)
async def update_link(request: schemas.DownloadLink, id: int, db: Session = Depends(get_db)):
    return await services.update_link(request, id, db)


@router.get('/{id}/download-links/', status_code=status.HTTP_200_OK)
async def get_links(id: int, idlink: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.get_links(id, idlink, db)


@router.get('/download-links/{id}/activate/', status_code=status.HTTP_200_OK)
async def activate_links(id: int, idlink: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.activate_links(id, idlink, db)


@router.delete('/{id}/download-links/', status_code=status.HTTP_200_OK)
async def delete_links(id: int, idlink: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.delete_links(id, idlink, db)


@router.post('/slides/', status_code=status.HTTP_200_OK)
async def create_slide(
    movieId: int = Header(...),
    gallery: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    return await services.create_slide(movieId=movieId, imgs=gallery, db=db)


@router.get('/{id}/slides/')
async def get_slides(id: int, idSlide: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.get_slides(id=id, idSlide=idSlide, db=db)


@router.delete('/{id}/slides/')
async def delete_slide(id: int, idSlide: Optional[int] = Header(None), db: Session = Depends(get_db)):
    return await services.delete_slide(id, idSlide, db)