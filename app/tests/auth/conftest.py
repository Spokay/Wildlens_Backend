import os
import tempfile
from contextlib import asynccontextmanager
from typing import Generator, Any

import pytest
from sqlalchemy import inspect, create_engine
from sqlmodel import Session
from starlette.testclient import TestClient

from app.database import drop_tables, create_tables
from app.dto.users import AuthenticatedUser
from app.main import app


def create_temp_db():
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    return db_path


def setup_engine(db_path):
    engine = create_engine(
        f"sqlite:///{db_path}",
        echo=False,
        connect_args={"check_same_thread": False}
    )
    return engine


def verify_tables(engine):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables confirmed in engine: {tables}")
    if not tables:
        raise Exception("No tables were created!")
    return tables


def cleanup_db(engine, db_path):
    drop_tables(engine)
    engine.dispose()
    try:
        os.unlink(db_path)
    except OSError:
        pass


@pytest.fixture(scope="session")
def test_engine():
    db_path = create_temp_db()
    engine = setup_engine(db_path)

    try:
        create_tables(engine)
        verify_tables(engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

    yield engine

    cleanup_db(engine, db_path)

@asynccontextmanager
async def test_lifespan(app):
    yield


def check_session_tables(session):
    session_inspector = inspect(session.bind)
    session_tables = session_inspector.get_table_names()
    print(f"Tables accessible from session: {session_tables}")
    return session_tables


@pytest.fixture(scope="function")
def test_session(test_engine):
    with Session(test_engine) as session:
        check_session_tables(session)
        yield session


def create_override_session(test_session):
    def _get_test_session() -> Generator[Session, Any, None]:
        print("Using test session override")

        inspector = inspect(test_session.bind)
        tables = inspector.get_table_names()
        print(f"Tables in overridden session: {tables}")

        try:
            yield test_session
        finally:
            pass

    return _get_test_session


@pytest.fixture
def override_get_session(test_session):
    return create_override_session(test_session)


def setup_client_overrides(override_get_session):
    app.router.lifespan_context = test_lifespan
    from app.database import get_session
    app.dependency_overrides[get_session] = override_get_session

def verify_client_tables(test_session):
    inspector = inspect(test_session.bind)
    tables = inspector.get_table_names()
    print(f"Tables available to test client: {tables}")


def cleanup_client_overrides():
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_session, override_get_session):
    setup_client_overrides(override_get_session)

    with TestClient(app) as client:
        verify_client_tables(test_session)
        yield client

    cleanup_client_overrides()

@pytest.fixture
def invalid_token():
    return "invalid_token"

@pytest.fixture
def expired_token():
    return ""

@pytest.fixture
def jwt_secret_key() -> str:
    return "hIxw40sQsDfq0Dip+yxlYec2sp3q0REOIs8JNXPvW0Wiy0cM3kq/6tDFfpLwgcDLdD3AqT+il43kGV6vcN3nqQ=="

@pytest.fixture
def jwt_expiration_minutes() -> int:
    return 60

@pytest.fixture
def jwt_algorithm():
    return "HS256"

@pytest.fixture
def valid_token():
    return "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

@pytest.fixture
def authenticated_user():
    return AuthenticatedUser(
        user_id=1,
        username="testuser@test.fr",
        role_name="USER"
    )

@pytest.fixture
def authenticated_admin():
    return AuthenticatedUser(
        user_id=2,
        username="testadminuser@test.fr",
        role_name="ADMIN"
    )

@pytest.fixture
def request_object_with_no_token(client, request_info_with_no_token):
    return client.build_request(
        method=request_info_with_no_token["method"],
        url=request_info_with_no_token["url"],
        headers=request_info_with_no_token["headers"]
    )


@pytest.fixture
def request_info_with_no_token():
    return {
        "method": "GET",
        "url": "/species/1",
        "headers": {
            "Content-Type": "application/json"
        }
    }

@pytest.fixture
def request_with_invalid_token(invalid_token: str):
    headers = {
            "Authorization": invalid_token,
            "Content-Type": "application/json"
    }

    return {
        "method": "POST",
        "url": "/species/1",
        "headers": headers
    }

@pytest.fixture
def request_with_valid_token(valid_token: str) -> dict[str, str]:

    headers = {
            "Authorization": valid_token,
            "Content-Type": "application/json"
    }

    return {
        "method": "POST",
        "url": "/species/1",
        "headers": headers
    }