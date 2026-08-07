"""
Train Data Model for Railway Traffic Management and Optimization
"""

class Train:
    def __init__(
        self,
        train_id,
        current_station,
        next_station,
        speed_kmph=80,
        current_delay_min=0,
        weather="Clear",
        signal_status="Green",
        track_status="Clear",
        platform_available="Yes",
        train_priority="High",
        congestion_level="Low",
        predicted_delay_min=0,
        train_name=None,
        train_type="Express"
    ):
        self.train_id = str(train_id)
        self.train_name = train_name or f"Train {train_id}"
        self.train_type = train_type
        self.current_station = str(current_station)
        self.next_station = str(next_station)
        self.speed_kmph = int(speed_kmph)
        self.speed = int(speed_kmph)
        self.current_delay_min = int(current_delay_min)
        self.current_delay = int(current_delay_min)
        self.weather = str(weather)
        self.signal_status = str(signal_status)
        self.track_status = str(track_status)
        self.platform_available = str(platform_available)
        self.train_priority = str(train_priority)
        self.priority = str(train_priority)
        self.congestion_level = str(congestion_level)
        self.predicted_delay_min = int(predicted_delay_min)
        self.predicted_delay = int(predicted_delay_min)
        self.status = "WAITING"

    def to_dict(self):
        return {
            "train_id": self.train_id,
            "train_name": self.train_name,
            "train_type": self.train_type,
            "current_station": self.current_station,
            "next_station": self.next_station,
            "speed_kmph": self.speed_kmph,
            "current_delay_min": self.current_delay_min,
            "weather": self.weather,
            "signal_status": self.signal_status,
            "track_status": self.track_status,
            "platform_available": self.platform_available,
            "train_priority": self.train_priority,
            "congestion_level": self.congestion_level,
            "predicted_delay_min": self.predicted_delay_min,
            "status": self.status
        }
