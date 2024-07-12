from gurobipy import Model, GRB, quicksum


def create_cti_model(customers, start_depot, end_depot, capacity):
    model = Model("VRPTW")

    # Variables
    x = {}
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v:
                x[u.id, v.id] = model.addVar(
                    vtype=GRB.BINARY, name=f"x_{u.id}_{v.id}")

    tau = {u.id: model.addVar(
        lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}

    # Objective
    model.setObjective(quicksum(u.cost[v.index] * x[u.id, v.id] for u in [start_depot] + customers for v in customers + [
                       end_depot] if u != v and (u != start_depot or v != end_depot)), GRB.MINIMIZE)

    # Constraints
    # Each customer serviced once, each customer left once
    for u in customers:
        model.addConstr(quicksum(
            x[u.id, v.id] for v in customers + [end_depot] if u != v) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum(x[v.id, u.id] for v in [
                        start_depot] + customers if u != v) == 1, name=f"servicing_{u}")

    # Time/capacity windows/demands are met
    for u in customers:
        for v in customers:
            if u != v:
                model.addConstr(delta[v.id] >= delta[u.id] + v.demand - (
                    (capacity + v.demand) * (1 - x[v.id, u.id])), name=f"capacity_{u.id}_{v.id}")
                model.addConstr(tau[v.id] >= tau[u.id] + v.travel_time[u.index] - (
                    (u.time_window_start + v.travel_time[u.index]) * (1 - x[v.id, u.id])), name=f"time_{u.id}_{v.id}")

    # Enforce at least minimum number of vehicles are used
    model.addConstr(quicksum(x[start_depot.id, v.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles")

    return model
