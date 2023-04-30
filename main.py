import uvicorn as uvicorn
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from config.celery_utils import create_celery
<<<<<<< HEAD
from routers import send_email, Book, stock
=======
from routers import send_email, Book, search
>>>>>>> 669f1c28e3f9edbb60101bebbb4f87df685a539c



def create_app() -> FastAPI:
    current_app = FastAPI(title="LAW TK2",
                          description="LibLAW",
                          version="1.0.0", )

    current_app.celery_app = create_celery()
    current_app.include_router(send_email.router)
    current_app.include_router(Book.router)
<<<<<<< HEAD
    current_app.include_router(stock.router)
=======
    current_app.include_router(search.router)
>>>>>>> 669f1c28e3f9edbb60101bebbb4f87df685a539c
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
    uvicorn.run("main:app", port=8000, reload=True)