from gurobipy import GRB


def contract_LA_neighbors(model, customers, E_u, prev_ku):
    ku = {}
    if not prev_ku:
        prev_ku = initial_ku(customers)
    removed_constraints = []
    if model.status == GRB.OPTIMAL:
        for u in customers:
            max_k = 0
            for k in range(1, len(u.LA_neighbors) + 1):
                N_k_u = u.LA_neighbors[:k]
                N_k_plus_u = N_k_u + [u]

                # Sum dual values for (8a) constraints
                constraints8a = [model.getConstrByName(
                    f"LA_route_{u.id}_{w.id}_{v.id}_{k}") for w in N_k_plus_u for v in sorted(set(N_k_u) - {w}, key=lambda c: c.id) if (w, v) in E_u[u.id]]
                sum_dual_8a = sum(c.Pi for c in constraints8a)

                # Sum dual values for (8b) constraints
                constraints8b = [model.getConstrByName(
                    f"LA_route_end_{u.id}_{w.id}_{k}") for w in N_k_plus_u]
                sum_dual_8b = sum(c.Pi for c in constraints8b)

                # Check if the combined dual value is positive
                if sum_dual_8a + sum_dual_8b > 0:
                    max_k = k

            ku[u.id] = max_k

        for u in customers:
            if ku[u.id] < prev_ku[u.id]:
                u.LA_neighbors = u.LA_neighbors[:ku[u.id]]
                for k in range(ku[u.id] + 1, prev_ku[u.id] + 1):
                    N_k_u = u.LA_neighbors[:k]
                    N_k_plus_u = N_k_u + [u]

                    constraints8a = [model.getConstrByName(f"LA_route_{u.id}_{w.id}_{v.id}_{k}") for w in N_k_plus_u for v in sorted(
                        set(N_k_u) - {w}, key=lambda c: c.id) if (w, v) in E_u[u.id]]
                    for c in constraints8a:
                        model.remove(c)
                        removed_constraints.append(c)

    else:
        print("Model not optimal. LA-N contraction operation failed.")

    return ku, removed_constraints


def initial_ku(customers):
    ku = {}
    for u in customers:
        ku[u.id] = len(u.LA_neighbors)
    return ku
