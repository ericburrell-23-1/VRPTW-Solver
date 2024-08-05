import gurobipy as gp
from gurobipy import GRB


def contract_LA_neighbors(model, customers, E_u, prev_ku):
    ku = {}
    if not prev_ku:
        prev_ku = initial_ku(customers)
    removed_constraints = []
    # constr8a_count = 0
    # constr8b_count = 0
    if model.status == GRB.OPTIMAL:
        for u in customers:
            max_k = 0
            for k in range(1, len(u.LA_neighbors) + 1):
                N_k_u = u.LA_neighbors[:k]
                N_k_plus_u = N_k_u + [u]

                # Sum dual values for (8a) constraints
                constraints8a = [model.getConstrByName(
                    f"LA_route_{u.id}_{w.id}_{v.id}_{k}") for w in N_k_plus_u for v in sorted(set(N_k_u) - {w}, key=lambda c: c.id) if (w, v) in E_u[u.id]]
                for c in constraints8a:
                    if not isinstance(c, gp.Constr):
                        print("Bad constraint in LA_N contraction")
                # constr8a_count += len(constraints8a)
                sum_dual_8a = sum(c.Pi for c in constraints8a)

                # Sum dual values for (8b) constraints
                constraints8b = [model.getConstrByName(
                    f"LA_route_end_{u.id}_{w.id}_{k}") for w in N_k_plus_u]
                # constr8b_count += len(constraints8b)
                sum_dual_8b = sum(c.Pi for c in constraints8b)

                # Check if the combined dual value is positive
                if sum_dual_8a + sum_dual_8b > 0:
                    max_k = k

            ku[u.id] = max_k
        # print(
        #     f"Found {constr8a_count} 8a constraints and {constr8b_count} 8b constraints during L-N contraction.")

        # constr_removed_count = 0
        for u in customers:
            if ku[u.id] < prev_ku[u.id]:
                u.LA_neighbors = u.LA_neighbors[:ku[u.id]]
                for k in range(ku[u.id] + 1, prev_ku[u.id] + 1):
                    N_k_u = u.all_LA_neighbors[:k]
                    N_k_plus_u = N_k_u + [u]

                    constr_removed_count = 0
                    constraints8a = []
                    for w in N_k_plus_u:
                        for v in sorted(set(N_k_u) - {w}, key=lambda c: c.id):
                            if (w, v) in E_u[u.id]:
                                constr = model.getConstrByName(
                                    f"LA_route_{u.id}_{w.id}_{v.id}_{k}")
                                constraints8a.append(constr)
                    for c in constraints8a:
                        lhs, sense, rhs, name = model.getRow(
                            c), c.Sense, c.RHS, c.ConstrName
                        model.remove(c)
                        removed_constraints.append((lhs, sense, rhs, name))
                        constr_removed_count += 1

                    constraints8b = [model.getConstrByName(
                        f"LA_route_end_{u.id}_{w.id}_{k}") for w in N_k_plus_u]
                    for c in constraints8b:
                        lhs, sense, rhs, name = model.getRow(
                            c), c.Sense, c.RHS, c.ConstrName
                        model.remove(c)
                        removed_constraints.append((lhs, sense, rhs, name))
                        constr_removed_count += 1

    else:
        print("Model not optimal. LA-N contraction operation failed.")

    print_neighbors_removed(ku, prev_ku)
    return ku, removed_constraints


def initial_ku(customers):
    ku = {}
    for u in customers:
        ku[u.id] = len(u.LA_neighbors)
    return ku


def print_neighbors_removed(ku, prev_ku):
    total = 0
    for new, old in zip(ku.values(), prev_ku.values()):
        # print(f"Old: {old} \tNew: {new}")
        total += old - new

    print(f"{total} neighbors removed via LA-N contraction.")
