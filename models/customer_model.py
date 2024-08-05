class Customer:
    def __init__(self, id, cost: list, demand, travel_time: list, time_window_start, time_window_end, service_time, index):
        self.id = id
        self.cost = cost
        self.demand = demand
        self.travel_time = travel_time
        self.time_window_start = time_window_start
        self.time_window_end = time_window_end
        self.service_time = service_time
        self.index = index
        self.LA_neighbors = []
        self.all_LA_neighbors = []

    def __repr__(self):
        return f"Cutomer({self.id}, {self.cost}, {self.demand}, {self.travel_time}, {self.time_window_start}, {self.time_window_end}, {self.index})"

    def __eq__(self, other):
        if isinstance(other, Customer):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
