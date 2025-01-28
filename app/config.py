import os
import re

# AI models
WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH = "cnn_models/wildlens_test.h5"
WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH = "cnn_models/wildlens_test.h5"
WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD = 0.6

NUMBER_OF_CLASSES = 14

# JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 30))

# Regex patterns
email_validation_regex = re.compile(r"([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\"([]!#-[^-~ \t]|(\\[\t -~]))+\")@([-!#-'*+/-9=?A-Z^-~]+(\.[-!#-'*+/-9=?A-Z^-~]+)*|\[[\t -Z^-~]*])")


# API
API_PREFIX = os.getenv("API_PREFIX", "/api")

EXCLUDED_PATHS = [
    "/docs", # Swagger UI
    f"{API_PREFIX}/openapi.json", # OpenAPI schema
    f"{API_PREFIX}/users/token", # Login
    f"{API_PREFIX}/users/register" # Register
]