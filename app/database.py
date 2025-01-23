import os

from sqlalchemy import URL, create_engine
from sqlmodel import SQLModel, Session

from app.models import Role, Family, Habitat, Specie, User, Badge, UserBadge, SpecieHabitat, Identification

database_url = URL.create(
    drivername="postgresql",
    username=os.getenv("DATABASE_USERNAME"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT"),
    database=os.getenv("DATABASE_NAME")
)

database_engine = create_engine(
    database_url,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(database_engine, tables=[
        Role.__table__,
        Family.__table__,
        Habitat.__table__,
        Specie.__table__,
        User.__table__,
        Badge.__table__,
        UserBadge.__table__,
        SpecieHabitat.__table__,
        Identification.__table__,
    ])

def get_session():
    with Session(database_engine) as session:
        yield session