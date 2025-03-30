import traceback
from functools import wraps
from typing import Optional

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlmodel import Session
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import EXCLUDED_PATHS, logger
from app.dto.users import AuthenticatedUser
from app.models import User
from app.services.token_service import decode_access_token
from app.services.user_service import get_user_by_username, verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

async def authenticate_user(session : Session, username: str, password: str):
    user : Optional[User] = await get_user_by_username(session, username)
    if not user:
        return False
    if not await verify_password(password, user.password):
        return False
    return user

async def get_current_user(request: Request) -> AuthenticatedUser:
    user_id = request.state.user_id
    username = request.state.username
    role_name = request.state.role_name

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return AuthenticatedUser(user_id=user_id, username=username, role_name=role_name)


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
            payload : dict = await decode_access_token(token)
            username = payload.get("sub")
            user_id = payload.get("user_id")
            role_name = payload.get("role")

            request.state.user_id = user_id
            request.state.username = username
            request.state.role_name = role_name

        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        response = await call_next(request)
        return response

class ExceptionHandlerLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as http_exc:
            logger.info(f"HTTP error: {http_exc.detail} (status: {http_exc.status_code})")
            return JSONResponse(
                status_code=http_exc.status_code,
                content={"detail": http_exc.detail}
            )
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            logger.debug(traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"detail": "An unexpected error occurred."}
            )

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