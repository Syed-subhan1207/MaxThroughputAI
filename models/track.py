"""
Track Data Model for Railway Network Connectivity
"""

class Track:
    def __init__(self, from_station, to_station, weight=0, delay=0):
        self.from_station = str(from_station)
        self.to_station = str(to_station)
        self.weight = float(weight)
        self.delay = float(delay)

    def to_dict(self):
        return {
            "from_station": self.from_station,
            "to_station": self.to_station,
            "weight": self.weight,
            "delay": self.delay
        }
