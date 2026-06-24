"""
Loads the trained model + scaler and exposes run_prediction().
"""

import numpy as np
import tensorflow as tf
import joblib
from config import SCALER_PATH

_heart_model = tf.saved_model.load("model/saved_model")
_heart_scaler = joblib.load(SCALER_PATH)


def run_prediction(form_values):
    arr = np.array(form_values, dtype=float).reshape(1, -1)
    arr = _heart_scaler.transform(arr)

    infer = _heart_model.signatures["serving_default"]

    output = infer(tf.constant(arr, dtype=tf.float32))

    prob = float(list(output.values())[0].numpy()[0][0])

    return prob