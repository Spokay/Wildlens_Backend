import numpy
import numpy as np
import pytest

from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.dto.species import SpeciePrediction
from app.services.prediction_service import prepare_input_tensor


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
