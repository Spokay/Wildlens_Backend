from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: int
    email: str
    role_name: str