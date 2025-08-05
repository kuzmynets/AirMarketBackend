from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    email: EmailStr

class UserProfile(BaseModel):
    uid: str
    email: EmailStr
    name: Optional[str]

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None