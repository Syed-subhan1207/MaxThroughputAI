import time
from ortools.sat.python import cp_model
from optimization.constraints import Constraints
from optimization.conflict_detector import ConflictDetector


class RailwayOptimizer:

    def optimize(self, trains):
        start_time = time.time()
        model = cp_model.CpModel()

        move = {}
        decisions = {}

        # -----------------------------
        # Decision Variables
        # -----------------------------
        for train in trains:
            move[train.train_id] = model.NewBoolVar(train.train_id)

        # -----------------------------
        # Safety & Feasibility Constraints
        # -----------------------------
        for train in trains:
            if not Constraints.can_move(train):
                model.Add(move[train.train_id] == 0)

        # -----------------------------
        # Track Occupancy Constraints
        # (Trains on same track section cannot both move if track is congested/single)
        # -----------------------------
        track_conflicts = ConflictDetector.detect_track_conflicts(trains)
        for t1, t2, _ in track_conflicts:
            if t1.train_id in move and t2.train_id in move:
                # Limit simultaneous track movement
                model.Add(move[t1.train_id] + move[t2.train_id] <= 1)

        # -----------------------------
        # Priority Mapping
        # -----------------------------
        priority_weights = {
            "High": 5,
            "Medium": 3,
            "Low": 1
        }

        # -----------------------------
        # Objective Function
        # -----------------------------
        objective = []

        for train in trains:
            priority = priority_weights.get(getattr(train, 'priority', 'Medium'), 2)
            current_delay = int(getattr(train, 'current_delay', 0))
            predicted_delay = int(getattr(train, 'predicted_delay', 0))
            congestion = 3 if getattr(train, 'congestion_level', 'Low') == "High" else 1

            # High weight on priority, delay recovery, and high throughput
            score = (
                priority * 40
                + current_delay * 20
                + predicted_delay * 3
                - congestion * 5
            )

            objective.append(
                score * move[train.train_id]
            )

        model.Maximize(sum(objective))

        # -----------------------------
        # Solve with CP-SAT Solver
        # -----------------------------
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 2.0
        status = solver.Solve(model)
        end_time = time.time()

        solve_time_ms = round((end_time - start_time) * 1000, 2)
        moved = 0
        waiting = 0

        status_map = {
            cp_model.OPTIMAL: "OPTIMAL",
            cp_model.FEASIBLE: "FEASIBLE",
            cp_model.INFEASIBLE: "INFEASIBLE",
            cp_model.MODEL_INVALID: "MODEL_INVALID",
            cp_model.UNKNOWN: "UNKNOWN"
        }
        status_name = status_map.get(status, "UNKNOWN")

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            for train in trains:
                if solver.Value(move[train.train_id]) == 1:
                    decisions[train.train_id] = "MOVE"
                    train.status = "MOVING"
                    moved += 1
                else:
                    decisions[train.train_id] = "WAIT"
                    train.status = "WAITING"
                    waiting += 1
            objective_value = float(solver.ObjectiveValue())
        else:
            for train in trains:
                decisions[train.train_id] = "WAIT"
                train.status = "WAITING"
                waiting += 1
            objective_value = 0.0

        total = len(trains)
        throughput = round((moved / total * 100) if total > 0 else 0.0, 1)

        print("\n========== Google OR-Tools CP-SAT Optimization Summary ==========")
        print(f"Solver Status   : {status_name}")
        print(f"Objective Value : {objective_value}")
        print(f"Solve Time      : {solve_time_ms} ms")
        print(f"Total Trains    : {total}")
        print(f"Moved           : {moved}")
        print(f"Waiting         : {waiting}")
        print(f"Throughput      : {throughput}%")
        print("=================================================================\n")

        return {
            "decisions": decisions,
            "total_trains": total,
            "moved_trains": moved,
            "waiting_trains": waiting,
            "throughput_percentage": throughput,
            "solver_status": status_name,
            "objective_value": objective_value,
            "solve_time_ms": solve_time_ms
        }

