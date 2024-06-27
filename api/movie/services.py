from fastapi import HTTPException, status, UploadFile, Request, BackgroundTasks
from sqlalchemy import select, func, text, or_, and_
from sqlalchemy.orm import Session
from typing import List, Optional
from PIL import Image
import io, os, time, math, aiofiles, py7zr, zipfile, shutil

from core.models import Movie, GenreMovie, Genre, Langue, Comment, DownloadLink, Slide
from movie import responses


BASE_MEDIA_URL = "./media"
TEMP_DIR = os.path.join(BASE_MEDIA_URL, 'temp')
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
    temp_zip_file_path = os.path.join(TEMP_DIR, f"{int(time.time())}_{zip_filename}")
    
    async with aiofiles.open(temp_zip_file_path, 'wb') as f:
        while True:
            chunk = await zip_file.read(1024 * 1024)  # Lire en chunks de 1MB
            if not chunk:
                break
            await f.write(chunk)
            
    if not os.path.isfile(temp_zip_file_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save videos file temporarily.'
        )
        
    zip_file_path = os.path.join(base_media_url, 'videos', zip_filename)
    os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
    
    shutil.move(temp_zip_file_path, zip_file_path)
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
            detail='Width of the player image must not be less than 1000 px'
        )
    
    if p_height < 500:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Height of the player image must not be less than 500 px'
        )
    
    new_p_image = Image.open(io.BytesIO(img_player))
    new_p_image = new_p_image.resize((1110, 624))
    
    cover_p_extension = cover_player.content_type.split('/')[1]
    if cover_p_extension not in ['jpeg', 'jpg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover player type should be either jpeg or jpg.'
        )
        
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    temp_cover_p_filename = f'{timestamp}_p_temp.{cover_p_extension}'
    temp_cover_p_path = os.path.join(TEMP_DIR, temp_cover_p_filename)
    
    new_p_image.save(temp_cover_p_path)
    if not os.path.isfile(temp_cover_p_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save cover player temporarily.'
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

    # Lire et redimensionner l'image
    new_image = Image.open(io.BytesIO(cover_image_content))
    new_image = new_image.resize((190, 270))

    cover_image_extension = cover_image.content_type.split('/')[1]
    if cover_image_extension not in ['jpeg', 'jpg']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Cover image type should be either jpeg ou jpg.'
        )

    temp_cover_image_filename = f'{timestamp}_cover_temp.{cover_image_extension}'
    temp_cover_image_path = os.path.join(TEMP_DIR, temp_cover_image_filename)
    
    new_image.save(temp_cover_image_path)
    if not os.path.isfile(temp_cover_image_path):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to save cover image temporarily.'
        )
    
    cover_image_filename = f'{timestamp}.{cover_image_extension}'
    cover_image_path = os.path.join(BASE_MEDIA_URL, 'images', cover_image_filename)        
    
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
    shutil.move(temp_cover_p_path, cover_p_path)
    shutil.move(temp_cover_image_path, cover_image_path)

    # Vérification si les images ont bien été sauvegardées
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

    
async def update_movie(
    id: int, 
    db: Session,
    background: BackgroundTasks,
    cover_player: Optional[UploadFile] = None,
    genreId: Optional[List[int]] = None,
    langueId: Optional[int] = None,
    title: Optional[str] = None,
    cover_image: Optional[UploadFile] = None,
    zip_file: Optional[UploadFile] = None,
    movie_type: Optional[str] = None,
    description: Optional[str] = None,
    release_year: Optional[str] = None,
    running_time: Optional[str] = None,
    age_limit: Optional[str] = None,
    meta_keywords: Optional[str] = None
) -> str:
    timestamp = int(time.time())
    movie = (
        db.query(Movie)
        .filter(Movie.id != id)
        .filter(func.lower(Movie.title) == title.lower(), Movie.langueId == langueId)
        .first()
    )
    if movie:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='This movie already exists.'
        )
     
    if title:
        movie.title = title 
        
    if description:
        movie.description = description
        
    if release_year:
        movie.release_year = release_year
        
    if running_time:
        movie.running_time = running_time
        
    if age_limit:
        movie.age_limit = age_limit
        
    if meta_keywords:
        movie.meta_keywords = meta_keywords
       
    if cover_player:
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
            
        os.makedirs(TEMP_DIR, exist_ok=True)
        
        temp_cover_p_filename = f'{timestamp}_p_temp.{cover_p_extension}'
        temp_cover_p_path = os.path.join(TEMP_DIR, temp_cover_p_filename)
        
        new_p_image.save(temp_cover_p_path)
        if not os.path.isfile(temp_cover_p_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to save cover player temporarily.'
            )
            
        cover_p_filename = f'{timestamp}_p.{cover_p_extension}'
        cover_p_path = os.path.join(BASE_MEDIA_URL, 'images', cover_p_filename)
        
        shutil.move(temp_cover_p_path, cover_p_path)
        
        if not os.path.isfile(cover_p_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to save cover player.'
            )
        movie.cover_player = cover_p_filename
    
    if genreId:
        for genre_id in genreId:
            if not db.query(Genre).filter(Genre.id == genre_id).first():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="This genre doesn't exist."
                )
        
        db.query(GenreMovie).filter(GenreMovie.movieId == movie.id).delete()
        db.commit()
        
        for genre_id in genreId:
            new_genre_movie = GenreMovie(genreId=genre_id, movieId=movie.id)
            db.add(new_genre_movie)

    if langueId:
        if not db.query(Langue).filter(Langue.id == langueId).first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="This language doesn't exist."
            )
        movie.langueId = langueId
            
    if movie_type:
        if movie_type.lower() not in ['serie', 'film']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The only two types allowed are serie or film.'
            )
        movie.movie_type = movie_type
    
    if cover_image:
        if cover_image.size > 1 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cover image size should not exceed 1MB.'
            )
        
        cover_image_content = await cover_image.read()

        new_image = Image.open(io.BytesIO(cover_image_content))
        new_image = new_image.resize((190, 270))

        cover_image_extension = cover_image.content_type.split('/')[1]
        if cover_image_extension not in ['jpeg', 'jpg']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Cover image type should be either jpeg or jpg.'
            )

        temp_cover_image_filename = f'{timestamp}_temp.{cover_image_extension}'
        temp_cover_image_path = os.path.join(TEMP_DIR, temp_cover_image_filename)
        
        new_image.save(temp_cover_image_path)
        if not os.path.isfile(temp_cover_image_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to save cover image temporarily.'
            )
        
        cover_image_filename = f'{timestamp}.{cover_image_extension}'
        cover_image_path = os.path.join(BASE_MEDIA_URL, 'images', cover_image_filename)
        
        shutil.move(temp_cover_image_path, cover_image_path)
        
        if not os.path.isfile(cover_image_path):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to save cover image.'
            )
        
        movie.cover_image = cover_image_filename 
    
    if zip_file:
        if not (zip_file.filename.endswith('.zip') or zip_file.filename.endswith('.rar')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The file must have a zip or rar extension.'
            )
        
        if zip_file.filename.endswith('.zip'):
            zip_filename = f'{timestamp}.zip'
        else:
            zip_filename = f'{timestamp}.rar'
        
        background.add_task(save_large_file(zip_file, zip_filename, BASE_MEDIA_URL))
        movie.zip_file = zip_filename 
        
    db.commit()
    db.refresh(movie)
    return 'Movie is updated successfully!'
        
    
    
