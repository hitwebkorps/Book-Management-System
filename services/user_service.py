from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.user_model import User
from schemas.user_schema import UserCreate, UserLogin
from utils.hashing import Hash
import logging

logger = logging.getLogger(__name__)

def create_user_service(db: Session, user_data: UserCreate):
    try:
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
        logger.info(f"User created successfully: {new_user.email}")
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error while creating user: {str(e)}")
        raise

def authenticate_user_service(db: Session, login_data: UserLogin):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        logger.warning(f"Authentication failed: User not found ({login_data.email})")
        return None
    if not Hash.verify_password(login_data.password, user.password):
        logger.warning(f"Authentication failed: Wrong password for {login_data.email}")
        return None
    if user.role != login_data.role:
        logger.warning(f"Authentication failed: Role mismatch for {login_data.email}")
        return None
    logger.info(f"User authenticated successfully: {login_data.email}")
    return user

def get_user_service(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        logger.info(f"User fetched: {email}")
    else:
        logger.warning(f"User not found: {email}")
    return user
