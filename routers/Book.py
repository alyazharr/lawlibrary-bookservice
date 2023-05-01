from supabase import create_client, Client
from fastapi import APIRouter, Depends
import os
from dotenv import load_dotenv

from config.jwt_utils import User, verify_jwt
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
    books = supabase.table('bookshelf_book').select('*', count='exact').limit(1000).execute()
    return books.data

@router.get("/get-book-by-id")
async def getBookbyId(id:int):
    books = supabase.table('bookshelf_book').select('*', count='exact').eq('id', id).execute()
    if books.count == 0:
        return "Buku tidak ditemukan."
    return books.data

@router.get("/get-targetreminder")
async def getTargetReminderbyId(id:int):
    data = supabase.table('targetmembaca').select('*', count='exact').eq('id', id).execute()
    if data.count == 0:
        return "Data target reminder tidak ditemukan."
    return data.data
#guys kalo emg butuh user tinggal naro -> user: User = Depends(verify_jwt), nanti klo mau akses datanya tinggal user.username atau user.email
@router.post("/target-reminder")
async def targetReminder(idbuku:int, selesai:str, user: User = Depends(verify_jwt)):
    data, count = supabase.table('targetmembaca').insert({"selesai": selesai, "id_buku":idbuku, "email_user":user.email}).execute()
    buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', idbuku).execute()
    mulai = data[1][0]['created_at'][0:10]
    task = reminder_schedule.apply_async(args=[buku.data[0], mulai, selesai, user.email])
    return data

@router.get("/get-targetreminder-user")
async def getTargetReminderUser(user: User = Depends(verify_jwt)):
    data = supabase.table('targetmembaca').select('*', count='exact').eq('email_user', user.email).execute()
    if data.count == 0:
        return "Data target reminder tidak ditemukan."
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.post("/konfirmasi-pinjam")
async def konfirmasiPinjam(idbuku:int, selesai:str, user: User = Depends(verify_jwt)):
    data, count = supabase.table('peminjaman').insert({"selesai": str(selesai), "id_buku":idbuku, "email_user":user.email}).execute()
    return data

@router.get("/get-peminjaman")
async def getpeminjamanbyId(id:int):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', id).execute()
    if data.count == 0:
        return "Data peminjaman tidak ditemukan."
    return data.data

@router.get("/get-peminjaman-user")
async def getpeminjamanUser(user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('email_user', user.email).execute()
    if data.count == 0:
        return "Data peminjaman tidak ditemukan."
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.put("/konfirmasi-pengembalian")
async def getpeminjamanUser(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').update({ 'status': 'dikembalikan' }).match({'id':idpeminjaman, 'email_user':user.email}).execute()
    print(data)
    return data.data