async def add_episodes(
    id: int, 
    db: Session,
    episodes: Optional[List[UploadFile]] = None
) -> str:
    movie = db.query(Movie).filter(Movie.id == id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This identifier does not belong to any film in the database!'
        )
        
    movie_file = os.path.join(BASE_MEDIA_URL, 'videos', movie.zip_file)
    
    if not os.path.isfile(movie_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This film has no files!'
        )
        
    supported_extensions = ['mp4', 'mkv', 'webm', 'flv']
    
     # Ensure the temporary directory exists
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    with zipfile.ZipFile(movie_file, 'a') as zipf:
        for episode in episodes:
            episode_extension = episode.filename.split('.')[-1]
            if episode_extension not in supported_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f'Unsupported file extension: {episode_extension}. Only mp4, mkv, webm, and flv are supported.'
                )
            episode_name = episode.filename
            episode_path = os.path.join(TEMP_DIR, episode_name)
            
             # Save the episode temporarily to add to zip
            with open(episode_path, 'wb') as temp_file:
                temp_file.write(await episode.read())
                
            # Add the file to the zip
            zipf.write(episode_path, arcname=episode_name)
            
            # Remove the temporary file
            os.remove(episode_path)
            
    return 'Episodes added successfully.'


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
        
    return query.all()


