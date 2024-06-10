from fastapi import APIRouter, status, Depends, Header, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import get_token_payload, oauth2_scheme
from core.models import User
from auth import services, responses, schemas


router = APIRouter(
    prefix='/auth',
    tags=['Auth Router'],
    responses={404: {"description": "Not found"}}
)


@router.post("/token", response_model=responses.TokenResponse, status_code=status.HTTP_200_OK)
async def authenticate_user(
    data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    return await services.get_token(data=data, db=db)


@router.post("/refresh", response_model=responses.TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_access_token(refresh_token: str = Header(), db: Session = Depends(get_db)):
    return await services.get_refresh_token(token=refresh_token, db=db)


@router.post("/password-forgotten", status_code=status.HTTP_200_OK)
async def password_forgotten(request: schemas.ChangePWD, db: Session = Depends(get_db)):
    return await services.forgotten_password_user(request, db)


@router.get('/{id}/confirm-reset-pwd', status_code=status.HTTP_200_OK)
async def confirm_reset_pwd(id: int, db: Session = Depends(get_db)):
    return await services.confirm_reset_pwd(id, db)