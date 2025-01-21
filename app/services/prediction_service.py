from PIL import Image
from fastapi import UploadFile, HTTPException
import numpy as np

from app.classifier_models import binary_classifier_model, multiclass_classifier_model
from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD
from app.models.specie import SpeciePrediction


class PredictionService:
    def __init__(self, binary_classifier, multiclass_classifier):
        self.binary_classifier_model = binary_classifier
        self.multiclass_classifier_model = multiclass_classifier


    def check_image_for_footprint(self, image_file: UploadFile) -> bool:
        try:
            image = Image.open(image_file.file).convert("RGB")

            image_array = np.array(image)

            input_tensor = np.expand_dims(image_array, axis=0)

            print(input_tensor.shape)

            # Perform inference (preprocessing is handled in the model)
            predictions = self.binary_classifier_model.predict(input_tensor)

            print(predictions)

            # Return True if the model predicts a footprint, False otherwise
            return predictions[0][0] >= WILDLENS_FOOTPRINT_BINARY_CLASSIFICATION_THRESHOLD

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint check: {str(e)}")

    def classify_image(self, image_file: UploadFile) -> list[SpeciePrediction]:
        try:
            image = Image.open(image_file.file).convert("RGB")

            image_array = np.array(image)

            input_tensor = np.expand_dims(image_array, axis=0)

            print(input_tensor.shape)

            # Perform inference (preprocessing is handled in the model)
            predictions = self.multiclass_classifier_model.predict(input_tensor)

            print(predictions)

            # Get the top 3 predicted classes with their probabilities
            top_classes = np.argsort(predictions[0])[-3:][::-1]

            top_probabilities = predictions[0][top_classes]

            return [
                SpeciePrediction(class_number=class_number, probability=probability) for class_number, probability in zip(top_classes, top_probabilities)
            ]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error while processing footprint classification: {str(e)}")



prediction_service = PredictionService(
    binary_classifier=binary_classifier_model,
    multiclass_classifier=multiclass_classifier_model
)