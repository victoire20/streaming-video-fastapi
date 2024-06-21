from fastapi import APIRouter, status, Depends, Request, HTTPException, Header
from sqlalchemy.orm import Session
from core.security import oauth2_scheme
from core.database import get_db
from genre import services, schemas


router = APIRouter(
    prefix='/genres',
    tags=['Genre Router'],
    responses={404: {"description": "Not found"}}
)


@router.post('/', dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_201_CREATED)
async def create_genre(request: schemas.Genre, db: Session = Depends(get_db)):
    return await services.create_genre(request, db)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_genres(
    request: Request,
    page: int = Header(1),
    limit: int = Header(10, gt=0, le=100),
    columns: str = Header(None, alias='columns'),
    sort: str = Header(None, alias='sort'),
    filter: str = Header(None, alias='filter'),
    db: Session = Depends(get_db)
):
    columns = 'id-libelle-is_active-created_at-updated_at'
    
    return await services.get_genres(
        request=request, 
        page=page, 
        limit=limit, 
        columns=columns,
        sort=sort, 
        filter=filter, 
        db=db
    )


@router.get('/{id}/', status_code=status.HTTP_200_OK)
async def get_genre(id: int, db: Session = Depends(get_db)):
    return await services.get_genre(id, db)


@router.put('/{id}/', dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_200_OK)
async def update_genre(id: int, request: schemas.Genre, db: Session = Depends(get_db)):
    return await services.update_genre(id, request, db)


@router.get('/{id}/activate/', dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_200_OK)
async def activate_genre(id: int, db: Session = Depends(get_db)):
    return await services.activate_genre(id, db)


@router.delete('/{id}/', dependencies=[Depends(oauth2_scheme)], status_code=status.HTTP_202_ACCEPTED)
async def delete_genre(id: int, db: Session = Depends(get_db)):
    return await services.delete_genre(id, db)