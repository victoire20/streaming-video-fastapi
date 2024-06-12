from pathlib import Path
from fastapi import FastAPI, Request, Response, Header, status, HTTPException
from starlette.middleware.authentication import AuthenticationMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn, zipfile, io, os, ffmpeg
from core.security import JWTAuth, get_current_user

from auth import router as auth_router
from user import router as user_router
from genre import router as genre_router
from langue import router as langue_router
from movie import router as movie_router

from typing import Optional


app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name="static")

origins = [
    'http://127.0.0.1:8000',
    'http://127.0.0.1:8001',
    'http://127.0.0.1:8002'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(user_router.router)
app.include_router(genre_router.router)
app.include_router(langue_router.router)
app.include_router(movie_router.router)


CHUNK_SIZE = 10*1024*1024 # 10 MB


@app.get('/', status_code=status.HTTP_200_OK)
async def index_root():
    return {'message': 'API Running'}


@app.get('/categories', status_code=status.HTTP_200_OK)
async def get_categories(request: Request):
    categories = [
        {'id': 1, 'name': 'Action', 'is_active': True},
        {'id': 2, 'name': 'Adventure', 'is_active': True},
        {'id': 3, 'name': 'Horror', 'is_active': True},
        {'id': 4, 'name': 'Romance', 'is_active': False},
        {'id': 5, 'name': 'Comic', 'is_active': True}
    ]
    return categories


@app.get('/{video_name}/videos')
async def read_all_video(
    request: Request,
    video_name: str,
    range: str = Header(None)
):
    serie_name = f'media/videos/{video_name}.zip'
    
    if not os.path.isfile(serie_name):
        return JSONResponse(content={"error": "Video not found"}, status_code=404)
    
    try:
        with zipfile.ZipFile(serie_name, 'r') as listzip:
            file_list = listzip.namelist()
        
        results = []
        for result in file_list:
            results.append({
                'name': result.split('.')[0].split('_')[0],
                'duration': f"{result.split('.')[0].split('_')[1]}:{result.split('.')[0].split('_')[2]}"
            })
        return results
    except zipfile.BadZipFile:
        return JSONResponse(content={"error": "Bad zip file"}, status_code=400)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Episode not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get('/{video_name}/{eps_name}/video')
async def read_zip_file(
    request: Request, 
    video_name: str,
    eps_name: str,
    range: str = Header(None)
):
    serie_name = f'media/videos/{video_name}.zip'
    
    if not os.path.isfile(serie_name):
        return JSONResponse(content={"error": "Video not found"}, status_code=404)
    
    try:
        with zipfile.ZipFile(serie_name, 'r') as listzip:
            file_list = listzip.namelist()

            # Vérifier si le fichier demandé est dans la liste
            video_file = None
            for file in file_list:
                if file.lower().startswith(eps_name.lower()):
                    video_file = file
                    break

            if not video_file:
                return JSONResponse(content={"error": "Episode not found"}, status_code=404)

            # Lire le fichier vidéo en mémoire
            with listzip.open(video_file) as video:
                video_data = video.read()

            # Déterminer la plage à lire
            start, end = 0, CHUNK_SIZE
            if range:
                range = range.replace("bytes=", "")
                parts = range.split("-")
                start = int(parts[0])
                end = int(parts[1]) if len(parts) > 1 and parts[1] else start + CHUNK_SIZE

            end = min(end, len(video_data) - 1)

            # Lire la plage de bytes spécifiée
            data = video_data[start:end + 1]
            filesize = len(video_data)

            headers = {
                'Content-Range': f'bytes {start}-{end}/{filesize}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(len(data))
            }
            return Response(content=data, status_code=206, headers=headers, media_type="video/mp4")

    except zipfile.BadZipFile:
        return JSONResponse(content={"error": "Bad zip file"}, status_code=400)
    except FileNotFoundError:
        return JSONResponse(content={"error": "Episode not found"}, status_code=404)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
    

@app.get('/other-playlist')
async def other_playlist_root(request: Request):
    data = [
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-1.jpg",
            "ep": "18 / 18",
            "comments": 11,
            "views": 9141,
            "title": "The Seven Deadly Sins: Wrath of the Gods",
            "tags": ["Active", "Movie"]
        },
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-3.jpg",
            "ep": "12 / 12",
            "comments": 5,
            "views": 5000,
            "title": "Another Anime",
            "tags": ["Drama", "Movie"]
        },
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-3.jpg",
            "ep": "12 / 12",
            "comments": 5,
            "views": 5000,
            "title": "Another Anime",
            "tags": ["Drama", "Movie"]
        },
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-3.jpg",
            "ep": "12 / 12",
            "comments": 5,
            "views": 5000,
            "title": "Another Anime",
            "tags": ["Drama", "Movie"]
        },
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-3.jpg",
            "ep": "12 / 12",
            "comments": 5,
            "views": 5000,
            "title": "Another Anime",
            "tags": ["Drama", "Movie"]
        },
        {
            "image": "http://127.0.0.1:8001/static/img/anime/review-3.jpg",
            "ep": "12 / 12",
            "comments": 5,
            "views": 5000,
            "title": "Another Anime",
            "tags": ["Drama", "Movie"]
        }
    ]
    return data


