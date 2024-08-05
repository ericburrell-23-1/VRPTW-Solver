def compute_a_coeffs(customers, LA_routes):
    a_wvr = {}
    a_wrstar = {}
    a_k_wr = {}
    a_k_wvr = {}
    a_k_wrstar = {}
    E_u = {}

    print("Computing 'a' coefficients")
    for u in customers:
        E_u[u.id] = set()
        for w in set(u.LA_neighbors) | {u}:
            for v in set(u.LA_neighbors) - {w}:
                E_u[u.id].add((w, v))

        # Compute a_wvr
        # print(f"Computing a_wvr and a_wrstar for customer {u.id}")
        for r in LA_routes[u]:
            for (w, v) in E_u[u.id]:
                if w in r.visits:
                    v_index = r.visits.index(w) + 1
                    if v_index < len(r.visits):
                        # a_wrstar[u.id, w.id, r] = 0
                        if r.visits[v_index] == v:
                            a_wvr[u.id, w.id, v.id, r] = 1
                        else:
                            a_wvr[u.id, w.id, v.id, r] = 0
                    else:
                        # a_wrstar[u.id, w.id, r] = 1
                        a_wvr[u.id, w.id, v.id, r] = 0
                else:
                    # a_wrstar[u.id, w.id, r] = 0
                    a_wvr[u.id, w.id, v.id, r] = 0

        # Compute a_wrstar
        for r in LA_routes[u]:
            for w in customers:
                if w in r.visits:
                    if (r.visits.index(w) + 1) == len(r.visits):
                        a_wrstar[u.id, w.id, r] = 1
                        # print(
                        #     f"a_wrstar = 1 for u = {u.id}, w = {w.id}, r = {[c.id for c in r.visits]}")
                    else:
                        a_wrstar[u.id, w.id, r] = 0
                else:
                    a_wrstar[u.id, w.id, r] = 0

        # print(f"Computing a_k_wvr and a_k_wrstar for customer {u.id}")
        for k in range(1, len(u.LA_neighbors) + 1):
            N_k_u = u.LA_neighbors[:k]  # The k closest LA-neighbors
            N_k_plus_u = N_k_u + [u]
            # Compute a_k_wr
            for r in LA_routes[u]:
                for w in N_k_plus_u:
                    if w in r.visits:
                        if all(c in N_k_plus_u for c in r.visits[:r.visits.index(w)+1]):
                            a_k_wr[u.id, k, w.id, r] = 1
                        else:
                            a_k_wr[u.id, k, w.id, r] = 0
                    else:
                        a_k_wr[u.id, k, w.id, r] = 0

            # Compute a_k_wvr
            for w in N_k_plus_u:
                for v in set(N_k_u) - {w}:
                    for r in LA_routes[u]:
                        if a_wvr[u.id, w.id, v.id, r] and a_k_wr[u.id, k, v.id, r]:
                            a_k_wvr[u.id, k, w.id, v.id, r] = 1
                        else:
                            a_k_wvr[u.id, k, w.id, v.id, r] = 0

            # Compute a_k_wrstar
            for r in LA_routes[u]:
                for w in N_k_plus_u:
                    v_values = set(N_k_u) - {w}
                    a_wvr_all_v = [a_wvr[u.id, w.id, v.id, r]
                                   for v in v_values]
                    a_wvr_sums = sum(a_wvr_all_v)
                    if a_k_wr[u.id, k, w.id, r] == 1 and (a_wrstar[u.id, w.id, r] == 1 or a_wvr_sums == 1):
                        a_k_wrstar[u.id, k, w.id, r] = 1
                    else:
                        a_k_wrstar[u.id, k, w.id, r] = 0

    return a_wvr, a_wrstar, a_k_wvr, a_k_wrstar, E_u
