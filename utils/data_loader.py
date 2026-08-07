import os
import pandas as pd
import logging

from models.train import Train
from models.station import Station
from models.track import Track

logger = logging.getLogger("data_loader")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

CLEAN_TRAINS_PATH = os.path.join(PROJECT_ROOT, "data", "processed_CSV", "clean_trains.csv")
CLEAN_STATIONS_PATH = os.path.join(PROJECT_ROOT, "data", "processed_CSV", "clean_stations.csv")
CLEAN_SCHEDULES_PATH = os.path.join(PROJECT_ROOT, "data", "processed_CSV", "clean_schedules.csv")

class DataLoader:

    @staticmethod
    def load_trains_df():
        if os.path.exists(CLEAN_TRAINS_PATH):
            return pd.read_csv(CLEAN_TRAINS_PATH)
        return pd.DataFrame()

    @staticmethod
    def load_stations_df():
        if os.path.exists(CLEAN_STATIONS_PATH):
            return pd.read_csv(CLEAN_STATIONS_PATH)
        return pd.DataFrame()

    @staticmethod
    def load_schedules_df():
        if os.path.exists(CLEAN_SCHEDULES_PATH):
            return pd.read_csv(CLEAN_SCHEDULES_PATH)
        return pd.DataFrame()

    @staticmethod
    def load_trains(limit=50):
        df = DataLoader.load_trains_df()
        trains = []

        if not df.empty:
            df_subset = df.head(limit) if limit else df
            for _, row in df_subset.iterrows():
                num = str(row.get("number", "101"))
                name = str(row.get("name", f"Train {num}"))
                raw_type = str(row.get("type", "Express"))
                from_code = str(row.get("from_station_code", "S1"))
                to_code = str(row.get("to_station_code", "S2"))

                # Speed calculation
                dist = float(row.get("distance", 0)) if pd.notnull(row.get("distance")) else 0
                dur = float(row.get("duration_m", 0)) if pd.notnull(row.get("duration_m")) else 0
                if dur > 0 and dist > 0:
                    speed = int(dist / (dur / 60))
                else:
                    speed = 90 if "EXP" in raw_type.upper() or "SF" in raw_type.upper() else 60
                speed = max(40, min(130, speed))

                # Deterministic delay mapping based on train number
                try:
                    num_val = int("".join([c for c in num if c.isdigit()]))
                    delay = num_val % 25
                except:
                    delay = 5

                # Priority mapping
                priority = "High" if any(x in raw_type.upper() for x in ["EXP", "SF", "RAJ", "DRNT", "SHTB"]) else "Medium"
                
                # Signal, track, platform and congestion mappings
                signal = "Green" if delay <= 12 else "Red"
                track = "Clear" if delay <= 18 else "Blocked"
                platform = "Yes" if delay <= 18 else "No"
                congestion = "High" if delay > 15 else ("Medium" if delay > 8 else "Low")
                predicted_delay = delay + (2 if delay > 10 else -1)
                predicted_delay = max(0, predicted_delay)

                trains.append(
                    Train(
                        train_id=num,
                        current_station=from_code,
                        next_station=to_code,
                        speed_kmph=speed,
                        current_delay_min=delay,
                        weather="Clear",
                        signal_status=signal,
                        track_status=track,
                        platform_available=platform,
                        train_priority=priority,
                        congestion_level=congestion,
                        predicted_delay_min=predicted_delay,
                        train_name=name,
                        train_type=raw_type
                    )
                )
        else:
            # Fallback synthetic train list if CSV is missing
            default_routes = [("S1", "S2"), ("S2", "S3"), ("S2", "S5"), ("S3", "S4"), ("S5", "S4")]
            for i, (src, dst) in enumerate(default_routes):
                trains.append(
                    Train(
                        train_id=f"100{i+1}",
                        current_station=src,
                        next_station=dst,
                        speed_kmph=95 - (i * 5),
                        current_delay_min=(i * 6) % 20,
                        weather="Clear",
                        signal_status="Green" if (i % 2 == 0) else "Red",
                        track_status="Clear",
                        platform_available="Yes",
                        train_priority="High" if i == 0 else "Medium",
                        congestion_level="Low" if i < 2 else "High",
                        predicted_delay_min=((i * 6) % 20) + 1
                    )
                )

        return trains

    @staticmethod
    def load_stations():
        df = DataLoader.load_stations_df()
        stations = []

        if not df.empty and "code" in df.columns:
            for _, row in df.iterrows():
                code = str(row.get("code", "")).strip()
                if code:
                    stations.append(
                        Station(
                            station_id=code,
                            name=str(row.get("name", code)),
                            state=str(row.get("state", "")),
                            zone=str(row.get("zone", "")),
                            latitude=row.get("latitude"),
                            longitude=row.get("longitude")
                        )
                    )
        else:
            default_codes = ["S1", "S2", "S3", "S4", "S5", "S6", "S7"]
            for code in default_codes:
                stations.append(Station(station_id=code, name=f"Station {code}"))

        return stations

    @staticmethod
    def load_tracks():
        trains_df = DataLoader.load_trains_df()
        unique_tracks = set()

        if not trains_df.empty:
            for _, row in trains_df.iterrows():
                src = str(row.get("from_station_code", "")).strip()
                dst = str(row.get("to_station_code", "")).strip()
                if src and dst and src != dst:
                    unique_tracks.add((src, dst))

        if not unique_tracks:
            unique_tracks = {
                ("S1", "S2"), ("S2", "S3"), ("S2", "S5"),
                ("S3", "S4"), ("S5", "S4"), ("S4", "S6"), ("S5", "S7")
            }

        return [
            Track(source, destination, weight=1.0, delay=0.0)
            for source, destination in sorted(unique_tracks)
        ]
