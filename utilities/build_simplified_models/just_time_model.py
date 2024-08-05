from data import load_data
from models.simplified_models.just_time_model import create_just_time_model, create_relaxed_just_time_model, add_z_vars, add_z_constrs
from utilities.discrete_resource_graphs import build_disc_time_graph_from_buckets, create_time_buckets
from utilities.thresholds import create_time_buckets_from_thresholds


def initialize_just_time_data(data_set, num_customers, t_s):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=num_customers, capacity=200)

    T_u = create_time_buckets(customers, t_s)

    return customers, start_depot, end_depot, capacity, T_u


def build_relaxed_just_time(customers, start_depot, end_depot, capacity, T_u):
    # Create discrete resource graphs
    print("Initializing discrete time graph.")
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    # Build and relax the model
    model, x, z_t = create_relaxed_just_time_model(
        customers, start_depot, end_depot, capacity, G_t, E_t)

    model.update()

    return model, x, z_t, G_t, E_t


def build_MILP_just_time(customers, start_depot, end_depot, capacity, W_t):

    T_u = create_time_buckets_from_thresholds(W_t, customers)
    # Create discrete resource graphs

    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    model = create_just_time_model(
        customers, start_depot, end_depot, capacity, G_t, E_t)

    return model


def update_relaxed_just_time_model(model, customers, start_depot, end_depot, W_t, x):

    T_u = create_time_buckets_from_thresholds(W_t, customers)

    # Create new discrete resource graphs

    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    # Remove old z vars/constraints
    z_var_names = [var.varName for var in model.getVars()
                   if var.varName.startswith("z_")]

    z_constr_names = [constr.constrName for constr in model.getConstrs() if constr.constrName.startswith(
        "time_flow_conserv") or constr.constrName.startswith("Time_flow")]

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
    z_t, z_t_next_nodes, z_t_prev_nodes, G_t_u = add_z_vars(
        model, customers, start_depot, end_depot, G_t, E_t)
    model.update()

    add_z_constrs(model, start_depot, end_depot, x, z_t, G_t, E_t,
                  G_t_u, z_t_next_nodes, z_t_prev_nodes)

    model.update()

    return G_t, E_t
