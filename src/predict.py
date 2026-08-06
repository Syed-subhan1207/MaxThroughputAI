# ==========================================================
# AI-Powered Railway Traffic Control System
# Delay Prediction
# ==========================================================

import numpy as np
import joblib
import json

from tensorflow.keras.models import load_model

# ==========================================================
# STEP 1 : LOAD TRAINED MODEL
# ==========================================================

print("=" * 60)
print("LOADING TRAINED MODEL")
print("=" * 60)

model = load_model("../models/delay_predictor.keras")

print("\nModel Loaded Successfully!")

# ==========================================================
# STEP 2 : LOAD SCALER
# ==========================================================

print("\n" + "=" * 60)
print("LOADING SCALER")
print("=" * 60)

scaler = joblib.load("../processed_data/scaler.pkl")

encoders = joblib.load("../processed_data/label_encoders.pkl")

print("Label Encoders Loaded Successfully!")



# ==========================================================
# STEP 3 : CREATE SAMPLE INPUT
# ==========================================================

print("\n" + "=" * 60)
print("CREATING SAMPLE RAILWAY INPUT")
print("=" * 60)

# ==========================================================
# USER INPUT
# ==========================================================

print("\nEnter Railway Details\n")

train_type_input = input("Train Type (Express/Freight/Passenger): ")

current_station_input = input("Current Station (S1/S2/S3/S4): ")

next_station_input = input("Next Station (S2/S3/S4/S5): ")

speed = int(input("Speed (km/h): "))

current_delay = int(input("Current Delay (minutes): "))

weather_input = input("Weather (Fog/Rain/Sunny): ")

signal_status_input = input("Signal Status (Green/Yellow/Red): ")

track_status_input = input("Track Status (Free/Occupied): ")

platform_available_input = input("Platform Available (Yes/No): ")

train_priority = int(input("Train Priority (1/2/3): "))

day_of_week_input = input("Day of Week: ")

hour_of_day = int(input("Hour of Day (0-23): "))

congestion_level_input = input("Congestion Level (Low/Medium/High): ")

train_type = encoders["train_type"].transform([train_type_input])[0]

current_station = encoders["current_station"].transform([current_station_input])[0]

next_station = encoders["next_station"].transform([next_station_input])[0]

weather = encoders["weather"].transform([weather_input])[0]

signal_status = encoders["signal_status"].transform([signal_status_input])[0]

track_status = encoders["track_status"].transform([track_status_input])[0]

platform_available = encoders["platform_available"].transform([platform_available_input])[0]

day_of_week = encoders["day_of_week"].transform([day_of_week_input])[0]

congestion_level = encoders["congestion_level"].transform([congestion_level_input])[0]

sample_input = np.array([

    [
        train_type,
        current_station,
        next_station,
        speed,
        current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        train_priority,
        day_of_week,
        hour_of_day,
        congestion_level
    ],

    [
        train_type,
        current_station,
        next_station,
        speed,
        current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        train_priority,
        day_of_week,
        hour_of_day,
        congestion_level
    ],

    [
        train_type,
        current_station,
        next_station,
        speed,
        current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        train_priority,
        day_of_week,
        hour_of_day,
        congestion_level
    ],

    [
        train_type,
        current_station,
        next_station,
        speed,
        current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        train_priority,
        day_of_week,
        hour_of_day,
        congestion_level
    ],

    [
        train_type,
        current_station,
        next_station,
        speed,
        current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        train_priority,
        day_of_week,
        hour_of_day,
        congestion_level
    ]

])

print("\n" + "=" * 60)
print("AI RAILWAY DELAY PREDICTION")
print("=" * 60)

print(f"Train Type          : {train_type_input}")
print(f"Current Station     : {current_station_input}")
print(f"Next Station        : {next_station_input}")
print(f"Speed               : {speed} km/h")
print(f"Current Delay       : {current_delay} minutes")
print(f"Weather             : {weather_input}")
print(f"Signal Status       : {signal_status_input}")
print(f"Track Status        : {track_status_input}")
print(f"Platform Available  : {platform_available_input}")
print(f"Train Priority      : {train_priority}")
print(f"Day                 : {day_of_week_input}")
print(f"Hour                : {hour_of_day}")
print(f"Congestion Level    : {congestion_level_input}")

# ==========================================================
# STEP 4 : SCALE INPUT
# ==========================================================

print("\n" + "=" * 60)
#print("SCALING INPUT")
print("=" * 60)

scaled_input = scaler.transform(sample_input)

print("\nScaled Input:\n")

#print(scaled_input)

# ==========================================================
# STEP 5 : RESHAPE INPUT
# ==========================================================

print("\n" + "=" * 60)
#print("RESHAPING INPUT")
print("=" * 60)

lstm_input = scaled_input.reshape(1,5,13)

print("\nInput Shape :")

#print(lstm_input.shape)

# ==========================================================
# STEP 6 : PREDICT DELAY
# ==========================================================

print("\n" + "=" * 60)
print("PREDICTING DELAY")
print("=" * 60)

prediction = model.predict(lstm_input, verbose=0)
predicted_delay = prediction[0][0]
print("\n" + "-" * 60)

print(f"\nPredicted Delay : {predicted_delay:.2f} minutes")

print("=" * 60)


print("\n" + "=" * 60)
print("AI RECOMMENDATION")
print("=" * 60)

if predicted_delay < 5:

    severity = "ON TIME"

    recommendations = [
        "Train is running on schedule.",
        "No action required."
    ]

elif predicted_delay < 15:

    severity = "MINOR DELAY"

    recommendations = [
        "Increase signal priority.",
        "Monitor train movement.",
        "Notify next station."
    ]

elif predicted_delay < 30:

    severity = "MODERATE DELAY"

    recommendations = [
        "Notify next station.",
        "Passenger announcement required.",
        "Increase signal priority.",
        "Prepare platform staff."
    ]

else:

    severity = "SEVERE DELAY"

    recommendations = [
        "Alert Railway Control Room.",
        "Passenger announcement required.",
        "Prioritize train at upcoming signals.",
        "Prepare alternate platform if needed.",
        "Monitor surrounding train traffic."
    ]

print("\n" + "=" * 60)
print("RAILWAY STATUS")
print("=" * 60)

# ==========================================================
# SAVE RESULT AS JSON
# ==========================================================

prediction_result = {

    "train_type": train_type_input,
    "current_station": current_station_input,
    "next_station": next_station_input,

    "speed": speed,
    "current_delay": current_delay,

    "weather": weather_input,
    "signal_status": signal_status_input,
    "track_status": track_status_input,
    "platform_available": platform_available_input,

    "train_priority": train_priority,
    "day_of_week": day_of_week_input,
    "hour_of_day": hour_of_day,
    "congestion_level": congestion_level_input,

    "predicted_delay": round(float(prediction[0][0]), 2),

    "severity": severity,

    "recommendations": recommendations
}

with open("../processed_data/prediction_result.json", "w") as file:

    json.dump(
        prediction_result,
        file,
        indent=4
    )

print("\nPrediction saved successfully!")

print("Location : ../processed_data/prediction_result.json")

print("=" * 60)

if severity == "ON TIME":

    print("🟢 STATUS : ON TIME")

elif severity == "MINOR DELAY":

    print("🟡 STATUS : MINOR DELAY")

elif severity == "MODERATE DELAY":

    print("🟠 STATUS : MODERATE DELAY")

else:

    print("🔴 STATUS : CRITICAL DELAY")

print("\nDelay Severity :", severity)

print("\nRecommended Actions:\n")

for action in recommendations:
    print(f"• {action}")

print("\n" + "=" * 60)