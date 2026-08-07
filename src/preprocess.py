# ==========================================================
# AI-Powered Railway Traffic Control System
# LSTM Data Preprocessing (Real Dataset Integration)
# ==========================================================

import os
import joblib
import hashlib
import numpy as np
import pandas as pd

from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split

# Set random seed for reproducibility
np.random.seed(42)

# ==========================================================
# STEP 1 : DATASET LOADING WITH SCHEMA DETECTION
# ==========================================================

print("=" * 60)
print("STEP 1 : LOADING DATASET & DETECTING SCHEMA")
print("=" * 60)

# Resolve directories
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../data")

# Fallback path search for clean schedules, trains and stations
schedules_paths = [
    os.path.join(data_dir, "processed_CSV/clean_schedules.csv"),
    os.path.join(data_dir, "processed_CSV/schedules.csv"),
    os.path.join(data_dir, "additional_train_files/train_schedule.csv")
]

trains_paths = [
    os.path.join(data_dir, "processed_CSV/clean_trains.csv"),
    os.path.join(data_dir, "processed_CSV/trains.csv"),
    os.path.join(data_dir, "additional_train_files/train_info.csv")
]

stations_paths = [
    os.path.join(data_dir, "processed_CSV/clean_stations.csv"),
    os.path.join(data_dir, "processed_CSV/stations.csv")
]

def load_first_available(paths, name):
    for path in paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                print(f"Loaded {name} from: {path} (Shape: {df.shape})")
                return df
            except Exception as e:
                print(f"Error loading {path}: {e}")
    raise FileNotFoundError(f"Could not load any version of {name} from {paths}")

df_schedules_raw = load_first_available(schedules_paths, "schedules")
df_trains_raw = load_first_available(trains_paths, "trains")
df_stations_raw = load_first_available(stations_paths, "stations")

# ==========================================================
# STEP 2 : COLUMN MAPPING FOR BACKWARD COMPATIBILITY
# ==========================================================

def map_df_columns(df, expected_to_aliases):
    rename_dict = {}
    for expected, aliases in expected_to_aliases.items():
        for alias in aliases:
            # Check case-insensitive match
            matches = [c for c in df.columns if c.lower() == alias.lower()]
            if matches:
                rename_dict[matches[0]] = expected
                break
    return df.rename(columns=rename_dict)

schedules_mapping = {
    "train_number": ["train_number", "train_no", "number", "Train_No"],
    "station_code": ["station_code", "code", "Station_Code"],
    "station_name": ["station_name", "name", "Station_Name"],
    "arrival": ["arrival", "arrival_time", "Arrival_time", "Arrival_Time"],
    "departure": ["departure", "departure_time", "Departure_Time"],
    "day": ["day", "days", "day_of_week"],
    "id": ["id", "sn", "SN"]
}

trains_mapping = {
    "train_number": ["number", "train_number", "train_no", "Train_No"],
    "train_type": ["type", "train_type"],
    "train_name": ["name", "train_name", "Train_Name"],
    "distance": ["distance", "Distance"],
    "duration_m": ["duration_m", "duration_h"]
}

stations_mapping = {
    "station_code": ["code", "station_code"],
    "station_name": ["name", "station_name"]
}

df_schedules = map_df_columns(df_schedules_raw.copy(), schedules_mapping)
df_trains = map_df_columns(df_trains_raw.copy(), trains_mapping)
df_stations = map_df_columns(df_stations_raw.copy(), stations_mapping)

print("Columns mapped successfully!")

# Ensure keys are strings for joining
df_schedules["train_number"] = df_schedules["train_number"].astype(str)
df_trains["train_number"] = df_trains["train_number"].astype(str)

# ==========================================================
# STEP 3 : DERIVE CONGESTION & OTHER Timetable METRICS
# ==========================================================

print("\n" + "=" * 60)
print("STEP 3 : DERIVING CONGESTION & OPERATION METRICS")
print("=" * 60)

# Extract hour from scheduled times
def extract_hour(time_str):
    if pd.isna(time_str) or time_str == "Not Available" or ":" not in str(time_str):
        return 12  # Default hour
    try:
        return int(str(time_str).split(":")[0])
    except:
        return 12

df_schedules["arrival_hour"] = df_schedules["arrival"].apply(extract_hour)
df_schedules["departure_hour"] = df_schedules["departure"].apply(extract_hour)

