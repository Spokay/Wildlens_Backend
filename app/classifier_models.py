import keras

from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH, \
    WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH

# Model which predicts whether an image contains a footprint or not
binary_classifier_model = keras.models.load_model(WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH)

# Model which classifies a footprint image into classes of species
multiclass_classifier_model = keras.models.load_model(WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH)