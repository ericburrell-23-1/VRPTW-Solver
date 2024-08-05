from gurobipy import Model, GRB, quicksum


def create_cti_model(customers, start_depot, end_depot, capacity):
    model = Model("VRPTW")

    customers_by_id = {}
    for c in customers:
        customers_by_id[c.id] = c

    # Variables
    x = {}
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                x[u.id, v.id] = model.addVar(
                    vtype=GRB.BINARY, name=f"x_{u.id}_{v.id}")

    tau = {u.id: model.addVar(
        vtype=GRB.CONTINUOUS, lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        vtype=GRB.CONTINUOUS, lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}

    # Objective
    cost_terms = []
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                new_term = (u.cost[v.index]) * x[u.id, v.id]
                cost_terms.append(new_term)
    model.setObjective(quicksum(cost_terms) -
                       (customers[0].service_time * len(customers)), GRB.MINIMIZE)

    # Constraints
    # Each customer serviced once, each customer left once
    for u in customers:
        model.addConstr(quicksum(
            [x[u.id, v.id] for v in customers + [end_depot] if u != v]) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum([x[v.id, u.id] for v in [
                        start_depot] + customers if u != v]) == 1, name=f"servicing_{u.id}")

    # Time/Capacity constraints
    for v_id, u_id in x:
        v = get_customer_by_id(v_id, customers_by_id, start_depot, end_depot)
        u = get_customer_by_id(u_id, customers_by_id, start_depot, end_depot)
        if u != end_depot and v != start_depot:
            model.addConstr(delta[v_id] - v.demand >= delta[u_id] - (
                (capacity + v.demand) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(tau[v_id] - v.travel_time[u.index] >= tau[u_id] - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")
        elif u == end_depot:
            model.addConstr(delta[v_id] - v.demand >= 0 - (
                (capacity + v.demand) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(tau[v_id] - v.travel_time[u.index] >= 0 - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")
        elif v == start_depot:
            model.addConstr(capacity >= delta[u_id] - (
                (capacity) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(v.time_window_start - v.travel_time[u.index] >= tau[u_id] - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")

    # Enforce at least minimum number of vehicles are used
    model.addConstr(quicksum(x[start_depot.id, v.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_out")
    model.addConstr(quicksum(x[v.id, end_depot.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_in")

    return model


def create_relaxed_cti_model(customers, start_depot, end_depot, capacity):
    model = Model("VRPTW")

    customers_by_id = {}
    for c in customers:
        customers_by_id[c.id] = c

    # Variables
    x = {}
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                x[u.id, v.id] = model.addVar(
                    vtype=GRB.CONTINUOUS, name=f"x_{u.id}_{v.id}")

    tau = {u.id: model.addVar(
        vtype=GRB.CONTINUOUS, lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        vtype=GRB.CONTINUOUS, lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}

    # Objective
    cost_terms = []
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                new_term = (u.cost[v.index]) * x[u.id, v.id]
                cost_terms.append(new_term)
    model.setObjective(quicksum(cost_terms) -
                       (customers[0].service_time * len(customers)), GRB.MINIMIZE)

    # Constraints
    # Each customer serviced once, each customer left once
    for u in customers:
        model.addConstr(quicksum(
            [x[u.id, v.id] for v in customers + [end_depot] if u != v]) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum([x[v.id, u.id] for v in [
                        start_depot] + customers if u != v]) == 1, name=f"servicing_{u.id}")

    # Time/Capacity constraints
    for v_id, u_id in x:
        v = get_customer_by_id(v_id, customers_by_id, start_depot, end_depot)
        u = get_customer_by_id(u_id, customers_by_id, start_depot, end_depot)
        if u != end_depot and v != start_depot:
            model.addConstr(delta[v_id] - v.demand >= delta[u_id] - (
                (capacity + v.demand) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(tau[v_id] - v.travel_time[u.index] >= tau[u_id] - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")
        elif u == end_depot:
            model.addConstr(delta[v_id] - v.demand >= 0 - (
                (capacity + v.demand) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(tau[v_id] - v.travel_time[u.index] >= 0 - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")
        elif v == start_depot:
            model.addConstr(capacity >= delta[u_id] - (
                (capacity) * (1 - x[v_id, u_id])), name=f"capacity_{v.id}_{u.id}")
            model.addConstr(v.time_window_start - v.travel_time[u.index] >= tau[u_id] - (
                (u.time_window_start + v.travel_time[u.index]) * (1 - x[v_id, u_id])), name=f"time_{v_id}_{u_id}")

    # Enforce at least minimum number of vehicles are used
    model.addConstr(quicksum(x[start_depot.id, v.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_out")
    model.addConstr(quicksum(x[v.id, end_depot.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_in")

    return model


def get_customer_by_id(id, customers_by_id, start_depot, end_depot):
    if id == start_depot.id:
        return start_depot
    if id == end_depot.id:
        return end_depot
    return customers_by_id[id]
