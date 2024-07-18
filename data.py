import numpy as np
import math
import csv
from models.customer_model import Customer


def generate_data(n_customers):
    np.random.seed(42)  # For reproducibility

    # Generate random costs, demands, and time windows
    cost = np.random.randint(10, 100, size=(
        n_customers + 1, n_customers + 1)).tolist()
    demand = [0] + np.random.randint(1, 10, size=n_customers).tolist()
    capacity = 50
    travel_time = np.random.randint(1, 10, size=(
        n_customers + 1, n_customers + 1)).tolist()
    time_window_start = [np.random.randint(
        10, 20) for _ in range(n_customers + 1)]
    time_window_end = [
        start - np.random.randint(1, 5) for start in time_window_start]

    # Ensure no self-loop
    for i in range(n_customers + 1):
        cost[i][i] = 0
        travel_time[i][i] = 0

    t_0 = max(time_window_end) + max(travel_time[0])

    # Print data generated to terminal
    # print("n_customers =", n_customers)
    # print("cost =", cost)
    # print("demand =", demand)
    # print("capacity =", capacity)
    # print("travel_time =", travel_time)
    # print("time_window_start =", time_window_start)
    # print("time_window_end =", time_window_end)

    # for i in range(1, n_customers + 1):
    #     print(
    #         f"customer {i}: [{time_window_start[i]} - {time_window_end[i]}]")

    return n_customers, cost, demand, travel_time, time_window_start, time_window_end, capacity, t_0


def get_data_from_set(data_set, num_customers):
    file_name = f'./data_sets/{data_set}'
    with open(file_name, 'r') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',',
                               quoting=csv.QUOTE_NONNUMERIC)
        data = [row for row in csvreader if row[0] < num_customers + 2]

    t_0 = data[0][5]
    n_customers = len(data) - 1
    cost = []
    demand = []
    travel_time = []
    time_window_start = []
    time_window_end = []
    travel_speed = 1

    for row in data:
        demand.append(row[3])
        time_window_start.append(t_0 - row[4])
        time_window_end.append(t_0 - row[5])
        cost.append([])
        travel_time.append([])
        for destination in data:
            distance = math.sqrt((row[1] - destination[1]) ** 2 +
                                 (row[2] - destination[2]) ** 2)
            distance = round(distance, 2)
            time = (distance / travel_speed) + row[6]
            cost[len(cost) - 1].append(distance)
            travel_time[len(travel_time) - 1].append(time)

    return n_customers, cost, demand, travel_time, time_window_start, time_window_end, t_0


def load_data(data_set, num_customers, capacity):
    n_customers, cost, demand, travel_time, time_window_start, time_window_end, t_0 = get_data_from_set(
        data_set, num_customers=num_customers)

    customers = []

    # Build Customer Objects
    for c in range(1, n_customers + 1):
        newCustomer = Customer(c, cost[c], demand[c],
                               travel_time[c], time_window_start[c], time_window_end[c], c)
        customers.append(newCustomer)

    start_depot = Customer("Start", cost[0], 0, travel_time[0], t_0, t_0, 0)
    end_depot = Customer("End", cost[0], 0, travel_time[0], t_0, 0, 0)

    return customers, start_depot, end_depot, capacity


def verify_data(data_sets):
    for data_set in data_sets:
        file_name = f'./data_sets/{data_set}'
        with open(file_name, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',',
                                   quoting=csv.QUOTE_NONNUMERIC)
            data = [row for row in csvreader]

            data_is_good = True
            i = 0
            while data_is_good and i < len(data):
                if len(data[i]) != 7:
                    data_is_good = False

                i += 1

            if data_is_good:
                print("✅" + data_set + "Data processed correctly")
            else:
                print("❌" + data_set + "Data processing failed")


# verify_data(["rc101.csv", "rc102.csv", "rc103.csv", "rc104.csv",
#             "rc105.csv", "rc106.csv", "rc107.csv", "rc108.csv"])
