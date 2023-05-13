from pydantic import BaseModel

class ReviewCreate(BaseModel):
    rating: float
    review_text: str

class Review(BaseModel):
    id: int
    created_at:str
    book_id: int
    user_id: str
    rating: float
    review_text: str
