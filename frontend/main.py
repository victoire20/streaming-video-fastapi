from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn


app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index_root(request: Request):
    return templates.TemplateResponse("index.html", context={"request": request})


@app.get('/{id}/category')
async def categories_root(request: Request, id: int):
    return templates.TemplateResponse("category.html", context={"request": request})


@app.get('/{name}/watch')
async def watch_anime_root(request: Request, name: str):
    return templates.TemplateResponse("video.html", context={"request": request})


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
