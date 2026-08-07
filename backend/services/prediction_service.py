"""
Prediction Service (Person 3 Module)
Responsible strictly for LSTM Neural Network Delay Predictions.
Uses lazy loading for fast server boot.
"""

import os
import joblib
import numpy as np
import logging

logger = logging.getLogger("prediction_service")

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../models/delay_predictor.keras"))
SCALER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../processed_data/scaler.pkl"))
ENCODERS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../processed_data/label_encoders.pkl"))

class PredictionService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoders = None
        self.artifacts_loaded = False

    def _load_artifacts(self):
        if self.artifacts_loaded:
            return
        try:
            if os.path.exists(SCALER_PATH):
                self.scaler = joblib.load(SCALER_PATH)
            if os.path.exists(ENCODERS_PATH):
                self.encoders = joblib.load(ENCODERS_PATH)
            if os.path.exists(MODEL_PATH):
                from tensorflow.keras.models import load_model
                self.model = load_model(MODEL_PATH)
            self.artifacts_loaded = True
            logger.info("AI Model artifacts lazy loaded successfully.")
        except Exception as e:
            logger.error(f"Error lazy loading AI model artifacts ({e}). Failsafe predictor active.")
            self.artifacts_loaded = True

    def _safe_transform(self, column: str, value: str):
        if not self.encoders or column not in self.encoders:
            return 0
        encoder = self.encoders[column]
        if value in encoder.classes_:
            return int(encoder.transform([value])[0])
        else:
            return 0

    def predict(self, input_data: dict) -> dict:
        self._load_artifacts()
        try:
            train_type = self._safe_transform("train_type", input_data.get("train_type", "Express"))
            current_station = self._safe_transform("current_station", input_data.get("current_station", "S1"))
            next_station = self._safe_transform("next_station", input_data.get("next_station", "S2"))
            weather = self._safe_transform("weather", input_data.get("weather", "Sunny"))
            signal_status = self._safe_transform("signal_status", input_data.get("signal_status", "Green"))
            track_status = self._safe_transform("track_status", input_data.get("track_status", "Free"))
            platform_available = self._safe_transform("platform_available", input_data.get("platform_available", "Yes"))
            day_of_week = self._safe_transform("day_of_week", input_data.get("day_of_week", "Monday"))
            congestion_level = self._safe_transform("congestion_level", input_data.get("congestion_level", "Low"))

            speed = float(input_data.get("speed", 90))
            current_delay = float(input_data.get("current_delay", 5))
            train_priority = float(input_data.get("train_priority", 1))
            hour_of_day = float(input_data.get("hour_of_day", 14))

            sample_input = np.array([[
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
            ]])

            if self.scaler is not None:
                scaled_input = self.scaler.transform(sample_input)
            else:
                scaled_input = sample_input

            if self.model is not None:
                sequence = np.repeat(scaled_input, 5, axis=0).reshape(1, 5, 13)
                predicted_delay = float(self.model.predict(sequence, verbose=0)[0][0])
            else:
                predicted_delay = current_delay + (2.0 if congestion_level > 0 else 0.5)

            predicted_delay = max(0.0, predicted_delay)

            if predicted_delay <= 5:
                severity = "ON TIME"
            elif predicted_delay <= 15:
                severity = "MINOR DELAY"
            elif predicted_delay <= 30:
                severity = "MODERATE DELAY"
            else:
                severity = "CRITICAL DELAY"

            return {
                "predicted_delay": round(predicted_delay, 2),
                "delay_status": severity,
                "model_status": "LSTM_NEURAL_NETWORK" if self.model is not None else "FAILSAFE_ESTIMATOR"
            }
        except Exception as e:
            logger.error(f"Prediction execution failed ({e}). Returning fallback response.")
            return {
                "predicted_delay": float(input_data.get("current_delay", 5)),
                "delay_status": "ON TIME",
                "model_status": "FAILSAFE_FALLBACK"
            }

prediction_service = PredictionService()
