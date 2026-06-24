"""
Loads the trained model + scaler and exposes run_prediction().
"""

import numpy as np
import tensorflow as tf
import joblib
from config import MODEL_PATH, SCALER_PATH

_heart_model  = tf.keras.models.load_model(MODEL_PATH)
_heart_scaler = joblib.load(SCALER_PATH)


def run_prediction(form_values):
    arr  = np.array(form_values, dtype=float).reshape(1, -1)
    arr  = _heart_scaler.transform(arr)
    prob = float(_heart_model.predict(arr, verbose=0)[0][0])
    return prob