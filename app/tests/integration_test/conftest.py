from app.main import app
import pytest
from fastapi.testclient import TestClient

from sqlmodel import create_engine, Session, select
from contextlib import asynccontextmanager
from app.database import create_db_and_tables
from app.models import (
    User,
    Role,
    Family,
    Habitat,
    Specie,
    Identification,
)


@pytest.fixture(scope="session")
def test_engine():
    """Créer un moteur SQLite en mémoire pour les tests."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )

    # Importation explicite
    from sqlmodel import SQLModel
    from app.models import User, Role, Family, Habitat, Specie, Identification

    create_db_and_tables(engine)

    # Vérification avec échec forcé pour afficher
    from sqlalchemy import inspect

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    yield engine


@asynccontextmanager
async def test_lifespan(app):
    yield


@pytest.fixture(scope="function")  # Changez à function pour isoler les tests
def test_session(test_engine):
    # Créez une nouvelle session pour chaque test
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(test_session):
    app.router.lifespan_context = test_lifespan

    from app.database import get_session

    app.dependency_overrides[get_session] = lambda: test_session

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def get_token(client, test_session):
    def _get_token(username="user"):
        user = test_session.exec(select(User).where(User.username == username)).first()

        if not user:
            raise Exception(f"User {username} not found")

        response = client.post(
            "api/users/token",
            data={
                "username": user.username,
                "password": "admin123",
            },
        )


        if response.status_code != 200:
            raise Exception(
                f"Failed to get token: {response.status_code} - {response.text}"
            )

        token_data = response.json()
        return token_data["access_token"]

    return _get_token
