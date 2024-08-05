from data import load_data
from models.simplified_models.compact_two_index_model import create_cti_model, create_relaxed_cti_model
from app import full_solution, full_no_LA_N, full_just_time
from utilities.debug.cti_test import check_outbound_for_each_node, check_inbound_for_each_node, count_x_vars, count_leaving_u_constrs, count_servicing_u_constrs, compute_true_cost, max_and_min_x, check_objective_val, count_capacity_constraints, count_time_constraints
from gurobipy import GRB


def compact_two_index(data_set, num_customers):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=num_customers, capacity=200)

    model = create_cti_model(
        customers, start_depot, end_depot, capacity)

    model.update()
    model.optimize()

    if model.status == GRB.Status.OPTIMAL:
        check_outbound_for_each_node(
            model, customers, start_depot, end_depot)
        check_inbound_for_each_node(
            model, customers, start_depot, end_depot)
        count_x_vars(model, num_customers)
        count_leaving_u_constrs(model, num_customers)
        count_servicing_u_constrs(model, num_customers)
        count_capacity_constraints(model, num_customers)
        count_time_constraints(model, num_customers)
        # compute_true_cost(model, customers, start_depot, end_depot)
        max_and_min_x(model)
        check_objective_val(model, customers, start_depot, end_depot)

    else:
        print("No optimal solution found.")


def relaxed_compact(data_set, num_customers):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=num_customers, capacity=200)

    model = create_relaxed_cti_model(
        customers, start_depot, end_depot, capacity)

    model.update()
    model.optimize()

    if model.status == GRB.Status.OPTIMAL:
        check_outbound_for_each_node(
            model, customers, start_depot, end_depot)
        check_inbound_for_each_node(
            model, customers, start_depot, end_depot)
        count_x_vars(model, num_customers)
        count_leaving_u_constrs(model, num_customers)
        count_servicing_u_constrs(model, num_customers)
        count_capacity_constraints(model, num_customers)
        count_time_constraints(model, num_customers)
        # compute_true_cost(model, customers, start_depot, end_depot)
        max_and_min_x(model)
        check_objective_val(model, customers, start_depot, end_depot)

    else:
        print("No optimal solution found.")


compact_two_index("c103.csv", 25)

# relaxed_compact("c103.csv", 25)

# full_solution("c103.csv", 25)

# full_no_LA_N("c103.csv", 50)

# full_just_time("c103.csv", 25)
