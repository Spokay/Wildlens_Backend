import pytest
from fastapi.testclient import TestClient


class TestUserAuthentication:
    """Test user authentication endpoints"""

    def test_login_success(self, client):
        """Test successful login with valid credentials"""
        response = client.post(
            "api/users/token",
            data={"username": "user", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client):
        """Test login with invalid username"""
        response = client.post(
            "api/users/token",
            data={"username": "nonexistent", "password": "admin123"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        response = client.post(
            "api/users/token",
            data={"username": "user", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials"""
        response = client.post("api/users/token", data={})
        assert response.status_code == 422


class TestUserRegistration:
    """Test user registration endpoints"""

    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post(
            "api/users/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "validpassword123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_username(self, client):
        """Test registration with existing username"""
        response = client.post(
            "api/users/register",
            json={
                "username": "user",  # Already exists in test data
                "email": "different@test.com",
                "password": "validpassword123"
            }
        )
        assert response.status_code == 409
        assert "User already exists" in response.json()["detail"]

    def test_register_invalid_password(self, client):
        """Test registration with invalid password"""
        response = client.post(
            "api/users/register",
            json={
                "username": "newuser2",
                "email": "newuser2@test.com",
                "password": "weak"  # Too weak password
            }
        )
        assert response.status_code == 400
        assert "Password is not valid" in response.json()["detail"]

    def test_register_missing_fields(self, client):
        """Test registration with missing required fields"""
        response = client.post(
            "api/users/register",
            json={"username": "incomplete"}
        )
        assert response.status_code == 422


class TestUserProfile:
    """Test user profile management endpoints"""

    def test_get_user_profile_authenticated(self, authenticated_client):
        """Test getting user profile when authenticated"""
        response = authenticated_client.get("api/users/me")
        assert response.status_code == 200
        data = response.json()
        assert "username" in data
        assert "email" in data
        assert "created_at" in data

    def test_get_user_profile_unauthenticated(self, client):
        """Test getting user profile without authentication"""
        response = client.get("api/users/me")
        assert response.status_code == 401

    def test_update_user_profile_authenticated(self, authenticated_client):
        """Test updating user profile when authenticated"""
        response = authenticated_client.put(
            "api/users/me",
            json={
                "username": "updateduser",
                "email": "updated@test.com"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "user updated successfully"
        assert data["user"]["username"] == "updateduser"
        assert data["user"]["email"] == "updated@test.com"

    def test_update_user_profile_partial(self, authenticated_client):
        """Test partial update of user profile"""
        response = authenticated_client.put(
            "api/users/me",
            json={"username": "partialupdate"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["username"] == "partialupdate"

    def test_update_user_profile_unauthenticated(self, client):
        """Test updating user profile without authentication"""
        response = client.put(
            "api/users/me",
            json={"username": "shouldfail"}
        )
        assert response.status_code == 401


class TestUserDeletion:
    """Test user deletion endpoints (admin only)"""

    def test_delete_user_as_admin(self, admin_client):
        """Test deleting user as admin"""
        # First create a user to delete
        response = admin_client.post(
            "api/users/register",
            json={
                "username": "todelete",
                "email": "todelete@test.com",
                "password": "validpassword123"
            }
        )
        assert response.status_code == 201

        # Get the user ID (we'll use ID 3 as it should be the newly created user)
        response = admin_client.delete("api/users/delete/3")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "user deleted successfully"

    def test_delete_user_as_regular_user(self, authenticated_client):
        """Test deleting user as regular user (should fail)"""
        response = authenticated_client.delete("api/users/delete/1")
        assert response.status_code == 403

    def test_delete_user_unauthenticated(self, client):
        """Test deleting user without authentication"""
        response = client.delete("api/users/delete/1")
        assert response.status_code == 401

    def test_delete_nonexistent_user(self, admin_client):
        """Test deleting non-existent user"""
        response = admin_client.delete("api/users/delete/999")
        assert response.status_code == 404


class TestUserBadges:
    """Test user badges endpoints"""

    def test_get_user_badges_authenticated(self, authenticated_client):
        """Test getting user badges when authenticated"""
        response = authenticated_client.get("api/users/me/badges")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_badges_unauthenticated(self, client):
        """Test getting user badges without authentication"""
        response = client.get("api/users/me/badges")
        assert response.status_code == 401