from functools import lru_cache

from fastapi import UploadFile, HTTPException
from httpx import Headers, Client

from app.config import get_settings
from app.dto.species import SpeciePrediction

settings = get_settings()

BINARY_PREDICTION_URL = f"{settings.wildlens_prediction_api_base_url}/predictions/binary"
MULTICLASS_PREDICTION_URL = f"{settings.wildlens_prediction_api_base_url}/predictions/multiclass"


def get_client():
    headers = Headers({"Authorization": f"Key {settings.wildlens_prediction_api_key}"})
    return Client(
        headers=headers,
        base_url=settings.wildlens_prediction_api_base_url,
    )


async def assert_content_type_is_valid(content_type: str):
    if content_type not in settings.prediction_authorized_mime_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload a JPEG or PNG image.",
        )


class WildlensAPIService:
    def __init__(self, client, nb_classes=10):
        self.client = client
        self.nb_classes = nb_classes
        self.classes = [i for i in range(1, nb_classes + 1)]

    async def check_image_for_footprint(self, image_file: UploadFile) -> bool:
        try:
            image_file.file.seek(0)
            # Perform inference with the Prediction API (preprocessing is handled in the model)
            predictions = self.client.post(BINARY_PREDICTION_URL, files={"image_file": image_file.file}).json()

            probability = predictions["predictions"][0]

            # Return True if the probability that it is a footprint is greater than the threshold, False otherwise
            return bool(probability >= settings.wildlens_footprint_binary_classification_threshold)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint check: {str(e)}")

    async def classify_image(self, image_file: UploadFile) -> list[SpeciePrediction]:
        try:
            image_file.file.seek(0)
            # Perform inference (preprocessing is handled in the model)
            predictions = self.client.post(MULTICLASS_PREDICTION_URL, files={"image_file": image_file.file}).json()

            # Get the top 3 predicted classes with their probabilities

            probability_by_classes = zip(predictions["predictions"], self.classes)

            top_3_predictions = sorted(probability_by_classes, key=lambda x: x[0], reverse=True)[:3]

            return [
                SpeciePrediction(class_number=class_number, probability=probability) for probability, class_number in
                top_3_predictions
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint classification: {str(e)}")

@lru_cache
def get_wildlens_api_service():
    return WildlensAPIService(
        client=get_client(),
        nb_classes=settings.number_of_classes
    )
