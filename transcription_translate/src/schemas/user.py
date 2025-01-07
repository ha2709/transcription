# src/schemas/user.py

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


# Schema for user registration
class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    first_name: str
    last_name: str
    password: constr(min_length=6)


# Schema for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema for user response
class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


# Schema for token response
class Token(BaseModel):
    access_token: str
    token_type: str
