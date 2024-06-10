import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

class Settings(BaseSettings):
    
    APP_ENV: str = os.getenv('APP_ENV', 'development')
    BASE_URL: str = os.getenv('BASE_URL', 'http://api.zoneanimee.com')
    
    # Datatbase
    DB_USER: str = os.getenv('DATABASE_USER')
    DB_PASSWORD: str = os.getenv('DATABASE_PASSWORD')
    DB_NAME: str = os.getenv('DATABASE_DB')
    DB_NAME_TEST: str = os.getenv('DATABASE_DB_TEST')
    DB_HOST: str = os.getenv('DATABASE_SERVER')
    DB_PORT: str = os.getenv('DATABASE_PORT')
    # DATABASE_URL: str = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME_TEST}"
    DATABASE_URL: str = "sqlite:///./zoneanimee.db"
    
    # JWT 
    JWT_SECRET: str = os.getenv('JWT_SECRET')
    JWT_ALGORITHM: str = os.getenv('JWT_ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv('JWT_TOKEN_EXPIRE_MINUTES')
    COOKIE_NAME: str = os.getenv('COOKIE_NAME')
    
    # Email
    EMAIL_USER: str = os.getenv('EMAIL_USER', 'noreply@doubleclic-tech.com')
    EMAIL_PASSWORD: str = os.getenv('EMAIL_PASSWORD', '!j8GXPwqm')
    EMAIL_FROM: str = os.getenv('EMAIL_FROM', 'noreply@doubleclic-tech.com')
    
    EMAIL_SERVER: str = os.getenv('EMAIL_SERVER', 'mail.doubleclic-tech.com')
    EMAIL_PORT: int = os.getenv('PORT', 587)
    
def get_settings() -> Settings:
    return Settings()