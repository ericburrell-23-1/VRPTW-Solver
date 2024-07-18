
class Ordering:
    def __init__(self, visits: list):
        self.visits = visits
        self.earliest_departure = earliest_departure(visits)
        self.latest_departure = latest_departure(visits)
        self.cost = cost(visits)

    def __repr__(self):
        return f"Ordering({self.visits})"

    def __eq__(self, other):
        if isinstance(other, Ordering):
            return len(self.visits) == len(other.visits) and all(a.id == b.id for a, b in zip(self.visits, other.visits))
        return False

    def __hash__(self):
        return hash(tuple(c.id for c in self.visits))


def earliest_departure(visits):
    if len(visits) == 1:
        return visits[0].time_window_start
    if len(visits) == 2:
        return min([visits[0].time_window_start, (visits[1].time_window_start + visits[0].travel_time[visits[1].index])])
    else:
        r_minus_visits = visits[1:]
        return min([visits[0].time_window_start, (earliest_departure(r_minus_visits) + visits[0].travel_time[visits[1].index])])


def latest_departure(visits):
    if len(visits) == 1:
        return visits[0].time_window_end
    if len(visits) == 2:
        return max([visits[0].time_window_end, (visits[1].time_window_end + visits[0].travel_time[visits[1].index])])
    else:
        r_minus_visits = visits[1:]
        return max([visits[0].time_window_end, (latest_departure(r_minus_visits) + visits[0].travel_time[visits[1].index])])


def cost(visits):
    total_cost = 0
    for i in range(0, len(visits) - 1):
        total_cost += visits[i].cost[visits[i + 1].index]

    return total_cost
