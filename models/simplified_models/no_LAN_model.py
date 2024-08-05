from gurobipy import Model, GRB, quicksum


def create_no_LAN_model(customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t):
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

    # Resource vars
    z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t)

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

    # Discrete time/capacity flow graphs (Z)
    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

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


def create_relaxed_no_LAN_model(customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t):
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

    # Resource vars
    z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t)

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

    # Discrete time/capacity flow graphs (Z)
    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

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

    return model, x, z_d, z_t,


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

    model.update()

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

    model.update()


def get_customer_by_id(id, customers_by_id, start_depot, end_depot):
    if id == start_depot.id:
        return start_depot
    if id == end_depot.id:
        return end_depot
    return customers_by_id[id]
