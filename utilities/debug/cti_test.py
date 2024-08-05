
tol = 0.0001


def check_outbound_for_each_node(model, customers, start_depot, end_depot):
    for u in customers + [start_depot, end_depot]:
        total = 0
        for var in model.getVars():
            if var.varName.startswith(f"x_{u.id}_"):
                total += var.x
        if (total > (1 + tol) or total < (1 - tol)) and u not in [start_depot, end_depot]:
            print(f"❌ Total outgoing from {u.id}: {total}")


def check_inbound_for_each_node(model, customers, start_depot, end_depot):
    for u in customers + [start_depot, end_depot]:
        total = 0
        for var in model.getVars():
            if var.varName.startswith("x_") and var.varName.endswith(f"_{u.id}"):
                total += var.x
        if (total > (1 + tol) or total < (1 - tol)) and u not in [start_depot, end_depot]:
            print(f"❌ Total ingoing to {u.id}: {total}")


def count_x_vars(model, num_customers):
    all_x_vars = [var for var in model.getVars(
    ) if var.varName.startswith("x_")]
    total = len(all_x_vars)
    expected = num_customers * (num_customers + 1)
    if total == expected:
        print(f"✅ {expected} x vars (routes) created")
    else:
        print(f"❌ Expected {expected} x vars (routes), {total} created")


def count_leaving_u_constrs(model, num_customers):
    all_leaving_constr = [constr for constr in model.getConstrs(
    ) if constr.getAttr("ConstrName").startswith("leaving_")]

    if len(all_leaving_constr) != num_customers:
        print(
            f"❌ {len(all_leaving_constr)} leaving constr found (expected {num_customers})")
    else:
        print(f"✅ {len(all_leaving_constr)} leaving constr found.")


def count_servicing_u_constrs(model, num_customers):
    all_leaving_constr = [constr for constr in model.getConstrs(
    ) if constr.getAttr("ConstrName").startswith("servicing_")]

    if len(all_leaving_constr) != num_customers:
        print(
            f"❌ {len(all_leaving_constr)} servicing constr found (expected {num_customers})")
    else:
        print(f"✅ {len(all_leaving_constr)} servicing constr found.")


def count_capacity_constraints(model, num_customers):
    all_capacity_constrs = [constr for constr in model.getConstrs(
    ) if constr.getAttr("ConstrName").startswith("capacity_")]

    expected = num_customers * (num_customers + 1)

    if len(all_capacity_constrs) != expected:
        print(
            f"❌ {len(all_capacity_constrs)} capacity constr found (expected {expected})")
    else:
        print(f"✅ {len(all_capacity_constrs)} capacity constr found.")


def count_time_constraints(model, num_customers):
    all_time_constrs = [constr for constr in model.getConstrs(
    ) if constr.getAttr("ConstrName").startswith("time_")]

    expected = num_customers * (num_customers + 1)

    if len(all_time_constrs) != expected:
        print(
            f"❌ {len(all_time_constrs)} time constr found (expected {expected})")
    else:
        print(f"✅ {len(all_time_constrs)} time constr found.")


def compute_true_cost(model, customers, start_depot, end_depot):
    true_cost = 0
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                route_cost = (u.cost[v.index] - u.service_time) * \
                    model.getVarByName(f"x_{u.id}_{v.id}").x
                true_cost += route_cost
    print(f"True cost of the solution: {true_cost}")


def max_and_min_x(model):
    all_vars = model.getVars()
    all_x_vals = [
        var.x for var in all_vars if var.varName.startswith("x_")]
    print(f"Minimum x: {min(all_x_vals)}")
    print(f"Maximum x: {max(all_x_vals)}")


def check_tau_vals(model, customers):
    print("Checking tau...")


def check_objective_val(model, customers, start_depot, end_depot):
    cost = 0
    routes_computed = 0
    for u in customers + [start_depot]:
        for v in customers + [end_depot]:
            if u != v and ((u != start_depot) or (v != end_depot)):
                routes_computed += 1
                route_cost = ((u.cost[v.index]) - u.service_time) * \
                    model.getVarByName(f"x_{u.id}_{v.id}").x
                cost += route_cost
    print(
        f"Verified objective of the solution: {cost}; {routes_computed} x vars used.")
