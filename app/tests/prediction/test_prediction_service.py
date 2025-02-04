from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.dto.species import SpeciePrediction


def test_check_image_for_footprint_returns_false_when_threshold_is_not_met(
        wildlens_prediction_api_service,
        valid_image_file
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    wildlens_prediction_api_service.client.post.return_value = {
        "predictions": [threshold - 0.1]
    }

    result = wildlens_prediction_api_service.check_image_for_footprint(valid_image_file)

    assert result is False

def test_check_image_for_footprint_returns_true_when_threshold_is_met(
        wildlens_prediction_api_service,
        valid_image_file
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    wildlens_prediction_api_service.client.post.return_value = {
        "predictions": [threshold + 0.1]
    }

    result = wildlens_prediction_api_service.check_image_for_footprint(valid_image_file)

    assert result is True

def test_classify_image_returns_top_3_predictions(
        wildlens_prediction_api_service,
        valid_image_file
, classification_for_10_classes):
    wildlens_prediction_api_service.client.post.return_value = classification_for_10_classes["prediction_result"]

    result = wildlens_prediction_api_service.classify_image(valid_image_file)

    assert all(isinstance(prediction, SpeciePrediction) for prediction in result)
    assert len(result) == 3
    assert result == classification_for_10_classes["expected_top_3"]
