"""
Collaborative Truck-Drone VRP Solver.
Extends base VRP routing to include aerial vehicles launched from ground trucks.
"""
import math
from typing import List, Tuple
from src.routing.models import Location, Vehicle, Route, DroneSubRoute, CollaborativeRoutingResult
from src.routing.vrp_solver import VRPSolver

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth."""
    R = 6371.0 # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c


class CollaborativeVRPSolver:
    """
    Solves VRP with heterogeneous fleets (trucks and drones).
    Trucks solve the base VRP for reachable nodes.
    Drones are assigned to blocked nodes from the nearest truck stop.
    """
    
    def __init__(self, base_solver: VRPSolver):
        """
        Initialize with a base VRPSolver instance.
        """
        self.base_solver = base_solver

    def _find_nearest_truck_stop(
        self, blocked_loc: Location, truck_routes: List[Route], locations: List[Location]
    ) -> Tuple[str, str, float]:
        """
        Finds the nearest location in the planned truck routes to the blocked location.
        """
        best_truck = None
        best_loc_id = None
        min_dist = float('inf')
        
        loc_dict = {l.id: l for l in locations}
        
        for route in truck_routes:
            for loc_id in route.location_ids:
                stop_loc = loc_dict.get(loc_id)
                if not stop_loc: 
                    continue
                
                dist = haversine_distance(stop_loc.lat, stop_loc.lon, blocked_loc.lat, blocked_loc.lon)
                if dist < min_dist:
                    min_dist = dist
                    best_truck = route.vehicle_id
                    best_loc_id = loc_id
                    
        return best_truck, best_loc_id, min_dist

    def _drone_flight_feasible(self, drone: Vehicle, flight_distance_km: float, demand: int) -> bool:
        """
        Validates if the drone can fulfill this request (range and payload constraints).
        """
        # Maximum flight range of 5.0 km
        if flight_distance_km > 5.0:
            return False
        # Must carry enough payload
        if demand > drone.capacity:
            return False
        return True

    def solve(
        self, locations: List[Location], trucks: List[Vehicle], drones: List[Vehicle], depot_id: str
    ) -> CollaborativeRoutingResult:
        """
        Executes the collaborative routing strategy.
        """
        # STEP 1: SEPARATE LOCATIONS
        reachable_locations = [loc for loc in locations if not loc.is_roadblocked or loc.id == depot_id]
        blocked_locations = [loc for loc in locations if loc.is_roadblocked and loc.id != depot_id]
        
        # STEP 2: SOLVE TRUCK ROUTES
        truck_res = self.base_solver.solve(reachable_locations, trucks, depot_id)
        truck_routes = truck_res.routes
        unassigned = list(truck_res.unassigned)
        
        # STEP 3: ASSIGN DRONES TO BLOCKED LOCATIONS
        drone_subroutes = []
        available_drones = {d.id: d for d in drones}
        
        # Assign each blocked location to a drone launching from the nearest truck stop
        for b_loc in blocked_locations:
            if not b_loc.drone_accessible:
                unassigned.append(b_loc.id)
                continue
                
            truck_id, stop_loc_id, dist_one_way = self._find_nearest_truck_stop(b_loc, truck_routes, locations)
            
            if not truck_id:
                # No truck route exists
                unassigned.append(b_loc.id)
                continue
                
            flight_distance = round(dist_one_way * 2, 3)
            
            # Find a feasible drone
            assigned_drone = None
            for d_id, drone in available_drones.items():
                if self._drone_flight_feasible(drone, flight_distance, b_loc.demand):
                    assigned_drone = drone
                    break
                    
            if assigned_drone:
                subroute = DroneSubRoute(
                    drone_id=assigned_drone.id,
                    launch_truck_id=truck_id,
                    truck_location_id=stop_loc_id,
                    served_locations=[b_loc.id],
                    flight_distance_km=flight_distance,
                    flight_time_min=int((flight_distance / assigned_drone.speed_kmh) * 60) if assigned_drone.speed_kmh > 0 else 0,
                    payload_delivered=b_loc.demand
                )
                drone_subroutes.append(subroute)
            else:
                unassigned.append(b_loc.id)
                
        # STEP 4: COMBINE RESULTS
        total_truck_dist = sum(r.total_distance_km for r in truck_routes)
        total_drone_dist = sum(ds.flight_distance_km for ds in drone_subroutes)
        total_dist = total_truck_dist + total_drone_dist
        
        total_demand = sum(l.demand for l in locations if l.id != depot_id)
        if total_demand > 0:
            unassigned_demand = sum(l.demand for l in locations if l.id in unassigned)
            coverage = ((total_demand - unassigned_demand) / total_demand) * 100
        else:
            coverage = 100.0
            
        return CollaborativeRoutingResult(
            truck_routes=truck_routes,
            drone_subroutes=drone_subroutes,
            unassigned=unassigned,
            solver_status=truck_res.solver_status,
            total_distance_km=round(total_dist, 3),
            coverage_percentage=round(coverage, 2)
        )
