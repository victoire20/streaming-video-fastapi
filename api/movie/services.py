from fastapi import HTTPException, status, UploadFile, Request, BackgroundTasks
from sqlalchemy import select, func, text, or_, and_
from sqlalchemy.orm import Session
from typing import List, Optional
from PIL import Image
import io, os, time, math, aiofiles, py7zr

from core.models import Movie, GenreMovie, Genre, Langue, Comment, DownloadLink, Slide
from movie import responses


BASE_MEDIA_URL = "./media"
CHUNK_SIZE = 1024 * 1024 # 1 MB chunks, adjust as needed


# Fonction pour convertir le tri
def convert_sort(sort: str) -> str:
    return ','.join(sort.split('-'))


# Function to convert columns
def convert_columns(columns: str) -> List:
    return list(map(lambda x: getattr(Movie, x), columns.split('-')))


def get_image_dimensions(image_data: bytes):
    with Image.open(io.BytesIO(image_data)) as img:
        width, height = img.size
        return width, height


async def save_large_file(zip_file: UploadFile, zip_filename: str, base_media_url: str):
    zip_file_path = os.path.join(base_media_url, 'videos', zip_filename)
    os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
    
    async with aiofiles.open(zip_file_path, 'wb') as f:
        while True:
            chunk = await zip_file.read(CHUNK_SIZE)
            if not chunk:
                break
            await f.write(chunk)
            
    if not os.path.isfile(zip_file_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save videos file.'
        )


async def create_movie(
    cover_player: UploadFile,
    genreId: List[int],
    langueId: int,
    title: str,
    cover_image: UploadFile,
    zip_file: UploadFile,
    movie_type: str,
    db: Session,
    background: BackgroundTasks,
    gallery: Optional[List[UploadFile]] = None,
    description: Optional[str] = None,
    release_year: Optional[str] = None,
    running_time: Optional[str] = None,
    age_limit: Optional[str] = None,
    meta_keywords: Optional[str] = None
) -> str:
    timestamp = int(time.time())
    movie = (
        db.query(Movie)
        .filter(func.lower(Movie.title) == title.lower(), Movie.langueId == langueId)
        .first()
    )
    if movie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This movie already exists.'
        )
        
    if cover_player.size > 1 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover Player size should not exceed 1MB.'
        )
        
    img_player = await cover_player.read()
    p_width, p_height = get_image_dimensions(img_player)
    if p_width < 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Height of the player image must not be greater than 1000 px'
        )
    
    if p_height < 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Height of the player image must not be greater than 624 px'
        )
    
    new_p_image = Image.open(io.BytesIO(img_player))
    new_p_image = new_p_image.resize((1110, 624))
    
    cover_p_extension = cover_player.content_type.split('/')[1]
    if cover_p_extension not in ['jpeg', 'jpg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover player type should be either jpeg or jpg.'
        )
        
    cover_p_filename = f'{timestamp}_p.{cover_p_extension}'
    cover_p_path = os.path.join(BASE_MEDIA_URL, 'images', cover_p_filename)

    for genre_id in genreId:
        if not db.query(Genre).filter(Genre.id == genre_id).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This genre doesn't exist."
            )

    if not db.query(Langue).filter(Langue.id == langueId).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This language doesn't exist."
        )
    
    if movie_type.lower() not in ['serie', 'film']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The only two types allowed are serie or film.'
        )

    # Vérification de la taille de l'image de couverture 1Mo
    if cover_image.size > 1 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover image size should not exceed 1MB.'
        )
        
    # Lire le contenu de l'image en mémoire
    cover_image_content = await cover_image.read()

    # Lire et redimenssionner l'image
    new_image = Image.open(io.BytesIO(cover_image_content))
    new_image = new_image.resize((190, 270))

    cover_image_extension = cover_image.content_type.split('/')[1]
    if cover_image_extension not in ['jpeg', 'jpg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover image type should be either jpeg or jpg.'
        )

    # Création du nom de fichier pour l'image de couverture basé sur le timestamp
    cover_image_filename = f'{timestamp}.{cover_image_extension}'

    # Chemin d'accès pour sauvegarder l'image de couverture
    cover_image_path = os.path.join(BASE_MEDIA_URL, 'images', cover_image_filename)
    galery_filename = []
        
    if gallery:
        for img_gallery in gallery:
            contents = await img_gallery.read()
            width, height = get_image_dimensions(contents)
            if width < 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Width of the gallery image must not be greater than 1000 px'
                )
            
            if height < 500:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Height of the gallery image must not be greater than 500 px'
                )
                
        for img_gallery in gallery:
            # Redimentionner la taille des image de la gallérie
            img_content = Image.open(io.BytesIO(contents))
            img_content = img_content.resize((1172, 564))
            
            img_extension = img_gallery.content_type.split('/')[1]
            if img_extension not in ['jpeg', 'jpg']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Gallery images type should be either jpeg or jpg.'
                )
            img_filename = f'{timestamp}.{img_extension}' 
            img_path = os.path.join(BASE_MEDIA_URL, 'slides', img_filename)
            
            img_content.save(img_path)
            galery_filename.append(img_filename)

    if not zip_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No videos provided.'
        )

    if not (zip_file.filename.endswith('.zip') or zip_file.filename.endswith('.rar')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The file must have a zip or rar extension.'
        )
    
    if zip_file.filename.endswith('.zip'):
        zip_filename = f'{timestamp}.zip'
    else:
        zip_filename = f'{timestamp}.rar'
    
    background.add_task(await save_large_file(zip_file, zip_filename, BASE_MEDIA_URL))
    
    # Sauvegarde de l'image de couverture
    new_p_image.save(cover_p_path)
    new_image.save(cover_image_path)

    # Vérification si les images ont bien été sauvegardée
    if not os.path.isfile(cover_image_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save cover image.'
        )
    if not os.path.isfile(cover_p_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save cover player.'
        )
        
    new_movie = Movie(
        cover_player=cover_p_filename,
        langueId=langueId,
        title=title,
        cover_image=cover_image_filename,
        description=description,
        release_year=release_year,
        running_time=running_time,
        age_limit=age_limit,
        movie_type=movie_type,
        zip_file=zip_filename,
        meta_keywords=meta_keywords
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)

    for genre_id in genreId:
        new_genre_movie = GenreMovie(genreId=genre_id, movieId=new_movie.id)
        db.add(new_genre_movie)
        db.commit()
        
    if gallery:
        for img_g in galery_filename:
            new_img_g = Slide(movieId=new_movie.id, img=img_g)
            db.add(new_img_g)
            db.commit()

    return "Movie created successfully."


