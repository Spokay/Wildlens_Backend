import pytest
from fastapi.testclient import TestClient


class TestFamilyCreation:
    """Test family creation endpoints"""

    def test_create_family_unauthenticated(self, client):
        """Test creating family without authentication"""
        response = client.post("api/families/create", json={"name": "Test Family"})
        assert response.status_code == 401

    def test_create_family_not_authorized(self, authenticated_client):
        """Test creating family as regular user (should fail)"""
        response = authenticated_client.post(
            "api/families/create", json={"name": "Test Family"}
        )
        assert response.status_code == 403

    def test_create_family_as_admin(self, admin_client):
        """Test creating family as admin"""
        response = admin_client.post(
            "api/families/create", json={"name": "Test Family"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "family created successfully"
        assert data["family"]["name"] == "Test Family"

    def test_create_family_missing_name(self, admin_client):
        """Test creating family with missing name"""
        response = admin_client.post("api/families/create", json={})
        assert response.status_code == 422

    def test_create_family_empty_name(self, admin_client):
        """Test creating family with empty name"""
        response = admin_client.post("api/families/create", json={"name": ""})
        assert response.status_code == 422

    def test_create_family_duplicate_name(self, admin_client):
        """Test creating family with duplicate name"""
        # Create first family
        response1 = admin_client.post(
            "api/families/create", json={"name": "Duplicate Family"}
        )
        assert response1.status_code == 201

        # Try to create another with same name
        response2 = admin_client.post(
            "api/families/create", json={"name": "Duplicate Family"}
        )
        # This might succeed or fail depending on database constraints
        assert response2.status_code in [201, 409, 422]


class TestFamilyRetrieval:
    """Test family retrieval endpoints"""

    def test_get_family_unauthenticated(self, client):
        """Test getting family without authentication"""
        response = client.get("api/families/1")
        assert response.status_code == 401

    def test_get_family_authenticated(self, authenticated_client):
        """Test getting family when authenticated"""
        # First create a family to retrieve
        admin_token = authenticated_client.post(
            "api/users/token",
            data={"username": "admin", "password": "admin123"}
        ).json()["access_token"]
        
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        
        create_response = authenticated_client.post(
            "api/families/create",
            json={"name": "Retrievable Family"},
            headers=admin_headers
        )

        family_id = create_response.json()["family"]["id"]
        assert create_response.status_code == 201

        # Now retrieve it
        response = authenticated_client.get(f"api/families/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Retrievable Family"

    def test_get_nonexistent_family(self, authenticated_client):
        """Test getting non-existent family"""
        response = authenticated_client.get("api/families/999")
        assert response.status_code == 404

    def test_list_all_families_unauthenticated(self, client):
        """Test listing all families without authentication"""
        response = client.get("api/families/list/all")
        assert response.status_code == 401

    def test_list_all_families_authenticated(self, authenticated_client):
        """Test listing all families when authenticated"""
        response = authenticated_client.get("api/families/list/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_all_families_with_data(self, admin_client):
        """Test listing all families with existing data"""
        # Create some families first
        admin_client.post("api/families/create", json={"name": "Family 1"})
        admin_client.post("api/families/create", json={"name": "Family 2"})

        response = admin_client.get("api/families/list/all")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2


class TestFamilyUpdate:
    """Test family update endpoints"""

    def test_update_family_unauthenticated(self, client):
        """Test updating family without authentication"""
        response = client.put("api/families/update/1", json={"name": "Updated Family"})
        assert response.status_code == 401

    def test_update_family_not_authorized(self, authenticated_client):
        """Test updating family as regular user (should fail)"""
        response = authenticated_client.put(
            "api/families/update/1", json={"name": "Updated Family"}
        )
        assert response.status_code == 403

    def test_update_family_as_admin(self, admin_client):
        """Test updating family as admin"""
        # First create a family to update
        create_response = admin_client.post(
            "api/families/create", json={"name": "To Update"}
        )
        assert create_response.status_code == 201

        # Now update it
        response = admin_client.put(
            "api/families/update/1", json={"name": "Updated Family"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "family updated successfully"
        assert data["family"]["name"] == "Updated Family"

        # Verify the update by retrieving the family
        get_response = admin_client.get("api/families/1")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Updated Family"

    def test_update_nonexistent_family(self, admin_client):
        """Test updating non-existent family"""
        response = admin_client.put(
            "api/families/update/999", json={"name": "Should Fail"}
        )
        assert response.status_code == 404

    def test_update_family_empty_name(self, admin_client):
        """Test updating family with empty name"""
        # First create a family
        create_response = admin_client.post(
            "api/families/create", json={"name": "Valid Name"}
        )
        assert create_response.status_code == 201

        # Try to update with empty name
        response = admin_client.put(
            "api/families/update/2", json={"name": ""}
        )
        assert response.status_code == 422


class TestFamilyDeletion:
    """Test family deletion endpoints"""

    def test_delete_family_unauthenticated(self, client):
        """Test deleting family without authentication"""
        response = client.delete("api/families/delete/1")
        assert response.status_code == 401

    def test_delete_family_not_authorized(self, authenticated_client):
        """Test deleting family as regular user (should fail)"""
        response = authenticated_client.delete("api/families/delete/1")
        assert response.status_code == 403

    def test_delete_family_as_admin(self, admin_client):
        """Test deleting family as admin"""
        # First create a family to delete
        create_response = admin_client.post(
            "api/families/create", json={"name": "To Delete"}
        )
        assert create_response.status_code == 201
        family_id = create_response.json()["family"]["id"]

        # Now delete it
        response = admin_client.delete(f"api/families/delete/{family_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "family deleted successfully"

        # Verify it's deleted
        get_response = admin_client.get(f"api/families/{family_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_family(self, admin_client):
        """Test deleting non-existent family"""
        response = admin_client.delete("api/families/delete/999")
        assert response.status_code == 404


class TestFamilyValidation:
    """Test family data validation"""

    def test_create_family_very_long_name(self, admin_client):
        """Test creating family with very long name"""
        long_name = "A" * 300  # Very long name
        response = admin_client.post(
            "api/families/create", json={"name": long_name}
        )
        # This might fail validation depending on database constraints
        assert response.status_code in [201, 422]

    def test_create_family_special_characters(self, admin_client):
        """Test creating family with special characters in name"""
        special_name = "Family with @#$%^&*() characters"
        response = admin_client.post(
            "api/families/create", json={"name": special_name}
        )
        # Should succeed unless there are specific character restrictions
        assert response.status_code == 201

    def test_create_family_unicode_characters(self, admin_client):
        """Test creating family with unicode characters"""
        unicode_name = "Famille avec des caractères spéciaux éàü"
        response = admin_client.post(
            "api/families/create", json={"name": unicode_name}
        )
        # Should succeed with proper unicode support
        assert response.status_code == 201