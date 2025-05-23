from typing import Optional


from passlib.context import CryptContext
from sqlmodel import Session, select
from fastapi import HTTPException, status

from app.dto.users import UpdateUserInfo, UserResponse, AuthenticatedUser
from app.mappers.user_mapper import UserMapper
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# not async, would cause issues in database.py when creating the admin pwd
def get_password_hash(password):
    return pwd_context.hash(password)


async def is_password_valid(password: str) -> bool:
    return len(password) > 8


async def user_exists(session: Session, username: str) -> bool:
    user: Optional[User] = session.exec(
        select(User).where(User.email == username or User.username == username)
    ).first()
    return user is not None


async def get_user_by_id(session: Session, user_id: int) -> User:
    user: Optional[User] = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {user_id} not found",
        )

    return user


async def create_user(
        session: Session, username: str, email: str, password: str
) -> User:
    hashed_password: str = get_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role_id=2)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


async def update_user_fields(
        session: Session, new_user_info: UpdateUserInfo, user_to_update: User
) -> User:
    for key, value in new_user_info.model_dump(mode="json", exclude_unset=True).items():
        if key == "password":
            if not await is_password_valid(value):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="password must be at least 8 characters long",
                )
            user_to_update.password = get_password_hash(value)
        elif hasattr(user_to_update, key):
            setattr(user_to_update, key, value)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"user does not have property {key}",
            )

    session.add(user_to_update)
    session.commit()
    session.commit()
    return user_to_update


async def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(
        select(User).where(User.email == username or User.username == username)
    ).first()

async def get_current_user_info(
        session: Session, current_user: AuthenticatedUser, user_mapper: UserMapper
) -> UserResponse:
    statement = (
        select(User)
        .where(current_user.user_id == User.id)
    )

    response: User = session.exec(statement).first()
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Erreur lors de la récupération des informations de l'utilisateur."
        )

    return await user_mapper.user_to_response(response)


async def update_user(
        session: Session, user_mapper: UserMapper, new_user_info: UpdateUserInfo, user_id
) -> UserResponse:
    user_to_update: User = await get_user_by_id(session, user_id)

    user_with_same_username: Optional[User] = await get_user_by_username(
        session, new_user_info.username
    )

    if user_with_same_username and user_with_same_username.id != user_to_update.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already taken",
        )
    updated_user = await update_user_fields(session, new_user_info, user_to_update)
    return await user_mapper.user_to_response(updated_user)


async def delete_user(
        session: Session, user_id: int, user_mapper: UserMapper
) -> UserResponse:
    user_to_delete = await get_user_by_id(session, user_id)

    response = await user_mapper.user_to_response(user_to_delete)

    session.delete(user_to_delete)
    session.commit()
    return response