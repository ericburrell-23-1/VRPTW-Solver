from gurobipy import quicksum


def expand_LA_neighbors(model, customers, removed_constraints):
    customers.LA_neighbors = customers.all_LA_neighbors

    for constr in removed_constraints:
        model.addConstr(constr)
