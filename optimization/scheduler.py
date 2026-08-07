class RailwayScheduler:

    @staticmethod
    def generate_schedule(trains, decisions):

        movable = []

        for train in trains:

            if decisions.get(train.train_id) == "MOVE":

                movable.append(train)

        priority = {
            "High": 3,
            "Medium": 2,
            "Low": 1
        }

        movable.sort(

            key=lambda t: (

                priority.get(t.priority, 1),
                t.current_delay

            ),

            reverse=True

        )

        return movable
