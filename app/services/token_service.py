from datetime import timedelta, datetime, timezone

import jwt
from pydantic import BaseModel

from app.config import SECRET_KEY, ALGORITHM


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub : str
    user_id: int | None = None
    role_name: str | None = None


async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
