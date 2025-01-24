import os

from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from app.models import Role, Family, Habitat, Specie, User, Badge, UserBadge, SpecieHabitat, Identification

params = os.getenv("AZURE_DATABASE_CONNECTION_PARAMS")

conn_string = f'mssql+pyodbc:///?odbc_connect={params}'

database_engine = create_engine(conn_string, echo=True)

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine, tables=[
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