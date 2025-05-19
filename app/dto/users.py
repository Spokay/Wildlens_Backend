from pydantic import BaseModel
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
    email: str
    password: str
    username: str

class UpdateUserInfo(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    profile_picture : Optional[str] = None

class UpdateUserResponse(BaseModel):
    message: str
    user: UserResponse

class DeleteUserResponse(BaseModel):
    message: str
    user: UserResponse