# Congestion level based on station-hour train density
# Count scheduled arrivals & departures per station per hour
density_arrival = df_schedules.groupby(["station_code", "arrival_hour"]).size().reset_index(name="count_arr")
density_departure = df_schedules.groupby(["station_code", "departure_hour"]).size().reset_index(name="count_dep")

# Rename hour columns to join
density_arrival.rename(columns={"arrival_hour": "hour"}, inplace=True)
density_departure.rename(columns={"departure_hour": "hour"}, inplace=True)

density = pd.merge(density_arrival, density_departure, on=["station_code", "hour"], how="outer").fillna(0)
density["train_density"] = density["count_arr"] + density["count_dep"]

# Keep station-hour congestion lookup
congestion_lookup = {}
for _, row in density.iterrows():
    st = row["station_code"]
    hr = int(row["hour"])
    dens = row["train_density"]
    
    if dens <= 2:
        level = "Low"
    elif dens <= 5:
        level = "Medium"
    else:
        level = "High"
    congestion_lookup[(st, hr)] = level

def get_congestion(station, hour):
    return congestion_lookup.get((station, hour), "Low")

# Map train type to Express, Passenger, Freight
def normalize_train_type(t_type):
    t_type = str(t_type).upper()
    if any(x in t_type for x in ["SF", "EXP", "RAJ", "DRNT", "SHTB", "JSHTB", "GR", "SKR", "MAIL"]):
        return "Express"
    elif any(x in t_type for x in ["PASS", "MEMU", "DEMU", "TOY", "HYD", "DEL", "KLKT"]):
        return "Passenger"
    elif "FREIGHT" in t_type or "GOODS" in t_type:
        return "Freight"
    else:
        return "Express"  # Fallback

# Build train details lookup
train_type_lookup = {}
train_speed_lookup = {}
for _, row in df_trains.iterrows():
    num = str(row["train_number"])
    name = str(row.get("train_name", ""))
    raw_type = row.get("train_type", "Express")
    
    norm_type = normalize_train_type(raw_type)
    train_type_lookup[num] = norm_type
    
    # Speed calculation
    dist = float(row.get("distance", 0))
    dur = float(row.get("duration_m", 0))
    if "duration_h" in df_trains.columns and dur == 0:
        dur = float(row.get("duration_h", 0)) * 60
        
    if dur > 0 and dist > 0:
        calculated_speed = dist / (dur / 60)
        speed = max(30, min(130, calculated_speed))
    else:
        # Default speeds
        if norm_type == "Express":
            speed = 90
        elif norm_type == "Freight":
            speed = 45
        else:
            speed = 50
    train_speed_lookup[num] = round(speed)

print("Congestion and train lookup tables built successfully.")

# ==========================================================
# STEP 4 : GENERATING CHRONOLOGICAL SEGMENTS & DETERMINISTIC PROPAGATION
# ==========================================================

print("\n" + "=" * 60)
print("STEP 4 : CHRONOLOGICAL SEGMENT PREPARATION")
print("=" * 60)

# Sort schedules by train and stopping index ID
if "id" in df_schedules.columns:
    df_schedules = df_schedules.sort_values(by=["train_number", "id"])
else:
    df_schedules = df_schedules.sort_values(by=["train_number", "day", "arrival"])

# Group by train and generate sequential segments
segments = []
day_names = {1.0: "Monday", 2.0: "Tuesday", 3.0: "Wednesday", 4.0: "Thursday", 5.0: "Friday", 6.0: "Saturday", 7.0: "Sunday"}

