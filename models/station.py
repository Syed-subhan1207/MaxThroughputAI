"""
Station Data Model for Railway Traffic Management
"""

class Station:
    def __init__(self, station_id, name=None, state=None, zone=None, latitude=None, longitude=None):
        self.station_id = str(station_id)
        self.name = name or str(station_id)
        self.state = state or ""
        self.zone = zone or ""
        self.latitude = latitude
        self.longitude = longitude

    def to_dict(self):
        return {
            "station_id": self.station_id,
            "name": self.name,
            "state": self.state,
            "zone": self.zone,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
