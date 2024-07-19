from data import load_data
from models.compact_two_index_model import create_cti_model
from models.LA_Disc_model import create_LAD_model
from utilities.find_LA_neighbors import find_all_LA_neighbors
from utilities.all_LA_arcs import all_LA_arcs
from utilities.efficient_frontier import compute_efficient_frontier
from gurobipy import GRB


def vrptw_cti(data_set):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=12, capacity=200)

    vrptw_model = create_cti_model(customers, start_depot, end_depot, capacity)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


def vrptw_LAD(data_set):
    k_count = 5
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=12, capacity=200)

    find_all_LA_neighbors(customers, k_count, capacity)
    P_plus, P_arcs = all_LA_arcs(customers)
    LA_routes = compute_efficient_frontier(P_plus)

    vrptw_model = create_LAD_model(
        customers, start_depot, end_depot, capacity, LA_routes)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


# vrptw_cti("rc103.csv")
vrptw_LAD("rc103.csv")
