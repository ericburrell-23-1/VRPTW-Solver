from models.LA_arc_model import LA_arc
from models.ordering_model import Ordering


def compute_efficient_frontier(all_LA_arcs):
    print("Computing the efficient frontier Rp")
    efficient_frontier = {}
    sorted_LA_arcs = sorted(all_LA_arcs, key=lambda arc: len(arc.N_p))
    plus_np_index = len(sorted_LA_arcs)

    # ASSIGN LA ARCS WITH NO N_P AS ROUTES IN EFFICIENT FRONTIER
    for idx, p in enumerate(sorted_LA_arcs):

        if len(p.N_p) == 0:
            efficient_frontier[p] = {Ordering([p.u, p.v])}
            continue
        else:
            plus_np_index = idx
            break

    # DYNAMICALLY BUILD EFFICIENT FRONTIER FROM EXISTING ROUTES
    for p in sorted_LA_arcs[plus_np_index:]:
        efficient_frontier[p] = set()
        sorted_N_p = sorted(p.N_p, key=lambda c: c.id)
        for w in sorted_N_p:
            p_hat = LA_arc(w, p.N_p - {w}, p.v)
            for r_minus in efficient_frontier[p_hat]:
                r = Ordering([p.u] + r_minus.visits)
                if r.latest_departure <= r.visits[0].time_window_start:
                    efficient_frontier[p].add(r)
        # REMOVE PARETO DOMINATED ROUTES IN R_P
        pareto_dominated_routes = set()
        for r in efficient_frontier[p]:
            for r_hat in efficient_frontier[p] - {r}:
                if (r.cost >= r_hat.cost) and (r.latest_departure >= r_hat.latest_departure) and (r.earliest_departure <= r_hat.earliest_departure):
                    if (r.cost > r_hat.cost) or (r.latest_departure > r_hat.latest_departure) or (r.earliest_departure < r_hat.earliest_departure):
                        pareto_dominated_routes.add(r)
        efficient_frontier[p] -= pareto_dominated_routes

    # UPDATE THE USER ON ROUTES IDENTIFIED
    total_LA_routes = 0
    total_LA_arcs = 0
    for R_p in efficient_frontier:
        total_LA_routes += len(efficient_frontier[R_p])
        if len(efficient_frontier[R_p]) > 0:
            total_LA_arcs += 1
    print(
        f"The efficient frontier (R_p) has {total_LA_routes} LA Routes from {total_LA_arcs} LA-arcs.")

    # LOOP OVER ALL CUSTOMERS TO BUILD R_U FROM R_P
    flattened_Rp = []
    for orderings in efficient_frontier.values():
        flattened_Rp.extend(orderings)

    sorted_flat_Rp = sorted(flattened_Rp, key=lambda r: r.visits[0].id)
    Ru = {}
    last_u = None
    for r in sorted_flat_Rp:
        u_r = r.visits[0]
        if u_r != last_u:
            Ru[u_r] = {Ordering(r.visits[:-1])}
            last_u = u_r
        else:
            Ru[u_r].add(Ordering(r.visits[:-1]))

    # UPDATE THE USER ON R_U ROUTES IDENTIFIED
    total_LA_routes = 0
    total_customer_arcs = 0
    for R_u in Ru:
        total_LA_routes += len(Ru[R_u])
        if len(Ru[R_u]) > 0:
            total_customer_arcs += 1

    print(
        f"The efficient frontier (R_u) has {total_LA_routes} LA Routes starting from {total_customer_arcs} customers (u).")

    return Ru
