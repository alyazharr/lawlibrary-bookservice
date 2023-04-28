import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from fastapi import APIRouter
from typing import Optional

from supabase import create_client
from dotenv import load_dotenv

router = APIRouter(prefix='/search', tags=['Search'], responses={404: {"description": "Not found"}})

load_dotenv() 
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/title")
def search_books_author(title: Optional[str] = None):
    query = supabase.table('bookshelf_book').select('*')
    if title:
        query = query.ilike('title', f'%{title}%')
    response = query.execute()
    return response.data

@router.get("/author")
def search_books_title(author: Optional[str] = None):
    query = supabase.table('bookshelf_book').select('*')
    if author:
        query = query.ilike('author', f'%{author}%')
    response = query.execute()
    return response.data

@router.get("/")
def search_books(q: Optional[str] = None):
    if not q:
        return []
    query = supabase.table('bookshelf_book').select('*')
    query_auth = query.ilike('author', f'%{q}%').execute()
    query_title = query.ilike('title', f'%{q}%').execute()
    response = query_auth.data
    response.append(query_title.data)
    return response