@app.get('/playlist', status_code=status.HTTP_200_OK)
async def playlist_root(
    request: Request, 
    limit: Optional[int] = Header(6), 
    category: Optional[str] = None
):
    data = [
        {
            'title': 'trending now',
            'data': [
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-1.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'The Seven Deadly Sins: Wrath of the Gods',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-2.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Gintama Movie 2: Kanketsu-hen - Yorozuya yo Eien',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-3.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Shingeki no Kyojin Season 3 Part 2',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-4.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Fullmetal Alchemist: Brotherhood',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-5.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Shiratorizawa Gakuen Koukou',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/trending/trend-6.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Code Geass: Hangyaku no Lelouch R2',
                    "tags": ["Action", "Movie"]
                }
            ]
        },
        {
            'title': 'popular shows',
            'data': [
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-1.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Sen to Chihiro no Kamikakushi',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-2.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Kizumonogatari III: Reiket su-hen',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-3.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Shirogane Tamashii hen Kouhan sen',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-4.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Rurouni Kenshin: Meiji Kenkaku Romantan',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-5.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Mushishi Zoku Shou 2nd Season',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/popular/popular-6.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Monogatari Series: Second Season',
                    "tags": ["Action", "Movie"]
                }
            ]
        },
        {
            'title': 'recently added shows',
            'data': [
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-1.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Great Teacher Onizuka',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-2.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Fate/stay night Movie: Heaven\'s Feel - II. Lost',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-3.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Mushishi Zoku Shou: Suzu no Shizuku',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-4.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Fate/Zero 2nd Season',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-5.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Kizumonogatari II: Nekket su-hen',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/recent/recent-6.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'The Seven Deadly Sins: Wrath of the Gods',
                    "tags": ["Action", "Movie"]
                }
            ]
        },
        {
            'title': 'live action',
            'data': [
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-1.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Shouwa Genroku Rakugo Shinjuu',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-2.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Mushishi Zoku Shou 2nd Season',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-3.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Mushishi Zoku Shou: Suzu no Shizuku',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-4.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'The Seven Deadly Sins: Wrath of the Gods',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-5.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Fate/stay night Movie: Heaven\'s Feel - II. Lost',
                    "tags": ["Action", "Movie"]
                },
                {
                    'image': 'http://127.0.0.1:8001/static/img/live/live-6.jpg',
                    'ep': '18 / 18',
                    'comments': 11,
                    'views': 9141,
                    'title': 'Kizumonogatari II: Nekketsu-hen',
                    "tags": ["Action", "Movie"]
                }
            ]
        }
    ]
    
    category = category.lower() if category else None
    
    result = []
    
    for category_data in data:
        filtered_items = category_data['data']
    
        if category:
            filtered_items  = [
                item for item in filtered_items if category in [tag.lower() for tag in item['tags']]
            ]
        
        limited_items = filtered_items[:limit]
        
        if limited_items:
            result.append({
                'title': category_data['title'],
                'data': limited_items
            })
            
    if category and not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='No video is recorded for this category.'
        )
    
    return result


app.add_middleware(AuthenticationMiddleware, backend=JWTAuth())
       
    
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)