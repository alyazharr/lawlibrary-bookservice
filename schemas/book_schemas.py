from pydantic import BaseModel
from typing import Optional

class Book(BaseModel):
    title: str
    author: str
    isbn: str
    publication_year: int
    publisher: str
    status: str = 'available'
    stok: int = 1
    image_url_l: Optional[str]
    image_url_m: Optional[str]
    image_url_s: Optional[str]

class BookRecom(BaseModel):
    title: str