import logging
import pathlib
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration"""

    # Environment
    environment: str = Field(default="development", description="Runtime environment")
    debug: bool = Field(default=True, description="Debug mode")
    app_port: int = Field(default=8002, description="Application port")

    # Prediction API - Wildlens
    wildlens_footprint_binary_classification_threshold: float = Field(
        default=0.6,
        description="Binary classification threshold for footprints"
    )
    wildlens_prediction_api_base_url: str = Field(
        default="",
        description="Wildlens prediction API base URL",
        validation_alias="WILDLENS_PREDICTION_API_BASE_URL"
    )
    wildlens_prediction_api_key: str = Field(
        default="",
        description="Wildlens API key",
        validation_alias="WILDLENS_PREDICTION_API_KEY"
    )

    # Authorized MIME types for predictions
    prediction_authorized_mime_types: List[str] = Field(
        default=["image/jpeg", "image/png"],
        description="Authorized MIME types for predictions"
    )

    # Prediction configuration
    number_of_classes: int = Field(default=1, description="Number of classes for prediction")

    # JWT Configuration
    jwt_secret_key: Optional[str] = Field(
        default=None,
        description="Secret key for JWT",
        validation_alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signature algorithm",
        validation_alias="JWT_ALGORITHM"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes",
        validation_alias="JWT_EXPIRATION_MINUTES"
    )

    # Azure Blob Storage Configuration
    azure_storage_account_name: str = Field(
        default="",
        description="Azure Storage account name",
        validation_alias="AZURE_STORAGE_ACCOUNT_NAME"
    )
    azure_storage_account_key: str = Field(
        default="",
        description="Azure Storage account key",
        validation_alias="AZURE_STORAGE_ACCOUNT_KEY"
    )
    azure_storage_container_name: str = Field(
        default="",
        description="Azure Storage container name",
        validation_alias="AZURE_STORAGE_CONTAINER_NAME"
    )

    # API Configuration
    api_prefix: str = Field(
        default="/api",
        description="Prefix for API routes"
    )

    # Database Configuration
    db_host: Optional[str] = Field(
        default=None,
        description="Database host"
    )
    db_port: int = Field(
        default=3306,
        description="Database port"
    )
    db_name: Optional[str] = Field(
        default=None,
        description="Database name"
    )
    db_user: Optional[str] = Field(
        default=None,
        description="Database user"
    )
    db_password: Optional[str] = Field(
        default=None,
        description="Database password"
    )
    db_driver: str = Field(
        default="mariadb+pymysql",
        description="Database driver (mariadb+pymysql, mysql+pymysql, etc.)"
    )

    # Computed properties
    @property
    def project_root(self) -> pathlib.Path:
        """Project root directory"""
        return pathlib.Path(__file__).resolve().parent.parent

    @property
    def excluded_paths(self) -> List[str]:
        """Paths excluded from authentication"""
        return [
            "/metrics",  # Prometheus metrics
            "/docs",  # Swagger UI
            f"{self.api_prefix}/openapi.json",  # OpenAPI schema
            f"{self.api_prefix}/users/token",  # Login
            f"{self.api_prefix}/users/register"  # Register
        ]

    @property
    def is_using_memory_db(self) -> bool:
        """Check if using in-memory database"""
        return self.database_url == "sqlite:///:memory:"

    @property
    def database_url(self) -> str:
        """Build database connection string dynamically"""
        if not all([self.db_host, self.db_name, self.db_user, self.db_password]):
            return "sqlite:///:memory:"

        return f"{self.db_driver}://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.environment.lower() == "production"

    # Pydantic V2 field validators
    @field_validator('environment')
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = ['development', 'production', 'testing']
        if v.lower() not in allowed:
            raise ValueError(f'Environment must be one of: {allowed}')
        return v.lower()

    @field_validator('wildlens_footprint_binary_classification_threshold')
    @classmethod
    def validate_threshold(cls, v: float) -> float:
        if not 0 <= v <= 1:
            raise ValueError('Threshold must be between 0 and 1')
        return v

    @field_validator('access_token_expire_minutes')
    @classmethod
    def validate_token_expiry(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('Expiration time must be positive')
        return v

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 characters long')
        return v

    @field_validator('api_prefix')
    @classmethod
    def validate_api_prefix(cls, v: str) -> str:
        if not v.startswith('/'):
            v = f'/{v}'
        return v.rstrip('/')

    @field_validator('db_port')
    @classmethod
    def validate_db_port(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError('Database port must be between 1 and 65535')
        return v

    # Model validator for cross-field validation (Pydantic V2)
    @model_validator(mode='after')
    def validate_production_requirements(self) -> 'Settings':
        """Production-specific validation"""
        if self.environment == 'production':
            if not self.jwt_secret_key:
                raise ValueError('JWT_SECRET_KEY is required in production')
        return self

    # Pydantic settings configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Environment variable mapping
        env_nested_delimiter="__",
        extra="ignore"
    )


# Environment-specific configuration classes
class DevelopmentSettings(Settings):
    """Development environment configuration"""
    environment: str = "development"
    debug: bool = True

    # Default values for development
    jwt_secret_key: str = "dev-secret-key-1234567891234567890"


class ProductionSettings(Settings):
    """Production environment configuration"""
    environment: str = "production"
    debug: bool = False

    # Required values in production
    wildlens_prediction_api_base_url: str = Field(..., description="API URL required in production")
    wildlens_prediction_api_key: str = Field(..., description="API key required in production")
    jwt_secret_key: str = Field(..., description="JWT key required in production")

    azure_storage_account_name: str = Field(..., description="Azure account name required in production")
    azure_storage_account_key: str = Field(..., description="Azure account key required in production")
    azure_storage_container_name: str = Field(..., description="Azure container name required in production")



class TestingSettings(Settings):
    """Testing environment configuration"""
    environment: str = "testing"
    debug: bool = True
    jwt_secret_key: str = "test-secret-key-12345678901234567890"

    # Database configuration for testing (defaults to in-memory)
    db_host: Optional[str] = None
    db_name: Optional[str] = None
    db_user: Optional[str] = None
    db_password: Optional[str] = None


@lru_cache()
def get_settings() -> Settings:
    """
    Returns configuration based on environment.
    Uses cache to keep the config between each calls.
    """
    import os
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    elif environment == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()
