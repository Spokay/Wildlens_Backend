import io

import keras
import pytest
from fastapi import UploadFile

from app.services.prediction_service import PredictionService

@pytest.fixture
def image_file():
    file_content = io.BytesIO(b"fake image data")
    return UploadFile(filename="otter.jpg", file=file_content)

@pytest.fixture
def binary_classifier_model(mocker):
    fake_model = keras.Model()
    mocker.patch("keras.models.load_model", return_value=fake_model)
    return keras.Model()

@pytest.fixture
def multiclass_classifier_model(mocker):
    fake_model = keras.Model()
    mocker.patch("keras.models.load_model", return_value=fake_model)
    return fake_model

@pytest.fixture
def prediction_service(binary_classifier_model, multiclass_classifier_model):
    return PredictionService(
        binary_classifier=binary_classifier_model,
        multiclass_classifier=multiclass_classifier_model
    )

def test_check_image_for_footprint_transforms_image_to_a_vector_of_expected_shape(
        mocker,
        binary_classifier_model,
        prediction_service,
        image_file
):
    print(image_file)
    mocker.patch("PIL.Image.open")
    mocker.patch("numpy.array")
    mocker.patch("numpy.expand_dims")
    mocker.patch.object(binary_classifier_model, "predict", return_value=[[0.5, 0.5]])

    prediction_service.check_image_for_footprint(image_file)

    assert mocker.call_count == 4