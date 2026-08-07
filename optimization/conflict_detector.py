class ConflictDetector:

    @staticmethod
    def detect_track_conflicts(trains):
        conflicts = []
        for i in range(len(trains)):
            for j in range(i + 1, len(trains)):
                t1 = trains[i]
                t2 = trains[j]
                # Same track
                if (
                    t1.current_station == t2.current_station
                    and t1.next_station == t2.next_station
                ):
                    conflicts.append((t1, t2, "Same Track"))
        return conflicts

    @staticmethod
    def detect_station_conflicts(trains):
        station_map = {}
        for train in trains:
            station_map.setdefault(train.current_station, []).append(train)

        conflicts = []
        for station, train_list in station_map.items():
            if len(train_list) > 1:
                conflicts.append((station, train_list))
        return conflicts

    @staticmethod
    def detect_signal_conflicts(trains):
        conflicts = []
        for train in trains:
            if train.signal_status == "Red":
                conflicts.append(train)
        return conflicts

    @staticmethod
    def detect_blocked_tracks(trains):
        conflicts = []
        for train in trains:
            if train.track_status == "Blocked":
                conflicts.append(train)
        return conflicts

    @staticmethod
    def detect_platform_conflicts(trains):
        conflicts = []
        for train in trains:
            if str(train.platform_available).lower() == "no":
                conflicts.append(train)
        return conflicts

    @staticmethod
    def detect_congestion(trains):
        conflicts = []
        for train in trains:
            if train.congestion_level == "High":
                conflicts.append(train)
        return conflicts

    @staticmethod
    def detect_priority_conflicts(trains):
        conflicts = []
        priority = {
            "High": 3,
            "Medium": 2,
            "Low": 1
        }
        for i in range(len(trains)):
            for j in range(i + 1, len(trains)):
                t1 = trains[i]
                t2 = trains[j]
                if (
                    t1.current_station == t2.current_station
                    and t1.next_station == t2.next_station
                ):
                    p1 = priority.get(t1.priority, 1)
                    p2 = priority.get(t2.priority, 1)
                    if p1 != p2:
                        higher = t1 if p1 > p2 else t2
                        lower = t2 if higher == t1 else t1
                        conflicts.append((higher, lower))
        return conflicts
