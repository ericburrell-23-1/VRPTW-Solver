from gurobipy import Model, GRB, quicksum


def create_disc_model(customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t):
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

    # Resource vars
    G_d_u = {}
    for u in customers + [start_depot, end_depot]:
        G_d_u[u.id] = [G_d[(u.id, k)] for (u_key, k) in G_d if u_key == u.id]
        # print(
        #     f"Customer {u.id} has G_d_u nodes {[i.name for i in G_d_u[u.id]]}")
    z_d = {}
    z_d_next_nodes = {i: [] for i in G_d.values()}
    z_d_prev_nodes = {i: [] for i in G_d.values()}

    for i in G_d.values():
        for j in G_d.values():
            if (i, j) in E_d:
                # print(f"Creating a z variable for i={i.name}, j={j.name}")
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

    # Discrete time/capacity flow graphs (Z)
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
        # print(f"Looping through x for customers with ids ({u_id}, {v_id})")
        u_nodes = G_t_u[u_id]
        v_nodes = G_t_u[v_id]
        z_ij = []
        for i in u_nodes:
            for j in v_nodes:
                if (i, j) in E_t:
                    # print(
                    #     f"Adding edge ({i.name},{j.name}) in E_t to z_ij")
                    z_ij.append(z_t[i.name, j.name])
        model.addConstr(
            x[u_id, v_id] == quicksum(z_ij),
            name=f"Time_flow_{u_id}_{v_id}_x_consistent")

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
