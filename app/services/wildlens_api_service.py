from fastapi import UploadFile, HTTPException
from httpx import Headers, Client, AsyncClient

from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD, NUMBER_OF_CLASSES, \
    WILDLENS_PREDICTION_API_BASE_URL, WILDLENS_PREDICTION_API_KEY
from app.dto.species import SpeciePrediction

BINARY_PREDICTION_URL = f"{WILDLENS_PREDICTION_API_BASE_URL}/predictions/binary"
MULTICLASS_PREDICTION_URL = f"{WILDLENS_PREDICTION_API_BASE_URL}/predictions/multiclass"


def get_client():
    headers = Headers({"Authorization": f"Key {WILDLENS_PREDICTION_API_KEY}"})
    return Client(
        headers=headers,
        base_url=WILDLENS_PREDICTION_API_BASE_URL,
    )


class WildlensAPIService:
    def __init__(self, client, nb_classes=10):
        self.client = client
        self.nb_classes = nb_classes
        self.classes = [i for i in range(1, nb_classes + 1)]

    async def check_image_for_footprint(self, image_file: UploadFile) -> bool:
        try:
            # Perform inference with the Prediction API (preprocessing is handled in the model)
            predictions = self.client.post(BINARY_PREDICTION_URL, files={"image_file": image_file.file}).json()

            probability = predictions["predictions"][0]

            # Return True if the probability that it is a footprint is greater than the threshold, False otherwise
            return bool(probability >= WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint check: {str(e)}")

    async def classify_image(self, image_file: UploadFile) -> list[SpeciePrediction]:
        try:
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


def get_wildlens_api_service():
    return WildlensAPIService(
        client=get_client(),
        nb_classes=NUMBER_OF_CLASSES
    )
