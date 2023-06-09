import uvicorn as uvicorn
from fastapi import FastAPI
import logging
import sys

from fastapi.middleware.cors import CORSMiddleware
from config.celery_utils import create_celery
from routers import send_email, Book, search, review, stock, book_recommendation


def create_app() -> FastAPI:
    current_app = FastAPI(title="LAW TK2",
                          description="LibLAW",
                          version="1.0.0", )

    current_app.celery_app = create_celery()
    current_app.include_router(send_email.router)
    current_app.include_router(Book.router)
    current_app.include_router(stock.router)
    current_app.include_router(search.router)
    current_app.include_router(review.router)
    current_app.include_router(book_recommendation.router)

    return current_app


app = create_app()
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://34.29.43.52",
    "http://35.223.65.194",
    "http://34.133.211.90",
    "http://34.68.143.87"
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
    uvicorn.run("main:app", port=8000, reload=True)