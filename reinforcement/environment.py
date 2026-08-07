"""
Railway Environment Module for Reinforcement Learning Policy Evaluation
Provides state discretization, safety constraint validation, and state transitions.
"""

from typing import Dict, Any, List

class RailwayEnvironment:
    ACTIONS = {
        0: "MOVE",
        1: "WAIT",
        2: "PRIORITY_OVERRIDE",
        3: "INCREASE_SPEED",
        4: "REDUCE_SPEED",
        5: "ALTERNATE_ROUTE"
    }

    ACTION_NAMES = {v: k for k, v in ACTIONS.items()}

    def __init__(self):
        pass

    @staticmethod
    def get_state_key(state: Dict[str, Any]) -> str:
        """
        Converts live/predicted railway state variables into a discrete, hashable state string.
        Features: current_delay, predicted_delay, current_station, next_station,
                  train_priority, signal_status, track_status, congestion_level, weather, speed.
        """
        current_station = str(state.get("current_station", "S1")).upper()
        next_station = str(state.get("next_station", "S2")).upper()
        
        priority = str(state.get("train_priority", "High")).capitalize()
        if priority in ["1", "High"]:
            priority = "High"
        elif priority in ["2", "Medium"]:
            priority = "Medium"
        else:
            priority = "Low"

        signal_status = str(state.get("signal_status", "Green")).capitalize()
        track_status = str(state.get("track_status", "Clear")).capitalize()
        congestion = str(state.get("congestion_level", "Low")).capitalize()
        weather = str(state.get("weather", "Clear")).capitalize()

        curr_delay = float(state.get("current_delay", 0))
        if curr_delay <= 5:
            delay_bucket = "LowDelay"
        elif curr_delay <= 15:
            delay_bucket = "MedDelay"
        else:
            delay_bucket = "HighDelay"

        speed = float(state.get("speed", 80))
        if speed <= 60:
            speed_bucket = "Slow"
        elif speed <= 100:
            speed_bucket = "Normal"
        else:
            speed_bucket = "Fast"

        return f"{current_station}_{next_station}|P:{priority}|Sig:{signal_status}|Trk:{track_status}|Cong:{congestion}|Wth:{weather}|Dly:{delay_bucket}|Spd:{speed_bucket}"

    @staticmethod
    def is_action_safe(state: Dict[str, Any], action_id: int) -> bool:
        """
        Validates safety constraints.
        Actions 0 (MOVE) and 3 (INCREASE_SPEED) are unsafe if track is blocked or signal is red.
        """
        action_name = RailwayEnvironment.ACTIONS.get(action_id, "MOVE")
        signal = str(state.get("signal_status", "Green")).upper()
        track = str(state.get("track_status", "Clear")).upper()

        if track == "BLOCKED" and action_name in ["MOVE", "INCREASE_SPEED", "PRIORITY_OVERRIDE"]:
            return False
        
        if signal == "RED" and action_name in ["MOVE", "INCREASE_SPEED"]:
            return False

        return True

    @staticmethod
    def get_valid_actions(state: Dict[str, Any]) -> List[int]:
        """Returns list of valid action IDs for the given state."""
        valid = []
        for action_id in RailwayEnvironment.ACTIONS:
            if RailwayEnvironment.is_action_safe(state, action_id):
                valid.append(action_id)
        if not valid:
            valid = [1]  # Default to WAIT if all else restricted
        return valid

    @staticmethod
    def get_next_state(state: Dict[str, Any], action_id: int) -> Dict[str, Any]:
        """
        Simulates state transition given the chosen action.
        """
        next_s = dict(state)
        action_name = RailwayEnvironment.ACTIONS.get(action_id, "MOVE")

        curr_delay = float(state.get("current_delay", 0))
        pred_delay = float(state.get("predicted_delay", curr_delay))
        speed = float(state.get("speed", 80))
        congestion = str(state.get("congestion_level", "Low")).upper()
        conf_prob = float(state.get("conflict_probability_pct", 10.0))

        if action_name == "MOVE":
            next_s["predicted_delay"] = max(0.0, pred_delay - 2.0)
            next_s["conflict_probability_pct"] = max(1.0, conf_prob - 2.0)
        elif action_name == "WAIT":
            next_s["current_delay"] = curr_delay + 3.0
            next_s["predicted_delay"] = pred_delay + 3.0
        elif action_name == "PRIORITY_OVERRIDE":
            next_s["predicted_delay"] = max(0.0, pred_delay - 5.0)
            next_s["conflict_probability_pct"] = max(1.0, conf_prob - 5.0)
        elif action_name == "INCREASE_SPEED":
            next_s["speed"] = speed + 15.0
            next_s["predicted_delay"] = max(0.0, pred_delay - 3.0)
        elif action_name == "REDUCE_SPEED":
            next_s["speed"] = max(20.0, speed - 15.0)
            next_s["conflict_probability_pct"] = max(1.0, conf_prob - 4.0)
        elif action_name == "ALTERNATE_ROUTE":
            next_s["congestion_level"] = "Low"
            next_s["conflict_probability_pct"] = max(1.0, conf_prob - 10.0)
            next_s["predicted_delay"] = max(0.0, pred_delay - 4.0)

        return next_s
