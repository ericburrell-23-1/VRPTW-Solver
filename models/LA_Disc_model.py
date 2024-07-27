from gurobipy import Model, GRB, quicksum


def create_LAD_model(customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_wvr, a_wrstar, E_u):
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

    # Resource vars
    z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t)

    # Objective
    model.setObjective(quicksum(u.cost[v.index] * x[u.id, v.id] for u in [start_depot] + customers for v in customers + [
                       end_depot] if u != v and (u != start_depot or v != end_depot)), GRB.MINIMIZE)

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
        for w, v in E_u[u.id]:
            model.addConstr(quicksum(
                (y[r] * a_wvr[u.id, w.id, v.id, r]) for r in LA_routes[u]
            ) <= x[w.id, v.id], name=f"LA_route_{u.id}_with_{w.id}_{v.id}_is_in_x")

        for w in set(u.LA_neighbors) | {u}:
            model.addConstr(quicksum(x[w.id, v.id] for w, v in E_u[u.id]) >= quicksum(
                y[r] * a_wrstar[u.id, w.id, r] for r in LA_routes[u]), name=f"LA_route_{u.id}_ends_at_{w.id}_is_in_x")

    # Discrete time/capacity flow graphs (Z)
    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

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


def create_relaxed_LAD_model(customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_k_wvr, a_k_wrstar, E_u):
    model = Model("VRPTW")

    # Variables
    x = {}
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v:
                x[u.id, v.id] = model.addVar(
                    vtype=GRB.CONTINUOUS, name=f"x_{u.id}_{v.id}")

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
            y[r] = model.addVar(vtype=GRB.CONTINUOUS, name=y_var_name)

    # Resource vars
    z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t)

    # Objective
    model.setObjective(quicksum(u.cost[v.index] * x[u.id, v.id] for u in [start_depot] + customers for v in customers + [
                       end_depot] if u != v and (u != start_depot or v != end_depot)), GRB.MINIMIZE)

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
                lhs_8b = epsilon * k + \
                    quicksum(x[w.id, v.id]
                             for v in N_k_plus_u if (w, v) in E_u[u.id])
                rhs_8b = quicksum(y[r] * a_k_wrstar[u.id, k, w.id, r]
                                  for r in LA_routes[u])
                model.addConstr(lhs_8b >= rhs_8b,
                                name=f"LA_route_end_{u.id}_{w.id}_{k}")

    # Discrete time/capacity flow graphs (Z)
    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

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

    return model, x, y, z_d, z_t


def add_z_vars(model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t):
    G_d_u = {}
    for u in customers + [start_depot, end_depot]:
        G_d_u[u.id] = [G_d[(u.id, k)] for (u_key, k) in G_d if u_key == u.id]

    z_d = {}
    z_d_next_nodes = {i: [] for i in G_d.values()}
    z_d_prev_nodes = {i: [] for i in G_d.values()}
    for i in G_d.values():
        for j in G_d.values():
            if (i, j) in E_d:
                z_d[i.name, j.name] = model.addVar(
                    name=f"z_d_{i.name}_{j.name}")
                z_d_next_nodes[i].append(j)
                z_d_prev_nodes[j].append(i)

    G_t_u = {}
    for u in customers + [start_depot, end_depot]:
        G_t_u[u.id] = [G_t[(u.id, k)] for (u_key, k) in G_t if u_key == u.id]

    z_t = {}
    z_t_next_nodes = {i: [] for i in G_t.values()}
    z_t_prev_nodes = {i: [] for i in G_t.values()}
    for i in G_t.values():
        for j in G_t.values():
            if (i, j) in E_t:
                z_t[i.name, j.name] = model.addVar(
                    name=f"z_t_{i.name}_{j.name}")
                z_t_next_nodes[i].append(j)
                z_t_prev_nodes[j].append(i)

    return z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u


def add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t, G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes):
    # Flow conservation
    for i in G_d.values():
        if i.u.id not in {start_depot.id, end_depot.id}:
            model.addConstr(quicksum(z_d[i.name, j.name] for j in z_d_next_nodes[i]) ==
                            quicksum(z_d[j.name, i.name] for j in z_d_prev_nodes[i]), name=f"cap_flow_conserv_{i.name}")

    for i in G_t.values():
        if i.u.id not in {start_depot.id, end_depot.id}:
            model.addConstr(quicksum(z_t[i.name, j.name] for j in z_t_next_nodes[i]) ==
                            quicksum(z_t[j.name, i.name] for j in z_t_prev_nodes[i]), name=f"time_flow_conserv_{i.name}")

    # Z is consistent with X
    for u_id, v_id in x:
        u_nodes = G_d_u[u_id]
        v_nodes = G_d_u[v_id]
        z_ij = []
        for i in u_nodes:
            for j in v_nodes:
                if (i, j) in E_d:
                    z_ij.append(z_d[i.name, j.name])
        model.addConstr(
            x[u_id, v_id] == quicksum(z_ij),
            name=f"Cap_flow_{u_id}_{v_id}_x_consistent")

    for u_id, v_id in x:
        u_nodes = G_t_u[u_id]
        v_nodes = G_t_u[v_id]
        z_ij = []
        for i in u_nodes:
            for j in v_nodes:
                if (i, j) in E_t:
                    z_ij.append(z_t[i.name, j.name])
        model.addConstr(
            x[u_id, v_id] == quicksum(z_ij),
            name=f"Time_flow_{u_id}_{v_id}_x_consistent")
