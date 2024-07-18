import numpy as np
# from utilities.debug.LA_neighbors import print_infeasible_neighbor


def find_LA_neighbors_for(customer_index, LA_n_count, all_customers, capacity):
    customer = all_customers[customer_index]

    # Build sorted array of closest neighbors indices
    neighbor_indices = []
    neighbor_costs = []
    for i in range(0, len(all_customers)):
        neighbor_indices.append(i)
        neighbor_costs.append(customer.cost[i + 1])

    sorted_cost_index = np.argsort(neighbor_costs)
    all_neighbors_sorted = [neighbor_indices[i] for i in sorted_cost_index]

    LA_neighbors = []
    # Loop through all customers, starting with the closest
    for neighbor_index in all_neighbors_sorted[1:]:
        neighbor = all_customers[neighbor_index]

        # Check to make sure time/capacity are feasible
        if (capacity - neighbor.demand > customer.demand) and (customer.time_window_start - customer.travel_time[neighbor.index] > neighbor.time_window_end):
            LA_neighbors.append(neighbor)
        # else:
        #     print_infeasible_neighbor(customer, neighbor, capacity)

        if len(LA_neighbors) >= LA_n_count:
            return LA_neighbors

    return LA_neighbors


def find_all_LA_neighbors(customers, LA_n_count, capacity):
    for i in range(0, len(customers)):
        customers[i].LA_neighbors.update(find_LA_neighbors_for(
            i, LA_n_count, customers, capacity))
