"""
VRP Solver using Google OR-Tools.
Dependencies: ortools, pydantic
"""
import math
from typing import List, Optional

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from src.routing.models import Location, Vehicle, Route, RoutingResult


class VRPSolver:
    """
    Solves the Vehicle Routing Problem (VRP) using Google OR-Tools.

    For the ResQ-MAR MVP, this implements:
      - Single depot
      - Multiple demand locations
      - Multiple vehicles with capacity constraints
      - Haversine (great-circle) distance metric
      - PATH_CHEAPEST_ARC first-solution heuristic
      - 5-second time limit
    """

    def __init__(self):
        """Initialize the VRP solver. No special OR-Tools setup needed at this stage."""
        pass

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great-circle distance between two points on Earth using the
        Haversine formula.

        Args:
            lat1, lon1: Latitude and longitude of the first point (degrees).
            lat2, lon2: Latitude and longitude of the second point (degrees).

        Returns:
            float: Distance in kilometers.
        """
        R = 6371.0  # Earth's mean radius in km

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        d_phi = math.radians(lat2 - lat1)
        d_lambda = math.radians(lon2 - lon1)

        a = (math.sin(d_phi / 2) ** 2
             + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def _build_distance_matrix(self, locations: List[Location]) -> List[List[int]]:
        """
        Build a full N×N distance matrix (in meters, as integers) for OR-Tools.
        OR-Tools requires integer costs, so we multiply km by 1000 and round.

        Args:
            locations: Ordered list of Location objects.

        Returns:
            List[List[int]]: Square matrix where matrix[i][j] is the distance
                             in meters from location i to location j.
        """
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist_km = self._haversine(
                        locations[i].lat, locations[i].lon,
                        locations[j].lat, locations[j].lon
                    )
                    # Convert to integer meters for OR-Tools
                    matrix[i][j] = int(dist_km * 1000)
        return matrix

    def _extract_routes(
        self,
        solution,
        routing,
        manager,
        locations: List[Location],
        vehicles: List[Vehicle],
        distance_matrix: List[List[int]]
    ) -> List[Route]:
        """
        Walk each vehicle's route through the OR-Tools solution graph and
        convert it into a list of Route Pydantic objects.

        Args:
            solution: The OR-Tools solution object.
            routing: The RoutingModel object.
            manager: The RoutingIndexManager object.
            locations: The ordered list of Location objects.
            vehicles: The list of Vehicle objects.
            distance_matrix: The pre-computed distance matrix in meters.

        Returns:
            List[Route]: One Route per vehicle that was actually used.
        """
        routes = []
        loc_by_index = {i: loc for i, loc in enumerate(locations)}

        for vehicle_idx, vehicle in enumerate(vehicles):
            route_location_ids = []
            total_distance_m = 0
            total_demand = 0

            # OR-Tools: start walking from the depot node for this vehicle
            index = routing.Start(vehicle_idx)

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                loc = loc_by_index[node_index]
                route_location_ids.append(loc.id)
                total_demand += loc.demand

                # Move to the next node and accumulate arc distance
                prev_index = index
                index = solution.Value(routing.NextVar(index))
                total_distance_m += routing.GetArcCostForVehicle(prev_index, index, vehicle_idx)

            # Append the final depot node to close the loop
            node_index = manager.IndexToNode(index)
            route_location_ids.append(loc_by_index[node_index].id)

            # Only record vehicles that actually do work (visited at least one demand node)
            # A route with only 2 stops (depot → depot) means the vehicle was idle.
            if len(route_location_ids) > 2:
                total_distance_km = total_distance_m / 1000.0
                # Estimated time = distance / speed (converting to minutes)
                estimated_time_min = int(
                    (total_distance_km / vehicle.speed_kmh) * 60
                ) if total_distance_km > 0 else 0

                routes.append(Route(
                    vehicle_id=vehicle.id,
                    location_ids=route_location_ids,
                    total_distance_km=round(total_distance_km, 3),
                    estimated_time_min=estimated_time_min,
                    total_demand=total_demand
                ))

        return routes

    def solve(
        self,
        locations: List[Location],
        vehicles: List[Vehicle],
        depot_id: str
    ) -> RoutingResult:
        """
        Solve the Vehicle Routing Problem for the given locations and vehicles.

        Args:
            locations: List of all Location objects (must include the depot).
            vehicles: List of Vehicle objects starting at the depot.
            depot_id: The 'id' field of the depot Location.

        Returns:
            RoutingResult: The optimized routing plan with status.
        """
        # --- STEP 1: Validate input ---
        if not locations or not vehicles:
            return RoutingResult(routes=[], unassigned=[], solver_status="FAILED")

        # Find the depot index in our ordered location list
        depot_index = next(
            (i for i, loc in enumerate(locations) if loc.id == depot_id), None
        )
        if depot_index is None:
            print(f"[VRPSolver] ERROR: Depot ID '{depot_id}' not found in locations.")
            return RoutingResult(routes=[], unassigned=[l.id for l in locations if l.demand > 0], solver_status="FAILED")

        # --- STEP 2: Build distance matrix ---
        distance_matrix = self._build_distance_matrix(locations)

        # --- STEP 3: Create OR-Tools RoutingIndexManager ---
        # Maps between node indices (OR-Tools internal) and location indices (our list)
        manager = pywrapcp.RoutingIndexManager(
            len(locations),   # number of locations
            len(vehicles),    # number of vehicles
            depot_index       # index of the single depot
        )

        # --- STEP 4: Create RoutingModel ---
        routing = pywrapcp.RoutingModel(manager)

        # --- STEP 5: Register transit (distance) callback ---
        # This function tells OR-Tools the cost of moving between any two nodes.
        def distance_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return distance_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)

        # --- STEP 6: Set arc cost evaluator for all vehicles ---
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # --- STEP 7: Add capacity dimension ---
        # This enforces that each vehicle never exceeds its carrying capacity.
        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return locations[from_node].demand

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,                                              # slack_max (no slack)
            [v.capacity for v in vehicles],                 # vehicle capacities
            True,                                           # fix_start_cumul_to_zero
            "Capacity"
        )

        # Allow dropping nodes (locations) if they cannot be assigned to any vehicle.
        # The penalty is set very high so OR-Tools only does this as a last resort.
        penalty = 100_000_000
        for node in range(len(locations)):
            if node != depot_index:
                routing.AddDisjunction([manager.NodeToIndex(node)], penalty)

        # --- STEP 8: Configure search parameters ---
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        # Use PATH_CHEAPEST_ARC as the first solution heuristic — good for emergency routing
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        # Hard 5-second time limit so the demo doesn't hang
        search_parameters.time_limit.FromSeconds(5)

        # --- STEP 9: Solve ---
        solution = routing.SolveWithParameters(search_parameters)

        # --- STEP 10: Extract results ---
        if solution is None:
            print("[VRPSolver] No solution found.")
            return RoutingResult(
                routes=[],
                unassigned=[l.id for l in locations if l.demand > 0],
                solver_status="FAILED"
            )

        # Determine solver quality
        status_map = {
            0: "ROUTING_NOT_SOLVED",
            1: "ROUTING_SUCCESS",       # Optimal
            2: "ROUTING_PARTIAL_SUCCESS_LOCAL_OPTIMUM_NOT_REACHED",
            3: "ROUTING_FAIL",
            4: "ROUTING_FAIL_TIMEOUT",
            5: "ROUTING_INVALID"
        }
        raw_status = routing.status()
        if raw_status == 1:
            solver_status = "OPTIMAL"
        elif raw_status in (2, 4):
            solver_status = "FEASIBLE"
        else:
            solver_status = "FAILED"

        routes = self._extract_routes(solution, routing, manager, locations, vehicles, distance_matrix)

        # Detect any dropped/unassigned nodes
        assigned_ids = {loc_id for route in routes for loc_id in route.location_ids}
        unassigned = [
            loc.id for loc in locations
            if loc.demand > 0 and loc.id not in assigned_ids
        ]

        return RoutingResult(
            routes=routes,
            unassigned=unassigned,
            solver_status=solver_status
        )


if __name__ == "__main__":
    print("=== VRP Solver Demo ===")
    solver = VRPSolver()

    # 1 depot + 5 demand points, 2 vehicles
    demo_locations = [
        Location(id="depot",    lat=12.9716, lon=77.5946, demand=0,  priority=1),
        Location(id="site_A",   lat=12.9730, lon=77.5960, demand=4,  priority=4),
        Location(id="site_B",   lat=12.9700, lon=77.5920, demand=3,  priority=3),
        Location(id="site_C",   lat=12.9750, lon=77.5940, demand=5,  priority=4),
        Location(id="site_D",   lat=12.9680, lon=77.5970, demand=2,  priority=2),
        Location(id="site_E",   lat=12.9760, lon=77.5910, demand=3,  priority=3),
    ]
    demo_vehicles = [
        Vehicle(id="ambulance_1", capacity=10, start_location_id="depot"),
        Vehicle(id="ambulance_2", capacity=10, start_location_id="depot"),
    ]

    result = solver.solve(demo_locations, demo_vehicles, depot_id="depot")
    print(f"Status: {result.solver_status}")
    for route in result.routes:
        print(f"  {route.vehicle_id}: {' → '.join(route.location_ids)}")
        print(f"    Distance: {route.total_distance_km:.3f} km | Time: {route.estimated_time_min} min | Demand: {route.total_demand}")
    if result.unassigned:
        print(f"  Unassigned: {result.unassigned}")
