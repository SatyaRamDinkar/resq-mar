"""
RouterAgent: Converts task plans into optimized vehicle routes using OR-Tools.
Dependencies: pyautogen, ortools, pydantic
"""
import os
import sys
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.base_agent import ResQAgent
from src.routing.models import Location, Vehicle, RoutingResult
from src.routing.vrp_solver import VRPSolver


class RouterAgent(ResQAgent):
    """
    RouterAgent converts a PlannerAgent task plan into an optimized vehicle routing
    solution using the Google OR-Tools VRP solver.

    Unlike other agents, the RouterAgent does NOT call the LLM for routing decisions.
    The LLM (via ResQAgent) is only available if route explanations are requested.
    The actual optimization is handled deterministically by VRPSolver.

    Test Cases:
        1. Fire incident with 3 locations, 2 ambulances:
           - Expect both vehicles get distinct routes across the 3 demand sites.
        2. Flood incident with 5 locations, 1 rescue truck with limited capacity:
           - Expect some locations to be marked as unassigned due to capacity overflow.
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the RouterAgent.

        Args:
            llm_config (Dict[str, Any]): LLM configuration for optional explanation tasks.
        """
        system_message = (
            "You are the Logistics Router for an emergency response system. "
            "Given a task plan with locations and resource requirements, formulate a "
            "Vehicle Routing Problem and solve it using OR-Tools. "
            "You must output a JSON object with optimized routes."
        )
        super().__init__(name="RouterAgent", system_message=system_message, llm_config=llm_config)
        self.vrp_solver = VRPSolver()

    def plan_routes(
        self,
        task_plan: Dict[str, Any],
        locations: List[Dict[str, Any]],
        vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Convert a task plan and raw location/vehicle dicts into an optimized
        routing solution via OR-Tools.

        Args:
            task_plan (Dict[str, Any]): Output from PlannerAgent, containing keys:
                - tasks, resources_needed, estimated_total_time_min, sops_referenced
            locations (List[Dict]): List of location dicts. The first entry with demand=0
                is assumed to be the depot. Each dict must contain:
                - id (str), lat (float), lon (float), demand (int), priority (int)
            vehicles (List[Dict]): List of vehicle dicts. Each must contain:
                - id (str), capacity (int), start_location_id (str)

        Returns:
            Dict[str, Any]: Routing result containing:
                - routes (list): Per-vehicle optimized routes
                - unassigned (list): Location IDs that couldn't be served
                - solver_status (str): OPTIMAL / FEASIBLE / FAILED
                - total_distance_km (float): Sum of all route distances
        """
        try:
            # --- Step 1: Convert dicts to Pydantic models ---
            location_objects: List[Location] = [Location(**loc) for loc in locations]
            vehicle_objects: List[Vehicle] = [Vehicle(**veh) for veh in vehicles]

            # --- Step 2: Identify the depot (first zero-demand location) ---
            depot_id = next(
                (loc.id for loc in location_objects if loc.demand == 0),
                location_objects[0].id  # fallback: use first location
            )

            # --- Step 3: Run the OR-Tools VRP solver ---
            result: RoutingResult = self.vrp_solver.solve(
                locations=location_objects,
                vehicles=vehicle_objects,
                depot_id=depot_id
            )

            # --- Step 4: Convert result to a plain JSON-friendly dict ---
            total_distance_km = round(
                sum(r.total_distance_km for r in result.routes), 3
            )

            output = {
                "routes": [
                    {
                        "vehicle_id": r.vehicle_id,
                        "location_ids": r.location_ids,
                        "total_distance_km": r.total_distance_km,
                        "estimated_time_min": r.estimated_time_min,
                        "total_demand": r.total_demand,
                    }
                    for r in result.routes
                ],
                "unassigned": result.unassigned,
                "solver_status": result.solver_status,
                "total_distance_km": total_distance_km,
            }

            self.log_action("plan_routes", {"depot_id": depot_id, "num_locations": len(locations)}, output)
            return output

        except Exception as e:
            error_output = {
                "error": "routing_failed",
                "details": str(e),
                "routes": [],
                "unassigned": [loc.get("id", "?") for loc in locations if loc.get("demand", 0) > 0],
                "solver_status": "FAILED",
                "total_distance_km": 0.0,
                "fallback": "manual_dispatch_required"
            }
            self.log_action("plan_routes_error", {"error": str(e)}, error_output)
            return error_output
