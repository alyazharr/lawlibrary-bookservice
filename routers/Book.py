from supabase import create_client, Client
from fastapi import APIRouter
import os
from dotenv import load_dotenv
load_dotenv('.env')
from celery_tasks.email_task import reminder_schedule
from starlette.responses import JSONResponse
import datetime

router = APIRouter(prefix='/book', tags=['book'], responses={404: {"description": "Not found"}})

url = os.getenv('supabase_url')
key = os.getenv('supabase_key')

supabase: Client = create_client(url, key)
@router.get("/get-books")
async def getBook():
    books = supabase.table('bookshelf_book').select('*', count='exact').limit(20).execute()
    return books.data

@router.get("/get-book-by-id")
async def getBookbyId(id:int):
    books = supabase.table('bookshelf_book').select('*', count='exact').eq('id', id).execute()
    return books.data

@router.get("/get-targetreminder")
async def getTargetReminderbyId(id:int):
    data = supabase.table('targetmembaca').select('*', count='exact').eq('id', id).execute()
    return data.data

@router.post("/target-reminder")
async def targetReminder(idbuku:int, selesai:str, user:str):
    data, count = supabase.table('targetmembaca').insert({"selesai": selesai, "idbuku":idbuku, "user":user}).execute()
    buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', idbuku).execute()
    mulai = data[1][0]['created_at'][0:10]
    print(type(buku.data[0]))
    task = reminder_schedule.apply_async(args=[buku.data[0], mulai, selesai, user])
    return data