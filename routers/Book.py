from supabase import create_client, Client
from fastapi import APIRouter, Depends, HTTPException
import os
from dotenv import load_dotenv

from config.jwt_utils import User, verify_jwt
load_dotenv('.env')
from celery_tasks.email_task import reminder_schedule
from starlette.responses import JSONResponse
import datetime
from config.celery_utils import get_task_info

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
        raise HTTPException(status_code=404, detail="Target Reminder Item not found")
    return data.data

@router.post("/target-reminder")
async def targetReminder(idbuku:int, targetdate:datetime.date, user: User = Depends(verify_jwt)):
    buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', idbuku).execute()
    if buku.count == 0:
        raise HTTPException(status_code=404, detail="Buku Item not found. Failed to create Target Reminder.")
    if datetime.date.today() > targetdate:
        raise HTTPException(status_code=400, detail="The target date must be filled with a date after today (or today).")
    data, count = supabase.table('targetmembaca').insert({"target_date": str(targetdate), "id_buku":idbuku, "email_user":user.email, "username":user.username}).execute()
    return data

@router.get("/target-reminder-start")
async def targetReminderStart(idreminder:int):
    reminder = supabase.table('targetmembaca').select('*', count='exact').eq('id', idreminder).execute()
    if reminder.count == 0:
        raise HTTPException(status_code=404, detail="Reminder Item not found. Failed to start Target Reminder.")
    buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', reminder.data[0]['id_buku']).execute()
    if buku.count == 0:
        raise HTTPException(status_code=404, detail="Buku Item not found. Failed to start Target Reminder.")
    mulai = reminder.data[0]['start_date'][0:10]
    selesai = reminder.data[0]['target_date']
    task = reminder_schedule.apply_async(args=[buku.data[0], mulai, str(selesai), reminder.data[0]['email_user']])
    return task.id

@router.get("/get-targetreminder-user")
async def getTargetReminderUser(user: User = Depends(verify_jwt)):
    data = supabase.table('targetmembaca').select('*', count='exact').eq('username', user.username).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Target Reminder Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.post("/ajukan-pinjam")
async def ajukanPinjam(idbuku:int, returndate:datetime.date, reminder:int=None, user: User = Depends(verify_jwt)):
    buku = supabase.table('bookshelf_book').select('*', count='exact').eq('id', idbuku).execute()
    if buku.count == 0:
        raise HTTPException(status_code=404, detail="Buku Item not found. Failed to create Peminjaman.")
    if datetime.date.today() > returndate:
        raise HTTPException(status_code=400, detail="The return (returning book) date must be filled with a date after today (or today).")
    data, count = supabase.table('peminjaman').insert({"return_date": str(returndate), "id_buku":idbuku, "email_user":user.email, "username":user.username, "reminder":reminder}).execute()
    return data

@router.put("/konfirmasi-pinjam")
async def konfirmasiPinjam(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', idpeminjaman).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    if user.roles != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').update({ 'status': 'dipinjam' }).match({'id':idpeminjaman}).execute()
    return data.data

@router.put("/tolak-pinjam")
async def tolakPinjam(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', idpeminjaman).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    if user.roles != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').update({ 'status': 'ditolak' }).match({'id':idpeminjaman}).execute()
    return data.data

@router.get("/get-all-peminjaman-request")
async def getPeminjamanRequest():
    data = supabase.table('peminjaman').select('*', count='exact').eq('status', 'diajukan').execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.get("/get-all-returning-request")
async def getReturningRequest():
    data = supabase.table('peminjaman').select('*', count='exact').eq('status', 'pengembalian').execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.get("/get-all-peminjaman")
async def getPeminjaman():
    data = supabase.table('peminjaman').select('*', count='exact').eq('status', 'dipinjam').execute()
    data2 = supabase.table('peminjaman').select('*', count='exact').eq('status',  'ditolak').execute()
    data3 = supabase.table('peminjaman').select('*', count='exact').eq('status',  'dikembalikan').execute()

    if data.count+data2.count+data3.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    data = data.data + data2.data + data3.data
    for datanya in data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data

@router.get("/get-peminjaman")
async def getpeminjamanbyId(id:int):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', id).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    return data.data

@router.get("/get-peminjaman-user")
async def getpeminjamanUser(user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('username', user.username).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.get("/get-peminjaman-user-admin")
async def getpeminjamanUserbyAdmin(username:str, user: User = Depends(verify_jwt)):
    if user.roles != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').select('*', count='exact').eq('username', username).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.get("/get-peminjaman-user")
async def getpeminjamanUser(user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('email_user', user.email).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    for datanya in data.data:
        buku = await getBookbyId(datanya['id_buku'])
        datanya['buku'] = buku
    return data.data

@router.put("/konfirmasi-pengembalian")
async def putPengembalian(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', idpeminjaman).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    if user.roles != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').update({ 'status': 'dikembalikan' }).match({'id':idpeminjaman}).execute()
    return data.data

@router.put("/tolak-pengembalian")
async def putTolakPengembalian(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', idpeminjaman).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    if user.roles != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').update({ 'status': 'dipinjam' }).match({'id':idpeminjaman}).execute()
    return data.data

@router.put("/ajukan-pengembalian")
async def getpeminjamanUser(idpeminjaman:int, user: User = Depends(verify_jwt)):
    data = supabase.table('peminjaman').select('*', count='exact').eq('id', idpeminjaman).execute()
    if data.count == 0:
        raise HTTPException(status_code=404, detail="Peminjaman Item not found")
    if data.data[0]['email_user'] != user.email:
        raise HTTPException(status_code=403, detail="Forbidden, user doesn't have permission to edit this Peminjaman.")
    data = supabase.table('peminjaman').update({ 'status': 'pengembalian' }).match({'id':idpeminjaman, 'email_user': user.email}).execute()
    return data.data

@router.get("/task/{task_id}")
async def get_task_status3(task_id: str) -> dict:
    return get_task_info(task_id)
