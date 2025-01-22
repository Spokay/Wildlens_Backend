from typing import Any

from PIL import Image
from fastapi import UploadFile, HTTPException
import numpy as np
from numpy import ndarray, dtype, generic

from app.classifier_models import binary_classifier_model, multiclass_classifier_model
from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.models.specie import SpeciePrediction


def prepare_input_tensor(image_file: UploadFile) -> ndarray[Any, dtype[generic | Any]]:
    image = Image.open(image_file.file).convert("RGB")

    image_array = np.array(image)

    return np.expand_dims(image_array, axis=0)


class PredictionService:
    def __init__(self, binary_classifier, multiclass_classifier, nb_classes=10):
        self.binary_classifier_model = binary_classifier
        self.multiclass_classifier_model = multiclass_classifier
        self.nb_classes = nb_classes
        self.classes = list(range(nb_classes))


    def check_image_for_footprint(self, image_file: UploadFile) -> bool:
        try:
            input_tensor = prepare_input_tensor(image_file)

            # Perform inference (preprocessing is handled in the model)
            predictions = self.binary_classifier_model.predict(input_tensor)

            probability = predictions[0]

            # Return True if the probability that it is a footprint is greater than the threshold, False otherwise
            return bool(probability >= WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint check: {str(e)}")

    def classify_image(self, image_file: UploadFile) -> list[SpeciePrediction]:
        try:
            input_tensor = prepare_input_tensor(image_file)

            # Perform inference (preprocessing is handled in the model)
            predictions = self.multiclass_classifier_model.predict(input_tensor)


            # Get the top 3 predicted classes with their probabilities
            probability_by_classes = zip(predictions, self.classes)
            top_3_predictions = sorted(probability_by_classes, key=lambda x: x[0], reverse=True)[:3]

            return [
                SpeciePrediction(class_number=class_number, probability=probability) for probability, class_number  in top_3_predictions
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint classification: {str(e)}")


prediction_service = PredictionService(
    binary_classifier=binary_classifier_model,
    multiclass_classifier=multiclass_classifier_model,
    nb_classes=10
)