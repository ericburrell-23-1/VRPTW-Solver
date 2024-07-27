
class Node:
    def __init__(self, u, k_lower, k_upper):
        self.u = u
        self.k_lower = k_lower
        self.k_upper = k_upper
        self.name = f"{u.id}_{k_lower}_{k_upper}"

    def __repr__(self):
        return f"Node({self.u}, {self.k_lower}, {self.k_upper})"

    def __eq__(self, other):
        if isinstance(other, Node):
            return (self.u == other.u) and (self.k_lower == other.k_lower) and (self.k_upper == other.k_upper)
        return False

    def __hash__(self):
        return hash((self.u, self.k_lower, self.k_upper))


def create_cap_buckets(customers, bucket_size, capacity):
    D_u = {}
    for u in customers:
        D_u[u.id] = []
        bucket_min = u.demand
        while (bucket_min + bucket_size) < capacity:
            bucket_max = bucket_min + bucket_size
            D_u[u.id].append((bucket_min, bucket_max))
            bucket_min = bucket_max
        D_u[u.id].append((bucket_min, capacity))

    return D_u


def build_disc_cap_graph_from_buckets(customers, start_depot, end_depot, buckets, capacity):
    G_d = {}
    E_d = set()

    # Create customer nodes
    for u in customers:
        for k, bucket in enumerate(buckets[u.id]):
            G_d[u.id, k] = Node(u, bucket[0], bucket[1])

    # Add depot nodes
    start_node = Node(start_depot, capacity, capacity)
    end_node = Node(end_depot, 0, capacity)

    # Create edges
    for u in customers:
        last_k = len(buckets[u.id]) - 1
        # Create edge from start depot to each customer
        E_d.add((start_node, G_d[u.id, last_k]))
        # Create edge from each customer to end depot
        E_d.add((G_d[u.id, 0], end_node))

        for k in list(range(0, last_k)):
            # Create edges to "dump excess capacity"
            E_d.add((G_d[u.id, k + 1], G_d[u.id, k]))

    # Create possible edges between customers
    for i in G_d.values():
        u = i.u
        k_min = i.k_lower
        k_max = i.k_upper
        for j in G_d.values():
            v = j.u
            m_min = j.k_lower
            if v != u:
                if (k_max - u.demand) >= m_min:
                    if (k_min == u.demand) or (m_min > k_min - u.demand):
                        E_d.add((i, j))

    G_d[start_depot.id, 0] = start_node
    G_d[end_depot.id, 0] = end_node

    return G_d, E_d


def create_time_buckets(customers, bucket_size):
    T_u = {}
    for u in customers:
        T_u[u.id] = []
        bucket_min = u.time_window_end
        while (bucket_min + bucket_size) < u.time_window_start:
            bucket_max = bucket_min + bucket_size
            T_u[u.id].append((bucket_min, bucket_max))
            bucket_min = bucket_max
        T_u[u.id].append((bucket_min, u.time_window_start))
    return T_u


def build_disc_time_graph_from_buckets(customers, start_depot, end_depot, buckets):
    G_t = {}
    E_t = set()

    # Create customer nodes
    for u in customers:
        for k, bucket in enumerate(buckets[u.id]):
            G_t[u.id, k] = Node(u, bucket[0], bucket[1])

    # Add depot nodes
    start_node = Node(start_depot, start_depot.time_window_end,
                      start_depot.time_window_start)
    end_node = Node(end_depot, end_depot.time_window_end,
                    end_depot.time_window_start)

    # Create edges
    for u in customers:
        last_k = len(buckets[u.id]) - 1
        # Create edge from start depot to each customer
        E_t.add((start_node, G_t[u.id, last_k]))
        # Create edge from each customer to end depot
        E_t.add((G_t[u.id, 0], end_node))

        for k in list(range(0, last_k)):
            # Create edges to "dump excess capacity"
            E_t.add((G_t[u.id, k + 1], G_t[u.id, k]))

    # Create possible edges between customers
    for i in G_t.values():
        u = i.u
        k_min = i.k_lower
        k_max = i.k_upper
        for j in G_t.values():
            v = j.u
            m_min = j.k_lower
            if v != u:
                travel_time = u.travel_time[v.index]
                if (k_max - travel_time) >= m_min:
                    if (k_min == u.time_window_end) or (m_min > k_min - travel_time):
                        E_t.add((i, j))

    G_t[start_depot.id, 0] = start_node
    G_t[end_depot.id, 0] = end_node

    return G_t, E_t


def build_disc_cap_graph(customers, start_depot, end_depot, bucket_size, capacity):
    D_u = create_cap_buckets(customers, bucket_size, capacity)

    G_d, E_d = build_disc_cap_graph_from_buckets(
        customers, start_depot, end_depot, D_u, capacity)

    return G_d, E_d, D_u


def build_disc_time_graph(customers, start_depot, end_depot, bucket_size):
    T_u = create_time_buckets(customers, bucket_size)

    G_t, E_t = build_disc_time_graph_from_buckets(
        customers, start_depot, end_depot, T_u)

    return G_t, E_t, T_u
