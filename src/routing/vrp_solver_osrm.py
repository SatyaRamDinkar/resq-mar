"""
OR-Tools Vehicle Routing Problem Solver equipped with OSRM real-road distances.
"""
from typing import List, Dict, Any
from src.routing.osrm_client import OSRMClient
from src.routing.distance_matrix import build_distance_matrix, format_matrix_for_ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

class VRPSolverOSRM:
    """Solves the Vehicle Routing Problem using actual OSRM road distances."""
    
    def __init__(self, osrm_client: OSRMClient = None):
        self.osrm_client = osrm_client if osrm_client else OSRMClient()

    def solve_with_osrm(self, incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Solves routing for the given resources to incidents.
        Uses a combined distance matrix (Resources + Incidents).
        """
        # Node 0..R-1 are resources (vehicles)
        # Node R..R+I-1 are incidents
        locations = resources + incidents
        
        matrix_result = build_distance_matrix(locations, self.osrm_client)
        distance_matrix_m = matrix_result["matrix"]
        duration_matrix_s = matrix_result["durations"]
        
        # Convert distances to integers for OR-Tools
        ortools_matrix = format_matrix_for_ortools(distance_matrix_m)
        
        num_vehicles = len(resources)
        # Simplified: all vehicles start at their respective indices, and end at 0 (dummy) or their own index
        # We will set start nodes to their respective indices
        starts = list(range(num_vehicles))
        ends = starts.copy()  # return to depot
        
        manager = pywrapcp.RoutingIndexManager(len(locations), num_vehicles, starts, ends)
        routing = pywrapcp.RoutingModel(manager)
        
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return ortools_matrix[from_node][to_node]
            
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add penalty for dropping visits (incidents)
        for i in range(num_vehicles, len(locations)):
            routing.AddDisjunction([manager.NodeToIndex(i)], 1000000)
            
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_parameters.time_limit.seconds = 2
        
        solution = routing.SolveWithParameters(search_parameters)
        
        routes = []
        if solution:
            for vehicle_id in range(num_vehicles):
                index = routing.Start(vehicle_id)
                route_dist = 0
                route_dur = 0
                route_nodes = []
                while not routing.IsEnd(index):
                    node = manager.IndexToNode(index)
                    route_nodes.append(locations[node]["id"])
                    previous_index = index
                    index = solution.Value(routing.NextVar(index))
                    next_node = manager.IndexToNode(index)
                    
                    dist = distance_matrix_m[node][next_node]
                    dur = duration_matrix_s[node][next_node]
                    route_dist += dist if dist < 999999 else 0
                    route_dur += dur if dur < 999999 else 0
                    
                routes.append({
                    "vehicle_id": resources[vehicle_id]["id"],
                    "route": route_nodes,
                    "distance_km": round(route_dist / 1000.0, 2),
                    "duration_min": round(route_dur / 60.0, 1)
                })
                
        return {
            "routes": routes,
            "distance_source": matrix_result["source"],
            "total_vehicles_used": sum(1 for r in routes if len(r["route"]) > 1)
        }
