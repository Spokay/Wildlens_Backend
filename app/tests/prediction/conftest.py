from unittest.mock import patch

import numpy as np
import pytest

from app.dto.species import SpeciePrediction
from app.services.prediction_service import WildlensAPIService


@pytest.fixture
def mock_api_client():
    with patch('app.services.prediction_service.client') as client_mock:
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
        "prediction_result": {
            [0.17042333, 0.06296999, 0.02549643, 0.03818705, 0.10345666, 0.27900936, 0.03107355, 0.04685892,
                      0.08450808, 0.05701663]
        },
        "expected_top_3": [
            SpeciePrediction(class_number=5, probability=0.27900936),
            SpeciePrediction(class_number=0, probability=0.17042333),
            SpeciePrediction(class_number=4, probability=0.10345666)
        ]
    }