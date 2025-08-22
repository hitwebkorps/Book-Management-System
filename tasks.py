from celery_app import celery_app
from database.database import SessionLocal
from models.book_model import Book

@celery_app.task(name="save_books_to_db")
def save_books_to_db(books_data: list):
    
    db = SessionLocal()  
    try:
        books_to_insert = []
        for item in books_data:
            book = Book(
                title=item.get("title", "No Title"),
                author=", ".join(item.get("authors", ["Unknown"])),
                description=item.get("description", ""),
                published_date=item.get("publishedDate", ""),
                page_count=item.get("pageCount", 0),
                source="google"
            )
            books_to_insert.append(book)

        if books_to_insert:
            db.bulk_save_objects(books_to_insert)
            db.commit()
            print(f"Saved {len(books_to_insert)} books to DB")
    except Exception as e:
        db.rollback()
        print("Error saving books:", e)
    finally:
        db.close()