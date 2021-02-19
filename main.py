from classes import *
import parameters
import time
import numpy as np
import sys
import pdb
import random


def line_contains_digit(line):
    for c in line:
        if c.isdigit():
            return True
    return False


def unassigned_customer_exists(customers):
    for customer in customers:
        if not customer.is_routed:
            return True
    return False


def remove_last_from_route(vehicle, customers, total_cost):
    if len(vehicle.route) > 1:
        cust_index = vehicle.route.pop().pid
        reverse_cost = vehicle.route_costs.pop() - vehicle.route_costs[-1]
        vehicle.time = vehicle.route_costs[-1]
        vehicle.position = customers[cust_index - 1].position
        vehicle.capacity += customers[cust_index].demand
        customers[cust_index].is_routed = False
        return total_cost - reverse_cost
    else:
        print("Can't remove the customer from the vehicle's route.")


def get_used_vehicles(vehicles):
    return list(filter(lambda x: len(x.route) > 2, [v for v in vehicles]))


def get_total_cost(vehicles):
    return sum([vehicle.time for vehicle in vehicles])


def get_number_of_used_vehicles(vehicles):
    return len(list(filter(lambda x: len(x) > 2, [v.route for v in vehicles])))


def get_current_solution(vehicles):
    return [[cust for cust in vehicle.route] for vehicle in vehicles]


def save_solution_to_file(filename, vehicles):
    with open(filename, 'w') as f:
        f.write(str(get_number_of_used_vehicles(vehicles)) + "\n")
        for vehicle in vehicles:
            if len(vehicle.route) > 2:
                f.write("{0}: ".format(vehicle.pid))
                for i, (node, cost) in enumerate(zip(vehicle.route, vehicle.route_costs)):
                    f.write("{0}({1})".format(str(node.pid), str(cost - node.service_time)))
                    if i+1 != len(vehicle.route):
                        f.write("->")
                    else:
                        f.write("\n")
        f.write(str(sum([vehicle.total_distance for vehicle in vehicles])))


def transfer_customer(veh_to_remove, index_remove, veh_to_insert, index_insert):
    customer = veh_to_remove.route[index_remove]
    if veh_to_insert.insert_into_route(customer, index_insert):
        veh_to_remove.remove_from_route(index_remove)
        return True
    return False


