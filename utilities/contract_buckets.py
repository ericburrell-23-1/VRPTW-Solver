def contract_cap_buckets(model, E_d, thresholds):
    for (i, j) in E_d:
        if i.u == j.u:
            var = model.getVarByName(f"z_d_{i.name}_{j.name}")
            if var is not None and var.RC == 0:
                if j.k_upper in thresholds[i.u.id]:
                    thresholds[i.u.id].remove(j.k_upper)

    return thresholds


def contract_time_buckets(model, E_t, thresholds):
    for (i, j) in E_t:
        if i.u == j.u:
            var = model.getVarByName(f"z_t_{i.name}_{j.name}")
            if var is not None and var.RC == 0:
                if j.k_upper in thresholds[i.u.id]:
                    thresholds[i.u.id].remove(j.k_upper)

    return thresholds
