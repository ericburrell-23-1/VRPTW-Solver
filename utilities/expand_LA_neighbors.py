import gurobipy as gp


def expand_LA_neighbors(model, customers, removed_constraints):
    total = 0
    for customer in customers:
        customer.LA_neighbors = customer.all_LA_neighbors

    for constr in removed_constraints:
        if constr is not None:
            lhs, sense, rhs, name = constr[0], constr[1], constr[2], constr[3]
            model.addConstr(lhs, sense, rhs, name)
            total += 1
        else:
            print(f"❌ Attempted to re-add invalid LA-N constraint")

    print(f"Re-added {total} LA-N constraints.")

    return compute_ku(customers)


def compute_ku(customers):
    ku = {}
    for u in customers:
        ku[u.id] = len(u.LA_neighbors)
    return ku
