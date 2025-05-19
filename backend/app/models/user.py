from typing import Optional, List
from pydantic import EmailStr, Field, BaseModel
from app.models.base import MongoBaseModel

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str

    class Config:
        from_attributes = True

class UserUpdate(MongoBaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(User):
    hashed_password: str 