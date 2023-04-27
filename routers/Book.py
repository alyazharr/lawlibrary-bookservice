from supabase import create_client, Client
from fastapi import APIRouter
import os
from dotenv import load_dotenv
load_dotenv('.env')
email_sender = 'bookservice.law@gmail.com'
email_password = os.getenv('MAIL_PASSWORD')

router = APIRouter(prefix='/book', tags=['book'], responses={404: {"description": "Not found"}})

url = os.getenv('supabase_url')
key = os.getenv('supabase_key')

supabase: Client = create_client(url, key)
@router.get("/get-books")
def getBook():
    books = supabase.table('bookshelf_book').select('*', count='exact').limit(3).execute()
    return books
