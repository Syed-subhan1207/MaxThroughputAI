class Constraints:

    @staticmethod
    def track_available(train):
        return train.track_status != "Blocked"

    @staticmethod
    def signal_clear(train):
        return train.signal_status == "Green"

    @staticmethod
    def platform_available(train):
        return str(train.platform_available).lower() == "yes"

    @staticmethod
    def weather_safe(train):
        return train.weather.lower() not in [
            "storm",
            "heavy rain",
            "cyclone"
        ]

    @staticmethod
    def can_move(train):
        return (
            Constraints.track_available(train)
            and Constraints.signal_clear(train)
            and Constraints.platform_available(train)
            and Constraints.weather_safe(train)
        )
