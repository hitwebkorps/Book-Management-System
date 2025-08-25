import logging,requests
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from typing import List
import stripe,requests
from database.database import get_db
from database.database import engine, get_db
from models import user_model, book_model
from schemas import user_schema, book_schema
from services import user_service, book_service
from utils.jwt_handler import create_access_token, decode_access_token
from tasks import save_books_to_db
import os
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bookstore_app")


user_model.Base.metadata.create_all(bind=engine)
book_model.Base.metadata.create_all(bind=engine)

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Bookstore Management System API",
        version="1.0.0",
        description="API for user signup/login, book publishing, searching, and Stripe-based purchase",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_token_from_header(authorization: str = Security(api_key_header)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    return authorization.split(" ")[1]



@app.get("/")
def read_root():
    logger.info("Root endpoint hit")
    return {"message": "BookStore API is Working...."}

@app.post("/signup", response_model=user_schema.UserResponse)
def signup(user_data: user_schema.UserCreate, db: Session = Depends(get_db)):
    existing_user = user_service.get_user_service(db, user_data.email)
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {user_data.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = user_service.create_user_service(db, user_data)
    logger.info(f"New user signed up: {new_user.email}, Role: {new_user.role}")

    return new_user


@app.post("/login")
def login(login_data: user_schema.UserLogin, db: Session = Depends(get_db)):
    user = user_service.authenticate_user_service(db, login_data)
    if not user:
        logger.warning("Invalid login attempt")
        raise HTTPException(status_code=401, detail="Invalid credentials or role mismatch")
    token = create_access_token({"sub": user.email})
    logger.info(f"User logged in: {user.email}")
    return {"access_token": token, "token_type": "bearer"}

@app.get("/user/{email}", response_model=user_schema.UserResponse)
def get_user(email: str, db: Session = Depends(get_db)):
    user = user_service.get_user_service(db, email)
    if not user:
        logger.warning(f"User not found: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/books/", response_model=book_schema.BookResponse)
def publish_book(
    book: book_schema.BookCreate,
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    user = user_service.get_user_service(db, email)
    if user.role not in ["Author", "Seller"]:
        raise HTTPException(status_code=403, detail="Only sellers and authors can publish books")
    logger.info(f"Book published by {user.email}: {book.title}")
    return book_service.create_book_service(db, book, user.id)

@app.get("/books/search", response_model=List[book_schema.BookResponse])
def search_books(title: str = "", author: str = "", db: Session = Depends(get_db)):
    logger.info(f"Searching books with title='{title}' author='{author}'")
    return book_service.search_books_service(db, title, author)

@app.get("/books/{book_id}", response_model=book_schema.BookResponse)
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    book = book_service.get_book_by_id_service(db, book_id)
    if not book:
        logger.warning(f"Book not found with id={book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    return book



stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

@app.post("/books/{book_id}/pay_with_card")
def pay_for_book_with_card(
    book_id: int,
    token: str = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    book = book_service.get_book_by_id_service(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book.price:
        raise HTTPException(status_code=400, detail="Book price is missing")

    try:
        logger.info(f"Starting Stripe payment for book: {book.title}, price: {book.price}")
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={"token": "tok_visa"}
        )
        payment_intent = stripe.PaymentIntent.create(
            amount=int(book.price * 100),
            currency="inr",
            payment_method=payment_method.id,
            confirm=True,
            automatic_payment_methods={
                "enabled": True,
                "allow_redirects": "never"
            }
        )
        logger.info(f"Payment successful for {book.title}, PaymentIntent={payment_intent.id}")
        return {
            "message": f"Payment successful for '{book.title}' (Test Mode)",
            "amount": book.price,
            "payment_intent_id": payment_intent.id,
            "status": payment_intent.status
        }
    except stripe.error.CardError as e:
        logger.error(f"Card error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Card error: {str(e)}")
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Payment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Payment failed: {str(e)}")



GOOGLE_BOOKS_API = "https://www.googleapis.com/books/v1/volumes"
API_KEY = os.environ.get("GOOGLE_BOOKS_API_KEY")


@app.get("/google/books/search")
def search_books(query: str):
    try:
        r = requests.get(f"{GOOGLE_BOOKS_API}?q={query}")
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    books_data = [item.get("volumeInfo", {}) for item in data.get("items", [])]

    if books_data:
        save_books_to_db.delay(books_data)
        return {"message": "Saving books in background."}
    else:
        return {"message": "No books found for this query."}