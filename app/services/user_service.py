from typing import Optional

from passlib.context import CryptContext
from sqlmodel import Session, select

from app.config import email_validation_regex
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def get_password_hash(password):
    return pwd_context.hash(password)

async def is_password_valid(password: str) -> bool:
    return len(password) > 8

async def user_exists(session: Session, username: str) -> bool:
    user : Optional[User] = session.exec(select(User).where(User.email == username or User.username == username)).first()
    return user is not None

async def create_user(session: Session, username: str, email: str, password: str) -> User:
    hashed_password = await get_password_hash(password)
    user = User(username=username, email=email, password=hashed_password, role_id=2)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

async def get_user_by_username(session: Session, username: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == username or User.username == username)).first()
