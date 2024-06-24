from fastapi import APIRouter, status, Depends, Request, HTTPException, Header, Form, File, UploadFile
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from core.database import get_db
from movie import services, schemas, responses
from typing import Optional, List


router = APIRouter(
    prefix='/movies',
    tags=['Movies Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_movie(
    background: BackgroundTasks,
    genreId: List[int] = Form(...),
    langueId: int = Form(...),
    title: str = Form(...),
    cover_image: UploadFile = Form(...),
    description: Optional[str] = Form(None),
    release_year: Optional[str] = Form(None),
    running_time: Optional[str] = Form(None),
    age_limit: Optional[str] = Form(None),
    gallery: Optional[List[UploadFile]] = File(None),
    zip_file: UploadFile = Form(...),
    movie_type: str = Form(...),
    meta_keywords: str = Form(...),
    db: Session = Depends(get_db)
):
    return await services.create_movie(
        genreId=genreId,
        langueId=langueId,
        title=title,
        cover_image=cover_image,
        description=description,
        release_year=release_year,
        running_time=running_time,
        age_limit=age_limit,
        gallery=gallery,
        zip_file=zip_file,
        movie_type=movie_type, 
        meta_keywords=meta_keywords,
        background=background,
        db=db
    )


@router.get('/', status_code=status.HTTP_200_OK)
async def get_movies(
    request: Request,
    page: int = Header(1),
    limit: int = Header(10, gt=0, le=100),
    columns: str = Header(None, alias="columns"),
    sort: str = Header(None, alias='sort'),
    filter: str = Header(None, alias='filter'),
    db: Session = Depends(get_db)
):
    return await services.get_movies(
        request=request, 
        page=page, 
        limit=limit, 
        columns=columns, 
        sort=sort, 
        filter=filter, 
        db=db
    )


@router.get('/{id}/', response_model=responses.MovieResponse, status_code=status.HTTP_200_OK)
async def get_movie(id: int, db: Session = Depends(get_db)):
    return await services.get_movie(id, db)


# @router.put('/{id}/', status_code=status.HTTP_200_OK)
# async def update_movie(id: int, request: schemas.Movie, db: Session = Depends(get_db)):
#     return await services.update_movie(id, request, db)


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