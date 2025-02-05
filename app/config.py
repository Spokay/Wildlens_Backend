import os
import re

# Prediction API
WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD = 0.6

WILDLENS_PREDICTION_API_BASE_URL = os.getenv("WILDLENS_PREDICTION_API_BASE_URL", "")
WILDLENS_PREDICTION_API_KEY = os.getenv("WILDLENS_PREDICTION_API_KEY", "")


NUMBER_OF_CLASSES = 1

# JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

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