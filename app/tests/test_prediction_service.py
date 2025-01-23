import io
from unittest.mock import patch

import numpy
import numpy as np
import pytest
from PIL import Image
from fastapi import UploadFile

from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.dto.species import SpeciePrediction
from app.services.prediction_service import PredictionService, prepare_input_tensor


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

def test_check_image_for_footprint_throws_exception_when_image_is_invalid(
        prediction_service,
        invalid_image_file
):
    with pytest.raises(Exception):
        prediction_service.check_image_for_footprint(invalid_image_file)

def test_classify_image_throws_exception_when_image_is_invalid(
        prediction_service,
        invalid_image_file
):
    with pytest.raises(Exception):
        prediction_service.classify_image(invalid_image_file)

def test_prepare_input_tensor_transforms_valid_image_to_a_vector_of_expected_shape(
        mocker,
        prediction_service,
        valid_image_file
):

    expected_shape_before_expansion = (100, 100, 3)
    expected_shape_after_expansion = (1, 100, 100, 3)

    spy_numpy_conversion = mocker.spy(numpy, "array")
    spy_numpy_expansion = mocker.spy(numpy, "expand_dims")

    prepare_input_tensor(valid_image_file)

    assert spy_numpy_conversion.spy_return.shape == expected_shape_before_expansion
    assert spy_numpy_conversion.call_count == 1
    assert spy_numpy_expansion.spy_return.shape == expected_shape_after_expansion
    assert spy_numpy_expansion.call_count == 1


def test_check_image_for_footprint_returns_false_when_threshold_is_not_met(
        prediction_service,
        valid_image_file
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    prediction_service.binary_classifier_model.predict.return_value = np.array([threshold - 0.1])

    result = prediction_service.check_image_for_footprint(valid_image_file)

    assert result is False

def test_check_image_for_footprint_returns_true_when_threshold_is_met(
        prediction_service,
        valid_image_file
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    prediction_service.binary_classifier_model.predict.return_value = np.array([threshold + 0.1])

    result = prediction_service.check_image_for_footprint(valid_image_file)

    assert result is True

def test_classify_image_returns_top_3_predictions(
        prediction_service,
        valid_image_file
, classification_for_10_classes):
    prediction_service.multiclass_classifier_model.predict.return_value = classification_for_10_classes["prediction_result"]

    result = prediction_service.classify_image(valid_image_file)

    assert all(isinstance(prediction, SpeciePrediction) for prediction in result)
    assert len(result) == 3
    assert result == classification_for_10_classes["expected_top_3"]
