from pydantic import BaseModel
from typing import List, Optional


class GoogleBook(BaseModel):
    title: str
    authors: Optional[List[str]]
    publisher: Optional[str]
    publishedDate: Optional[str]
    description: Optional[str]
    source: str = "Google Books"
    google_id: str
    price: Optional[float]


class GoogleBooksResponse(BaseModel):
    count: int
    books: List[GoogleBook]


