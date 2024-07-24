from data import load_data
from models.compact_two_index_model import create_cti_model
from models.cti_LA_model import create_LA_model
from models.cti_disc_model import create_disc_model
from models.LA_Disc_model import create_LAD_model
from utilities.find_LA_neighbors import find_all_LA_neighbors
from utilities.all_LA_arcs import all_LA_arcs
from utilities.efficient_frontier import compute_efficient_frontier
from utilities.discrete_resource_graphs import build_disc_cap_graph, build_disc_time_graph
from gurobipy import GRB


def vrptw_cti(data_set):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=8, capacity=200)

    vrptw_model = create_cti_model(customers, start_depot, end_depot, capacity)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


def vrptw_LA(data_set):
    k_count = 5
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=8, capacity=200)

    find_all_LA_neighbors(customers, k_count, capacity)
    P_plus, P_arcs = all_LA_arcs(customers)
    LA_routes = compute_efficient_frontier(P_plus)

    vrptw_model = create_LA_model(
        customers, start_depot, end_depot, capacity, LA_routes)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


def vrptw_disc(data_set):
    # Load data
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=8, capacity=200)

    # Create discrete resource graphs
    d_s = 30
    t_s = 50
    G_d, E_d, D_u = build_disc_cap_graph(
        customers, start_depot, end_depot, d_s, capacity)
    G_t, E_t, T_u = build_disc_time_graph(
        customers, start_depot, end_depot, t_s)

    vrptw_model = create_disc_model(
        customers, start_depot, end_depot, capacity, G_d, E_d, G_t, E_t)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


def vrptw_LAD(data_set):
    # Load data
    customers, start_depot, end_depot, capacity = load_data(
        data_set, num_customers=8, capacity=200)

    # Get LA-routes
    k_count = 5
    find_all_LA_neighbors(customers, k_count, capacity)
    P_plus, P_arcs = all_LA_arcs(customers)
    LA_routes = compute_efficient_frontier(P_plus)

    # Create discrete resource graphs
    d_s = 30
    t_s = 50
    G_d, E_d, D_u = build_disc_cap_graph(
        customers, start_depot, end_depot, d_s, capacity)
    G_t, E_t, T_u = build_disc_time_graph(
        customers, start_depot, end_depot, t_s)

    vrptw_model = create_LAD_model(
        customers, start_depot, end_depot, capacity, LA_routes, G_d, E_d, G_t, E_t)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


# vrptw_cti("r104.csv")
# vrptw_LA("r104.csv")
# vrptw_disc("r104.csv")
vrptw_LAD("r104.csv")
