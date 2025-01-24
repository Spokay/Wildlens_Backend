from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from starlette import status

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from app.dto.badge import BadgeResponse
from app.dto.users import AuthenticatedUser
from app.services.authentication_service import authenticate_user, get_current_user, user_exists, create_user
from app.services.badge_service import get_user_badges
from app.services.token_service import Token, create_access_token

router = APIRouter(
    prefix="/users",
)

@router.post(
    "/token",
    description="Login to get an access token",
    response_model=Token,
    status_code=status.HTTP_200_OK
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
) -> Token:

    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "role": user.role.name
        }, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.post(
    "/register",
    description="Register a new user",
    response_model=Token,
    status_code=status.HTTP_201_CREATED
)
async def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
) -> Token:

    if user_exists(session, form_data.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    created_user = create_user(session, form_data.username, form_data.password)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": created_user.email,
            "user_id": created_user.id,
            "role": created_user.role.name
        }, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get(
    "/me/badges",
    description="get the badges of the current user",
    response_model=list[BadgeResponse],
    status_code=status.HTTP_200_OK
)
async def get_current_user_badges(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
        session: Session = Depends(get_session)
) -> list[BadgeResponse]:
    badge_responses = get_user_badges(current_user.user_id, session)
    return badge_responses
