import os
from fastapi import APIRouter, Depends, HTTPException
from config.jwt_utils import User, verify_jwt
from starlette.responses import JSONResponse
from datetime import datetime

from supabase import create_client
from dotenv import load_dotenv
from schemas.review_schemas import Review, ReviewCreate
import logging

load_dotenv() 
SUPABASE_URL = os.getenv('supabase_url')
SUPABASE_KEY = os.getenv('supabase_key')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix='/reviews', tags=['Review'], responses={404: {"description": "Not found"}})
    
@router.get("/user")
def get_reviews_by_user(user: User = Depends(verify_jwt)):
    reviews = supabase.table('book_review').select('*', count='exact').eq('user_id', user.username).execute()
    logging.info(f'Get user\'s reviews for username:{user.username} successfully accessed')
    return reviews.data

@router.get("/book/{book_id}")
def get_reviews_by_bookid(book_id: int):
    book_data = supabase.table('bookshelf_book').select('*', count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        logging.info(f'Get book\'s reviews for book ID:{book_id} is FAILED. Book with ID {book_id} is NOT FOUND.')
        return HTTPException(status_code=404, detail="Book ID Not Found")
    reviews = supabase.table('book_review').select('*', count='exact').eq('book_id', book_id).execute()
    logging.info(f'Get book\'s reviews endpoint for book ID:{book_id} is successfully accessed')
    return reviews.data

@router.post("/add/{book_id}", response_model=Review)
async def create_review(book_id:int, review: ReviewCreate, user: User = Depends(verify_jwt)): 
    if review.rating < 0 or review.rating > 5 or not review.review_text.strip():
        logging.info('Create new review is FAILED. Input is INVALID.')
        raise HTTPException(status_code=400, detail="Invalid Input. Unable to Add Review.")
    
    book_data = supabase.table('bookshelf_book').select('*', count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        logging.info(f'Get book\'s reviews for book ID:{book_id} is FAILED. Book with ID {book_id} is NOT FOUND.')
        return HTTPException(status_code=404, detail="Book ID Not Found")

    data_review = supabase.table('book_review').select("*", count='exact').eq('book_id', book_id).eq('user_id', user.username).execute()
    if len(data_review.data) != 0 :
        logging.info(f'Create new review is FAILED. User {user.username} already created review object for Book {book_id}.')
        raise HTTPException(status_code=409, detail="You Already Reviewed This Book. Please Check My Reviews Page.")
    
    data, count = supabase.table('book_review').insert({
        "book_id": book_id, 
        "user_id": user.username, 
        "rating": review.rating, 
        "review_text": review.review_text
    }).execute()
    logging.info(f'Create new review for book ID:{book_id} is successfully created and endpoint successfully accessed.')

    data_dict = {
        'id': data[1][0]['id'],
        'created_at': data[1][0]['created_at'][0:10],
        'book_id': data[1][0]['book_id'],
        'user_id': data[1][0]['user_id'],
        'rating': data[1][0]['rating'],
        'review_text': data[1][0]['review_text']
    }
    return data_dict

@router.put("/update/{review_id}", response_model=Review)
async def update_review(review_id: int, review: ReviewCreate, user: User = Depends(verify_jwt)):
    if review.rating < 0 or review.rating > 5 or not review.review_text.strip():
        logging.info(f'Create new review is FAILED. Input is INVALID.')
        raise HTTPException(status_code=400, detail="Invalid Input. Unable to Change Review.")

    data_review = supabase.table('book_review').select("*", count='exact').eq('user_id', user.username).eq('id', review_id).execute()
    if len(data_review.data) == 0 :
        logging.info(f'Get reviews for ID:{review_id} is FAILED . Review with ID {review_id} is NOT FOUND.')
        raise HTTPException(status_code=404, detail="Review ID Not Found")
    
    updated_review = supabase.table('book_review').update({"rating": review.rating, "review_text": review.review_text}).eq('id', review_id).execute()
    logging.info(f'Review for ID:{review_id} is successfully changed and endpoint successfully accessed.')
    return JSONResponse({'detail': f"Review with id {review_id} Successfully Changed."})

@router.delete("/delete/{review_id}")
def delete_review(review_id: int, user: User = Depends(verify_jwt)):
    data_review = supabase.table('book_review').select("*", count='exact').eq('user_id', user.username).eq('id', review_id).execute()
    if len(data_review.data) == 0 :
        logging.info(f'Get reviews for ID:{review_id} is FAILED . Review with ID {review_id} is NOT FOUND.')
        return HTTPException(status_code=404, detail="Review ID Not Found")
    deleted_review = supabase.table('book_review').delete().eq('id', review_id).execute()
    if deleted_review:
        logging.info(f'Review for ID:{review_id} is successfully deleted and endpoint successfully accessed.')
        return JSONResponse({'detail': f"Review with id {review_id} Successfully Deleted."})
    return HTTPException(status_code=400, detail="Unable to Delete Review.")

@router.get("/avg-rate/{book_id}")
def get_avg_rate(book_id: int):
    book_data = supabase.table('bookshelf_book').select("*", count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        logging.info(f'Get book\'s reviews for book ID:{book_id} is FAILED. Book with ID {book_id} is NOT FOUND.')
        return HTTPException(status_code=404, detail="Book ID Not Found")
    reviews =  supabase.table('book_review').select('rating').eq('book_id', book_id).execute()
    if len(reviews.data) == 0:
        return {"book_id": book_id, "avg_rating": 0}
    total_reviews = len(reviews.data)
    total_rating = sum([review['rating'] for review in reviews.data])
    avg_rating = round(total_rating/total_reviews, 1) if total_reviews != 0 else 0
    logging.info(f'Get average rate endpoint for book ID: {book_id} is successfully accessed.')
    return {"book_id": book_id, "avg_rating": avg_rating}

