from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn


app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory='static'), name="static")
templates = Jinja2Templates(directory="templates")


def verify_cookies(request, response):
    if not request.cookies.get('access_token'):
        response.set_cookie(
            key='error_message', 
            value='Your session has expired! Please log in again!', 
            httponly=True,
            expires=2,  # 2 secondes
            max_age=2  # 2 secondes
        )
        return RedirectResponse(url='/login', headers=response.headers)


@app.get('/login')
async def login_root(request: Request, response: Response):
    if request.cookies.get('access_token'):
        return RedirectResponse(url='/')
    
    error_message = request.cookies.get('error_message')
    success_message = request.cookies.get('success_message')
    return templates.TemplateResponse(
        'login.html', 
        context={'request': request, 'error_message': error_message, 'success_message': success_message}
    )


@app.get('/forgot-pwd')
async def login_root(request: Request, response: Response):
    if request.cookies.get('access_token'):
        return RedirectResponse(url='/')
    return templates.TemplateResponse('forgot.html', context={'request': request})


@app.get('/')
async def index_root(request: Request, response: Response):
    if not request.cookies.get('access_token'):
        response.set_cookie(
            key='error_message', 
            value='Your session has expired! Please log in again!', 
            httponly=True,
            expires=2,  # 2 secondes
            max_age=2  # 2 secondes
        )
        return RedirectResponse(url='/login', headers=response.headers)
    return templates.TemplateResponse('index.html', context={'request': request})


@app.get('/users')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('users.html', context={'request': request})


@app.get('/edit-user')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('edit-user.html', context={'request': request})


@app.get('/categories')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('categories.html', context={'request': request})


@app.get('/add-category')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('add-category.html', context={'request': request})


@app.get('/movies')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('movies.html', context={'request': request})


@app.get('/add-movie')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('add-movie.html', context={'request': request})


@app.get('/comments')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('comments.html', context={'request': request})


@app.get('/reviews')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('reviews.html', context={'request': request})


@app.get('/add-movie')
async def index_root(request: Request, response: Response):
    return verify_cookies(request=request, response=response)
    return templates.TemplateResponse('add-movie.html', context={'request': request})


if __name__ == '__main__':
    uvicorn.run('main:app', host='127.0.0.1', port=8002, reload=True)
