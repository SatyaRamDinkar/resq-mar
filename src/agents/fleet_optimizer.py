"""
FleetOptimizer Agent: Global Multi-Ambulance Multi-Depot Fleet Coordination.
Uses Google OR-Tools to solve the Capacitated Vehicle Routing Problem (CVRP)
across multiple hospital depots and simultaneous disaster incidents.
"""
import math
import time
from typing import List, Dict, Any, Optional

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

from src.routing.osrm_client import OSRMClient


class FleetOptimizer:
    """
    FleetOptimizer coordinates an entire emergency fleet across multiple hospital
    depots and simultaneous disaster incidents.
    
    Features:
      - Multi-Depot Capacitated Vehicle Routing Problem (CVRP) formulation.
      - Dynamic distance/duration matrix via local OSRM (with offline Haversine fallback).
      - Strict capacity constraint enforcement (maximum patients per ambulance).
      - Minimizes global fleet response time and eliminates duplicate/redundant dispatches.
      - Returns structured JSON with per-vehicle routes, waypoint ETAs, and incident assignments.
    """

    def __init__(self, osrm_client: Optional[OSRMClient] = None, default_speed_kmh: float = 40.0):
        """
        Initialize the FleetOptimizer.
        
        Args:
            osrm_client: Client for local OSRM instance. If None, instantiates a default client.
            default_speed_kmh: Fallback vehicle speed for ETA calculations if OSRM is offline.
        """
        self.osrm_client = osrm_client if osrm_client is not None else OSRMClient()
        self.default_speed_kmh = default_speed_kmh

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in meters."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
        return R * c

    def _estimate_duration(self, distance_m: float) -> float:
        """Estimate duration in seconds based on default speed."""
        speed_mps = max(1.0, self.default_speed_kmh * (1000.0 / 3600.0))
        # Add 20% road winding factor for straight-line haversine
        return (distance_m * 1.20) / speed_mps

    def _build_cost_matrix(self, locations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct NxN distance and duration matrices for all nodes (depots + incidents).
        Tries OSRM first; if unavailable, falls back to Haversine.
        """
        n = len(locations)
        dist_matrix = [[0.0] * n for _ in range(n)]
        dur_matrix = [[0.0] * n for _ in range(n)]
        source = "osrm"

        # Check if OSRM is available
        if getattr(self.osrm_client, "available", False):
            try:
                matrix_res = self.osrm_client.get_distance_matrix(origins=locations, destinations=locations)
                if matrix_res and "distances" in matrix_res and matrix_res["distances"]:
                    dist_matrix = matrix_res["distances"]
                    dur_matrix = matrix_res["durations"]
                    source = matrix_res.get("source", "osrm")
                    return {
                        "distances": dist_matrix,
                        "durations": dur_matrix,
                        "source": source
                    }
            except Exception:
                source = "haversine_offline"
        else:
            source = "haversine_offline"

        # Offline fallback: compute pairwise haversine distances & durations
        for i in range(n):
            for j in range(n):
                if i != j:
                    d_m = self._haversine(
                        locations[i]["lat"], locations[i]["lon"],
                        locations[j]["lat"], locations[j]["lon"]
                    )
                    dist_matrix[i][j] = d_m
                    dur_matrix[i][j] = self._estimate_duration(d_m)

        return {
            "distances": dist_matrix,
            "durations": dur_matrix,
            "source": source
        }

    def optimize_fleet(
        self,
        incidents: List[Dict[str, Any]],
        hospital_depots: List[Dict[str, Any]],
        vehicle_capacities: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Solves the Multi-Depot Capacitated Vehicle Routing Problem (CVRP).

        Args:
            incidents: List of incident dicts, each containing:
                - 'id' (str)
                - 'lat' (float), 'lon' (float)
                - 'demand' (int, default=1): Number of patients or units required.
                - 'priority' (int, optional): 1=Critical, 2=High, 3=Medium.
            hospital_depots: List of hospital depot dicts, each containing:
                - 'id' (str)
                - 'lat' (float), 'lon' (float)
                - 'name' (str, optional)
            vehicle_capacities: Specification of vehicle fleet:
                - List of ints: e.g. [2, 2, 4] (distributed across depots).
                - List of dicts: [{'id': 'Amb_1', 'hospital_id': 'Hosp_A', 'capacity': 2}, ...]
                - If None: Defaults to 1 ambulance per hospital depot with capacity 2.

        Returns:
            Dict[str, Any] containing:
                - 'status': OPTIMAL, FEASIBLE, or FAILED
                - 'total_distance_km': float
                - 'total_duration_min': float
                - 'vehicle_routes': List of detailed per-vehicle dispatch routes
                - 'unassigned_incidents': List of incident IDs that couldn't be served
                - 'incident_assignments': Mapping of incident_id -> assigned vehicle & ETA
                - 'fleet_utilization_percent': float
                - 'routing_source': 'osrm' or 'haversine_offline'
        """
        # Edge case: No incidents to serve
        if not incidents:
            return {
                "status": "OPTIMAL",
                "total_distance_km": 0.0,
                "total_duration_min": 0.0,
                "vehicle_routes": [],
                "unassigned_incidents": [],
                "incident_assignments": {},
                "fleet_utilization_percent": 0.0,
                "routing_source": "none",
                "message": "No incidents to optimize."
            }

        # Edge case: No hospital depots available
        if not hospital_depots:
            return {
                "status": "FAILED",
                "error": "No hospital depots provided.",
                "total_distance_km": 0.0,
                "total_duration_min": 0.0,
                "vehicle_routes": [],
                "unassigned_incidents": [inc.get("id", str(idx)) for idx, inc in enumerate(incidents)],
                "incident_assignments": {},
                "fleet_utilization_percent": 0.0,
                "routing_source": "none"
            }

        num_depots = len(hospital_depots)
        depot_id_to_idx = {depot["id"]: idx for idx, depot in enumerate(hospital_depots)}

        # --- Step 1: Normalize Vehicles & Capacities ---
        vehicles: List[Dict[str, Any]] = []
        if vehicle_capacities is None:
            # Default: 1 vehicle per hospital depot, capacity 2
            for idx, depot in enumerate(hospital_depots):
                vehicles.append({
                    "id": f"Amb_{depot['id']}_1",
                    "depot_idx": idx,
                    "hospital_id": depot["id"],
                    "capacity": 2
                })
        elif isinstance(vehicle_capacities, list):
            if all(isinstance(v, dict) for v in vehicle_capacities):
                for idx, v in enumerate(vehicle_capacities):
                    h_id = v.get("hospital_id", hospital_depots[idx % num_depots]["id"])
                    d_idx = depot_id_to_idx.get(h_id, idx % num_depots)
                    vehicles.append({
                        "id": v.get("id", f"Amb_{idx + 1}"),
                        "depot_idx": d_idx,
                        "hospital_id": h_id,
                        "capacity": int(v.get("capacity", 2))
                    })
            else:
                # List of integer capacities
                for idx, cap in enumerate(vehicle_capacities):
                    d_idx = idx % num_depots
                    h_id = hospital_depots[d_idx]["id"]
                    vehicles.append({
                        "id": f"Amb_{h_id}_{idx + 1}",
                        "depot_idx": d_idx,
                        "hospital_id": h_id,
                        "capacity": int(cap)
                    })
        elif isinstance(vehicle_capacities, int):
            for idx, depot in enumerate(hospital_depots):
                vehicles.append({
                    "id": f"Amb_{depot['id']}_1",
                    "depot_idx": idx,
                    "hospital_id": depot["id"],
                    "capacity": vehicle_capacities
                })

        num_vehicles = len(vehicles)
        if num_vehicles == 0:
            return {
                "status": "FAILED",
                "error": "No vehicles available in fleet.",
                "total_distance_km": 0.0,
                "total_duration_min": 0.0,
                "vehicle_routes": [],
                "unassigned_incidents": [inc["id"] for inc in incidents],
                "incident_assignments": {},
                "fleet_utilization_percent": 0.0,
                "routing_source": "none"
            }

        # --- Step 2: Combine Locations (Depots first, then Incidents) ---
        # Nodes 0 .. num_depots - 1 are Hospital Depots
        # Nodes num_depots .. num_depots + num_incidents - 1 are Incidents
        locations: List[Dict[str, Any]] = []
        for depot in hospital_depots:
            locations.append({
                "id": depot["id"],
                "lat": float(depot["lat"]),
                "lon": float(depot["lon"]),
                "type": "depot",
                "demand": 0
            })

        for inc in incidents:
            locations.append({
                "id": inc["id"],
                "lat": float(inc["lat"]),
                "lon": float(inc["lon"]),
                "type": "incident",
                "demand": int(inc.get("demand", 1)),
                "priority": int(inc.get("priority", 1))
            })

        num_locations = len(locations)

        # --- Step 3: Build Cost Matrix ---
        cost_data = self._build_cost_matrix(locations)
        dist_matrix = cost_data["distances"]
        dur_matrix = cost_data["durations"]
        routing_source = cost_data["source"]

        # Convert durations to integer seconds for OR-Tools arc cost
        cost_matrix: List[List[int]] = []
        for row in dur_matrix:
            int_row = []
            for val in row:
                if val is None or val > 9999999:
                    int_row.append(9999999)
                else:
                    int_row.append(int(round(val)))
            cost_matrix.append(int_row)

        # --- Step 4: Configure OR-Tools Multi-Depot Model ---
        starts = [v["depot_idx"] for v in vehicles]
        ends = [v["depot_idx"] for v in vehicles]

        manager = pywrapcp.RoutingIndexManager(num_locations, num_vehicles, starts, ends)
        routing = pywrapcp.RoutingModel(manager)

        # Transit Callback (Arc Cost = Travel Duration in seconds)
        def travel_time_callback(from_index: int, to_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return cost_matrix[from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(travel_time_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Capacity Dimension
        def demand_callback(from_index: int) -> int:
            from_node = manager.IndexToNode(from_index)
            return locations[from_node]["demand"]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        vehicle_capacities_list = [v["capacity"] for v in vehicles]

        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            vehicle_capacities_list,  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity"
        )

        # Disjunction on Incidents (Allows dropping incidents if capacity overflows, with heavy penalty)
        # Priority penalty: Critical (priority 1) = higher penalty to encourage serving first
        for inc_idx in range(num_depots, num_locations):
            priority = locations[inc_idx].get("priority", 1)
            penalty = 1000000 * max(1, 4 - priority)
            routing.AddDisjunction([manager.NodeToIndex(inc_idx)], penalty)

        # Search Parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.seconds = 2

        # --- Step 5: Solve Optimization ---
        solution = routing.SolveWithParameters(search_parameters)

        if not solution:
            # Fallback if solver fails to find any feasible assignment
            return {
                "status": "FAILED",
                "error": "OR-Tools solver could not find a feasible solution.",
                "total_distance_km": 0.0,
                "total_duration_min": 0.0,
                "vehicle_routes": [],
                "unassigned_incidents": [inc["id"] for inc in incidents],
                "incident_assignments": {},
                "fleet_utilization_percent": 0.0,
                "routing_source": routing_source
            }

        # --- Step 6: Parse Solution & Extract Detailed Routes ---
        vehicle_routes = []
        assigned_incident_ids = set()
        incident_assignments = {}
        global_distance_m = 0.0
        global_duration_s = 0.0

        for vehicle_idx in range(num_vehicles):
            v_info = vehicles[vehicle_idx]
            index = routing.Start(vehicle_idx)
            route_stops = []
            route_dist_m = 0.0
            route_dur_s = 0.0
            patients_served = 0
            incident_ids_served = []

            while not routing.IsEnd(index):
                node = manager.IndexToNode(index)
                loc_data = locations[node]

                # Calculate step metrics to next node
                next_index = solution.Value(routing.NextVar(index))
                next_node = manager.IndexToNode(next_index)

                step_dist = dist_matrix[node][next_node]
                step_dur = dur_matrix[node][next_node]

                route_stops.append({
                    "node_id": loc_data["id"],
                    "type": loc_data["type"],
                    "lat": loc_data["lat"],
                    "lon": loc_data["lon"],
                    "demand": loc_data["demand"],
                    "cumulative_duration_min": round(route_dur_s / 60.0, 1),
                    "cumulative_distance_km": round(route_dist_m / 1000.0, 2)
                })

                if loc_data["type"] == "incident":
                    assigned_incident_ids.add(loc_data["id"])
                    incident_ids_served.append(loc_data["id"])
                    patients_served += loc_data["demand"]
                    incident_assignments[loc_data["id"]] = {
                        "vehicle_id": v_info["id"],
                        "hospital_id": v_info["hospital_id"],
                        "eta_min": round(route_dur_s / 60.0, 1),
                        "demand": loc_data["demand"],
                        "priority": loc_data.get("priority", 1)
                    }

                route_dist_m += step_dist
                route_dur_s += step_dur
                index = next_index

            # Final return stop (back to depot)
            final_node = manager.IndexToNode(index)
            final_loc = locations[final_node]
            route_stops.append({
                "node_id": final_loc["id"],
                "type": final_loc["type"],
                "lat": final_loc["lat"],
                "lon": final_loc["lon"],
                "demand": 0,
                "cumulative_duration_min": round(route_dur_s / 60.0, 1),
                "cumulative_distance_km": round(route_dist_m / 1000.0, 2)
            })

            global_distance_m += route_dist_m
            global_duration_s += route_dur_s

            vehicle_routes.append({
                "vehicle_id": v_info["id"],
                "hospital_id": v_info["hospital_id"],
                "capacity": v_info["capacity"],
                "patients_served": patients_served,
                "utilization_percent": round((patients_served / v_info["capacity"]) * 100.0, 1) if v_info["capacity"] > 0 else 0.0,
                "total_distance_km": round(route_dist_m / 1000.0, 2),
                "total_duration_min": round(route_dur_s / 60.0, 1),
                "incident_ids": incident_ids_served,
                "stops": route_stops
            })

        all_incident_ids = [inc["id"] for inc in incidents]
        unassigned_incidents = [i_id for i_id in all_incident_ids if i_id not in assigned_incident_ids]

        total_capacity = sum(v["capacity"] for v in vehicles)
        total_demand_served = sum(r["patients_served"] for r in vehicle_routes)
        fleet_utilization = round((total_demand_served / total_capacity) * 100.0, 1) if total_capacity > 0 else 0.0

        solver_status = "OPTIMAL" if len(unassigned_incidents) == 0 else "FEASIBLE"

        return {
            "status": solver_status,
            "total_distance_km": round(global_distance_m / 1000.0, 2),
            "total_duration_min": round(global_duration_s / 60.0, 1),
            "total_vehicles_active": sum(1 for r in vehicle_routes if len(r["incident_ids"]) > 0),
            "total_vehicles_fleet": num_vehicles,
            "fleet_utilization_percent": fleet_utilization,
            "vehicle_routes": vehicle_routes,
            "incident_assignments": incident_assignments,
            "unassigned_incidents": unassigned_incidents,
            "routing_source": routing_source
        }
