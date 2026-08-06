# ==========================================================
# AI-Powered Railway Traffic Control System
# LSTM Data Preprocessing
# ==========================================================

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split

# ==========================================================
# STEP 1 : LOAD DATASET
# ==========================================================

print("=" * 60)
print("STEP 1 : LOADING DATASET")
print("=" * 60)

df = pd.read_csv("../data/railway_traffic_control_dataset.csv")

print("Dataset Loaded Successfully!")
print("Shape :", df.shape)

# ==========================================================
# STEP 2 : INSPECT DATASET
# ==========================================================

print("\n" + "=" * 60)
print("STEP 2 : DATASET INSPECTION")
print("=" * 60)

print("\nMissing Values\n")
print(df.isnull().sum())

print("\nData Types\n")
print(df.dtypes)

# ==========================================================
# STEP 3 : ENCODE CATEGORICAL DATA
# ==========================================================

print("\n" + "=" * 60)
print("STEP 3 : ENCODING CATEGORICAL DATA")
print("=" * 60)

categorical_columns = [

    "train_type",
    "current_station",
    "next_station",
    "weather",
    "signal_status",
    "track_status",
    "platform_available",
    "day_of_week",
    "congestion_level"

]

label_encoders = {}

for column in categorical_columns:

    encoder = LabelEncoder()

    df[column] = encoder.fit_transform(df[column])

    label_encoders[column] = encoder

print("Categorical Encoding Completed!")

# ==========================================================
# STEP 4 : REMOVE UNNECESSARY COLUMNS
# ==========================================================

print("\n" + "=" * 60)
print("STEP 4 : REMOVING UNNECESSARY COLUMNS")
print("=" * 60)

columns_to_drop = [

    "timestamp",
    "train_id",
    "scheduled_arrival",
    "actual_arrival"

]

df.drop(columns=columns_to_drop, inplace=True)

print("Remaining Columns:")

print(df.columns.tolist())

# ==========================================================
# STEP 5 : FEATURES & TARGET
# ==========================================================

print("\n" + "=" * 60)
print("STEP 5 : FEATURES & TARGET")
print("=" * 60)

X = df.drop(columns=["predicted_delay_min"])

y = df["predicted_delay_min"]

print("Features Shape :", X.shape)

print("Target Shape :", y.shape)

# ==========================================================
# STEP 6 : NORMALIZATION
# ==========================================================

print("\n" + "=" * 60)
print("STEP 6 : NORMALIZING DATA")
print("=" * 60)

scaler = MinMaxScaler()

X_scaled = scaler.fit_transform(X)

print("Normalization Completed!")

# ==========================================================
# STEP 7 : CREATE LSTM SEQUENCES
# ==========================================================

print("\n" + "=" * 60)
print("STEP 7 : CREATING LSTM SEQUENCES")
print("=" * 60)

sequence_length = 5

X_sequences = []

y_sequences = []

for i in range(len(X_scaled) - sequence_length):

    X_sequences.append(
        X_scaled[i:i + sequence_length]
    )

    y_sequences.append(
        y.iloc[i + sequence_length]
    )

X_sequences = np.array(X_sequences)

y_sequences = np.array(y_sequences)

print("Sequence Shape :", X_sequences.shape)

# ==========================================================
# STEP 8 : TRAIN TEST SPLIT
# ==========================================================

print("\n" + "=" * 60)
print("STEP 8 : TRAIN TEST SPLIT")
print("=" * 60)

X_train, X_test, y_train, y_test = train_test_split(

    X_sequences,
    y_sequences,
    test_size=0.20,
    random_state=42

)

print("Training Samples :", X_train.shape)

print("Testing Samples  :", X_test.shape)

# ==========================================================
# STEP 9 : SAVE PROCESSED DATA
# ==========================================================

print("\n" + "=" * 60)
print("SAVING PROCESSED FILES")
print("=" * 60)

os.makedirs("../processed_data", exist_ok=True)

np.save("../processed_data/X_train.npy", X_train)

np.save("../processed_data/X_test.npy", X_test)

np.save("../processed_data/y_train.npy", y_train)

np.save("../processed_data/y_test.npy", y_test)

joblib.dump(scaler, "../processed_data/scaler.pkl")

joblib.dump(label_encoders, "../processed_data/label_encoders.pkl")

print("Processed Data Saved Successfully!")

print("\nFiles Created:")

print("X_train.npy")

print("X_test.npy")

print("y_train.npy")

print("y_test.npy")

print("scaler.pkl")

print("label_encoders.pkl")

print("\nPreprocessing Completed Successfully!")