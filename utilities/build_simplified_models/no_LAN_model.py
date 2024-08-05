from data import load_data
from models.simplified_models.no_LAN_model import create_no_LAN_model, create_relaxed_no_LAN_model, add_z_vars, add_z_constrs
from utilities.discrete_resource_graphs import build_disc_cap_graph_from_buckets, build_disc_time_graph_from_buckets, create_cap_buckets, create_time_buckets
from utilities.thresholds import create_cap_buckets_from_thresholds, create_time_buckets_from_thresholds


def initialize_no_LAN_data(data_set, num_customers, d_s, t_s):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=num_customers, capacity=200)

    D_u = create_cap_buckets(customers, d_s, capacity)
    T_u = create_time_buckets(customers, t_s)

    return customers, start_depot, end_depot, capacity, D_u, T_u


def build_relaxed_no_LAN(customers, start_depot, end_depot, capacity, D_u, T_u):
    # Create discrete resource graphs
    print("Initializing discrete capacity graph.")
    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)
    print("Initializing discrete time graph.")
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    # Build and relax the model
    model, x, z_d, z_t = create_relaxed_no_LAN_model(
        customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t)

    model.update()

    return model, x, z_d, z_t, G_d, E_d, G_t, E_t


def build_MILP_no_LAN(customers, start_depot, end_depot, capacity, W_d, W_t):
    D_u = create_cap_buckets_from_thresholds(W_d, capacity, customers)
    T_u = create_time_buckets_from_thresholds(W_t, customers)
    # Create discrete resource graphs
    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    model = create_no_LAN_model(
        customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t)

    return model


def update_relaxed_no_LAN_model(model, customers, start_depot, end_depot, capacity, W_d, W_t, x):
    D_u = create_cap_buckets_from_thresholds(W_d, capacity, customers)
    T_u = create_time_buckets_from_thresholds(W_t, customers)

    # Create new discrete resource graphs
    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    # Remove old z vars/constraints
    z_var_names = [var.varName for var in model.getVars()
                   if var.varName.startswith("z_")]

    z_constr_names = [constr.constrName for constr in model.getConstrs() if constr.constrName.startswith("cap_flow_conserv") or constr.constrName.startswith(
        "time_flow_conserv") or constr.constrName.startswith("Cap_flow") or constr.constrName.startswith("Time_flow")]

    for var_name in z_var_names:
        var = model.getVarByName(var_name)
        if var:
            model.remove(var)

    for constr_name in z_constr_names:
        constr = model.getConstrByName(constr_name)
        if constr:
            model.remove(constr)

    model.update()

    # Add new z vars/constraints
    z_d, z_t, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes, G_d_u, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_d, E_d, G_t, E_t)
    model.update()

    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

    model.update()

    return G_d, E_d, G_t, E_t
