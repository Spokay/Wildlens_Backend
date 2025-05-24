import os
from contextlib import asynccontextmanager
from typing import Any, Generator
import tempfile

from sqlalchemy import create_engine, inspect

from app.database import create_tables, drop_tables
from app.models import User, Role
from app.services.user_service import get_password_hash

os.environ["ENVIRONMENT"] = "testing"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import select, Session

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


def clear_existing_data(test_session):
    try:
        for user in test_session.exec(select(User)).all():
            test_session.delete(user)

        for role in test_session.exec(select(Role)).all():
            test_session.delete(role)

        test_session.commit()
    except Exception:
        test_session.rollback()


def create_test_roles(test_session):
    admin_role = Role(id=1, name="ADMIN")
    user_role = Role(id=2, name="USER")

    test_session.add(admin_role)
    test_session.add(user_role)
    test_session.commit()


def create_test_users(test_session):
    test_user = User(
        username="user",
        email="test@user.com",
        password=get_password_hash("admin123"),
        role_id=2,
    )

    test_admin = User(
        username="admin",
        email="test@admin.com",
        password=get_password_hash("admin123"),
        role_id=1,
    )

    test_session.add(test_user)
    test_session.add(test_admin)
    test_session.commit()


def verify_test_setup(test_session):
    user_count = len(test_session.exec(select(User)).all())
    role_count = len(test_session.exec(select(Role)).all())
    print(f"Setup complete - Users: {user_count}, Roles: {role_count}")

    users = test_session.exec(select(User)).all()
    for user in users:
        print(f"Created user: {user.username} (ID: {user.id}, Role: {user.role_id})")


@pytest.fixture(scope="function", autouse=True)
def setup_test_data(test_session):
    clear_existing_data(test_session)
    create_test_roles(test_session)
    create_test_users(test_session)
    verify_test_setup(test_session)


def verify_user_exists(test_session, username):
    user_check = test_session.exec(select(User).where(User.username == username)).first()
    if not user_check:
        all_users = test_session.exec(select(User)).all()
        print(f"Available users in test session: {[u.username for u in all_users]}")
        raise Exception(f"User '{username}' not found in database")
    return user_check


def check_dependency_override():
    from app.database import get_session
    if get_session in app.dependency_overrides:
        print("Dependency override is registered")
    else:
        print("Dependency override is NOT registered")


def make_token_request(client, username, password):
    response = client.post(
        "/api/users/token",
        data={
            "username": username,
            "password": password,
        },
    )
    return response


def handle_token_error(response, test_session, user_check):
    print(f"Token request failed. Status: {response.status_code}")
    print(f"Response: {response.text}")

    role_check = test_session.exec(select(Role).where(Role.id == user_check.role_id)).first()
    if role_check:
        print(f"User's role exists in test session: {role_check.name}")
    else:
        print(f"User's role (ID: {user_check.role_id}) does NOT exist in test session!")


def create_token_getter(client, test_session):
    def _get_token(username="user", password="admin123"):
        print(f"Requesting token for user: {username}")

        user_check = verify_user_exists(test_session, username)
        print(f"Found user in test session: {user_check.username} (ID: {user_check.id}, Role ID: {user_check.role_id})")

        check_dependency_override()
        response = make_token_request(client, username, password)

        if response.status_code != 200:
            handle_token_error(response, test_session, user_check)
            raise Exception(f"Failed to get token for user '{username}': {response.status_code} - {response.text}")

        token_data = response.json()
        print(f"Token obtained successfully")
        return token_data["access_token"]

    return _get_token


@pytest.fixture
def get_token(client, test_session):
    return create_token_getter(client, test_session)


@pytest.fixture
def authenticated_client(client, get_token):
    token = get_token(username="user", password="admin123")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def admin_client(client, get_token):
    token = get_token(username="admin", password="admin123")
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def test_users(test_session):
    users = test_session.exec(select(User)).all()
    user_dict = {user.username: user for user in users}
    return user_dict


@pytest.fixture
def admin_user(test_users):
    return test_users.get("admin")


@pytest.fixture
def regular_user(test_users):
    return test_users.get("user")