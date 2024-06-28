from fastapi import APIRouter, status, Depends, Request, HTTPException, Header, Form, File
from sqlalchemy.orm import Session
from core.database import get_db
from movie import services, schemas, responses
from typing import Optional, List
import os


BASE_MEDIA_URL = "./media"


router = APIRouter(
    prefix='/filemanagers',
    tags=['File Manager Router'],
    responses={404: {"description": "Not found"}}
)


@router.get('/', status_code=status.HTTP_200_OK)
async def get_media_folder():
    try:
        folder_details = []
        folder_count = 0
        for name in os.listdir(BASE_MEDIA_URL):
            folder_path = os.path.join(BASE_MEDIA_URL, name)
            if os.path.isdir(folder_path):
                folder_count += 1
                file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
                folder_details.append({'folder_names': name.title(), 'file_count': file_count})
                
        return {'folder_count': folder_count, 'folders': folder_details}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'An error occurd while accessing the media folder: {e}'
        )