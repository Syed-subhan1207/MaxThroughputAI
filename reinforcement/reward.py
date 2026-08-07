"""
Reward Calculator Module for Reinforcement Learning Decision Support
Evaluates positive and negative rewards based on operational network metrics and safety constraints.
"""

from typing import Dict, Any

class RewardCalculator:
    @staticmethod
    def calculate_reward(
        state: Dict[str, Any],
        action_name: str,
        next_state: Dict[str, Any],
        opt_results: Dict[str, Any] = None
    ) -> float:
        """
        Calculates numerical reward for the state-action transition.
        
        Positive Rewards:
          +20 if throughput improves
          +15 if predicted delay decreases
          +10 if conflict probability decreases
          +10 if route becomes shorter
          +8  if waiting trains decrease

        Negative Rewards:
          -30 if congestion increases
          -25 if signal violation occurs
          -20 if train must wait
          -15 if delay increases
          -40 if safety constraint is violated
        """
        opt_results = opt_results or {}
        reward = 0.0

        prev_delay = float(state.get("current_delay", 0))
        next_delay = float(next_state.get("current_delay", prev_delay))

        prev_pred_delay = float(state.get("predicted_delay", prev_delay))
        next_pred_delay = float(next_state.get("predicted_delay", prev_pred_delay))

        prev_conf = float(state.get("conflict_probability_pct", 15.0))
        next_conf = float(next_state.get("conflict_probability_pct", prev_conf))

        signal_status = str(state.get("signal_status", "Green")).upper()
        track_status = str(state.get("track_status", "Clear")).upper()
        congestion = str(state.get("congestion_level", "Low")).upper()
        train_priority = str(state.get("train_priority", "High")).upper()

        throughput_gain = float(opt_results.get("expected_throughput_gain_pct", 0.0))
        waiting_trains = int(opt_results.get("waiting_trains", 0))

        # --- SAFETY VIOLATIONS (-40) ---
        if track_status == "BLOCKED" and action_name in ["MOVE", "INCREASE_SPEED", "PRIORITY_OVERRIDE"]:
            reward -= 40.0

        # --- SIGNAL VIOLATIONS (-25) ---
        if signal_status == "RED" and action_name in ["MOVE", "INCREASE_SPEED"]:
            reward -= 25.0

        # --- TRAIN MUST WAIT (-20) ---
        if action_name == "WAIT":
            reward -= 20.0

        # --- CONGESTION INCREASES / HIGH CONGESTION (-30) ---
        if congestion == "HIGH" and action_name not in ["ALTERNATE_ROUTE", "PRIORITY_OVERRIDE"]:
            reward -= 30.0

        # --- DELAY INCREASES (-15) ---
        if next_delay > prev_delay:
            reward -= 15.0

        # --- POSITIVE REWARDS ---
        # +20 if throughput improves
        if throughput_gain > 0.0 or (action_name in ["MOVE", "PRIORITY_OVERRIDE"] and track_status != "BLOCKED"):
            reward += 20.0

        # +15 if predicted delay decreases
        if next_pred_delay < prev_pred_delay:
            reward += 15.0

        # +10 if conflict probability decreases
        if next_conf < prev_conf or (action_name == "REDUCE_SPEED" and prev_conf > 20.0):
            reward += 10.0

        # +10 if route becomes shorter / alternate route optimization
        if action_name == "ALTERNATE_ROUTE" or opt_results.get("path_distance_km", 0) > 0:
            reward += 10.0

        # +8 if waiting trains decrease / network throughput efficiency
        if waiting_trains == 0 or action_name == "PRIORITY_OVERRIDE":
            reward += 8.0

        return round(reward, 2)
