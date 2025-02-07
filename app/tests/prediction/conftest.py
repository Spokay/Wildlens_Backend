import io
from unittest.mock import patch

import pytest
from PIL import Image
from fastapi import UploadFile

from app.dto.species import SpeciePrediction
from app.services.wildlens_api_service import WildlensAPIService

@pytest.fixture
def valid_image_file():
    # Create an in-memory image
    img = Image.new("RGB", (100, 100), color="white")
    file_content = io.BytesIO()
    img.save(file_content, format="JPEG")
    file_content.seek(0)

    return UploadFile(filename="valid_image.jpg", file=file_content)

@pytest.fixture
def invalid_image_file():
    return UploadFile(filename="invalid_image.jpg", file=io.BytesIO("invalid_image".encode()))

@pytest.fixture
def mock_api_client():
    with patch('app.services.wildlens_api_service.get_client') as client_mock:
        yield client_mock

@pytest.fixture
def wildlens_prediction_api_service(mock_api_client):
    return WildlensAPIService(
        mock_api_client,
        nb_classes=10
    )

@pytest.fixture
def classification_for_10_classes():
    return {
        "prediction_result": [0.17042333, 0.06296999, 0.02549643, 0.03818705, 0.10345666, 0.27900936, 0.03107355, 0.04685892,
                      0.08450808, 0.05701663],
        "expected_top_3": [
            SpeciePrediction(class_number=6, probability=0.27900936),
            SpeciePrediction(class_number=1, probability=0.17042333),
            SpeciePrediction(class_number=5, probability=0.10345666)
        ]
    }