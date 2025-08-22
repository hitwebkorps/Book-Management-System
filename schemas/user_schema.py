from pydantic import BaseModel, EmailStr
from typing import Literal

class UserBase(BaseModel):
    email: EmailStr
    role: Literal["Author", "Seller", "User"]  
    username: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Literal["Author", "Seller", "User"]

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True
