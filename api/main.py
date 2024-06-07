from pathlib import Path
from fastapi import FastAPI, Request, Response, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn, zipfile, io, os, ffmpeg


app = FastAPI()

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


CHUNK_SIZE = 10*1024*1024 # 10 MB


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
    

@app.get('/test')
async def test_root(request: Request):
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
        },
    ]
    return data
    
    
    
if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)