if __name__ == '__main__':
    no_instance = int(input("Please state the wanted instance: "))
    instance = 'i' + str(no_instance)
    TXT_EXTENSION = ".txt"
    iter_time = input("Please input iterating time (1m, 5m or un)")

    customers = []
    positions = []
    with open("input_files/" + instance + TXT_EXTENSION, 'r') as f:
        found_vehicle = False
        for line in f.readlines():
            # print(line)
            if not line_contains_digit(line):
                continue
            if not found_vehicle:
                vehicle_number, capacity = line.split()
                vehicle_number = int(vehicle_number)
                capacity = int(capacity)
                found_vehicle = True
                continue
            no, xcoord, ycoord, demand, ready, due, service = line.split()
            position = Position(int(xcoord), int(ycoord))
            positions.append(position)
            if int(no) == 0:
                depot_position = position
                closing_time = int(due)
            # else:
            customers.append(Customer(int(no), position, int(demand), int(ready), int(due), int(service)))

    # print(vehicle_number, capacity)
    # print(depot_position, closing_time)
    # for customer in customers:
    #     print(customer)
    total_cost = 0
    vehicles = [Vehicle(i + 1, capacity, depot_position) for i in range(vehicle_number)]
    servings = {vehicle: [] for vehicle in vehicles}

    distances = np.array([[euclidean_distance(positions[i], positions[j]) for i in range(len(customers))]
                          for j in range(len(customers))], dtype=int)
    # print(distances)
    veh_index = 0


    ### INITIAL SOLUTION ###

    while unassigned_customer_exists(customers):
        candidate = None
        min_cost = np.inf
        curr_vehicle = vehicles[veh_index]

        if not curr_vehicle.route:
            curr_vehicle.add_customer(customers[0])

        for customer in customers[1:]:
            if not customer.is_routed:
                if curr_vehicle.fits(customer):
                    waiting_cost = curr_vehicle.get_ready_time(customer)
                    cand_cost = euclidean_distance(curr_vehicle.position, customer.position) + waiting_cost
                    if curr_vehicle.time + cand_cost + euclidean_distance(customer.position, depot_position) > closing_time:
                        continue
                    if min_cost > cand_cost:
                        min_cost = cand_cost
                        candidate = customer

        if candidate is None:                           # not a single customer fits
            if veh_index + 1 < len(vehicles):           # we have more vehicles to assign
                if curr_vehicle.position != depot_position:
                    end_cost = euclidean_distance(curr_vehicle.position, depot_position)
                    if curr_vehicle.time + end_cost > closing_time:
                        total_cost = remove_last_from_route(curr_vehicle, customers, total_cost)
                        end_cost = euclidean_distance(curr_vehicle.position, depot_position)
                    curr_vehicle.add_customer(customers[0])
                    total_cost += end_cost
                    print(curr_vehicle.time)
                    # if vehicles[veh_index].time > closing_time:
                    #     print("HEREEEEE!!!!")
                    #     print(vehicles[veh_index].route)
                veh_index += 1
            else:
                print("Customers that are left do not fit in any vehicle."
                      " Problem can't be solved under this constraints!", file=sys.stderr)
                sys.exit(1)
        else:
            # print("Candidate {0}".format(candidate))
            candidate.is_routed = True
            curr_vehicle.add_customer(candidate)
            total_cost += min_cost
            # print(veh_index)
            # print(vehicles[veh_index].route)
            # print(vehicles[veh_index].time)

    end_cost = euclidean_distance(vehicles[veh_index].position, depot_position)
    vehicles[veh_index].add_customer(customers[0])
    total_cost += end_cost

    for v in vehicles:
        print("Vehicle {0}".format(v.pid))
        print(v.route)

    save_solution_to_file("initial.txt", vehicles)


    ### ALGORITHM ###

    used_vehicles = get_used_vehicles(vehicles)

    start_time = time.time()
    times = {'1m': 60, '5m': 300, 'un': 1000}
    seconds = times[iter_time]

    incumbent_number = len(used_vehicles)
    incumbent_solution = [[cust for cust in vehicle.route] for vehicle in used_vehicles]
    incumbent_cost = get_total_cost(used_vehicles)

    print(incumbent_number)
    print(incumbent_solution)
    print(incumbent_cost)

    temperature = parameters.INITIAL_TEMPERATURE

    i = 0
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        if elapsed_time > seconds:
            break

        used_vehicles = get_used_vehicles(used_vehicles)
        current_solution = get_current_solution(used_vehicles)
        no_used = get_number_of_used_vehicles(used_vehicles)
        cost = get_total_cost(used_vehicles)

        # veh_to_rmv = random.choice(used_vehicles)
        # veh_to_insert = random.choice(used_vehicles)
        veh_to_rmv, veh_to_insert = random.sample(used_vehicles, 2)
        index_to_remove_from = random.randint(1, len(veh_to_rmv.route) - 2)
        index_to_insert_into = random.randint(1, len(veh_to_insert.route) - 2)

        if transfer_customer(veh_to_rmv, index_to_remove_from, veh_to_insert, index_to_insert_into):
            # check the solution, if it's not better than incumbent, keep it with prob, else keep for sure

            # diff = 1000 * (get_number_of_used_vehicles(vehicles) - no_used)
            # diff += (get_total_cost(used_vehicles) - cost)
            # prob = 1 / (1 + np.exp(diff / temperature))
            # if prob < np.random.random():
            #     reverse = transfer_customer(veh_to_insert, index_to_insert_into, veh_to_rmv, index_to_remove_from)
            #     temperature *= parameters.ALPHA
            #     continue

            if get_number_of_used_vehicles(vehicles) < incumbent_number or \
                    get_number_of_used_vehicles(vehicles) == incumbent_number and get_total_cost(used_vehicles) < incumbent_cost:

                used_vehicles = get_used_vehicles(used_vehicles)
                incumbent_cost = get_total_cost(used_vehicles)
                incumbent_number = get_number_of_used_vehicles(vehicles)
                incumbent_solution = get_current_solution(used_vehicles)
                print(incumbent_number)
                print(incumbent_solution)
                print(incumbent_cost)

            else:
                diff = 1000 * (no_used - get_number_of_used_vehicles(vehicles))
                diff += abs(cost - get_total_cost(used_vehicles))
                prob = np.exp(-diff / temperature)
                if prob < np.random.random():
                    reverse = transfer_customer(veh_to_insert, index_to_insert_into, veh_to_rmv, index_to_remove_from)

            # temperature = temperature / (1 + parameters.BETA * temperature)
            temperature *= parameters.ALPHA
            i += 1

    # print(i)
    vehicles_final = [Vehicle(i+1, capacity, depot_position) for i in range(len(used_vehicles))]
    for i, route in enumerate(incumbent_solution):
        for cust in route:
            vehicles_final[i].add_customer(cust)

    save_solution_to_file("output_files/res-" + iter_time + "-" + instance + TXT_EXTENSION, vehicles_final)