for train_num, group in df_schedules.groupby("train_number"):
    if len(group) < 2:
        continue  # Need at least 2 stations to form a segment
        
    records = group.to_dict("records")
    current_delay = 0  # Starting delay at source
    
    for i in range(len(records) - 1):
        stop_curr = records[i]
        stop_next = records[i+1]
        
        curr_station = str(stop_curr["station_code"])
        next_station = str(stop_next["station_code"])
        
        # Resolve train characteristics
        train_type = train_type_lookup.get(train_num, "Passenger")
        speed = train_speed_lookup.get(train_num, 50)
        
        # Priority mapping
        if train_type == "Express":
            # Check if superfast/Rajdhani
            train_name = str(stop_curr.get("train_name", "")).upper()
            if any(x in train_name for x in ["RAJDHANI", "SHATABDI", "DURONTO", "SUPERFAST", "SF"]):
                priority = 1
            else:
                priority = 2
        elif train_type == "Freight":
            priority = 4
        else:
            priority = 3
            
        day_num = float(stop_curr.get("day", 1.0))
        day_of_week = day_names.get(day_num, "Monday")
        hour_of_day = int(stop_curr["departure_hour"])
        
        # Congestion lookup
        congestion = get_congestion(curr_station, hour_of_day)
        
        # Platform, Track, Signal mapping (deterministic using congestion)
        if congestion == "High":
            platform = "No"
            track = "Occupied"
            signal = "Red"
        elif congestion == "Medium":
            platform = "Yes"
            track = "Free"
            signal = "Yellow"
        else:
            platform = "Yes"
            track = "Free"
            signal = "Green"
            
        # Deterministic weather mapping using station hashing
        h = int(hashlib.md5(curr_station.encode()).hexdigest(), 16)
        weather_idx = h % 10
        if weather_idx < 7:
            weather = "Sunny"
        elif weather_idx < 9:
            weather = "Rain"
        else:
            weather = "Fog"
            
        # Deterministic delay propagation logic
        delay_diff = 0
        if weather == "Fog":
            delay_diff += 15
        elif weather == "Rain":
            delay_diff += 5
            
        if congestion == "High":
            delay_diff += 10
        elif congestion == "Medium":
            delay_diff += 2
        elif congestion == "Low":
            delay_diff -= 5  # Catching up delay
            
        if priority == 3:
            delay_diff += 3  # Lower priority trains get stalled more
        elif priority == 1:
            delay_diff -= 2  # Higher priority trains get cleared faster
            
        # Accumulate
        next_delay = max(0, current_delay + delay_diff)
        
        segments.append({
            "train_id": train_num,
            "train_type": train_type,
            "current_station": curr_station,
            "next_station": next_station,
            "speed": speed,
            "current_delay": current_delay,
            "weather": weather,
            "signal_status": signal,
            "track_status": track,
            "platform_available": platform,
            "train_priority": priority,
            "day_of_week": day_of_week,
            "hour_of_day": hour_of_day,
            "congestion_level": congestion,
            "predicted_delay_min": next_delay
        })
        
        # Propagate delay to next station
        current_delay = next_delay

df_processed = pd.DataFrame(segments)
print(f"Generated {len(df_processed)} chronological segments across train runs.")

# ==========================================================
# STEP 5 : REPRESENTATIVE STRATIFIED JOURNEY SAMPLING
# ==========================================================

print("\n" + "=" * 60)
print("STEP 5 : STRATIFIED REPRESENTATIVE SAMPLING")
print("=" * 60)

# We must keep sequences of length 5 intact per train.
# Therefore, we sample complete train IDs proportionally.
train_stats = df_processed.groupby(["train_id", "train_type"]).size().reset_index(name="seg_count")
# Only keep trains that can form at least one sequence (length 5 needs 5 segments)
valid_trains = train_stats[train_stats["seg_count"] >= 5]

max_sequences = 45000  # Cap training sequences for efficient local hardware CPU run

if len(df_processed) > max_sequences:
    print(f"Dataset has {len(df_processed)} segments. Sampling representing trains to target ~{max_sequences} sequences...")
    # Stratified sampling of trains by type
    train_types = valid_trains["train_type"].unique()
    sampled_train_ids = []
    
    # Calculate target trains to sample
    total_valid_segs = valid_trains["seg_count"].sum()
    sample_ratio = max_sequences / total_valid_segs
    
    for t_type in train_types:
        type_trains = valid_trains[valid_trains["train_type"] == t_type]
        sample_size = int(len(type_trains) * sample_ratio)
        sample_size = max(1, min(len(type_trains), sample_size))
        
        # Sample deterministically using random state
        sampled_type = type_trains.sample(n=sample_size, random_state=42)
        sampled_train_ids.extend(sampled_type["train_id"].tolist())
        
    df_sampled = df_processed[df_processed["train_id"].isin(sampled_train_ids)].copy()
else:
    df_sampled = df_processed.copy()

print(f"Sampled Dataset Shape: {df_sampled.shape}")
print(df_sampled["train_type"].value_counts())

# ==========================================================
# STEP 6 : ENCODE CATEGORICAL DATA
# ==========================================================

