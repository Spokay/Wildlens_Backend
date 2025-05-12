from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from starlette import status
from starlette.responses import JSONResponse

from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_session
from app.dto.badge import BadgeResponse
from app.dto.users import AuthenticatedUser, RegisterRequest, UpdateUserInfo
from app.mappers.user_mapper import get_user_mapper
from app.services.authentication_service import authenticate_user, get_current_user, role_required
from app.services.badge_service import get_user_badges
from app.services.token_service import Token, create_access_token
from app.services.user_service import is_password_valid, create_user, user_exists, update_user, delete_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
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


    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={
            "sub": user.username,
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
    form_data: RegisterRequest = Body(...),
    session: Session = Depends(get_session)
) -> Token:
    try:

        if not await is_password_valid(form_data.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is not valid",
            )

        if await user_exists(session, form_data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already exists",
            )

        created_user = await create_user(session, form_data.username, form_data.email, form_data.password)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await create_access_token(
            data={
                "sub": created_user.email,
                "user_id": created_user.id,
                "role": created_user.role.name
            }, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
    except HTTPException as e:
        raise e

@router.put(
    "/me",
    description="User updates its informations",
    status_code=status.HTTP_200_OK
)
async def update_user_route(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    session: Session = Depends(get_session),
    user_mapper=Depends(get_user_mapper),
    user_update: UpdateUserInfo = Body(...),
):
    if user_update.password and not await is_password_valid(user_update.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is not valid",
        )

    if await user_exists(session, user_update.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    user = await update_user(
        session,
        user_mapper,
        user_update,
        current_user.user_id,
    )

    return JSONResponse(
        {
            "message": "user updated successfully",
            "user": user.model_dump(mode="json"),
        }
    )


@role_required("ADMIN")
@router.delete(
    "/delete/{user_id}",
    description="Delete the user",
    status_code=status.HTTP_200_OK
)
async def delete_user_route(
        user_id:int,
        session: Session = Depends(get_session),
        user_mapper=Depends(get_user_mapper)
):
    user = await delete_user(
        session,
        user_id,
        user_mapper
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"user with id {user_id} not found",
        )

    return JSONResponse(
        {
            "message": "user deleted successfully",
            "user": user.model_dump(mode="json"),
        }
    )

@router.get(
    "/me/badges",
    description="Get the badges of the current user",
    response_model=list[BadgeResponse],
    status_code=status.HTTP_200_OK
)
async def get_current_user_badges(
        current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
        session: Session = Depends(get_session)
) -> list[BadgeResponse]:
    badge_responses = await get_user_badges(current_user.user_id, session)
    return badge_responses
