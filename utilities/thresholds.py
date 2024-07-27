def create_thresholds_from_cap_buckets(buckets, capacity):
    thresholds = {}
    for u_id in buckets:
        thresholds[u_id] = []
        for bucket in buckets[u_id]:
            if bucket[1] != capacity:
                thresholds[u_id].append(bucket[1])
        thresholds[u_id] = sorted(thresholds[u_id])
    return thresholds


def create_thresholds_from_time_buckets(buckets, customers):
    customer_dict = {customer.id: customer for customer in customers}

    thresholds = {}
    for u_id in buckets:
        earliest_time = customer_dict[u_id].time_window_start
        thresholds[u_id] = []
        for bucket in buckets[u_id]:
            if bucket[1] != earliest_time:
                thresholds[u_id].append(bucket[1])
        thresholds[u_id] = sorted(thresholds[u_id])
    return thresholds


def create_cap_buckets_from_thresholds(thresholds, capacity, customers):
    customer_dict = {customer.id: customer for customer in customers}

    buckets = {}
    for u_id in thresholds:
        demand = customer_dict[u_id].demand
        buckets[u_id] = []
        lower_bound = demand

        thresholds[u_id] = sorted(thresholds[u_id])
        for upper_bound in thresholds[u_id]:
            buckets[u_id].append((lower_bound, upper_bound))
            lower_bound = upper_bound
        buckets[u_id].append((lower_bound, capacity))

    return buckets


def create_time_buckets_from_thresholds(thresholds, customers):
    customer_dict = {customer.id: customer for customer in customers}

    buckets = {}
    for u_id in thresholds:
        start_time = customer_dict[u_id].time_window_start
        end_time = customer_dict[u_id].time_window_end
        buckets[u_id] = []
        lower_bound = end_time

        thresholds[u_id] = sorted(thresholds[u_id])
        for upper_bound in thresholds[u_id]:
            buckets[u_id].append((lower_bound, upper_bound))
            lower_bound = upper_bound
        buckets[u_id].append((lower_bound, start_time))

    return buckets


def dicts_are_equal(dict1, dict2):
    if dict1.keys() != dict2.keys():
        return False
    for key in dict1:
        if dict1[key] != dict2[key]:
            return False
    return True
