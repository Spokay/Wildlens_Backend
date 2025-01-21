import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

load_dotenv()

WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH = "cnn_models/wildlens_test.h5"
WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH = "cnn_models/wildlens_test.h5"
WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD = 0.6


# Database
database_url = URL.create(
    drivername="postgresql",
    username=os.getenv("DATABASE_USERNAME"),
    password=os.getenv("DATABASE_PASSWORD"),
    host=os.getenv("DATABASE_HOST"),
    port=os.getenv("DATABASE_PORT"),
    database=os.getenv("DATABASE_NAME")
)

database_engine = create_engine(
    database_url,
)
