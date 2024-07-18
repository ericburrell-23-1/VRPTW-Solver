def print_infeasible_neighbor(customer, neighbor, capacity):
    if capacity - neighbor.demand > customer.demand:
        print(
            f"Customer {customer.index} -> Neighbor {neighbor.index}  Time violation ({customer.time_window_start} - {customer.travel_time[neighbor.index]} > {neighbor.time_window_end})")
    else:
        print(
            f"Customer {customer.index} -> Neighbor {neighbor.index}  Capacity violation ({capacity} - {neighbor.demand} > {customer.demand})")


def print_LA_neighbors_for(customer, capacity):
    print(f"Capacity: {capacity} Customer {customer.id} start window time: {customer.time_window_start}, demand: {customer.demand}")
    for neighbor in customer.LA_neighbors:
        j = neighbor.index
        print(
            f"Customer {j} is an LA-Neighbor at {customer.cost[j]} distance away. His travel time is {customer.travel_time[j]} and end window time is {neighbor.time_window_end}, and his demand is {neighbor.demand}.")
