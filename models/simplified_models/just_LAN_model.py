from gurobipy import Model, GRB, quicksum


def create_LAD_model(customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_wvr, a_wrstar, E_u):
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

    # Time/capacity vars
    tau = {u.id: model.addVar(
        lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}

    # LA-route vars
    y = add_y_vars(model, customers, LA_routes)

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
    for u in customers:
        # Each customer serviced once, each customer left once
        model.addConstr(quicksum(
            x[u.id, v.id] for v in customers + [end_depot] if u != v) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum(x[v.id, u.id] for v in [start_depot] + customers
                                 if u != v) == 1, name=f"servicing_{u.id}")
        # One LA ordering is followed starting at each customer
        model.addConstr(quicksum(
            y[r] for r in LA_routes[u]) == 1, name=f"LA_route_from_{u.id}")

    # Y is consistent with X
    for u in customers:
        for (w, v) in E_u[u.id]:
            model.addConstr(quicksum(
                (y[r] * a_wvr[u.id, w.id, v.id, r]) for r in LA_routes[u]
            ) <= x[w.id, v.id], name=f"LA_route_{u.id}_with_{w.id}_{v.id}_is_in_x")

        for w in set(u.LA_neighbors) | {u}:
            model.addConstr(quicksum(x[w.id, v.id] for (w, v) in E_u[u.id]) >= quicksum(
                y[r] * a_wrstar[u.id, w.id, r] for r in LA_routes[u]), name=f"LA_route_{u.id}_ends_at_{w.id}_is_in_x")

    # Time/capacity windows/demands are met
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
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles")
    model.addConstr(quicksum(x[v.id, end_depot.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_in")

    return model


def create_relaxed_LAD_model(customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_k_wvr, a_k_wrstar, E_u):
    print("Buliding relaxed LA-Disc model.")
    model = Model("VRPTW")
    model.setParam('OutputFlag', 0)

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

    # Time/capacity vars
    tau = {u.id: model.addVar(
        lb=u.time_window_end, ub=u.time_window_start, name=f"tau_{u.id}") for u in customers}
    delta = {u.id: model.addVar(
        lb=u.demand, ub=capacity, name=f"delta_{u.id}") for u in customers}

    # LA-route vars
    y = add_y_vars(model, customers, LA_routes)

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
    for u in customers:
        # Each customer serviced once, each customer left once
        model.addConstr(quicksum(
            x[u.id, v.id] for v in customers + [end_depot] if u != v) == 1, name=f"leaving_{u.id}")
        model.addConstr(quicksum(x[v.id, u.id] for v in [start_depot] + customers
                                 if u != v) == 1, name=f"servicing_{u.id}")
        # One LA ordering is followed starting at each customer
        model.addConstr(quicksum(
            y[r] for r in LA_routes[u]) == 1, name=f"LA_route_from_{u.id}")

    # Y is consistent with X
    constr8a_count = 0
    constr8b_count = 0
    epsilon = 1e-5
    for u in customers:
        # Add the new constraints (8a) and (8b)
        for k in range(1, len(u.LA_neighbors) + 1):
            N_k_u = u.LA_neighbors[:k]  # The k closest LA-neighbors
            N_k_plus_u = N_k_u + [u]

            for w in N_k_plus_u:
                for v in (set(N_k_u) - {w}):
                    if (w, v) in E_u[u.id]:
                        lhs_8a = epsilon * k + x[w.id, v.id]
                        rhs_8a = quicksum(y[r] * a_k_wvr[u.id, k, w.id, v.id, r]
                                          for r in LA_routes[u])
                        model.addConstr(lhs_8a >= rhs_8a,
                                        name=f"LA_route_{u.id}_{w.id}_{v.id}_{k}")
                        constr8a_count += 1
                lhs_8b = epsilon * k + \
                    quicksum(x[w.id, v.id]
                             for v in N_k_plus_u if (w, v) in E_u[u.id])
                rhs_8b = quicksum(y[r] * a_k_wrstar[u.id, k, w.id, r]
                                  for r in LA_routes[u])
                model.addConstr(lhs_8b >= rhs_8b,
                                name=f"LA_route_end_{u.id}_{w.id}_{k}")
                constr8b_count += 1

    # Time/capacity windows/demands are met
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
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles")
    model.addConstr(quicksum(x[v.id, end_depot.id] for v in customers) >= (
        sum(customer.demand for customer in customers) / capacity), name="min_vehicles_in")

    return model, x, y


def add_y_vars(model, customers, LA_routes):
    y = {}
    for u in customers:
        for r in LA_routes[u]:
            y_var_name = "y"
            for c in r.visits:
                y_var_name += f"_{c.id}"
            y[r] = model.addVar(vtype=GRB.CONTINUOUS, name=y_var_name)

    return y


def get_customer_by_id(id, customers_by_id, start_depot, end_depot):
    if id == start_depot.id:
        return start_depot
    if id == end_depot.id:
        return end_depot
    return customers_by_id[id]
