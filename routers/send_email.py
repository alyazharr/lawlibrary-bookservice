from fastapi import APIRouter
from starlette.responses import JSONResponse

from celery_tasks.email_task import send_emaila, send_emailb, reminder_schedule
from config.celery_utils import get_task_info
import schedule
import datetime

router = APIRouter(prefix='/send_email', tags=['send_email'], responses={404: {"description": "Not found"}})

@router.get("/send-email/async")
async def send_email(subject:str, recipient:str, message:str):
    task = send_emaila.apply_async(args=[subject, recipient, message])
    return JSONResponse({"task_id": task.id})

@router.get("/bookreminder")
async def reminder(time:str, recipient:str):
    # now = datetime.datetime.now()
    # end = now + datetime.timedelta(minutes=2)
    # schedule.every(10).seconds.do(lambda: send_emailb('test','adirasayidina3@gmail.com', 'yaaa'))
    # while end > datetime.datetime.now():
    #     schedule.run_pending()
    # return 'Done'
    task = reminder_schedule.apply_async(args=[time, recipient])
    return JSONResponse({"task_id": task.id})

@router.get("/task/{task_id}")
async def get_task_status2(task_id: str) -> dict:
    return get_task_info(task_id)