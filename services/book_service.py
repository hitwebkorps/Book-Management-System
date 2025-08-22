from sqlalchemy.orm import Session
from models.user_model import User
from schemas.user_schema import UserCreate, UserLogin
from utils.hashing import Hash
from database.database import SessionLocal  



def create_user_service(db: Session, user_data: UserCreate):
    hashed_password = Hash.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password=hashed_password,
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate_user_service(db: Session, login_data: UserLogin):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        return None
    if not Hash.verify_password(login_data.password, user.password):
        return None
    if user.role != login_data.role:
        return None
    return user


def get_user_service(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()



def create_user_task(user_data: dict):
  
    db: Session = SessionLocal()
    try:
        hashed_password = Hash.get_password_hash(user_data["password"])
        new_user = User(
            email=user_data["email"],
            username=user_data["username"],
            password=hashed_password,
            role=user_data["role"]
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "email": new_user.email, "role": new_user.role}
    finally:
        db.close()
