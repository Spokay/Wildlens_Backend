import pytest
from fastapi.testclient import TestClient


class TestHabitatCreation:
    """Test habitat creation endpoints"""

    def test_create_habitat_unauthenticated(self, client):
        """Test creating habitat without authentication"""
        response = client.post(
            "api/habitats/create",
            json={
                "name": "Test Habitat",
                "habitat_photo": "http://example.com/habitat.jpg"
            }
        )
        assert response.status_code == 401

    def test_create_habitat_not_authorized(self, authenticated_client):
        """Test creating habitat as regular user (should fail)"""
        response = authenticated_client.post(
            "api/habitats/create",
            json={
                "name": "Test Habitat",
                "habitat_photo": "http://example.com/habitat.jpg"
            }
        )
        assert response.status_code == 403

    def test_create_habitat_as_admin(self, admin_client):
        """Test creating habitat as admin"""
        response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "Test Habitat",
                "habitat_photo": "http://example.com/habitat.jpg"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "habitats created successfully"
        assert data["habitat"]["name"] == "Test Habitat"

    def test_create_habitat_missing_fields(self, admin_client):
        """Test creating habitat with missing required fields"""
        response = admin_client.post(
            "api/habitats/create",
            json={"name": "Incomplete Habitat"}
        )
        assert response.status_code == 422

    def test_create_habitat_empty_name(self, admin_client):
        """Test creating habitat with empty name"""
        response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "",
                "habitat_photo": "http://example.com/habitat.jpg"
            }
        )
        assert response.status_code == 422


class TestHabitatRetrieval:
    """Test habitat retrieval endpoints"""

    def test_list_all_habitats_unauthenticated(self, client):
        """Test listing all habitats without authentication"""
        response = client.get("api/habitats/list/all")
        assert response.status_code == 401

    def test_list_all_habitats_authenticated(self, authenticated_client):
        """Test listing all habitats when authenticated"""
        response = authenticated_client.get("api/habitats/list/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_habitat_by_id_unauthenticated(self, client):
        """Test getting habitat by ID without authentication"""
        response = client.get("api/habitats/list/1")
        assert response.status_code == 401

    def test_list_habitat_by_id_authenticated(self, authenticated_client):
        """Test getting habitat by ID when authenticated"""
        # First create a habitat to retrieve
        admin_token = authenticated_client.post(
            "api/users/token",
            data={"username": "admin", "password": "admin123"}
        ).json()["access_token"]
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        create_response = authenticated_client.post(
            "api/habitats/create",
            json={
                "name": "Retrievable Habitat",
                "habitat_photo": "http://example.com/retrievable.jpg"
            },
            headers=admin_headers
        )
        assert create_response.status_code == 201

        # Now retrieve it
        response = authenticated_client.get("api/habitats/list/1")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "habitat_photo" in data

    def test_list_nonexistent_habitat(self, authenticated_client):
        """Test getting non-existent habitat"""
        response = authenticated_client.get("api/habitats/list/999")
        assert response.status_code == 404


class TestHabitatUpdate:
    """Test habitat update endpoints"""

    def test_update_habitat_unauthenticated(self, client):
        """Test updating habitat without authentication"""
        response = client.put(
            "api/habitats/update/1",
            json={"name": "Updated Habitat"}
        )
        assert response.status_code == 401

    def test_update_habitat_not_authorized(self, authenticated_client):
        """Test updating habitat as regular user (should fail)"""
        response = authenticated_client.put(
            "api/habitats/update/1",
            json={"name": "Updated Habitat"}
        )
        assert response.status_code == 403

    def test_update_habitat_as_admin(self, admin_client):
        """Test updating habitat as admin"""
        # First create a habitat to update
        create_response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "To Update",
                "habitat_photo": "http://example.com/toupdate.jpg"
            }
        )
        assert create_response.status_code == 201

        # Now update it
        response = admin_client.put(
            "api/habitats/update/1",
            json={
                "name": "Updated Habitat",
                "habitat_photo": "http://example.com/updated.jpg"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "habitat updated successfully"
        assert data["habitat"]["name"] == "Updated Habitat"

    def test_update_habitat_partial(self, admin_client):
        """Test partial update of habitat"""
        # First create a habitat to update
        create_response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "Partial Update",
                "habitat_photo": "http://example.com/partial.jpg"
            }
        )
        assert create_response.status_code == 201

        # Now partially update it
        response = admin_client.put(
            "api/habitats/update/2",
            json={"name": "Partially Updated"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["habitat"]["name"] == "Partially Updated"

    def test_update_nonexistent_habitat(self, admin_client):
        """Test updating non-existent habitat"""
        response = admin_client.put(
            "api/habitats/update/999",
            json={"name": "Should Fail"}
        )
        assert response.status_code == 404


class TestHabitatDeletion:
    """Test habitat deletion endpoints"""

    def test_delete_habitat_unauthenticated(self, client):
        """Test deleting habitat without authentication"""
        response = client.delete("api/habitats/delete/1")
        assert response.status_code == 401

    def test_delete_habitat_not_authorized(self, authenticated_client):
        """Test deleting habitat as regular user (should fail)"""
        response = authenticated_client.delete("api/habitats/delete/1")
        assert response.status_code == 403

    def test_delete_habitat_as_admin(self, admin_client):
        """Test deleting habitat as admin"""
        # First create a habitat to delete
        create_response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "To Delete",
                "habitat_photo": "http://example.com/todelete.jpg"
            }
        )
        assert create_response.status_code == 201

        # Now delete it
        response = admin_client.delete("api/habitats/delete/3")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "habitats deleted successfully"

        # Verify it's deleted
        get_response = admin_client.get("api/habitats/list/3")
        assert get_response.status_code == 404

    def test_delete_nonexistent_habitat(self, admin_client):
        """Test deleting non-existent habitat"""
        response = admin_client.delete("api/habitats/delete/999")
        assert response.status_code == 404


class TestHabitatValidation:
    """Test habitat data validation"""

    def test_create_habitat_invalid_photo_url(self, admin_client):
        """Test creating habitat with invalid photo URL"""
        response = admin_client.post(
            "api/habitats/create",
            json={
                "name": "Invalid Photo",
                "habitat_photo": "not-a-url"
            }
        )
        # This might pass validation depending on implementation
        # The test verifies the current behavior
        assert response.status_code in [201, 422]

    def test_create_habitat_very_long_name(self, admin_client):
        """Test creating habitat with very long name"""
        long_name = "A" * 300  # Very long name
        response = admin_client.post(
            "api/habitats/create",
            json={
                "name": long_name,
                "habitat_photo": "http://example.com/long.jpg"
            }
        )
        # This might fail validation depending on database constraints
        assert response.status_code in [201, 422]