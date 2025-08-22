from sqlalchemy.orm import relationship
from database.database import Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)

    books = relationship("Book", foreign_keys="[Book.owner_id]", back_populates="owner")
    seller_books = relationship("Book", foreign_keys="[Book.seller_id]")
