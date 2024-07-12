class Customer:
    def __init__(self, id, cost, demand, travel_time, time_window_start, time_window_end, index):
        self.id = id
        self.cost = cost
        self.demand = demand
        self.travel_time = travel_time
        self.time_window_start = time_window_start
        self.time_window_end = time_window_end
        self.index = index
