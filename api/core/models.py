from sqlalchemy import Column, Boolean, String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, Session
from datetime import datetime

from core.database import Base, get_db


class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(300), unique=True)
    username = Column(String(30), unique=True)
    password = Column(String(300))
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    first_connection = Column(DateTime, nullable=True, default=None)
    last_connection = Column(DateTime, nullable=True, default=None)
    registered_at = Column(DateTime, nullable=False, server_default=func.now())
    
    comments = relationship('Comment', back_populates='user')
    favorites = relationship('Favorite', back_populates='user')
    
    
class Genre(Base):
    __tablename__ = "genres"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    libelle = Column(String(200), unique=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    
    genre_movie = relationship('GenreMovie', back_populates='genre')
    
    
class Langue(Base):
    __tablename__ = "languages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    libelle = Column(String(200), unique=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    
    movie = relationship('Movie', back_populates='langue')
    
    
class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    langueId = Column(Integer, ForeignKey('languages.id', ondelete="CASCADE", onupdate="CASCADE"))
    title = Column(String(200))
    cover_image = Column(String(300), nullable=True, default=None)
    meta_keywords = Column(String(500), nullable=True, default=None)
    description = Column(String(300), nullable=True, default=None)
    release_year = Column(String(4), nullable=True, default=None)
    running_time = Column(String(12), nullable=True, default=None)
    age_limit = Column(String(2), nullable=True, default=None)
    movie_type = Column(String(5)) # serie or film
    zip_file = Column(String(200))
    rate = Column(Float, nullable=True, default=0)
    views = Column(Integer, nullable=True, default=0)
    is_active = Column(String(7), default='running') # running, close
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, default=None, onupdate=datetime.now)
    
    genre_movie = relationship('GenreMovie', back_populates='movie')
    langue = relationship('Langue', back_populates='movie')
    download_links = relationship('DownloadLink', back_populates='movie')
    comments = relationship('Comment', back_populates='movie')
    favorites = relationship('Favorite', back_populates='movie')
    
    
class GenreMovie(Base):
    __tablename__ = "genre_movies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    genreId = Column(Integer, ForeignKey('genres.id', ondelete="CASCADE", onupdate="CASCADE"))
    movieId = Column(Integer, ForeignKey('movies.id', ondelete="CASCADE", onupdate="CASCADE"))
    
    genre = relationship('Genre', back_populates='genre_movie')
    movie = relationship('Movie', back_populates='genre_movie')
    
    
class DownloadLink(Base):
    __tablename__ = "download_links"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movieId = Column(Integer, ForeignKey('movies.id', ondelete="CASCADE", onupdate="CASCADE"))
    advertisement = Column(String(100), nullable=True, default=None)
    link = Column(String(500))
    is_active = Column(Boolean, default=True)
    
    movie = relationship('Movie', back_populates='download_links')
    
    
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parentId = Column(Integer, ForeignKey('comments.id', ondelete="CASCADE", onupdate="CASCADE"), nullable=True, default=None)
    userId = Column(Integer, ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"))
    movieId = Column(Integer, ForeignKey('movies.id', ondelete="CASCADE", onupdate="CASCADE"))
    content = Column(String(300))
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    parent = relationship('Comment', remote_side=[id], back_populates='replies')
    user = relationship('User', back_populates='comments')
    movie = relationship('Movie', back_populates='comments')
    replies = relationship('Comment', back_populates='parent', cascade="all, delete-orphan")
    
    
class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    userId = Column(Integer, ForeignKey('users.id', ondelete="CASCADE", onupdate="CASCADE"))
    movieId = Column(Integer, ForeignKey('movies.id', ondelete="CASCADE", onupdate="CASCADE"))
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    user = relationship('User', back_populates='favorites')
    movie = relationship('Movie', back_populates='favorites')
    
    