async def get_movies(
    request: Request, 
    page: int, 
    limit: int, 
    db: Session,
    columns: Optional[str] = None, 
    sort: Optional[str] = None, 
    filter: Optional[str] = None
):
    criteria_list = []

    default_columns = [
        Movie.id, 
        Movie.title, 
        Movie.cover_image,
        Movie.views,
        Movie.is_active,
        Movie.release_year,
        Movie.running_time,
        Movie.langueId,
        Movie.age_limit,
        Movie.movie_type,
        Movie.rate,
        Movie.created_at,
        Movie.updated_at
    ]
    
    if columns and columns != "all":
        selected_columns = convert_columns(columns)
        if not selected_columns:
            selected_columns = default_columns
    else:
        selected_columns = default_columns
        
    query = select(*selected_columns).select_from(Movie)

    if filter and filter != "null":
        criteria = dict(x.split("*") for x in filter.split('-'))
        for attr, value in criteria.items():
            _attr = getattr(Movie, attr)
            search = "%{}%".format(value)
            criteria_list.append(_attr.like(search))
        query = query.where(or_(*criteria_list))
    
    if sort and sort != "null":
        query = query.order_by(text(convert_sort(sort)))

    count_query = select(func.count()).select_from(Movie).where(
        or_(*criteria_list) if criteria_list else True
    )
    total_record = (db.execute(count_query)).scalar() or 0
    
    total_page = math.ceil(total_record / limit)
    offset_page = (page - 1) * limit

    query = query.offset(offset_page).limit(limit)
    
    result = db.execute(query)
    all_movies = result.fetchall()

    results = []
    for row in all_movies:
        movie_data = {}
        for col in selected_columns:
            # Accéder directement à l'attribut de la ligne
            movie_data[col.name] = getattr(row, col.name)
            
        movie_language = db.query(Langue).filter(Langue.id == row.langueId).first()
        movie_genres = db.query(GenreMovie).filter(GenreMovie.movieId == row.id).all()
        genre_data = []
        for g in movie_genres:
            genre = db.query(Genre).filter(Genre.id == g.genreId).first()
            genre_data.append({
                'id': genre.id,
                'libelle': genre.libelle
            })
        
        # comments = db.query(Comment).filter(Comment.userId == row.id).all()
        # movie_data['comments_count'] = len(comments)
        
        # favorites = db.query(Favorite).filter(Favorite.userId == row.id).all()
        # movie_data['favorites_count'] = len(favorites)
        
        # movie_data['comments'] = comments
        # movie_data['favorites'] = favorites
        
        movie_data['language'] = {
            'id': movie_language.id,
            'libelle': movie_language.libelle.title()
        }
        movie_data['genres'] = genre_data
        
        results.append(movie_data)

    return responses.PaginatedResponse(
        page_number=page,
        page_size=limit,
        total_pages=total_page,
        total_record=total_record,
        contents=results
    )


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
    
    if movie.is_active == 'running':
        movie.is_active = 'close'
    else:
        movie.is_active = 'running'
    db.commit()
    db.refresh(movie)
    
    if movie.is_active:
        return 'Movie is activated successfully.'
    return 'Movie is deactivated successfully.'


async def delete_movie(id: int, db: Session) -> str:
    movie = await get_movie(id, db)
    db.delete(movie)
    db.commit()
    
    return 'Movie is deleted successfully'
    
    
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