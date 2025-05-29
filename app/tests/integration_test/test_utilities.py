import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check_unauthenticated(self, client):
        """Test health check without authentication"""
        response = client.get("health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "debug" in data
        assert "api_prefix" in data

    def test_health_check_authenticated(self, authenticated_client):
        """Test health check with authentication"""
        response = authenticated_client.get("health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_response_structure(self, client):
        """Test health check response has correct structure"""
        response = client.get("health")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = ["status", "environment", "debug", "api_prefix"]
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["status"], str)
        assert isinstance(data["environment"], str)
        assert isinstance(data["debug"], bool)
        assert isinstance(data["api_prefix"], str)

    def test_health_check_status_value(self, client):
        """Test health check status is always healthy"""
        response = client.get("health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestConfigInfo:
    """Test configuration info endpoint"""

    def test_config_info_unauthenticated(self, client):
        """Test config info without authentication"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data
        assert "debug" in data
        assert "api_prefix" in data

    def test_config_info_authenticated(self, authenticated_client):
        """Test config info with authentication"""
        response = authenticated_client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        assert "environment" in data

    def test_config_info_response_structure(self, client):
        """Test config info response has correct structure"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        required_fields = [
            "environment",
            "debug",
            "api_prefix",
            "number_of_classes",
            "threshold",
            "mime_types",
            "token_expire_minutes"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data["environment"], str)
        assert isinstance(data["debug"], bool)
        assert isinstance(data["api_prefix"], str)
        assert isinstance(data["number_of_classes"], int)
        assert isinstance(data["threshold"], (int, float))
        assert isinstance(data["mime_types"], list)
        assert isinstance(data["token_expire_minutes"], int)

    def test_config_info_no_secrets(self, client):
        """Test config info doesn't expose secrets"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        # Check that sensitive fields are not exposed
        sensitive_fields = [
            "database_url",
            "secret_key",
            "password",
            "api_key",
            "token",
            "private_key"
        ]
        
        for field in sensitive_fields:
            assert field not in data

    def test_config_info_environment_value(self, client):
        """Test config info environment is testing"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        assert data["environment"] == "testing"

    def test_config_info_mime_types_structure(self, client):
        """Test config info mime types is a list"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        mime_types = data["mime_types"]
        assert isinstance(mime_types, list)
        
        # Check that mime types are strings
        for mime_type in mime_types:
            assert isinstance(mime_type, str)
            assert "/" in mime_type  # Basic mime type format check

    def test_config_info_threshold_range(self, client):
        """Test config info threshold is in valid range"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        threshold = data["threshold"]
        assert 0.0 <= threshold <= 1.0  # Threshold should be between 0 and 1

    def test_config_info_token_expire_positive(self, client):
        """Test config info token expire minutes is positive"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        token_expire = data["token_expire_minutes"]
        assert token_expire > 0  # Should be positive

    def test_config_info_number_of_classes_positive(self, client):
        """Test config info number of classes is positive"""
        response = client.get("config/info")
        assert response.status_code == 200
        data = response.json()
        
        num_classes = data["number_of_classes"]
        assert num_classes > 0  # Should be positive


class TestUtilitiesEndpointAccess:
    """Test utilities endpoints accessibility"""

    def test_health_endpoint_always_accessible(self, client):
        """Test health endpoint is always accessible"""
        response = client.get("health")
        assert response.status_code == 200

    def test_config_endpoint_always_accessible(self, client):
        """Test config endpoint is always accessible"""
        response = client.get("config/info")
        assert response.status_code == 200

    def test_health_endpoint_with_admin(self, admin_client):
        """Test health endpoint with admin user"""
        response = admin_client.get("health")
        assert response.status_code == 200

    def test_config_endpoint_with_admin(self, admin_client):
        """Test config endpoint with admin user"""
        response = admin_client.get("config/info")
        assert response.status_code == 200


class TestUtilitiesErrorHandling:
    """Test utilities endpoints error handling"""

    def test_health_endpoint_method_not_allowed(self, client):
        """Test health endpoint with wrong HTTP method"""
        response = client.post("health")
        assert response.status_code == 405

    def test_config_endpoint_method_not_allowed(self, client):
        """Test config endpoint with wrong HTTP method"""
        response = client.post("config/info")
        assert response.status_code == 405

    def test_health_endpoint_with_query_params(self, client):
        """Test health endpoint ignores query parameters"""
        response = client.get("health?param=value")
        assert response.status_code == 200

    def test_config_endpoint_with_query_params(self, client):
        """Test config endpoint ignores query parameters"""
        response = client.get("config/info?param=value")
        assert response.status_code == 200