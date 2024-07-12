from data import load_data
from compact_two_index_model import create_cti_model
from gurobipy import GRB


def vrptw(data_set):
    customers, start_depot, end_depot, capacity = load_data(
        data_set, capacity=200)

    vrptw_model = create_cti_model(customers, start_depot, end_depot, capacity)

    vrptw_model.optimize()

    if vrptw_model.status == GRB.Status.OPTIMAL:
        print("Optimal solution found!")
        # for var in vrptw_model.getVars():
        #     print(f"{var.varName}: {var.x}")
    else:
        print("No optimal solution found.")


vrptw("rc108.csv")
