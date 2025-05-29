from pydantic import BaseModel, Field
from typing import Optional
from sqlmodel import SQLModel
import datetime as dt

class UserResponse(SQLModel):
    # do we ever use it? not very secure bro!!! ahahaha my function works hugo!!! ratio!!!!
    # id: int
    username: str
    email: str
    profile_picture: Optional[str] = None
    created_at: dt.datetime

class AuthenticatedUser(BaseModel):
    user_id: int
    username: str
    role_name: str

class RegisterRequest(BaseModel):
    email: str = Field(..., min_length=2, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address required")
    password: str = Field(..., min_length=2, description="Password must be at least 2 characters")
    username: str = Field(..., min_length=2, description="Username must be at least 2 characters")

class UpdateUserInfo(BaseModel):
    username: Optional[str] = Field(None, min_length=2, description="Username must be at least 2 characters")
    email: Optional[str] = Field(None, min_length=2, pattern=r'^[^@]+@[^@]+\.[^@]+$', description="Valid email address required")
    profile_picture: Optional[str] = Field(None, min_length=2, description="Profile picture URL must be at least 2 characters")

class UpdateUserResponse(BaseModel):
    message: str
    user: UserResponse

class DeleteUserResponse(BaseModel):
    message: str
    user: UserResponse