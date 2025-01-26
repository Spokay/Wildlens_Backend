from functools import wraps
from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from passlib.context import CryptContext
from sqlmodel import Session
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import EXCLUDED_PATHS
from app.dto.users import AuthenticatedUser
from app.models import User
from app.services.token_service import decode_access_token
from app.services.user_service import get_user_by_email, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

def authenticate_user(session : Session, email: str, password: str):
    user : Optional[User] = get_user_by_email(session, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(request: Request) -> AuthenticatedUser:
    user_id = request.state.user_id
    email = request.state.email
    role_name = request.state.role_name

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return AuthenticatedUser(user_id=user_id, email=email, role_name=role_name)


async def extract_token_from_request(request: Request) -> str:
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.replace("Bearer ", "")
    return token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        normalized_path = request.url.path.rstrip('/')

        if normalized_path in EXCLUDED_PATHS:
            return await call_next(request)

        token = await extract_token_from_request(request)

        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        try:
            payload : dict = decode_access_token(token)
            email = payload.get("sub")
            user_id = payload.get("user_id")
            role_name = payload.get("role")

            request.state.user_id = user_id
            request.state.email = email
            request.state.role_name = role_name

        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        response = await call_next(request)
        return response

def role_required(role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            user_role = request.state.role_name
            if user_role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have the required permissions"
                )
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator