def expand_cap_buckets(model, E_d, end_depot, thresholds):
    thresholds_added = 0
    for (i, j) in E_d:
        if i.u != j.u and j.u != end_depot:
            var_name = f"z_d_{i.name}_{j.name}"
            var = model.getVarByName(var_name)
            if var is not None and var.x > 0:
                new_threshold_val = i.k_upper - i.u.demand
                if new_threshold_val not in thresholds[j.u.id]:
                    if thresholds[j.u.id]:
                        thresholds[j.u.id].append(new_threshold_val)
                        thresholds_added += 1
                    else:
                        thresholds[j.u.id] = [new_threshold_val]
                        thresholds_added += 1
                    thresholds[j.u.id] = sorted(thresholds[j.u.id])
            elif var is None:
                print(f"❌ Var is none: {var_name}")
    print(f"Added {thresholds_added} capacity thresholds")
    return thresholds


def expand_time_buckets(model, E_t, end_depot, thresholds):
    thresholds_added = 0
    for (i, j) in E_t:
        if i.u != j.u and j.u != end_depot:
            var_name = f"z_t_{i.name}_{j.name}"
            var = model.getVarByName(var_name)
            if var is not None and var.x > 0:
                new_threshold_val = min(
                    i.k_upper - i.u.travel_time[j.u.index], j.k_upper)
                if new_threshold_val not in thresholds[j.u.id]:
                    if thresholds[j.u.id]:
                        thresholds[j.u.id].append(new_threshold_val)
                        thresholds_added += 1
                    else:
                        thresholds[j.u.id] = [new_threshold_val]
                        thresholds_added += 1
                    thresholds[j.u.id] = sorted(thresholds[j.u.id])
            elif var is None:
                print(f"❌ Var is none: {var_name}")
    print(f"Added {thresholds_added} time thresholds")
    return thresholds
