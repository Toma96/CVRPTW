import math


def euclidean_distance(pos_a, pos_b):
    return math.ceil(math.sqrt((pos_a.x - pos_b.x)**2 + (pos_a.y - pos_b.y)**2))


def unceiled_distance(pos_a, pos_b):
    return math.sqrt((pos_a.x - pos_b.x)**2 + (pos_a.y - pos_b.y)**2)


class Position:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str(self.x) + " " + str(self.y)


class Vehicle:

    def __init__(self, pid, capacity, position):
        self.pid = pid
        self.capacity = capacity
        self.position = position
        self.time = 0
        self.route = []
        self.route_costs = []
        self.total_distance = 0

    def __repr__(self):
        return "Vehicle " + str(self.pid)

    def load(self, capacity):
        if self.capacity - capacity < 0:
            raise NotEnoughCapacityError("Not enough capacity in Vehicle!")
        else:
            self.capacity -= capacity

    def move(self, position):
        self.time += euclidean_distance(self.position, position)
        self.total_distance += unceiled_distance(self.position, position)
        self.position = position

    def process_customer(self, customer):
        if customer.due_date >= self.time >= customer.ready_time:
            self.time += customer.service_time
        else:
            raise NotInTimeError("Can't process the customer in that time window!")

    def add_customer(self, customer):
        self.route.append(customer)
        self.load(customer.demand)
        self.move(customer.position)
        self.wait_until_ready(customer)
        self.process_customer(customer)
        self.update_route_costs()

    def fits(self, customer):
        if self.capacity - customer.demand < 0:
            return False
        if self.time + euclidean_distance(self.position, customer.position) > customer.due_date:
            return False
        return True

    def wait_until_ready(self, customer):
        if customer.ready_time > self.time:
            self.time += (customer.ready_time - self.time)

    def get_ready_time(self, customer):
        if customer.ready_time > self.time:
            return customer.ready_time - self.time
        else:
            return 0

    def update_route_costs(self):
        self.route_costs.append(self.time)

    def get_cost_until(self, index):
        return self.route_costs[index]

    # def reset(self, capacity, position):
    #     self.route = [0]
    #     self.route_costs = [0]
    #     self.time = 0
    #     self.capacity = capacity
    #     self.position = position

    def remove_from_route(self, index):
        if index == 0 or index == len(self.route) - 1:
            raise IndexError("First and last customer (depot) cannot be removed from route!")
        new_route = self.route.copy()
        new_route.pop(index)
        if self.is_route_feasible(new_route):
            self.route = new_route

    def insert_into_route(self, customer, index):
        if customer.pid != 0 and customer in self.route:
            return False
        new_route = self.route.copy()
        new_route.insert(index, customer)
        if self.is_route_feasible(new_route):
            self.route = new_route
            return True
        else:
            return False

    def is_route_feasible(self, route):
        time = 0
        dist = 0
        capacity = self.capacity + sum([c.demand for c in self.route])
        position = route[0].position
        route_costs = [0]
        for customer in route[1:]:
            time += euclidean_distance(position, customer.position)
            dist += unceiled_distance(position, customer.position)
            if time > customer.due_date:
                return False
            if customer.ready_time > time:
                time += (customer.ready_time - time)
            if capacity - customer.demand < 0:
                return False
            capacity -= customer.demand
            time += customer.service_time
            route_costs.append(time)
            position = customer.position

        self.capacity = capacity
        self.time = time
        self.route_costs = route_costs
        self.total_distance = dist
        return True




class Customer:

    def __init__(self, pid, position, demand, ready_time, due_date, service_time):
        self.pid = pid
        self.position = position
        self.demand = demand
        self.ready_time = ready_time
        self.due_date = due_date
        self.service_time = service_time
        self.is_routed = False if pid != 0 else True

    def __repr__(self):
        return str(self.pid)


class NotEnoughCapacityError(Exception):
    pass


class NotInTimeError(Exception):
    pass
