from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database.database import Base
from models.user_model import User
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    price = Column(Float, default=0.0)   
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    source = Column(String, default="manual")  
    owner = relationship("User", foreign_keys=[owner_id], back_populates="books")
    published_date = Column(String, nullable=True)
    page_count = Column(Integer, nullable=True)