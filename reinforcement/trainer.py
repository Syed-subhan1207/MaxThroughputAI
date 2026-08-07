"""
RL Trainer Module for Reinforcement Learning Policy Evaluation
Orchestrates state observation, action recommendation, reward evaluation, Q-table updates,
and terminal policy summary logging.
"""

from typing import Dict, Any
from reinforcement.environment import RailwayEnvironment
from reinforcement.reward import RewardCalculator
from reinforcement.rl_agent import QLearningAgent

class RLTrainer:
    def __init__(self):
        self.agent = QLearningAgent()

    def train_cycle(self, state: Dict[str, Any], opt_results: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes one complete RL policy evaluation and Q-learning update step.
        """
        opt_results = opt_results or {}
        
        # 1. State observation
        state_key = RailwayEnvironment.get_state_key(state)

        # 2. Chosen Action from Q-agent
        action_id, action_name = self.agent.choose_action(state)

        # 3. Next State simulation
        next_state = RailwayEnvironment.get_next_state(state, action_id)

        # 4. Reward evaluation
        reward = RewardCalculator.calculate_reward(state, action_name, next_state, opt_results)

        # 5. Update Q-table & persist analytics
        self.agent.update(state, action_id, reward, next_state)

        # 6. Compute analytical metrics
        confidence = self.agent.get_confidence(state, action_id)
        exp_reward = self.agent.get_expected_reward(state, action_id)
        stability = self.agent.get_policy_stability(state)
        q_table_size = self.agent.get_q_table_size()
        episodes = self.agent.episodes_trained

        # Determine readable policy description
        if action_name == "MOVE":
            policy_desc = "NOMINAL_DISPATCH_EXPLOITATION"
        elif action_name == "WAIT":
            policy_desc = "HOLD_SAFETY_CLEARANCE"
        elif action_name == "PRIORITY_OVERRIDE":
            policy_desc = "PRIORITY_EXPRESS_OVERRIDE"
        elif action_name == "INCREASE_SPEED":
            policy_desc = "SPEED_ACCELERATION_POLICY"
        elif action_name == "REDUCE_SPEED":
            policy_desc = "SPEED_MODULATION_CAUTION"
        elif action_name == "ALTERNATE_ROUTE":
            policy_desc = "DYNAMIC_REROUTING_POLICY"
        else:
            policy_desc = "OPTIMAL_Q_POLICY"

        # 7. Print Terminal Policy Summary Log
        print("\n========== RL POLICY SUMMARY ==========")
        print(f"State            : {state_key}")
        print(f"Chosen Action    : {action_name}")
        print(f"Expected Reward  : {exp_reward:+}")
        print(f"Confidence       : {confidence}%")
        print(f"Policy Stability : {stability}%")
        print(f"Episodes         : {episodes}")
        print(f"Q Table Size     : {q_table_size}")
        print("======================================\n")

        return {
            "rl_action": action_name,
            "rl_recommended_action": action_name,
            "rl_reward": reward,
            "expected_reward": f"{exp_reward:+}",
            "expected_reward_val": exp_reward,
            "rl_policy": policy_desc,
            "rl_confidence": f"{confidence}%",
            "rl_confidence_val": confidence,
            "policy_stability": f"{stability}%",
            "policy_stability_val": stability,
            "episodes_trained": episodes,
            "learning_rate": self.agent.learning_rate,
            "epsilon": self.agent.epsilon,
            "q_table_size": q_table_size
        }

# Global singleton trainer instance
rl_trainer = RLTrainer()
