from fastapi import APIRouter, status, Depends, Request, HTTPException, Header, Form, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from core.database import get_db
from core.models import Movie
from typing import Optional, List
import os


BASE_MEDIA_URL = "./media"


router = APIRouter(
    prefix='/filemanagers',
    tags=['File Manager Router'],
    responses={404: {"description": "Not found"}}
)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_media_folder(folder_name: Optional[str] = Header(None)):
    try:
        if not folder_name:
            folder_details = []
            folder_count = 0
            for name in os.listdir(BASE_MEDIA_URL):
                folder_path = os.path.join(BASE_MEDIA_URL, name)
                if os.path.isdir(folder_path):
                    folder_count += 1
                    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                    file_count = len(files)
                    folder_details.append({'folder_names': name.title(), 'file_count': file_count, 'files': files})
                    
            return {'folder_count': folder_count, 'folders': folder_details}
        
        folder_details = []
        folder_count = 0
        for name in os.listdir(f'{BASE_MEDIA_URL}/{folder_name.lower()}'):
            folder_path = os.path.join(f'{BASE_MEDIA_URL}/{folder_name.lower()}', name)
            if os.path.isdir(folder_path):
                folder_count += 1
                files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                file_count = len(files)
                folder_details.append({'folder_names': name.title(), 'file_count': file_count, 'files': files})
                
        return {'folder_count': folder_count, 'folders': folder_details}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred while accessing the media folder: {e}'
        )
        
        
@router.get('/{filename}/', status_code=status.HTTP_200_OK)
async def get_file_details(filename: str, db: Session = Depends(get_db)):
    movie = (
        db.query(Movie)
        .filter(
            or_(Movie.zip_file == filename, 
                Movie.cover_image == filename,
                Movie.cover_player == filename
            )
        )
        .first()
    )
    if movie:
        return {'is_used': True}
    return {'is_used': False}


@router.get('/{foldername}/', status_code=status.HTTP_202_ACCEPTED)
async def delete_folder(foldername: str):
    folder_path = os.path.join(BASE_MEDIA_URL, foldername)
    
    if not os.path.exists(folder_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The folder {foldername} does not exist.'
        )
        
    if os.listdir(folder_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'The folder {foldername} is not empty.'
        )
        
    try:
        os.rmdir(folder_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occured while deleting the folder: {e}'
        )
        
    return {'details': f'The folder {foldername} has been successfully deleted.'}
