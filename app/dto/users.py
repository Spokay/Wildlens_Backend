from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel

class UserResponse(SQLModel):
    id: int
    username: str
    email: str

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