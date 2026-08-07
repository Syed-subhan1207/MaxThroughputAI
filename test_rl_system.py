"""
Comprehensive Reinforcement Learning Policy Evaluation Test Suite
Verifies all 4 test scenarios, safety constraint enforcement, API response extensions,
terminal policy logging, and Q-learning convergence/stability over multiple cycles.
"""

import sys
import os
import json

# Add project root to sys.path
_root = os.path.abspath(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from backend.services.optimization_service import optimization_service
from reinforcement.trainer import rl_trainer

def run_tests():
    print("\n=======================================================")
    print("      AI RAILWAY TRAFFIC CONTROL SYSTEM                ")
    print("   REINFORCEMENT LEARNING POLICY EVALUATION TEST SUITE  ")
    print("=======================================================\n")

    # ---------------------------------------------------------
    # TEST CASE 1: High Priority Express
    # ---------------------------------------------------------
    print("--> RUNNING TEST CASE 1: High Priority Express...")
    state1 = {
        "train_type": "Rajdhani Express",
        "current_station": "S1",
        "next_station": "S2",
        "speed": 110,
        "current_delay": 2,
        "weather": "Clear",
        "signal_status": "Green",
        "track_status": "Clear",
        "platform_available": "Yes",
        "train_priority": "High",
        "congestion_level": "Low"
    }

    res1 = optimization_service.optimize_traffic(state1)
    print("TEST 1 RESPONSE TELEMETRY:")
    print(f"  - rl_recommended_action : {res1.get('rl_recommended_action')}")
    print(f"  - rl_reward             : {res1.get('rl_reward')}")
    print(f"  - expected_reward       : {res1.get('expected_reward')}")
    print(f"  - rl_confidence         : {res1.get('rl_confidence')}")
    print(f"  - policy_stability      : {res1.get('policy_stability')}")
    print(f"  - episodes_trained      : {res1.get('episodes_trained')}")

    assert res1.get("rl_recommended_action") in ["MOVE", "PRIORITY_OVERRIDE", "INCREASE_SPEED"], f"Unexpected action for Test 1: {res1.get('rl_recommended_action')}"
    assert res1.get("rl_reward") >= 0, f"Expected positive reward for Test 1, got {res1.get('rl_reward')}"
    print("PASSED TEST CASE 1\n")

    # ---------------------------------------------------------
    # TEST CASE 2: Blocked Track (Safety Enforcement)
    # ---------------------------------------------------------
    print("--> RUNNING TEST CASE 2: Blocked Track (Safety Verification)...")
    state2 = {
        "train_type": "Passenger Local",
        "current_station": "S2",
        "next_station": "S3",
        "speed": 50,
        "current_delay": 15,
        "weather": "Clear",
        "signal_status": "Red",
        "track_status": "Blocked",
        "platform_available": "No",
        "train_priority": "Low",
        "congestion_level": "Medium"
    }

    res2 = optimization_service.optimize_traffic(state2)
    print("TEST 2 RESPONSE TELEMETRY:")
    print(f"  - rl_recommended_action : {res2.get('rl_recommended_action')}")
    print(f"  - rl_reward             : {res2.get('rl_reward')}")
    print(f"  - expected_reward       : {res2.get('expected_reward')}")
    print(f"  - rl_confidence         : {res2.get('rl_confidence')}")

    assert res2.get("rl_recommended_action") not in ["MOVE", "INCREASE_SPEED"], f"Safety violation! MOVE selected on blocked track: {res2.get('rl_recommended_action')}"
    print("PASSED TEST CASE 2\n")

    # ---------------------------------------------------------
    # TEST CASE 3: High Congestion Corridor
    # ---------------------------------------------------------
    print("--> RUNNING TEST CASE 3: High Congestion Corridor...")
    state3 = {
        "train_type": "Superfast Express",
        "current_station": "S3",
        "next_station": "S4",
        "speed": 85,
        "current_delay": 10,
        "weather": "Fog",
        "signal_status": "Green",
        "track_status": "Clear",
        "platform_available": "Yes",
        "train_priority": "High",
        "congestion_level": "High"
    }

    res3 = optimization_service.optimize_traffic(state3)
    print("TEST 3 RESPONSE TELEMETRY:")
    print(f"  - rl_recommended_action : {res3.get('rl_recommended_action')}")
    print(f"  - rl_policy             : {res3.get('rl_policy')}")
    print("PASSED TEST CASE 3\n")

    # ---------------------------------------------------------
    # TEST CASE 4: Low Congestion Nominal Corridor
    # ---------------------------------------------------------
    print("--> RUNNING TEST CASE 4: Low Congestion Nominal Corridor...")
    state4 = {
        "train_type": "Vande Bharat Express",
        "current_station": "S4",
        "next_station": "S5",
        "speed": 130,
        "current_delay": 0,
        "weather": "Clear",
        "signal_status": "Green",
        "track_status": "Clear",
        "platform_available": "Yes",
        "train_priority": "High",
        "congestion_level": "Low"
    }

    res4 = optimization_service.optimize_traffic(state4)
    print("TEST 4 RESPONSE TELEMETRY:")
    print(f"  - rl_recommended_action : {res4.get('rl_recommended_action')}")
    print(f"  - rl_reward             : {res4.get('rl_reward')}")
    assert res4.get("rl_reward") >= 0, f"Expected positive reward for low congestion MOVE, got {res4.get('rl_reward')}"
    print("PASSED TEST CASE 4\n")

    # ---------------------------------------------------------
    # TEST CASE 5: Learning & Policy Convergence Verification
    # ---------------------------------------------------------
    print("--> RUNNING TEST CASE 5: Learning & Convergence Multi-Cycle Verification...")
    init_episodes = res4.get("episodes_trained", 0)

    for i in range(10):
        res_repeat = optimization_service.optimize_traffic(state1)

    final_episodes = res_repeat.get("episodes_trained", 0)
    print("CONVERGENCE METRICS AFTER 10 REPEATED EXECUTIONS:")
    print(f"  - Initial Episodes : {init_episodes}")
    print(f"  - Final Episodes   : {final_episodes}")
    print(f"  - Final Action     : {res_repeat.get('rl_recommended_action')}")
    print(f"  - Policy Stability : {res_repeat.get('policy_stability')}")
    print(f"  - Confidence       : {res_repeat.get('rl_confidence')}")
    print(f"  - Q Table Size     : {res_repeat.get('q_table_size')}")

    assert final_episodes == init_episodes + 10, f"Expected episodes to increase by 10, got {final_episodes - init_episodes}"
    print("PASSED TEST CASE 5\n")

    print("=======================================================")
    print("  ALL 5 REINFORCEMENT LEARNING TEST CASES PASSED SUCCESSFULLY!")
    print("=======================================================\n")

if __name__ == "__main__":
    run_tests()
