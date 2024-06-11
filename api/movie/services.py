from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import and_
from typing import List, Optional
import os, time

from core.models import Movie, GenreMovie, Genre, Langue, Comment, DownloadLink


BASE_MEDIA_URL = "./media"


async def create_movie(request: dict, db: Session) -> str:
    movie = (
        db.query(Movie)
        .filter(Movie.title == request['title'].lower(), Movie.langueId == request['langueId'])
        .first()
    )
    if movie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This movie already exists.'
        )

    if not db.query(Genre).filter(Genre.id == request['genreId']).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This genre doesn't exist."
        )

    if not db.query(Langue).filter(Langue.id == request['langueId']).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This language doesn't exist."
        )

    if request['movie_type'].lower() not in ['serie', 'film']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The only two types allowed are serie or film.'
        )

    # Vérification de la taille de l'image de couverture
    if len(request['cover_image']) > 1 * 1024 * 1024:  # Assuming 'cover_image' is a byte string
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover image size should not exceed 1MB.'
        )

    cover_image_extension = request['cover_image'].type.split('/')[-1]
    if cover_image_extension not in ['jpeg', 'jpg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover image type should be either jpeg or jpg.'
        )

    # Création du nom de fichier pour l'image de couverture basé sur le timestamp
    timestamp = int(time.time())
    cover_image_filename = f'{timestamp}.{cover_image_extension}'

    # Chemin d'accès pour sauvegarder l'image de couverture
    cover_image_path = os.path.join(BASE_MEDIA_URL, 'images', cover_image_filename)

    # Sauvegarde de l'image de couverture
    with open(cover_image_path, 'wb') as f:
        f.write(request['cover_image'].file.read())

    # Vérification si l'image de couverture a bien été sauvegardée
    if not os.path.isfile(cover_image_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save cover image.'
        )

    # Vérification de la liste de vidéos
    videos_list = request.get('videos_list', [])
    if not videos_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No videos provided.'
        )

    # Vérification de l'extension des vidéos
    allowed_video_extensions = ['mp4', 'ts', 'mkv']
    for video in videos_list:
        video_extension = video.type.split('/')[-1]
        if video_extension not in allowed_video_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Video format not supported. Supported formats: {", ".join(allowed_video_extensions)}.'
            )

    # Création du fichier ZIP contenant les vidéos
    zip_file = f'{timestamp}.zip'
    zip_file_path = os.path.join(BASE_MEDIA_URL, 'videos', zip_file)
    with open(zip_file_path, 'wb') as zipf:
        for video in videos_list:
            zipf.write(video.file.read())

    new_movie = Movie(
        langueId=request['langueId'],
        title=request['title'],
        cover_image=cover_image_path,
        description=request.get('description'),
        release_year=request.get('release_year'),
        running_time=request.get('running_time'),
        age_limit=request.get('age_limit'),
        movie_type=request['movie_type'],
        zip_file=zip_file_path,
    )
    db.add(new_movie)
    db.commit()

    new_genre_movie = GenreMovie(
        genreId=request['genreId'],
        movieId=new_movie.id
    )
    db.add(new_genre_movie)
    db.commit()

    return "Movie created successfully."


async def get_movies(db: Session) -> List[Movie]:
    return db.query(Movie).all()


async def get_movie(id: int , db: Session) -> Movie:
    movie = db.query(Movie).filter(Movie.id == id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This movie don\'t exist.'
        )
        
    return movie


async def update_movie(id: int, request: dict, db: Session) -> str:
    movie = await get_movie(id, db)


async def activate_movie(id: int, db: Session) -> str:
    movie = await get_movie(id, db)
    
    movie.is_active = not movie.is_active
    db.commit()
    db.refresh(movie)
    
    if movie.is_active:
        return 'Movie is activated successfully.'
    return 'Movie is deactivated successfully.'


async def delete_movie(id: int, db: Session) -> str:
    movie = await get_movie(id, db)
    
    
async def get_comments(id: int, idComment: Optional[int], db: Session) -> List[Comment]:
    query = db.query(Comment).filter(Comment.movieId == id)
    
    if idComment:
        query = query.filter(Comment.id == idComment)
        
    return query


async def delete_comments(id: int, idComment: Optional[int], db: Session) -> str:
    query = db.query(Comment).filter(Comment.movieId == id)
    
    if idComment:
        query = query.filter(Comment.id == idComment)
        
    if idComment:
        query = query.filter(Comment.id == idComment)
    
    comments_to_delete = query.all()
    
    if not comments_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No comments found to delete."
        )
        
    for comment in comments_to_delete:
        db.delete(comment)
        
    db.commit()
    return 'Comment(s) deleted successfully.'


async def get_links(id: int, idLink: Optional[int], db: Session) -> List[DownloadLink]:
    query = db.query(DownloadLink).filter(DownloadLink.movieId == id)
    
    if idLink:
        query = query.filter(DownloadLink.id == idLink)
        
    return query


async def create_links(request: dict, db: Session) -> str:
    new_link = DownloadLink(
        movieId=request.movieId,
        advertisement=request.advertisement,
        link=request.link
    )
    db.add(new_link)
    db.commit()
    
    return 'Link added successfully.'


async def activate_links(id: int, idLink: int, db: Session) -> str:
    links = await get_links(id, idLink, db)
    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Link not found.'
        )
    
    link = links[0]
    link.is_active = not link.is_active
    db.commit()
    db.refresh(link)
    
    if link.is_active:
        return 'Link activated successfully.'
    return 'Link deactivated successfully.'


async def delete_links(id: int, idLink: Optional[int], db: Session) -> str:
    query = db.query(DownloadLink).filter(DownloadLink.movieId == id)
    
    if idLink:
        query = query.filter(DownloadLink.id == idLink)
        
    if idLink:
        query = query.filter(DownloadLink.id == idLink)
    
    links_to_delete = query.all()
    
    if not links_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No comments found to delete."
        )
        
    for link in links_to_delete:
        db.delete(link)
        
    db.commit()
    return 'Link(s) deleted successfully.'