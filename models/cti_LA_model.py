from gurobipy import Model, GRB, quicksum


def create_LA_model(customers, start_depot, end_depot, capacity, LA_routes):
    model = Model("VRPTW")

    # Variables
    x = {}
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v:
                x[u.id, v.id] = model.addVar(
                    vtype=GRB.BINARY, name=f"x_{u.id}_{v.id}")

    # Time/capacity vars
    tau = {u.id: model.addVar(
        lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}
    # LA-route vars
    y = {}
    for u in customers:
        for r in LA_routes[u]:
            y_var_name = "y"
            for c in r.visits:
                y_var_name += f"_{c.id}"
            y[r] = model.addVar(vtype=GRB.BINARY, name=y_var_name)

    # Objective
    model.setObjective(quicksum(u.cost[v.index] * x[u.id, v.id] for u in [start_depot] + customers for v in customers + [
                       end_depot] if u != v and (u != start_depot or v != end_depot)), GRB.MINIMIZE)

    # Constraints
    # Each customer serviced once, each customer left once
    for u in customers:
        model.addConstr(quicksum(
            x[u.id, v.id] for v in customers + [end_depot] if u != v) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum(x[v.id, u.id] for v in [start_depot] + customers
                                 if u != v) == 1, name=f"servicing_{u.id}")
        # One LA ordering is followed starting at each customer
        model.addConstr(quicksum(
            y[r] for r in LA_routes[u]) == 1, name=f"LA_route_from_{u.id}")

    # Y is consistent with X
    for u in customers:
        E_u = set()
        a_wvr = {}
        a_wr = {}
        for w in u.LA_neighbors | {u}:
            for v in u.LA_neighbors - {w}:
                E_u.add((w, v))
        for r in LA_routes[u]:
            for w, v in E_u:
                if w in r.visits:
                    v_index = r.visits.index(w) + 1
                    if v_index < len(r.visits):
                        a_wr[w.id, r] = 0
                        if r.visits[v_index] == v:
                            a_wvr[w.id, v.id, r] = 1
                        else:
                            a_wvr[w.id, v.id, r] = 0
                    else:
                        a_wr[w.id, r] = 1
                        a_wvr[w.id, v.id, r] = 0
                else:
                    a_wr[w.id, r] = 0
                    a_wvr[w.id, v.id, r] = 0
        for w, v in E_u:
            model.addConstr(quicksum(
                (y[r] * a_wvr[w.id, v.id, r]) for r in LA_routes[u]
            ) <= x[w.id, v.id], name=f"LA_route_{u.id}_with_{w.id}_{v.id}_is_in_x")

        for w in u.LA_neighbors | {u}:
            model.addConstr(quicksum(x[w.id, v.id] for w, v in E_u) >= quicksum(
                y[r] * a_wr[w.id, r] for r in LA_routes[u]), name=f"LA_route_{u.id}_ends_at_{w.id}_is_in_x")

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
