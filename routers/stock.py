from supabase import create_client, Client
from fastapi import APIRouter, Depends, HTTPException

import os
from dotenv import load_dotenv
load_dotenv()
from celery_tasks.email_task import reminder_schedule
from starlette.responses import JSONResponse
import datetime

router = APIRouter(prefix='/stock', tags=['stock'], responses={404: {"description": "Not found"}})

url = os.getenv('supabase_url')
key = os.getenv('supabase_key')

supabase: Client = create_client(url, key)

@router.get("/get-stock")
async def getBookbyId(id:int):
    stock = supabase.table('bookshelf_book').select('stok', count='exact').eq('id', id).execute()
    return stock.data

@router.put("/update")
async def updateBookbyId(id:int, stok:int):
    updated_stock = supabase.table('bookshelf_book').update({"stok": stok}).eq('id', id).execute()
    print(updated_stock)
    if updated_stock:
        return JSONResponse({'message': f"Stock with book id {id} Successfully Changed."})
    return JSONResponse({'message': "Unable to Change Stock. Try Again."})