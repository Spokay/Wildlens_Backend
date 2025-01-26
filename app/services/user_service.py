from typing import Optional

from sqlmodel import Session, select

from app.config import email_validation_regex
from app.models import User
from app.services.authentication_service import get_password_hash

def is_email_valid(email: str) -> bool:
    return email_validation_regex.fullmatch(email)

def is_password_valid(password: str) -> bool:
    return len(password) > 0

def user_exists(session: Session, email: str) -> bool:
    user : Optional[User] = session.exec(select(User).where(User.email == email)).first()
    return user is not None

def create_user(session: Session, email: str, password: str) -> User:
    hashed_password = get_password_hash(password)
    user = User(email=email, password=hashed_password, role_id=2)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()
