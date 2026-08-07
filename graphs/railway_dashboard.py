import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class RailwayDashboard:

    def __init__(self, decisions):

        # Load Phase 1 clean dataset
        import os
        csv_path = "data/processed_CSV/clean_trains.csv" if os.path.exists("data/processed_CSV/clean_trains.csv") else "data/railway_data.csv"
        self.data = pd.read_csv(csv_path)
        if "timestamp" in self.data.columns:
            self.data["timestamp"] = pd.to_datetime(self.data["timestamp"])
            self.times = sorted(self.data["timestamp"].unique())
        else:
            self.data["timestamp"] = pd.to_datetime("2026-08-07 08:00:00")
            self.times = [pd.to_datetime("2026-08-07 08:00:00")]
        self.decisions = decisions or {}
        # Station coordinates
        self.pos = {
            "S1": (1, 3),
            "S2": (3, 3),
            "S3": (5, 5),
            "S4": (8, 5),
            "S5": (6, 2),
            "S6": (11, 5),
            "S7": (10, 0)
        }

        # Railway tracks
        self.tracks = [
            ("S1", "S2"),
            ("S2", "S3"),
            ("S2", "S5"),
            ("S3", "S4"),
            ("S5", "S4"),
            ("S4", "S6"),
            ("S5", "S7")
        ]

        self.fig, self.ax = plt.subplots(figsize=(13, 7))

    # -------------------------------------------------

    def draw_map(self):

        self.ax.clear()

        # Default all tracks to green
    

        # Draw Tracks
        # Draw Tracks
        for start, end in self.tracks:

            x1, y1 = self.pos[start]
            x2, y2 = self.pos[end]

            self.ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                lw=4,
                color="black",
                mutation_scale=25,
                shrinkA=18,
                shrinkB=18
            )
        )

        # Draw Stations
        for station, (x, y) in self.pos.items():

            circle = plt.Circle(
                (x, y),
                0.35,
                color="skyblue",
                ec="black",
                zorder=3
            )

            self.ax.add_patch(circle)

            self.ax.text(
                x,
                y,
                station,
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold"
            )

        self.ax.set_xlim(0, 13)
        self.ax.set_ylim(-1, 6)

        self.ax.set_aspect("equal")

        self.ax.axis("off")

        self.ax.set_title(
            "AI Railway Traffic Control Dashboard",
            fontsize=20,
            fontweight="bold"
        )

    # -------------------------------------------------
    
    

    def animate(self, frame):

        self.draw_map()

        # -------------------------------
        # Simulation Time
        # -------------------------------

        current_time = self.times[(frame // 80) % len(self.times)]

        self.ax.text(
            9,
            5.2,
            f"Simulation Time\n{current_time.strftime('%H:%M')}",
            fontsize=12,
            weight="bold",
            bbox=dict(facecolor="lightyellow")
        )

        # -------------------------------
        # Active Trains
        # -------------------------------

        active_trains = self.data[
            self.data["timestamp"] == current_time
        ]

        

        colors = [
            "red",
            "blue",
            "purple",
            "orange",
            "green",
            "brown",
            "pink"
        ]

        for i, (_, row) in enumerate(active_trains.iterrows()):

            start = row["current_station"]
            end = row["next_station"]
            decision = self.decisions.get(
                row["train_id"],
                "WAIT"
            )

            if decision == "MOVE":
                progress = (frame % 80) / 80
            else:
                progress = 0

            x1, y1 = self.pos[start]
            x2, y2 = self.pos[end]

            x = x1 + (x2 - x1) * progress
            y = y1 + (y2 - y1) * progress

            self.ax.scatter(
                x,
                y,
                s=170,
                color = "red" if decision == "MOVE" else "orange",
                edgecolors="black",
                zorder=5
            )

            self.ax.text(
                x,
                y + 0.22,
                row["train_id"],
                fontsize=8,
                ha="center"
            )

        # -------------------------------
        # Dashboard (only if at least one train exists)
        # -------------------------------

        if len(active_trains) > 0:

            row = active_trains.iloc[0]

            decision = self.decisions.get(
                row["train_id"],
                "WAIT"
            )

            decision_colors = {
                "MOVE": "green",
                "WAIT": "orange",
                "STOP": "red",
                "SLOW": "purple",
                "PRIORITIZE": "blue"
            }

            panel = (
                f"Train ID : {row['train_id']}\n\n"
                f"Route : {row['current_station']} → {row['next_station']}\n\n"
                f"Speed : {row['speed_kmph']} km/h\n\n"
                f"Delay : {row['current_delay_min']} min\n\n"
                f"Priority : {row['train_priority']}\n\n"
                f"Decision : {decision}"
            )

            self.ax.text(
                8.9,
                0.4,
                panel,
                fontsize=11,
                bbox=dict(
                    facecolor="white",
                    edgecolor="black",
                    boxstyle="round,pad=0.5"
                )
            )

            self.ax.text(
                10.1,
                -0.45,
                decision,
                fontsize=14,
                fontweight="bold",
                color=decision_colors[decision]
            )

    # -------------------------------------------------

    def run(self):

        self.animation = FuncAnimation(
            self.fig,
            self.animate,
            frames=100000,
            interval=60,
            repeat=True
        )

        plt.show()


if __name__ == "__main__":

    dashboard = RailwayDashboard()
    dashboard.run()