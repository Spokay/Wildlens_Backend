from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm

class AuthenticatedUser(BaseModel):
    user_id: int
    username: str
    role_name: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    username: str