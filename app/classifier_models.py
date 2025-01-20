import tensorflow as tf

from app.config import WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH, \
    WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH

# Model which predicts whether an image contains a footprint or not
binary_classifier_model = None

# Model which classifies a footprint image into classes of species
multiclass_classifier_model = None

def load_binary_classifier_model():
    global binary_classifier_model
    binary_classifier_model = tf.keras.models.load_model(WILDLENS_FOOTPRINT_BINARY_CLASSIFIER_MODEL_PATH)

def load_multiclass_classifier_model():
    global multiclass_classifier_model
    multiclass_classifier_model = tf.keras.models.load_model(WILDLENS_FOOTPRINT_MULTICLASS_CLASSIFIER_MODEL_PATH)

def load_models():
    load_binary_classifier_model()
    load_multiclass_classifier_model()