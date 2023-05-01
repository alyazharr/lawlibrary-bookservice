from celery import group
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from celery.result import AsyncResult

from config.jwt_utils import User, verify_jwt


import os
import sys

# Add the root directory of your project to the Python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from celery_tasks.recommendation_task import predict_recommendation
from config.celery_utils import get_task_info
# from schemas.schemas import Tweet

router = APIRouter(prefix='/book-recommendation', responses={404: {"description": "Not found"}})

# @router.get('/')
# async def root() -> dict:
#     return {'Nama': 'Rizky Juniastiar',
#             'NPM': '2006596043',
#             'Tugas 2': 'LAW'
#             }

# @router.post('/predict-sentiment')
# async def predict_tweet_sentiment(tweet: Tweet) -> dict:
#     """
#     Return the predicted sentiment of given tweet input in a async way
#     """
#     task = predict_sentiment.apply_async(args=[tweet.tweet])
#     return JSONResponse({'task_id':task.id})

# @router.post("/target-reminder")
# async def targetReminder(idbuku:int, selesai:str, user: User = Depends(verify_jwt)):
#     data, count = supabase.table('targetmembaca').insert({"selesai": selesai, "id_buku":idbuku, "email_user":user.email}).execute()
#     buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', idbuku).execute()
#     mulai = data[1][0]['created_at'][0:10]
#     task = reminder_schedule.apply_async(args=[buku.data[0], mulai, selesai, user.email])
#     return data

@router.post('/')
async def predict_book_recommendation(title: str, user: User = Depends(verify_jwt)) -> dict:
# async def predict_book_recommendation(title: str, user: str) -> dict:
    """
    Return the predicted book recommendations of given title book input in a async way
    """
    task = predict_recommendation.apply_async(args=[title])
    return JSONResponse({'email_user':user.email,'task_id':task.id})

@router.get("/get-prediction/{task_id}")
async def get_task_status(task_id: str) -> dict:
    """
    Return the status of the submitted Task
    """
    return get_task_info(task_id)