# 🚄 MaxThroughputAI

> **Maximizing Section Throughput Using AI-Powered Precise Train Traffic Control**

An AI-powered Railway Traffic Control System developed for **Smart India Hackathon (SIH)** to improve railway safety, reduce delays, prevent conflicts, and maximize section throughput through intelligent decision support.

---

## 📌 Project Overview

MaxThroughputAI is an intelligent railway traffic management system that assists railway controllers by predicting train delays, detecting operational conflicts, and providing AI-generated recommendations in real time.

The system combines **Artificial Intelligence**, **LSTM Deep Learning**, **FastAPI**, and an interactive **Railway Operations Dashboard** to enhance railway efficiency and safety.

---

## ✨ Features

- 🚆 AI-Based Train Delay Prediction
- 🧠 LSTM (Long Short-Term Memory) Deep Learning Model
- 📊 Real-Time Railway Operations Dashboard
- ⚠️ Conflict Detection & Decision Support
- 📈 Analytics Dashboard
- 🌦️ Weather & Congestion Consideration
- 🔄 FastAPI Backend
- 🌐 Interactive Frontend
- 📑 Swagger API Documentation
- 🤖 AI Recommendation Engine

---

## 🛠️ Technology Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- FastAPI
- Python

### Artificial Intelligence
- TensorFlow / Keras
- LSTM Neural Network
- Scikit-learn
- NumPy
- Pandas

### Tools
- Git & GitHub
- Swagger UI
- VS Code

---

## 📂 Project Structure

```
MaxThroughputAI/
│
├── data/
│   └── railway_traffic_control_dataset.csv
│
├── processed_data/
│   ├── X_train.npy
│   ├── X_test.npy
│   ├── y_train.npy
│   ├── y_test.npy
│   ├── scaler.pkl
│   └── label_encoders.pkl
│
├── models/
│   └── delay_predictor.keras
│
├── src/
│   ├── preprocess.py
│   ├── train.py
│   ├── predict.py
│   ├── api.py
│   ├── login.html
│   ├── dashboard.html
│   ├── script.js
│   └── style.css
│
└── README.md
```

---

## 🧠 AI Workflow

```
Railway Input Parameters
        │
        ▼
Data Preprocessing
        │
        ▼
Feature Encoding & Scaling
        │
        ▼
LSTM Model
        │
        ▼
Delay Prediction
        │
        ▼
AI Recommendations
        │
        ▼
FastAPI Backend
        │
        ▼
Interactive Dashboard
```

---

## 📥 LSTM Input Features

The AI model predicts train delays using the following operational parameters:

- Train Type
- Current Station
- Next Station
- Train Speed
- Current Delay
- Weather Condition
- Signal Status
- Track Status
- Platform Availability
- Train Priority
- Day of Week
- Hour of Day
- Congestion Level

---

## 📤 Output

The AI system provides:

- Predicted Delay (minutes)
- Delay Status
- AI-Generated Recommendations

Example:

```
Predicted Delay : 21.1 Minutes

Status : MODERATE DELAY

Recommendations:
✔ Notify next station
✔ Passenger announcement required
✔ Increase signal priority
✔ Prepare platform staff
```

---

## 🚀 Running the Project

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Train the AI Model

```bash
python train.py
```

### Start FastAPI

```bash
uvicorn api:app --reload
```

### Open Swagger

```
http://127.0.0.1:8000/docs
```

### Launch Frontend

Open:

```
login.html
```

---

## 🎯 Future Enhancements

- Real-time Railway Data Integration
- GPS-Based Live Train Tracking
- Reinforcement Learning for Dynamic Scheduling
- IoT Sensor Integration
- Digital Twin Simulation
- AI-Based Route Optimization
- Predictive Maintenance
- Cloud Deployment

---

## 👥 Team

Developed as part of the **Smart India Hackathon (SIH)**.

---

## 📜 License

This project is developed for educational and research purposes under the Smart India Hackathon initiative.

---
