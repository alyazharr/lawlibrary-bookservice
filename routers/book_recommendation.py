from celery import group
from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import JSONResponse
from celery.result import AsyncResult

from config.jwt_utils import User, verify_jwt


import os
import sys
import pandas as pd

from dotenv import load_dotenv
from supabase import create_client
import logging
from schemas.book_schemas import BookRecom

load_dotenv() 
SUPABASE_URL = os.getenv('supabase_url')
SUPABASE_KEY = os.getenv('supabase_key')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Add the root directory of your project to the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from celery_tasks.recommendation_task import predict_recommendation
from config.celery_utils import get_task_info

router = APIRouter(prefix='/book-recommendation', tags=['Book Recommendation'], responses={404: {"description": "Not found"}})

@router.post('/')
async def predict_book_recommendation(bookRecom: BookRecom) -> dict:
    """
    Return the predicted book recommendations of given title book input in a async way
    """
    book_df = pd.read_csv('data/Books.csv')
    data = supabase.table('bookshelf_book').select('*', count='exact').eq('title', bookRecom.title).execute()
    
    if data.count == 0:
        if not bookRecom.title.lower() in book_df['Book-Title'].str.lower().values:
            
            logging.info('Post predict book recommendation endpoint failed, book with given title not found.')

            raise HTTPException(status_code=404, detail="Buku dengan judul tersebut tidak ditemukan.")
        
    task = predict_recommendation.apply_async(args=[bookRecom.title])
    logging.info('Post predict book recommendation endpoint successfully accessed')

    return JSONResponse({'task_id':task.id})

@router.get("/get-prediction/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """
    Return the status of the submitted Task
    """
    logging.info('Get predicted book recommendation endpoint successfully accessed')
    return get_task_info(task_id)