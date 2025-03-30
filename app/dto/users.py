from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: int
    username: str
    role_name: str