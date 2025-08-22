from sqlalchemy.orm import Session
from models.book_model import Book
from schemas.book_schema import BookCreate
from typing import List

def create_book(db: Session, book: BookCreate, seller_id: int):
    db_book = Book(
        title=book.title,
        author=book.author,
        description=book.description,
        price=book.price,
        seller_id=seller_id,
        google_id=book.google_id,       
        source=book.source or "manual"  
    )
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def bulk_create_books(db: Session, books: List[BookCreate], seller_id: int):
    db_books = [
        Book(
            title=book.title,
            author=book.author,
            description=book.description,
            price=book.price,
            google_id=book.google_id,       
            source=book.source or "manual"  
        )
        for book in books
    ]
    db.add_all(db_books)
    db.commit()
    return db_books




def search_books(db: Session, title: str = None, author: str = None):
    query = db.query(Book)
    if title:
        query = query.filter(Book.title.ilike(f"%{title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    return query.all()
