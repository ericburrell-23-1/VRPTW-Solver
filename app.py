import copy
from utilities.build_models import initialize_full_data, build_relaxed_vrptw_LAD, build_MILP_vrptw_LAD, update_relaxed_model
from utilities.build_simplified_models.no_LAN_model import initialize_no_LAN_data, build_relaxed_no_LAN, build_MILP_no_LAN, update_relaxed_no_LAN_model
from utilities.build_simplified_models.just_time_model import initialize_just_time_data, build_MILP_just_time, build_relaxed_just_time, update_relaxed_just_time_model
from utilities.contract_LA_neighbors import contract_LA_neighbors
from utilities.expand_LA_neighbors import expand_LA_neighbors
from utilities.contract_buckets import contract_cap_buckets, contract_time_buckets
from utilities.expand_buckets import expand_cap_buckets, expand_time_buckets
from utilities.thresholds import create_thresholds_from_cap_buckets, create_thresholds_from_time_buckets, dicts_are_equal


def full_solution(data_set, num_customers):
    DATA_SET = data_set
    K_COUNT = 6
    D_S = 100
    T_S = 50000

    customers, start_depot, end_depot, capacity, LA_routes, D_u, T_u, a_wvr, a_wrstar, a_k_wvr, a_k_wrstar, E_u = initialize_full_data(
        DATA_SET, num_customers, K_COUNT, D_S, T_S)

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
    lp_values = []
    new_best_lp_values = []

    while continue_iter:
        if iter_since_reset > ZETA:
            print("\nℹ️ Iter exceeds Zeta. Expanding neighbors.")
            ku = expand_LA_neighbors(relaxed_model, customers,
                                     all_removed_constr["LA_N"])
            prev_ku = copy.deepcopy(ku)
            all_removed_constr["LA_N"] = []

        relaxed_model.optimize()
        lp_values.append(relaxed_model.ObjVal)
        if relaxed_model.ObjVal > last_lp_val + MIN_INC:
            iter_since_reset = 0
            last_lp_val = relaxed_model.ObjVal
            new_best_lp_values.append(relaxed_model.ObjVal)

            print("\nℹ️ Model improved. Merging nodes and contracting neighbors.")
            W_d = contract_cap_buckets(relaxed_model, E_d, W_d)
            W_t = contract_time_buckets(relaxed_model, E_t, W_t)

            ku, removed_constraints = contract_LA_neighbors(
                relaxed_model, customers, E_u, prev_ku)
            all_removed_constr["LA_N"].extend(removed_constraints)

        # Expand Resource Nodes Here
        print("\nℹ️ Expanding buckets.")
        W_d = expand_cap_buckets(relaxed_model, E_d, end_depot, W_d)
        W_t = expand_time_buckets(relaxed_model, E_t, end_depot, W_t)

        iter_since_reset += 1

        if (dicts_are_equal(ku, prev_ku) and dicts_are_equal(W_d, prev_W_d) and dicts_are_equal(W_t, prev_W_t)) or iter_since_reset > ITER_MAX:
            continue_iter = False
            if iter_since_reset > ITER_MAX:
                print("\nℹ️ Loop ended due to too many iterations.")
            else:
                print("\nℹ️ Loop ended due to no changes.")
        else:
            G_d, E_d, G_t, E_t = update_relaxed_model(relaxed_model, customers,
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

    print(f"\nAll iteration LP objective vals: {lp_values}")
    print(f"\nBest LP objective vals: {new_best_lp_values}")


def full_no_LA_N(data_set, num_customers):
    DATA_SET = data_set
    D_S = 20
    T_S = 500

    customers, start_depot, end_depot, capacity, D_u, T_u = initialize_no_LAN_data(
        DATA_SET, num_customers, D_S, T_S)

    relaxed_model, x, z_d, z_t, G_d, E_d, G_t, E_t = build_relaxed_no_LAN(
        customers, start_depot, end_depot, capacity, D_u, T_u)
    relaxed_model.update()

    # Start Alg 1
    MIN_INC = 1
    ITER_MAX = 10
    iter_since_reset = 0
    last_lp_val = -999999
    continue_iter = True

    W_d = create_thresholds_from_cap_buckets(D_u, capacity)
    W_t = create_thresholds_from_time_buckets(T_u, customers)
    prev_W_d = copy.deepcopy(W_d)
    prev_W_t = copy.deepcopy(W_t)
    lp_values = []
    new_best_lp_values = []

    while continue_iter:
        relaxed_model.optimize()
        lp_values.append(relaxed_model.ObjVal)
        if relaxed_model.ObjVal > last_lp_val + MIN_INC:
            iter_since_reset = 0
            last_lp_val = relaxed_model.ObjVal
            new_best_lp_values.append(relaxed_model.ObjVal)

            print("\nℹ️ Model improved. Merging nodes.")
            W_d = contract_cap_buckets(relaxed_model, E_d, W_d)
            W_t = contract_time_buckets(relaxed_model, E_t, W_t)

        # Expand Resource Nodes Here
        print("\nℹ️ Expanding buckets.")
        W_d = expand_cap_buckets(relaxed_model, E_d, end_depot, W_d)
        W_t = expand_time_buckets(relaxed_model, E_t, end_depot, W_t)

        iter_since_reset += 1

        if (dicts_are_equal(W_d, prev_W_d) and dicts_are_equal(W_t, prev_W_t)) or iter_since_reset > ITER_MAX:
            continue_iter = False
            if iter_since_reset > ITER_MAX:
                print("\nℹ️ Loop ended due to too many iterations.")
            else:
                print("\nℹ️ Loop ended due to no changes.")
        else:
            G_d, E_d, G_t, E_t = update_relaxed_no_LAN_model(relaxed_model, customers,
                                                             start_depot, end_depot, capacity, W_d, W_t, x)
            prev_W_d = copy.deepcopy(W_d)
            prev_W_t = copy.deepcopy(W_t)

    W_d = contract_cap_buckets(relaxed_model, E_d, W_d)
    W_t = contract_time_buckets(relaxed_model, E_t, W_t)

    # Solve MILP
    MILP_model = build_MILP_no_LAN(
        customers, start_depot, end_depot, capacity, W_d, W_t)
    MILP_model.update()
    MILP_model.optimize()

    print(f"\nAll iteration LP objective vals: {lp_values}")
    print(f"\nBest LP objective vals: {new_best_lp_values}")


def full_just_time(data_set, num_customers):
    DATA_SET = data_set
    T_S = 50

    customers, start_depot, end_depot, capacity, T_u = initialize_just_time_data(
        DATA_SET, num_customers, T_S)

    relaxed_model, x, z_t, G_t, E_t = build_relaxed_just_time(
        customers, start_depot, end_depot, capacity, T_u)
    relaxed_model.update()

    # Start Alg 1
    MIN_INC = 1
    ITER_MAX = 10
    iter_since_reset = 0
    last_lp_val = -999999
    continue_iter = True

    W_t = create_thresholds_from_time_buckets(T_u, customers)
    prev_W_t = copy.deepcopy(W_t)
    lp_values = []
    new_best_lp_values = []

    while continue_iter:
        relaxed_model.optimize()
        lp_values.append(relaxed_model.ObjVal)
        if relaxed_model.ObjVal > last_lp_val + MIN_INC:
            iter_since_reset = 0
            last_lp_val = relaxed_model.ObjVal
            new_best_lp_values.append(relaxed_model.ObjVal)

            print("\nℹ️ Model improved. Merging nodes.")

            W_t = contract_time_buckets(relaxed_model, E_t, W_t)

        # Expand Resource Nodes Here
        print("\nℹ️ Expanding buckets.")

        W_t = expand_time_buckets(relaxed_model, E_t, end_depot, W_t)

        iter_since_reset += 1

        if dicts_are_equal(W_t, prev_W_t) or iter_since_reset > ITER_MAX:
            continue_iter = False
            if iter_since_reset > ITER_MAX:
                print("\nℹ️ Loop ended due to too many iterations.")
            else:
                print("\nℹ️ Loop ended due to no changes.")
        else:
            G_t, E_t = update_relaxed_just_time_model(relaxed_model, customers,
                                                      start_depot, end_depot, W_t, x)

            prev_W_t = copy.deepcopy(W_t)

    W_t = contract_time_buckets(relaxed_model, E_t, W_t)

    # Solve MILP
    MILP_model = build_MILP_just_time(
        customers, start_depot, end_depot, capacity, W_t)
    MILP_model.update()
    MILP_model.optimize()

    print(f"\nAll iteration LP objective vals: {lp_values}")
    print(f"\nBest LP objective vals: {new_best_lp_values}")
