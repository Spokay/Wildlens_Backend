import pytest

from app.dto.users import AuthenticatedUser


@pytest.fixture
def test_client():
    from fastapi.testclient import TestClient
    from app.main import app

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
def request_with_no_token():
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