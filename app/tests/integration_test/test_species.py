import pytest
from fastapi.testclient import TestClient
from io import BytesIO


class TestSpeciesPrediction:
    """Test species prediction endpoints"""

    def test_predict_image_class_unauthenticated(self, client):
        """Test image prediction without authentication"""
        # Create a mock image file
        image_data = b"fake image data"
        files = {"image": ("test.jpg", BytesIO(image_data), "image/jpeg")}
        
        response = client.post("api/species/predict", files=files)
        assert response.status_code == 401

    def test_predict_image_class_no_file(self, authenticated_client):
        """Test image prediction without file"""
        response = authenticated_client.post("api/species/predict")
        assert response.status_code == 422

    def test_predict_image_class_invalid_content_type(self, authenticated_client):
        """Test image prediction with invalid content type"""
        text_data = b"not an image"
        files = {"image": ("test.txt", BytesIO(text_data), "text/plain")}
        
        response = authenticated_client.post("api/species/predict", files=files)
        assert response.status_code == 400


class TestSpeciesUpload:
    """Test species identification upload endpoints"""

    def test_upload_identification_unauthenticated(self, client):
        """Test uploading identification without authentication"""
        response = client.post(
            "api/species/upload_identification",
            json={
                "user_id": 1,
                "specie_id": 1,
                "tmp_file_path": "/tmp/test.jpg",
                "image_file_name": "test.jpg"
            }
        )
        assert response.status_code == 401

    def test_upload_identification_missing_data(self, authenticated_client):
        """Test uploading identification with missing data"""
        response = authenticated_client.post(
            "api/species/upload_identification",
            json={"user_id": 1}
        )
        assert response.status_code == 422


