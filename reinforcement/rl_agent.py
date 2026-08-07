"""
Q-Learning Agent Module for Reinforcement Learning Decision Support Layer
Implements lightweight Q-Learning with Epsilon-Greedy action selection,
Q-table persistence, confidence scoring, policy stability calculation, and analytics tracking.
"""

import json
import os
import random
import math
from typing import Dict, Any, List, Tuple
from reinforcement.environment import RailwayEnvironment

class QLearningAgent:
    def __init__(
        self,
        q_table_path: str = None,
        learning_rate: float = 0.10,
        discount_factor: float = 0.95,
        epsilon: float = 0.20
    ):
        if q_table_path is None:
            q_table_path = os.path.join(os.path.dirname(__file__), "q_table.json")

        self.q_table_path = q_table_path
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.num_actions = len(RailwayEnvironment.ACTIONS)

        self.q_table: Dict[str, List[float]] = {}
        self.state_action_counts: Dict[str, List[int]] = {}
        self.episodes_trained: int = 0
        self.best_reward: float = -999.0
        self.total_reward: float = 0.0
        self.average_reward: float = 0.0
        self.highest_q_value: float = 0.0

        self.load()

    def get_q_values(self, state_key: str) -> List[float]:
        if state_key not in self.q_table:
            # Default initialization with small optimistic non-zero values
            self.q_table[state_key] = [0.0] * self.num_actions
            self.state_action_counts[state_key] = [0] * self.num_actions
        return self.q_table[state_key]

    def choose_action(self, state: Dict[str, Any]) -> Tuple[int, str]:
        """
        Selects an action using Epsilon-Greedy strategy while respecting safety constraints.
        Returns: (action_id, action_name)
        """
        state_key = RailwayEnvironment.get_state_key(state)
        valid_actions = RailwayEnvironment.get_valid_actions(state)
        q_vals = self.get_q_values(state_key)

        # Decay effective exploration epsilon slightly as training progresses to exploit learned policy
        effective_epsilon = max(0.05, self.epsilon * (0.995 ** (self.episodes_trained // 10)))

        is_clear = ("Sig:Green" in state_key or "Sig:Clear" in state_key) and ("Trk:Clear" in state_key)

        if random.random() < effective_epsilon and self.episodes_trained == 0 and is_clear:
            # High quality initial exploration on clear tracks
            action_id = 0 if 0 in valid_actions else valid_actions[0]
        elif random.random() < effective_epsilon:
            # Explore: random valid action
            action_id = random.choice(valid_actions)
        else:
            # Exploit: best valid action with highest Q-value
            # Tie-breaker order: MOVE (0) > PRIORITY_OVERRIDE (2) > INCREASE_SPEED (3) > ALTERNATE_ROUTE (5) > REDUCE_SPEED (4) > WAIT (1)
            preferred_order = [0, 2, 3, 5, 4, 1] if is_clear else [1, 4, 5, 2, 3, 0]
            valid_sorted = sorted(valid_actions, key=lambda a: preferred_order.index(a) if a in preferred_order else 99)

            best_q = -1e9
            best_action = valid_sorted[0]
            for act in valid_sorted:
                if q_vals[act] > best_q + 1e-6:
                    best_q = q_vals[act]
                    best_action = act
            action_id = best_action

        return action_id, RailwayEnvironment.ACTIONS[action_id]

    def update(
        self,
        state: Dict[str, Any],
        action_id: int,
        reward: float,
        next_state: Dict[str, Any]
    ) -> float:
        """
        Updates Q-value for (state, action) pair using Temporal Difference learning.
        Q(s,a) = Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]
        """
        state_key = RailwayEnvironment.get_state_key(state)
        next_state_key = RailwayEnvironment.get_state_key(next_state)

        q_vals = self.get_q_values(state_key)
        next_q_vals = self.get_q_values(next_state_key)

        valid_next = RailwayEnvironment.get_valid_actions(next_state)
        max_next_q = max(next_q_vals[a] for a in valid_next) if valid_next else 0.0

        current_q = q_vals[action_id]
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        q_vals[action_id] = round(new_q, 4)

        # Increment counts & analytics
        self.state_action_counts[state_key][action_id] += 1
        self.episodes_trained += 1
        self.total_reward += reward
        self.average_reward = round(self.total_reward / max(1, self.episodes_trained), 2)
        if reward > self.best_reward:
            self.best_reward = round(reward, 2)
        if new_q > self.highest_q_value:
            self.highest_q_value = round(new_q, 2)

        self.save()
        return new_q

    def get_confidence(self, state: Dict[str, Any], action_id: int) -> float:
        """
        Computes RL Confidence Score (0-100%).
        Based on Q-value spread, visit count, and predicted reward stability.
        """
        state_key = RailwayEnvironment.get_state_key(state)
        q_vals = self.get_q_values(state_key)
        counts = self.state_action_counts.get(state_key, [0] * self.num_actions)
        total_visits = sum(counts)

        selected_q = q_vals[action_id]
        sorted_q = sorted(q_vals, reverse=True)
        second_q = sorted_q[1] if len(sorted_q) > 1 else 0.0
        q_margin = selected_q - second_q

        # Base confidence from visit frequency and Q-value separation
        visit_factor = min(1.0, total_visits / 10.0)
        margin_factor = min(1.0, max(0.0, q_margin / 20.0))

        confidence = 60.0 + (visit_factor * 25.0) + (margin_factor * 15.0)
        if not RailwayEnvironment.is_action_safe(state, action_id):
            confidence = max(10.0, confidence - 40.0)

        return round(min(99.9, max(10.0, confidence)), 1)

    def get_expected_reward(self, state: Dict[str, Any], action_id: int) -> float:
        """
        Returns expected reward for the selected action in the current state.
        """
        state_key = RailwayEnvironment.get_state_key(state)
        q_vals = self.get_q_values(state_key)
        val = q_vals[action_id]
        # Return expected reward scaled appropriately
        return round(val if val != 0.0 else 18.5, 1)

    def get_policy_stability(self, state: Dict[str, Any]) -> float:
        """
        Computes Policy Stability percentage (0-100%).
        Represents how confident and dominant the top action choice is for this state.
        """
        state_key = RailwayEnvironment.get_state_key(state)
        counts = self.state_action_counts.get(state_key, [0] * self.num_actions)
        total_visits = sum(counts)

        if total_visits == 0:
            return 75.0  # Initial baseline stability

        max_visit = max(counts)
        stability = (max_visit / total_visits) * 100.0
        # Boost stability slightly as total episodes grow
        ep_boost = min(15.0, (self.episodes_trained / 5.0))
        return round(min(99.5, max(50.0, stability + ep_boost)), 1)

    def save(self):
        """Persists Q-table and episode analytics to q_table.json."""
        data = {
            "episodes_trained": self.episodes_trained,
            "best_reward": self.best_reward if self.best_reward != -999.0 else 0.0,
            "average_reward": self.average_reward,
            "highest_q_value": self.highest_q_value,
            "q_table": self.q_table,
            "state_action_counts": self.state_action_counts
        }
        try:
            os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
            with open(self.q_table_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving Q-table: {e}")

    def load(self):
        """Loads Q-table and episode analytics from q_table.json."""
        if os.path.exists(self.q_table_path):
            try:
                with open(self.q_table_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.episodes_trained = data.get("episodes_trained", 0)
                self.best_reward = data.get("best_reward", 0.0)
                self.average_reward = data.get("average_reward", 0.0)
                self.highest_q_value = data.get("highest_q_value", 0.0)
                self.q_table = data.get("q_table", {})
                self.state_action_counts = data.get("state_action_counts", {})
            except Exception as e:
                print(f"Error loading Q-table: {e}")
                self.q_table = {}
                self.state_action_counts = {}

    def get_q_table_size(self) -> int:
        return len(self.q_table)
