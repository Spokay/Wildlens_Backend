import pytest
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from app.database import create_db_and_tables
from app.dto.users import AuthenticatedUser
from app.main import app

TEST_DATABASE_URL = "sqlite:///:memory:"
test_database_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="function")
def test_session():
    # Creates a new database session with an in-memory DB
    create_db_and_tables(test_database_engine)
    with Session(test_database_engine) as session:
        try:
            yield session
        finally:
            # Clean up after the test
            session.close()
            SQLModel.metadata.drop_all(test_database_engine)

@pytest.fixture
def client(test_session):
    from fastapi.testclient import TestClient
    def override_get_db():
        yield test_session

    app.dependency_overrides[test_session] = override_get_db
    return TestClient(
        app,
        root_path="/api"
    )

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
        email="testuser@test.fr",
        role_name="USER"
    )

@pytest.fixture
def authenticated_admin():
    return AuthenticatedUser(
        user_id=2,
        email="testadminuser@test.fr",
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