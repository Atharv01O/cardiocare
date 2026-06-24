import numpy as np
import tensorflow as tf
import keras
import joblib
from config import MODEL_PATH, SCALER_PATH

_heart_model  = keras.layers.TFSMLayer(MODEL_PATH, call_endpoint='serving_default')
_heart_scaler = joblib.load(SCALER_PATH)


def run_prediction(form_values: list) -> float:
    arr    = np.array(form_values, dtype=float).reshape(1, -1)
    arr    = _heart_scaler.transform(arr)
    output = _heart_model(arr)
    # TFSMLayer returns a dict — get the first output value
    prob   = float(list(output.values())[0].numpy()[0][0])
    return prob