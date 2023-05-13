import os
from fastapi import APIRouter, Depends, HTTPException
from config.jwt_utils import User, verify_jwt
from starlette.responses import JSONResponse
from datetime import datetime

from supabase import create_client
from dotenv import load_dotenv
from schemas.review_schemas import Review, ReviewCreate

load_dotenv() 
SUPABASE_URL = os.getenv('supabase_url')
SUPABASE_KEY = os.getenv('supabase_key')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter(prefix='/reviews', tags=['Review'], responses={404: {"description": "Not found"}})
    
@router.get("/user")
def get_reviews_by_user(user: User = Depends(verify_jwt)):
    reviews = supabase.table('book_review').select('*', count='exact').eq('user_id', user.username).execute()
    return reviews.data

@router.get("/book/{book_id}")
def get_reviews_by_bookid(book_id: int):
    book_data = supabase.table('bookshelf_book').select('*', count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        return HTTPException(status_code=404, detail="Book ID Not Found")
    reviews = supabase.table('book_review').select('*', count='exact').eq('book_id', book_id).execute()
    return reviews.data

@router.post("/add/{book_id}", response_model=Review)
async def create_review(book_id:int, review: ReviewCreate, user: User = Depends(verify_jwt)): 
    if review.rating < 0 or review.rating > 5 or not review.review_text.strip():
        raise HTTPException(status_code=400, detail="Invalid Input. Unable to Add Review.")
    
    book_data = supabase.table('bookshelf_book').select('*', count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        return HTTPException(status_code=404, detail="Book ID Not Found")

    data_review = supabase.table('book_review').select("*", count='exact').eq('book_id', book_id).eq('user_id', user.username).execute()
    if len(data_review.data) != 0 :
        raise HTTPException(status_code=409, detail="You Already Reviewed This Book. Please Check My Reviews Page.")
    
    data, count = supabase.table('book_review').insert({
        "book_id": book_id, 
        "user_id": user.username, 
        "rating": review.rating, 
        "review_text": review.review_text
    }).execute()

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
        raise HTTPException(status_code=400, detail="Invalid Input. Unable to Change Review.")

    data_review = supabase.table('book_review').select("*", count='exact').eq('user_id', user.username).eq('id', review_id).execute()
    if len(data_review.data) == 0 :
        raise HTTPException(status_code=404, detail="Review ID Not Found")
    
    updated_review = supabase.table('book_review').update({"rating": review.rating, "review_text": review.review_text}).eq('id', review_id).execute()
    return JSONResponse({'detail': f"Review with id {review_id} Successfully Changed."})

@router.delete("/delete/{review_id}")
def delete_review(review_id: int, user: User = Depends(verify_jwt)):
    data_review = supabase.table('book_review').select("*", count='exact').eq('user_id', user.username).eq('id', review_id).execute()
    if len(data_review.data) == 0 :
        return HTTPException(status_code=404, detail="Review ID Not Found")
    deleted_review = supabase.table('book_review').delete().eq('id', review_id).execute()
    if deleted_review:
        return JSONResponse({'detail': f"Review with id {review_id} Successfully Deleted."})
    return HTTPException(status_code=400, detail="Unable to Delete Review.")

@router.get("/avg-rate/{book_id}")
def get_avg_rate(book_id: int):
    book_data = supabase.table('bookshelf_book').select("*", count='exact').eq('id', book_id).execute()
    if len(book_data.data) == 0:
        return HTTPException(status_code=404, detail="Book ID Not Found")
    reviews =  supabase.table('book_review').select('rating').eq('book_id', book_id).execute()
    if len(reviews.data) == 0:
        return {"book_id": book_id, "avg_rating": 0}
    total_reviews = len(reviews.data)
    total_rating = sum([review['rating'] for review in reviews.data])
    avg_rating = round(total_rating/total_reviews, 1) if total_reviews != 0 else 0
    return {"book_id": book_id, "avg_rating": avg_rating}

