from data import load_data
from utilities.find_LA_neighbors import find_all_LA_neighbors
from models.LA_Disc_model import create_LAD_model, create_relaxed_LAD_model, add_z_vars, add_z_constrs
from utilities.find_LA_neighbors import find_all_LA_neighbors
from utilities.all_LA_arcs import all_LA_arcs
from utilities.efficient_frontier import compute_efficient_frontier
from utilities.discrete_resource_graphs import build_disc_cap_graph_from_buckets, build_disc_time_graph_from_buckets, create_cap_buckets, create_time_buckets
from utilities.compute_a_coeffs import compute_a_coeffs
from utilities.thresholds import create_cap_buckets_from_thresholds, create_time_buckets_from_thresholds


def initialize_vrptw_data(data_set, k_count, d_s, t_s):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=8, capacity=200)

    # Find all LA-Neighbors
    find_all_LA_neighbors(customers, k_count, capacity)

    # Get LA-routes
    P_plus, P_arcs = all_LA_arcs(customers)
    LA_routes = compute_efficient_frontier(P_plus)

    a_wvr, a_wrstar, a_k_wvr, a_k_wrstar, E_u = compute_a_coeffs(
        customers, LA_routes)

    # Create discrete resource graphs
    D_u = create_cap_buckets(customers, d_s, capacity)
    T_u = create_time_buckets(customers, t_s)

    return customers, start_depot, end_depot, capacity, LA_routes, D_u, T_u, a_wvr, a_wrstar, a_k_wvr, a_k_wrstar, E_u


def build_relaxed_vrptw_LAD(customers, start_depot, end_depot, capacity, LA_routes, D_u, T_u, a_k_wvr, a_k_wrstar, E_u):
    # Create discrete resource graphs
    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    # Build and relax the model
    model, x, y, z_d, z_t = create_relaxed_LAD_model(
        customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_k_wvr, a_k_wrstar, E_u)

    model.update()

    return model, x, y, z_d, z_t, G_d, E_d, G_t, E_t


def build_MILP_vrptw_LAD(customers, start_depot, end_depot, capacity, LA_routes, W_d, W_t, a_wvr, a_wrstar, E_u):
    D_u = create_cap_buckets_from_thresholds(W_d, capacity, customers)
    T_u = create_time_buckets_from_thresholds(W_t, customers)
    # Create discrete resource graphs
    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)
    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    model = create_LAD_model(
        customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t, a_wvr, a_wrstar, E_u)

    return model


def update_relaxed_model(model, customers, start_depot, end_depot, capacity, W_d, W_t, x):
    D_u = create_cap_buckets_from_thresholds(W_d, capacity, customers)
    T_u = create_time_buckets_from_thresholds(W_t, customers)
    # Create discrete resource graphs
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
    add_z_constrs(model, start_depot, end_depot, x, z_d, z_t, G_d, E_d, G_t, E_t,
                  G_d_u, G_t_u, z_d_next_nodes, z_d_prev_nodes, z_t_next_nodes, z_t_prev_nodes)

    model.update()
