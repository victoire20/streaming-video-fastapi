from fastapi import Depends, status, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from core.models import User
from core.security import verify_password, get_password_hash
from core.config import get_settings
from datetime import timedelta
from core.security import create_access_token, create_refresh_token, get_token_payload
from auth.responses import TokenResponse

from datetime import datetime
from email.message import EmailMessage
import string, smtplib


settings = get_settings()


async def create_profil(request: dict, db: Session):
    if db.query(User).filter(User.email == request.email.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This email already used.'
        )
    
    if db.query(User).filter(User.username == request.username.lower()).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This username already used.'
        )
        
    new_user = User(
        email=request.email.lower(),
        username=request.username.lower(),
        password=get_password_hash(request.password),
        is_admin=False,
        is_active=False,
        is_verified=False,
    )
    db.add(new_user)
    db.commit()
    
    # Send Email To vérify profil
    
    return 'User successfully created. Please confirm your registration in your mailbox to be able to connect!'


def _verify_user_access(user: User):
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # if not user.is_verified:
    #     # Trigger user account verification email
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Your account is unverified. We have resend the account verification email.",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )


async def get_token(data: dict, db: Session):
    user = db.query(User).filter(User.username == data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is not registered in our database.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    _verify_user_access(user=user)
    
    if user.first_connection is None:
        user.first_connection = datetime.utcnow()
        
    user.last_connection = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return await _get_user_token(user=user)


async def get_refresh_token(token, db):
    payload =  get_token_payload(token=token)
    user_id = payload.get('id', None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return await _get_user_token(user=user, refresh_token=token)


async def _get_user_token(user: User, refresh_token = None):
    payload = {"serial_number": user.id}
    
    access_token_expiry = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = await create_access_token(payload, access_token_expiry)
    if not refresh_token:
        refresh_token = await create_refresh_token(payload)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=access_token_expiry.seconds  # in seconds
    )


async def forgotten_password_user(request: dict, db: Session):
    user = db.query(User).filter(User.username == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.password = get_password_hash(new_password)
    
    # Send new password in email
    smtp_server = settings.EMAIL_SERVER
    smtp_port = settings.EMAIL_PORT
    smtp_username = settings.EMAIL_TRANSFERT_REQUEST
    smtp_password = settings.EMAIL_PASSWORD_TRANSFERT_REQUEST
    
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('email.html')

    subject = 'Your New Password'
    html_content = template.render(new_password=new_password)
    
    em = EmailMessage()                    
    em['From'] = smtp_username
    em['To'] = [user.email]
    em['Subject'] = subject
    em.set_content(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(em)

        user.is_active = False
        db.commit()
        return 'Please check your mail to confirm this operation!'
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to send email"
        )
        
        
async def confirm_reset_pwd(id: int, db: Session):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = True
    db.commit()
    return RedirectResponse(url='http://127.0.0.1:8001/login')