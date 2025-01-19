import keras

from app.config import WILDLEN_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH, \
    WILDLEN_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH

binary_classifier_model = keras.models.Model()

binary_classifier_model.load_weights(WILDLEN_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH)

multiclass_classifier_model = keras.models.Model()

multiclass_classifier_model.load_weights(WILDLEN_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH)