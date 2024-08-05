import itertools
from models.LA_arc_model import LA_arc


def all_LA_arcs(customers):
    P_arcs = set()
    P_plus = set()
    print("Building P_plus")
    sorted_customers = sorted(customers, key=lambda c: c.id)

    for u in sorted_customers:
        # print(f"u = {u.id}")
        sorted_u_neighbors = sorted(u.LA_neighbors, key=lambda c: c.id)
        for u_p in [u] + sorted_u_neighbors:
            # print(f"\tu_p = {u_p.id}")
            for v_p in (sorted_customers):
                if v_p in u.LA_neighbors or v_p == u:
                    continue
                # print(f"\t\tv_p = {v_p.id}")
                possible_neighbors = sorted(
                    set(u.LA_neighbors) - {u_p, v_p}, key=lambda c: c.id)
                neighbor_sets = []
                for k in range(0, len(possible_neighbors) + 1):
                    neighbor_sets.extend(
                        itertools.combinations(possible_neighbors, k))
                for N_p in neighbor_sets:
                    # all_N_p = {n.id for n in N_p}
                    # print(f"\t\t\tN_p: {all_N_p}")
                    P_plus.add(LA_arc(u_p, set(N_p), v_p))
                    if u_p == u:
                        P_arcs.add(LA_arc(u_p, set(N_p), v_p))

    return P_plus, P_arcs
