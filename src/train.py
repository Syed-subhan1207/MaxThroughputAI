# ==========================================================
# AI-Powered Railway Traffic Control System
# LSTM Model Building
# ==========================================================

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout


# ==========================================================
# STEP 1 : LOAD PREPROCESSED DATA
# ==========================================================

print("=" * 60)
print("LOADING PREPROCESSED DATA")
print("=" * 60)

X_train = np.load("../processed_data/X_train.npy")
y_train = np.load("../processed_data/y_train.npy")

X_test = np.load("../processed_data/X_test.npy")
y_test = np.load("../processed_data/y_test.npy")

print("\nTraining Data Shape")
print("X_train :", X_train.shape)
print("y_train :", y_train.shape)

print("\nTesting Data Shape")
print("X_test :", X_test.shape)
print("y_test :", y_test.shape)

# ==========================================================
# STEP 2 : BUILD LSTM MODEL
# ==========================================================

print("\n" + "=" * 60)
print("BUILDING LSTM MODEL")
print("=" * 60)

model = Sequential()

# First LSTM Layer
model.add(
    LSTM(
        units=64,
        return_sequences=True,
        input_shape=(X_train.shape[1], X_train.shape[2])
    )
)

# Dropout Layer
model.add(Dropout(0.2))

# Second LSTM Layer
model.add(LSTM(units=32))

# Dense Hidden Layer
model.add(
    Dense(
        units=16,
        activation="relu"
    )
)

# Output Layer
model.add(Dense(units=1))

print("\nModel Created Successfully!\n")

model.summary()
# ==========================================================
# STEP 3 : COMPILE MODEL
# ==========================================================

print("\n" + "=" * 60)
print("COMPILING MODEL")
print("=" * 60)

model.compile(

    optimizer="adam",

    loss="mse",

    metrics=["mae"]

)

print("\nModel Compiled Successfully!")
# ==========================================================
# STEP 4 : TRAIN MODEL
# ==========================================================

print("\n" + "=" * 60)
print("TRAINING MODEL")
print("=" * 60)

history = model.fit(

    X_train,

    y_train,

    validation_data=(X_test, y_test),

    epochs=50,

    batch_size=32,

    verbose=1

)

print("\nModel Training Completed Successfully!")

# ==========================================================
# STEP 5 : EVALUATE MODEL
# ==========================================================

print("\n" + "=" * 60)
print("EVALUATING MODEL")
print("=" * 60)

loss, mae = model.evaluate(

    X_test,

    y_test,

    verbose=0

)

print(f"\nTest Loss : {loss:.4f}")

print(f"Test MAE  : {mae:.4f}")

# ==========================================================
# STEP 6 : SAVE MODEL
# ==========================================================

print("\n" + "=" * 60)
print("SAVING MODEL")
print("=" * 60)

model.save("../models/delay_predictor.keras")

print("\nModel Saved Successfully!")

print("\nLocation : ../models/delay_predictor.keras")

# ==========================================================
# STEP 7 : PLOT TRAINING GRAPHS
# ==========================================================

print("\n" + "=" * 60)
print("GENERATING TRAINING GRAPHS")
print("=" * 60)

# -----------------------------
# LOSS GRAPH
# -----------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history['loss'], label='Training Loss')

plt.plot(history.history['val_loss'], label='Validation Loss')

plt.title("Training vs Validation Loss")

plt.xlabel("Epoch")

plt.ylabel("Loss")

plt.legend()

plt.grid(True)

plt.savefig("../graphs/loss_curve.png")

plt.close()

# -----------------------------
# MAE GRAPH
# -----------------------------

plt.figure(figsize=(8,5))

plt.plot(history.history['mae'], label='Training MAE')

plt.plot(history.history['val_mae'], label='Validation MAE')

plt.title("Training vs Validation MAE")

plt.xlabel("Epoch")

plt.ylabel("MAE")

plt.legend()

plt.grid(True)

plt.savefig("../graphs/mae_curve.png")

plt.close()

print("\nGraphs Generated Successfully!")

print("\nSaved Files:")

print("../graphs/loss_curve.png")

print("../graphs/mae_curve.png")