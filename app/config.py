import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL



load_dotenv()

WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH = os.getenv("WILDLEN_FOOTPRINT_CLASSIFIER_MODEL_PATH")
WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH = os.getenv("WILDLEN_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH")
WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD = float(os.getenv("WILDLEN_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD"))


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
    connect_args={"check_same_thread": False}
)
