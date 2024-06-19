from pydantic import BaseModel, EmailStr, validator
import re


class User(BaseModel):
    email: EmailStr
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 4:
            raise ValueError('Username must be at least 3 characters long')
        
        if len(v) > 30:
            raise ValueError('Username must be less than 30 characters long')
        
        if not re.match("^[a-zA-Z0-9_]+$", v):
            raise ValueError('Username can only contain alphanumeric characters and underscores')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v or v == '@' or len(v) < 5:
            raise ValueError('Email must be a valid email')
        return v


class ChangePWD(BaseModel):
    pass