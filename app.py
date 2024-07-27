import copy
from utilities.build_models import initialize_vrptw_data, build_relaxed_vrptw_LAD, build_MILP_vrptw_LAD, update_relaxed_model
from utilities.contract_LA_neighbors import contract_LA_neighbors
from utilities.expand_LA_neighbors import expand_LA_neighbors
from utilities.contract_buckets import contract_cap_buckets, contract_time_buckets
from utilities.expand_buckets import expand_cap_buckets, expand_time_buckets
from utilities.thresholds import create_thresholds_from_cap_buckets, create_thresholds_from_time_buckets, dicts_are_equal

DATA_SET = "rc103.csv"
K_COUNT = 4
D_S = 30
T_S = 50

customers, start_depot, end_depot, capacity, LA_routes, D_u, T_u, a_wvr, a_wrstar, a_k_wvr, a_k_wrstar, E_u = initialize_vrptw_data(
    DATA_SET, K_COUNT, D_S, T_S)

relaxed_model, x, y, z_d, z_t, G_d, E_d, G_t, E_t = build_relaxed_vrptw_LAD(
    customers, start_depot, end_depot, capacity, LA_routes, D_u, T_u, a_k_wvr, a_k_wrstar, E_u)
relaxed_model.update()

# Start Alg 1
MIN_INC = 1
ZETA = 9
ITER_MAX = 10
iter_since_reset = 0
last_lp_val = -999999
continue_iter = True

all_removed_constr = {
    "LA_N": []
}

W_d = create_thresholds_from_cap_buckets(D_u, capacity)
W_t = create_thresholds_from_time_buckets(T_u, customers)
prev_W_d = copy.deepcopy(W_d)
prev_W_t = copy.deepcopy(W_t)
prev_ku = {}

while continue_iter:
    if iter_since_reset > ZETA:
        expand_LA_neighbors(relaxed_model, customers,
                            all_removed_constr["LA_N"])
        all_removed_constr["LA_N"] = []

    relaxed_model.optimize()
    if relaxed_model.ObjVal > last_lp_val + MIN_INC:
        W_d = contract_cap_buckets(relaxed_model, E_d, W_d)
        W_t = contract_time_buckets(relaxed_model, E_t, W_t)

        ku, removed_constraints = contract_LA_neighbors(
            relaxed_model, customers, E_u, prev_ku)
        all_removed_constr["LA_N"].extend(removed_constraints)

        iter_since_reset = 0
        last_lp_val = relaxed_model.ObjVal

    # Expand Resource Nodes Here
    W_d = expand_cap_buckets(relaxed_model, E_d, end_depot, W_d)
    W_t = expand_time_buckets(relaxed_model, E_t, end_depot, W_t)

    iter_since_reset += 1

    if (dicts_are_equal(ku, prev_ku) and dicts_are_equal(W_d, prev_W_d) and dicts_are_equal(W_t, prev_W_t)) or iter_since_reset > ITER_MAX:
        continue_iter = False
    else:
        update_relaxed_model(relaxed_model, customers,
                             start_depot, end_depot, capacity, W_d, W_t, x)
        prev_ku = copy.deepcopy(ku)
        prev_W_d = copy.deepcopy(W_d)
        prev_W_t = copy.deepcopy(W_t)

ku, removed_constraints = contract_LA_neighbors(
    relaxed_model, customers, E_u, prev_ku)
W_d = contract_cap_buckets(relaxed_model, E_d, W_d)
W_t = contract_time_buckets(relaxed_model, E_t, W_t)

# Solve MILP
MILP_model = build_MILP_vrptw_LAD(customers, start_depot, end_depot,
                                  capacity, LA_routes, W_d, W_t, a_wvr, a_wrstar, E_u)
MILP_model.update()
MILP_model.optimize()
