from fastapi import UploadFile
from keras.src.saving.saving_api import load_weights
from app.classifier_models import binary_classifier_model, multiclass_classifier_model


class WildlensModelService:
    def __init__(self):

        self.binary_classifier_model = binary_classifier_model
        self.multiclass_classifier_model = multiclass_classifier_model


    def check_image_for_footprint(self, image: UploadFile):
        # use Pillow to transform the image to a numpy array of pixels
        # image_pixels =
        # make the inference
        # self.binary_classifier_model.predict()
        pass



wildlens_model_service = WildlensModelService()