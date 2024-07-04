from fastapi import APIRouter, status, Depends, Request, HTTPException, Header, Form, File
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_
from core.database import get_db
from core.models import Movie, Slide
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


@router.get('/{foldername}/delete-folder', status_code=status.HTTP_202_ACCEPTED)
async def delete_folder(foldername: str):
    folder_path = os.path.join(BASE_MEDIA_URL, foldername.lower())
    
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


@router.get('/{fileName}/delete-file', status_code=status.HTTP_202_ACCEPTED)
async def delete_file(fileName: str, folderName: str = Header(...), db: Session = Depends(get_db)):
    # Ensure the folder name is sanitized and doesn't contain any unexpected characters
    if folderName not in ['videos', 'images', 'slides', 'slide']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid folder name: {folderName}"
        )

    # Construct the path URL using the folderName
    path_url = os.path.join(BASE_MEDIA_URL, folderName)
    file_path = os.path.join(path_url, fileName.lower())

    # Check if the file is being used in the database
    if folderName in ['videos', 'images']:
        data = (
            db.query(Movie)
            .filter(or_(
                    Movie.cover_image == fileName.lower(), 
                    Movie.cover_player == fileName.lower(),
                    Movie.zip_file == fileName.lower()
                ))
            .first()
        )
        if data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='This image is used in the movie table'
            )
            
    if folderName in ['slides', 'slide']:
        if db.query(Slide).filter(Slide.img == fileName.lower()).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='This image is used in the slide table'
            )
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'The file {fileName} does not exist.'
        )
        
    # Check if the directory is empty
    if os.path.isdir(file_path) and os.listdir(file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'The folder {fileName} is not empty.'
        )
        
    try:
        os.remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurred while deleting the file: {e}'
        )
        
    return {'details': f'The file {fileName} has been successfully deleted.'}