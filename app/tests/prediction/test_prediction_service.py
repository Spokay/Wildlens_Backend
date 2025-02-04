from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.dto.species import SpeciePrediction


def test_check_image_for_footprint_returns_false_when_threshold_is_not_met(
        wildlens_prediction_api_service,
        valid_image_file,
        mocker
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "predictions": [threshold - 0.1]
    }
    mocker.patch.object(wildlens_prediction_api_service.client, 'post', return_value=mock_response)

    result = wildlens_prediction_api_service.check_image_for_footprint(valid_image_file)

    assert result is False

def test_check_image_for_footprint_returns_true_when_threshold_is_met(
        wildlens_prediction_api_service,
        valid_image_file,
        mocker
):
    threshold = WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "predictions": [threshold + 0.1]
    }
    mocker.patch.object(wildlens_prediction_api_service.client, 'post', return_value=mock_response)

    result = wildlens_prediction_api_service.check_image_for_footprint(valid_image_file)

    assert result is True

def test_classify_image_returns_top_3_predictions(
        wildlens_prediction_api_service,
        valid_image_file,
        mocker
, classification_for_10_classes):
    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "predictions": classification_for_10_classes["prediction_result"]
    }

    mocker.patch.object(wildlens_prediction_api_service.client, 'post', return_value=mock_response)

    result = wildlens_prediction_api_service.classify_image(valid_image_file)

    assert all(isinstance(prediction, SpeciePrediction) for prediction in result)
    assert len(result) == 3
    assert result == classification_for_10_classes["expected_top_3"]
