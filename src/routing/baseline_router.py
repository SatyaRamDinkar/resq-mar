"""
Baseline routers for benchmarking against AET Routing.
Includes ContinuousRouter (always re-optimizes) and StaticRouter (never re-optimizes).
"""
import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.routing.vrp_solver import VRPSolver


class ContinuousRouter:
    """
    Re-optimizes after EVERY new incident.
    Acts as an upper-bound for route optimality, but a lower-bound for computational efficiency.
    """
    
    def __init__(self, solver: VRPSolver):
        self.solver = solver
        self.depot: Dict[str, Any] = {}
        self.vehicles: List[Dict[str, Any]] = []
        
        self.current_routes: List[Any] = []
        self.current_demands: Dict[str, Dict[str, Any]] = {}
        self.solver_call_count: int = 0
        self.incident_history: List[Dict[str, Any]] = []
        self.unassigned: List[str] = []

    def setup(self, depot: Dict[str, Any], vehicles: List[Dict[str, Any]]):
        self.depot = depot
        self.vehicles = vehicles
        self.reset()

    def reset(self):
        self.current_routes = []
        self.current_demands = {}
        self.solver_call_count = 0
        self.incident_history = []
        self.unassigned = []

    def add_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        self.incident_history.append(incident)
        self.current_demands[incident["id"]] = incident
        
        # Always re-optimize
        from src.routing.models import Location, Vehicle
        locations_data = [self.depot] + list(self.current_demands.values())
        locations = [Location(**loc) for loc in locations_data]
        vehicles = [Vehicle(**v) for v in self.vehicles]
        result = self.solver.solve(locations, vehicles, self.depot["id"])
        self.solver_call_count += 1
        
        self.current_routes = result.routes
        self.unassigned = result.unassigned
        
        return {
            "triggered": True,
            "reason": "Continuous re-optimization",
            "solver_status": result.solver_status
        }

    def get_stats(self) -> Dict[str, Any]:
        total_dist = sum(r.total_distance_km for r in self.current_routes)
        avg_time = sum(r.estimated_time_min for r in self.current_routes) / max(len(self.current_routes), 1)
        
        return {
            "total_incidents": len(self.incident_history),
            "solver_calls": self.solver_call_count,
            "solver_call_rate": self.solver_call_count / max(len(self.incident_history), 1),
            "total_distance_km": total_dist,
            "unassigned_count": len(self.unassigned),
            "avg_route_time_min": avg_time
        }


class StaticRouter:
    """
    Re-optimizes ONLY on the very first incident.
    All subsequent incidents are simply dumped into the unassigned queue.
    Acts as a lower-bound for optimality (highly inefficient operations).
    """
    
    def __init__(self, solver: VRPSolver):
        self.solver = solver
        self.depot: Dict[str, Any] = {}
        self.vehicles: List[Dict[str, Any]] = []
        
        self.current_routes: List[Any] = []
        self.current_demands: Dict[str, Dict[str, Any]] = {}
        self.solver_call_count: int = 0
        self.incident_history: List[Dict[str, Any]] = []
        self.unassigned: List[str] = []

    def setup(self, depot: Dict[str, Any], vehicles: List[Dict[str, Any]]):
        self.depot = depot
        self.vehicles = vehicles
        self.reset()

    def reset(self):
        self.current_routes = []
        self.current_demands = {}
        self.solver_call_count = 0
        self.incident_history = []
        self.unassigned = []

    def add_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        self.incident_history.append(incident)
        
        if self.solver_call_count == 0:
            self.current_demands[incident["id"]] = incident
            from src.routing.models import Location, Vehicle
            locations_data = [self.depot] + list(self.current_demands.values())
            locations = [Location(**loc) for loc in locations_data]
            vehicles = [Vehicle(**v) for v in self.vehicles]
            result = self.solver.solve(locations, vehicles, self.depot["id"])
            
            self.solver_call_count += 1
            self.current_routes = result.routes
            self.unassigned = result.unassigned
            
            return {
                "triggered": True,
                "reason": "First incident initialization",
                "solver_status": result.solver_status
            }
        else:
            # Never re-optimize again, queue forever
            if incident["id"] not in self.unassigned:
                self.unassigned.append(incident["id"])
                
            return {
                "triggered": False,
                "reason": "Static routing ignores new incidents",
                "solver_status": "SKIPPED"
            }

    def get_stats(self) -> Dict[str, Any]:
        total_dist = sum(r.total_distance_km for r in self.current_routes)
        avg_time = sum(r.estimated_time_min for r in self.current_routes) / max(len(self.current_routes), 1)
        
        return {
            "total_incidents": len(self.incident_history),
            "solver_calls": self.solver_call_count,
            "solver_call_rate": self.solver_call_count / max(len(self.incident_history), 1),
            "total_distance_km": total_dist,
            "unassigned_count": len(self.unassigned),
            "avg_route_time_min": avg_time
        }
