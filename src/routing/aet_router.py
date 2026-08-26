"""
Adaptive Event-Triggered (AET) Routing Engine.
Re-optimizes routes dynamically based on incoming incidents and capacity thresholds.
"""
import os
import sys
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.routing.vrp_solver import VRPSolver


class AETRouter:
    """
    Adaptive Event-Triggered Router.
    Monitors incoming incidents and re-optimizes routes only when significant
    changes occur, saving computational resources compared to continuous routing.
    """

    def __init__(
        self, 
        solver: VRPSolver, 
        trigger_threshold: float = 0.20, 
        slack_threshold: float = 0.10
    ):
        """
        Initializes the AETRouter.
        
        Args:
            solver (VRPSolver): The underlying OR-Tools VRP solver.
            trigger_threshold (float): Demand fraction threshold to trigger re-optimization.
            slack_threshold (float): Vehicle capacity slack threshold to trigger re-optimization.
        """
        self.solver = solver
        self.trigger_threshold = trigger_threshold
        self.slack_threshold = slack_threshold
        
        self.depot: Dict[str, Any] = {}
        self.vehicles: List[Dict[str, Any]] = []
        
        # State tracking
        self.current_routes: List[Any] = []
        self.current_demands: Dict[str, Dict[str, Any]] = {}
        self.total_demand: int = 0
        self.solver_call_count: int = 0
        self.incident_history: List[Dict[str, Any]] = []
        self.unassigned: List[str] = []

    def setup(self, depot: Dict[str, Any], vehicles: List[Dict[str, Any]]):
        """Sets the fleet and depot configuration."""
        self.depot = depot
        self.vehicles = vehicles
        self.reset()

    def reset(self):
        """Clears all dynamic state for a new simulation run."""
        self.current_routes = []
        self.current_demands = {}
        self.total_demand = 0
        self.solver_call_count = 0
        self.incident_history = []
        self.unassigned = []

    def _check_slack_depletion(self) -> bool:
        """
        Checks if any vehicle's remaining capacity falls below the slack threshold.
        """
        # Create a mapping of vehicle ID to capacity
        v_capacities = {v["id"]: v["capacity"] for v in self.vehicles}
        
        for route in self.current_routes:
            v_cap = v_capacities.get(route.vehicle_id)
            if not v_cap:
                continue
            
            remaining_capacity = v_cap - route.total_demand
            slack_ratio = remaining_capacity / max(v_cap, 1)
            
            if slack_ratio < self.slack_threshold:
                return True
                
        return False

    def _reoptimize(self) -> Any:
        """
        Re-runs the VRP solver with the updated demands.
        """
        from src.routing.models import Location, Vehicle
        
        locations_data = [self.depot] + list(self.current_demands.values())
        locations = [Location(**loc) for loc in locations_data]
        vehicles = [Vehicle(**v) for v in self.vehicles]
        
        # Warm-start could theoretically be injected here. For MVP, we solve from scratch.
        result = self.solver.solve(locations, vehicles, self.depot["id"])
        
        self.solver_call_count += 1
        self.current_routes = result.routes
        
        # Update unassigned list explicitly
        self.unassigned = result.unassigned
        
        return result

    def add_incident(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes a newly arrived incident.
        """
        self.incident_history.append(incident)
        
        # Add to current state
        self.current_demands[incident["id"]] = incident
        self.total_demand += incident.get("demand", 0)
        
        # Trigger Condition 1: Is this incident large relative to the total load?
        # Avoid division by zero
        trigger_demand = (incident.get("demand", 0) / self.total_demand) > self.trigger_threshold if self.total_demand > 0 else True
        
        # Trigger Condition 2: Are vehicles running out of capacity?
        trigger_slack = self._check_slack_depletion()
        
        # Always trigger on the very first incident
        is_first = self.solver_call_count == 0
        
        triggered = trigger_demand or trigger_slack or is_first
        
        if triggered:
            result = self._reoptimize()
            reason = "First incident" if is_first else ("Demand spike" if trigger_demand else "Capacity slack depleted")
            return {
                "triggered": True,
                "reason": reason,
                "solver_status": result.solver_status
            }
        else:
            # Queue for next re-optimization
            if incident["id"] not in self.unassigned:
                self.unassigned.append(incident["id"])
                
            return {
                "triggered": False,
                "reason": f"Incident {incident['id']} queued. Trigger conditions not met.",
                "solver_status": "SKIPPED"
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns benchmark statistics for this router.
        """
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
