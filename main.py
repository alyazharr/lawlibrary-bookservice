import uvicorn as uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from config.celery_utils import create_celery
from routers import send_email, Book



def create_app() -> FastAPI:
    current_app = FastAPI(title="LAW TK2",
                          description="LibLAW",
                          version="1.0.0", )

    current_app.celery_app = create_celery()
    current_app.include_router(send_email.router)
    current_app.include_router(Book.router)
    return current_app


app = create_app()
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
celery = app.celery_app

if __name__ == "__main__":
    uvicorn.run("main:app", port=9000, reload=True)