print("\n" + "=" * 60)
print("STEP 6 : ENCODING CATEGORICAL DATA")
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

# Ensure encoders include all stations, even those in fallback or master stations
all_stations = set(df_stations["station_code"].dropna().unique())
all_stations.update(df_processed["current_station"].unique())
all_stations.update(df_processed["next_station"].unique())
# Add default S1-S7 to avoid breaking if original test files are used
all_stations.update([f"S{i}" for i in range(1, 10)])
all_stations = sorted(list(all_stations))

# Base fits for standard category domains
pre_fit_categories = {
    "train_type": ["Express", "Passenger", "Freight"],
    "weather": ["Fog", "Rain", "Sunny"],
    "signal_status": ["Green", "Red", "Yellow"],
    "track_status": ["Free", "Occupied"],
    "platform_available": ["No", "Yes"],
    "day_of_week": ["Friday", "Monday", "Saturday", "Sunday", "Thursday", "Tuesday", "Wednesday"],
    "congestion_level": ["High", "Low", "Medium"],
    "current_station": all_stations,
    "next_station": all_stations
}

for column in categorical_columns:
    encoder = LabelEncoder()
    # Pre-fit classes to ensure all possible classes are covered
    encoder.fit(pre_fit_categories[column])
    df_sampled[column] = encoder.transform(df_sampled[column])
    label_encoders[column] = encoder

print("Categorical Encoding Completed!")

# ==========================================================
# STEP 7 : DROPPING NON-FEATURE COLUMNS
# ==========================================================

print("\n" + "=" * 60)
print("STEP 7 : SELECTING FEATURES")
print("=" * 60)

# Drop train_id since it is not a feature used by model
df_features = df_sampled.drop(columns=["train_id"])

X = df_features.drop(columns=["predicted_delay_min"])
y = df_features["predicted_delay_min"]

print("Features columns:", X.columns.tolist())

# ==========================================================
# STEP 8 : NORMALIZATION
# ==========================================================

print("\n" + "=" * 60)
print("STEP 8 : NORMALIZING DATA")
print("=" * 60)

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

print("Normalization Completed!")

# ==========================================================
# STEP 9 : CREATE LSTM SEQUENCES
# ==========================================================

print("\n" + "=" * 60)
print("STEP 9 : CREATING LSTM SEQUENCES")
print("=" * 60)

sequence_length = 5
X_sequences = []
y_sequences = []

# Group by train ID to create sequences only within the same train journey
df_sampled_scaled = pd.DataFrame(X_scaled, columns=X.columns)
df_sampled_scaled["train_id"] = df_sampled["train_id"].values
df_sampled_scaled["target"] = y.values

for train_id, train_group in df_sampled_scaled.groupby("train_id"):
    if len(train_group) <= sequence_length:
        continue
    
    group_features = train_group.drop(columns=["train_id", "target"]).values
    group_targets = train_group["target"].values
    
    for i in range(len(train_group) - sequence_length):
        X_sequences.append(group_features[i:i + sequence_length])
        y_sequences.append(group_targets[i + sequence_length])

X_sequences = np.array(X_sequences)
y_sequences = np.array(y_sequences)

print("Sequence Shapes :", X_sequences.shape, y_sequences.shape)

# ==========================================================
# STEP 10 : TRAIN TEST SPLIT
# ==========================================================

print("\n" + "=" * 60)
print("STEP 10 : TRAIN TEST SPLIT")
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
# STEP 11 : SAVE PROCESSED DATA
# ==========================================================

print("\n" + "=" * 60)
print("SAVING PROCESSED FILES")
print("=" * 60)

processed_dir = os.path.join(base_dir, "../processed_data")
os.makedirs(processed_dir, exist_ok=True)

np.save(os.path.join(processed_dir, "X_train.npy"), X_train)
np.save(os.path.join(processed_dir, "X_test.npy"), X_test)
np.save(os.path.join(processed_dir, "y_train.npy"), y_train)
np.save(os.path.join(processed_dir, "y_test.npy"), y_test)

joblib.dump(scaler, os.path.join(processed_dir, "scaler.pkl"))
joblib.dump(label_encoders, os.path.join(processed_dir, "label_encoders.pkl"))

print("Processed Data Saved Successfully!")
print("Preprocessing Completed Successfully!")