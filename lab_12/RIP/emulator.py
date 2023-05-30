import json

class Router:
    def __init__(self, ip_address):
        self.ip_address = ip_address
        self.routing_table = {}

    def add_route(self, destination, next_hop, metric):
        self.routing_table[destination] = (next_hop, metric)

    def update_routing_table(self, router):
        for destination, (next_hop, metric) in router.routing_table.items():
            if destination not in self.routing_table or self.routing_table[router.ip_address][1] + metric < self.routing_table[destination][1]:
                self.routing_table[destination] = (router.ip_address, self.routing_table[router.ip_address][1] + metric)

    def print_routing_table(self):
        print(f"Routing table for router {self.ip_address}:")
        print("[Source IP]\t\t[Destination IP]\t[Next Hop]\t\tMetric")
        for source, (next_hop, metric) in self.routing_table.items():
            print(f"{self.ip_address}\t\t{source}\t\t{next_hop}\t\t{metric}")
        print()

def simulate_rip(routers, network_diametr=10):
    num_routers = len(routers)
    converged = False
    iteration = 0
    while not converged and iteration < network_diametr:
        iteration += 1
        converged = True

        print(f"Simulation step {iteration} of RIP")
        print()

        for router_ip, router in routers.items():
            cur_rt = list(router.routing_table.keys())
            for neighbour_router in cur_rt:
                router.update_routing_table(routers[neighbour_router])

        for router_ip1, router1 in routers.items():
            for router_ip2, router2 in routers.items():
                if router_ip1 != router_ip2 and router1.routing_table.keys() != router2.routing_table.keys():
                    converged = False
                    break
            if not converged:
                break

        for router in routers.values():
            router.print_routing_table()

    if converged:
        print("RIP converged.")
    else:
        print("RIP did not converge within the maximum number of iterations.")


def main():
    with open('network_config.json') as file:
        network_config = json.load(file)

    routers = {}
    for router_config in network_config['routers']:
        router = Router(router_config['ip_address'])
        for route in router_config['routes']:
            router.add_route(route['destination'], route['next_hop'], route['metric'])
        routers[router.ip_address] = router

    simulate_rip(routers)

if __name__ == '__main__':
    main()
