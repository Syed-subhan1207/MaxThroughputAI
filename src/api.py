from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import joblib
import numpy as np
from tensorflow.keras.models import load_model

app = FastAPI(
    title="AI Railway Traffic Control API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =====================================================
# LOAD AI COMPONENTS
# =====================================================

model = load_model("../models/delay_predictor.keras")

scaler = joblib.load("../processed_data/scaler.pkl")

encoders = joblib.load("../processed_data/label_encoders.pkl")

print("AI Model Loaded Successfully!")
print("Scaler Loaded Successfully!")
print("Label Encoders Loaded Successfully!")

class RailwayInput(BaseModel):

    train_type: str
    current_station: str
    next_station: str

    speed: int
    current_delay: int

    weather: str
    signal_status: str
    track_status: str
    platform_available: str

    train_priority: int

    day_of_week: str

    hour_of_day: int

    congestion_level: str


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message": "AI Railway Traffic Control API Running Successfully"
    }
@app.post("/predict")
def predict(data: RailwayInput):

    # ============================================
    # Encode categorical values
    # ============================================

    train_type = encoders["train_type"].transform([data.train_type])[0]

    current_station = encoders["current_station"].transform([data.current_station])[0]

    next_station = encoders["next_station"].transform([data.next_station])[0]

    weather = encoders["weather"].transform([data.weather])[0]

    signal_status = encoders["signal_status"].transform([data.signal_status])[0]

    track_status = encoders["track_status"].transform([data.track_status])[0]

    platform_available = encoders["platform_available"].transform([data.platform_available])[0]

    day_of_week = encoders["day_of_week"].transform([data.day_of_week])[0]

    congestion_level = encoders["congestion_level"].transform([data.congestion_level])[0]


    # ============================================
    # Create Feature Vector
    # ============================================

    sample_input = np.array([[
        train_type,
        current_station,
        next_station,
        data.speed,
        data.current_delay,
        weather,
        signal_status,
        track_status,
        platform_available,
        data.train_priority,
        day_of_week,
        data.hour_of_day,
        congestion_level
    ]])


    # ============================================
    # Scale Input
    # ============================================

    scaled_input = scaler.transform(sample_input)


    # ============================================
    # Create LSTM Sequence
    # ============================================

    sequence = np.repeat(scaled_input, 5, axis=0)

    sequence = sequence.reshape(1, 5, 13)


    # ============================================
    # Predict
    # ============================================

    prediction = float(model.predict(sequence)[0][0])


    # ============================================
    # Delay Severity
    # ============================================

    if prediction <= 5:
        severity = "ON TIME"

    elif prediction <= 15:
        severity = "MINOR DELAY"

    elif prediction <= 30:
        severity = "MODERATE DELAY"

    else:
        severity = "CRITICAL DELAY"


    # ============================================
    # Recommendations
    # ============================================

    recommendations = []

    if severity == "ON TIME":

        recommendations = [
            "Proceed as scheduled."
        ]

    elif severity == "MINOR DELAY":

        recommendations = [
            "Notify next station.",
            "Monitor train speed."
        ]

    elif severity == "MODERATE DELAY":

        recommendations = [
            "Notify next station.",
            "Passenger announcement required.",
            "Increase signal priority.",
            "Prepare platform staff."
        ]

    else:

        recommendations = [
            "Emergency traffic management.",
            "Reschedule affected trains.",
            "Inform railway control room.",
            "Passenger assistance required."
        ]


    # ============================================
    # Return JSON
    # ============================================

    return {

        "predicted_delay": round(prediction, 2),

        "delay_status": severity,

        "recommendations": recommendations

    }