async def create_links(request: dict, movieId: int, db: Session) -> str:
    new_link = DownloadLink(
        movieId=movieId,
        advertisement=request.advertisement,
        link=request.link
    )
    db.add(new_link)
    db.commit()
    
    return 'Link added successfully.'


async def update_link(request: dict, id: int, db: Session) -> str:
    link = db.query(DownloadLink).filter(DownloadLink.id == id).first()
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This ID does not correspond to any link in our database!'
        )
        
    if request.advertisement:
        link.advertisement = request.advertisement
    if request.link:
        link.link = request.link
        
    db.commit()
    return 'Link is updated successfully!'


async def activate_links(id: int, idLink: Optional[int], db: Session) -> str:
    
    if idLink:
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
    
    links = db.query(DownloadLink).filter(DownloadLink.movieId == id).all()
    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This ID does not correspond to any film in our database!'
        )
        
    for link in links:
        link.is_active = False
        
    db.commit()
    return 'All links have been successfully deactivated!'
    


async def delete_links(id: int, idLink: Optional[int], db: Session) -> str:
    query = db.query(DownloadLink).filter(DownloadLink.movieId == id)
    
    if idLink:
        query = query.filter(DownloadLink.id == idLink)
    
    links_to_delete = query.all()
    
    if not links_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No links found to delete."
        )
        
    for link in links_to_delete:
        db.delete(link)
        
    db.commit()
    return 'Link(s) deleted successfully.'


async def create_slide(movieId: int, imgs: List[UploadFile], db: Session) -> str:
    timestamp = int(time.time())
    index = 0
    movie = db.query(Movie).filter(Movie.id == movieId).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='This ID does not correspond to any film in our database!'
        )
    
    for img in imgs:
        contents = await img.read()
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
    
        if img.size > 1 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Image size should not exceed 1MB.'
            )
        
        img_content = Image.open(io.BytesIO(contents))
        img_content = img_content.resize((1172, 564))
    
        img_extension = img.content_type.split('/')[1]
        if img_extension not in ['jpeg', 'jpg']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Gallery images type should be either jpeg or jpg.'
            )
        img_filename = f'{timestamp+index}.{img_extension}' 
        img_path = os.path.join(BASE_MEDIA_URL, 'slides', img_filename)
        img_content.save(img_path)
        index += 1
        
        new_slide = Slide(movieId=movie.id, img=img_filename)
        db.add(new_slide)
        
    db.commit()
    return 'The slide was successfully saved!'


async def get_slides(id, db, idSlide: Optional[int] = None) -> List[Slide]:
    movie = db.query(Movie).filter(Movie.id == id).first()
    query = db.query(Slide).filter(Slide.movieId == id)
    
    if idSlide:
        query = query.filter(Slide.id == idSlide)
        
    return [{
        'title': movie.title,
        'description': movie.description,
        'slides': query.all()
    }]


async def delete_slide(id: int, idSlide: int, db: Session) -> str:
    query = db.query(Slide).filter(Slide.movieId == id)
    
    if idSlide:
        query = query.filter(Slide.id == idSlide)
        
    slides_to_delete = query.all()
    
    if not slides_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No slides found to delete."
        )
        
    for slide in slides_to_delete:
        db.delete(slide)
        
        image_path = os.path.join(BASE_MEDIA_URL, 'slides', slide.img)
        if os.path.exists(image_path):
            os.remove(image_path)
        
    db.commit()
    return 'Slide(s) deleted successfully.'
