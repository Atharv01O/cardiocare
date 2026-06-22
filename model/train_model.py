"""
Run this once:  python model/train_model.py
Trains a neural network on heart.csv and saves:
  model/heart_model.h5
  model/scaler.pkl
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping

import joblib

import matplotlib.pyplot as plt
import seaborn as sns

from config import DATASET_PATH, MODEL_PATH, SCALER_PATH


# =========================
# LOAD DATA
# =========================

df = pd.read_csv(DATASET_PATH)

print(f"Dataset shape: {df.shape}")
print(df["target"].value_counts())


X = df.drop("target", axis=1).values
y = df["target"].values

# Shuffle the dataset first
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
X = df.drop("target", axis=1).values
y = df["target"].values
# =========================
# SCALE
# =========================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# =========================
# SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# =========================
# MODEL
# =========================

model = Sequential([
    Dense(64, activation="relu", input_shape=(X_train.shape[1],)),
    Dropout(0.4),
    Dense(32, activation="relu"),
    Dropout(0.3),
    Dense(16, activation="relu"),
    Dense(1, activation="sigmoid")
])
model.compile(
    optimizer="adam",
    loss="binary_crossentropy",
    metrics=["accuracy"]
)


model.summary()



# =========================
# TRAIN
# =========================

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=15,
    restore_best_weights=True
)


history = model.fit(

    X_train,
    y_train,

    epochs=150,

    batch_size=32,

    validation_split=0.15,

    callbacks=[early_stop],

    verbose=1

)



# =========================
# EVALUATE
# =========================

loss, acc = model.evaluate(
    X_test,
    y_test,
    verbose=0
)


print(
    f"\nTest Accuracy: {acc*100:.2f}%"
)



y_pred = (
    model.predict(X_test) > 0.5
).astype(int).flatten()


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred
    )
)



# =========================
# CONFUSION MATRIX
# =========================

cm = confusion_matrix(
    y_test,
    y_pred
)


plt.figure(
    figsize=(6,5)
)


sns.heatmap(

    cm,

    annot=True,

    fmt="d",

    cmap="Reds",

    xticklabels=[
        "No Disease",
        "Disease"
    ],

    yticklabels=[
        "No Disease",
        "Disease"
    ]

)


plt.title(
    "Confusion Matrix"
)


plt.ylabel(
    "Actual"
)


plt.xlabel(
    "Predicted"
)


plt.tight_layout()


plt.savefig(
    "model/confusion_matrix.png",
    dpi=150
)


print(
    "Confusion matrix saved."
)



# =========================
# SAVE
# =========================

model.save("model/heart_model.keras")


joblib.dump(
    scaler,
    SCALER_PATH
)


print(
    f"\nModel saved  → {MODEL_PATH}"
)


print(
    f"Scaler saved → {SCALER_PATH}"
)