class TestSpeciesRetrieval:
    """Test species information retrieval endpoints"""

    def test_get_specie_information_unauthenticated(self, client):
        """Test getting species information without authentication"""
        response = client.get("api/species/1")
        assert response.status_code == 401

    def test_get_specie_information_authenticated(self, authenticated_client):
        """Test getting species information when authenticated"""
        response = authenticated_client.get("api/species/1")
        assert response.status_code == 200

    def test_get_nonexistent_specie(self, authenticated_client):
        """Test getting non-existent species"""
        response = authenticated_client.get("api/species/999")
        assert response.status_code == 404

    def test_get_identified_species_by_user_unauthenticated(self, client):
        """Test getting identified species by user without authentication"""
        response = client.get("api/species/identified/1")
        assert response.status_code == 401

    def test_get_identified_species_by_user_authenticated(self, authenticated_client):
        """Test getting identified species by user when authenticated"""
        response = authenticated_client.get("api/species/identified/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_identified_species_unauthenticated(self, client):
        """Test getting current user's identified species without authentication"""
        response = client.get("api/species/identified/me/all")
        assert response.status_code == 401

    def test_get_user_identified_species_authenticated(self, authenticated_client):
        """Test getting current user's identified species when authenticated"""
        response = authenticated_client.get("api/species/identified/me/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_user_identified_specie_by_id_unauthenticated(self, client):
        """Test getting specific identified species by current user without authentication"""
        response = client.get("api/species/identified/me/1")
        assert response.status_code == 401

    def test_get_user_identified_specie_by_id_authenticated(self, authenticated_client):
        """Test getting specific identified species by current user when authenticated"""
        response = authenticated_client.get("api/species/identified/me/1")
        # This might return 404 if no identification exists, which is valid
        assert response.status_code in [200, 404]

    def test_get_all_species_for_user_unauthenticated(self, client):
        """Test getting all species for user without authentication"""
        response = client.get("api/species/me/all")
        assert response.status_code == 401

    def test_get_all_species_for_user_authenticated(self, authenticated_client):
        """Test getting all species for user when authenticated"""
        response = authenticated_client.get("api/species/me/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_all_species_unauthenticated(self, client):
        """Test listing all species without authentication"""
        response = client.get("api/species/list/all")
        assert response.status_code == 401

    def test_list_all_species_authenticated(self, authenticated_client):
        """Test listing all species when authenticated"""
        response = authenticated_client.get("api/species/list/all")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSpeciesManagement:
    """Test species management endpoints (admin only)"""

    def test_create_specie_unauthenticated(self, client):
        """Test creating species without authentication"""
        response = client.post(
            "api/species/create",
            json={
                "name": "Test Species",
                "latin_name": "Testus speciesus",
                "description": "A test species",
                "size": "Medium",
                "region": "Test Region",
                "fun_fact": "This is a test",
                "specie_exemple_photo": "http://example.com/photo.jpg",
                "footprint_exemple_photo": "http://example.com/footprint.jpg",
                "family_id": 1
            }
        )
        assert response.status_code == 401

    def test_create_specie_not_authorized(self, authenticated_client):
        """Test creating species as regular user (should fail)"""
        response = authenticated_client.post(
            "api/species/create",
            json={
                "name": "Test Species",
                "latin_name": "Testus speciesus",
                "description": "A test species",
                "size": "Medium",
                "region": "Test Region",
                "fun_fact": "This is a test",
                "specie_exemple_photo": "http://example.com/photo.jpg",
                "footprint_exemple_photo": "http://example.com/footprint.jpg",
                "family_id": 1
            }
        )
        assert response.status_code == 403

    def test_create_specie_as_admin(self, admin_client):
        """Test creating species as admin"""
        response = admin_client.post(
            "api/species/create",
            json={
                "name": "Test Species",
                "latin_name": "Testus speciesus",
                "description": "A test species",
                "size": "Medium",
                "region": "Test Region",
                "fun_fact": "This is a test",
                "specie_exemple_photo": "http://example.com/photo.jpg",
                "footprint_exemple_photo": "http://example.com/footprint.jpg",
                "family_id": 1
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "specie created successfully"

    def test_create_specie_missing_fields(self, admin_client):
        """Test creating species with missing required fields"""
        response = admin_client.post(
            "api/species/create",
            json={"name": "Incomplete Species"}
        )
        assert response.status_code == 422

    def test_update_specie_unauthenticated(self, client):
        """Test updating species without authentication"""
        response = client.put(
            "api/species/update/1",
            json={"name": "Updated Species"}
        )
        assert response.status_code == 401

    def test_update_specie_not_authorized(self, authenticated_client):
        """Test updating species as regular user (should fail)"""
        response = authenticated_client.put(
            "api/species/update/1",
            json={"name": "Updated Species"}
        )
        assert response.status_code == 403

    def test_update_specie_as_admin(self, admin_client):
        """Test updating species as admin"""
        response = admin_client.put(
            "api/species/update/1",
            json={
                "name": "Updated Species",
                "description": "Updated description"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "specie updated successfully"

    def test_update_nonexistent_specie(self, admin_client):
        """Test updating non-existent species"""
        response = admin_client.put(
            "api/species/update/999",
            json={"name": "Should Fail"}
        )
        assert response.status_code == 404

    def test_delete_specie_unauthenticated(self, client):
        """Test deleting species without authentication"""
        response = client.delete("api/species/delete/1")
        assert response.status_code == 401

    def test_delete_specie_not_authorized(self, authenticated_client):
        """Test deleting species as regular user (should fail)"""
        response = authenticated_client.delete("api/species/delete/1")
        assert response.status_code == 403

    def test_delete_specie_as_admin(self, admin_client):
        """Test deleting species as admin"""
        # First create a species to delete
        create_response = admin_client.post(
            "api/species/create",
            json={
                "name": "To Delete",
                "latin_name": "Deleteus speciesus",
                "description": "Will be deleted",
                "size": "Small",
                "region": "Delete Region",
                "fun_fact": "Will be gone",
                "specie_exemple_photo": "http://example.com/delete.jpg",
                "footprint_exemple_photo": "http://example.com/delete_foot.jpg",
                "family_id": 1
            }
        )
        assert create_response.status_code == 201

        # Now delete it (assuming it gets ID 2)
        response = admin_client.delete("api/species/delete/2")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "specie deleted successfully"

    def test_delete_nonexistent_specie(self, admin_client):
        """Test deleting non-existent species"""
        response = admin_client.delete("api/species/delete/999")
        assert response.status_code == 404