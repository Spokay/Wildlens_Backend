import io
from unittest.mock import patch

import numpy as np
import pytest
from PIL import Image
from fastapi import UploadFile

from app.dto.species import SpeciePrediction
from app.services.prediction_service import PredictionService


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
def mock_dependencies():
    with patch('app.classifier_models.multiclass_classifier_model') as multiclass_classifier_mock, \
         patch('app.classifier_models.binary_classifier_model') as binary_classifier_mock:
        multiclass_classifier_mock.predict.return_value = np.random.rand(1, 10)
        binary_classifier_mock.predict.return_value = np.array([0.5])
        yield multiclass_classifier_mock, binary_classifier_mock

@pytest.fixture
def prediction_service(mock_dependencies):
    multiclass_classifier_mock, binary_classifier_mock = mock_dependencies
    return PredictionService(
        binary_classifier=binary_classifier_mock,
        multiclass_classifier=multiclass_classifier_mock,
        nb_classes=10
    )

@pytest.fixture
def classification_for_10_classes():
    return {
        "prediction_result": np.array([0.17042333, 0.06296999, 0.02549643, 0.03818705, 0.10345666, 0.27900936, 0.03107355, 0.04685892, 0.08450808,0.05701663]),
        "expected_top_3": [
            SpeciePrediction(class_number=5, probability=0.27900936),
            SpeciePrediction(class_number=0, probability=0.17042333),
            SpeciePrediction(class_number=4, probability=0.10345666)
        ]
    }