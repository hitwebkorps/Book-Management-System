from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    price: float
    description: Optional[str] = None
    source: str = "manual"
    seller_id: Optional[int] = None  
    owner_id: Optional[int] = None  
    google_id: Optional[str] = None  
class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    seller_id: Optional[int] = None

    class Config:
        orm_mode = True
