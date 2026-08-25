"""
CommsAgent: Generates human-readable dispatch alerts based on the incident plan and routes.
Dependencies: pyautogen
"""
import os
import sys
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.base_agent import ResQAgent


class CommsAgent(ResQAgent):
    """
    CommsAgent formats the final output from the planner and router into a 
    concise, human-readable dispatch alert.
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the CommsAgent.

        Args:
            llm_config (Dict[str, Any]): LLM configuration.
        """
        system_message = (
            "You are the Communications Officer for an emergency response system. "
            "Given a completed task plan and routing solution, create a brief, "
            "human-readable dispatch alert for field responders. Include: hazard type, "
            "location, key tasks, vehicle assignments, and ETA. Keep it under 100 words. "
            "Output plain text only, no JSON."
        )
        super().__init__(name="CommsAgent", system_message=system_message, llm_config=llm_config)

    def broadcast_alert(self, metadata: Dict[str, Any], plan: Dict[str, Any], routes: Dict[str, Any]) -> str:
        """
        Generates a concise alert string.

        Args:
            metadata (Dict): Incident metadata.
            plan (Dict): Task plan from PlannerAgent.
            routes (Dict): Routing result from RouterAgent.

        Returns:
            str: The formatted dispatch alert.
        """
        hazard = metadata.get("hazard_type", "unknown").upper()
        location = metadata.get("location_description", "unknown location")
        urgency = metadata.get("urgency", "unknown").upper()
        
        eta = plan.get("estimated_total_time_min", "unknown")
        
        assigned_vehicles = []
        for r in routes.get("routes", []):
            assigned_vehicles.append(r.get("vehicle_id", "unknown"))
        v_str = ", ".join(assigned_vehicles) if assigned_vehicles else "None"
        
        tasks = plan.get("tasks", [])
        task_str = ", ".join([t.get("action", "") for t in tasks[:2]]) if tasks else "No specific tasks"
        if len(tasks) > 2:
            task_str += "..."

        # Generate a deterministic alert without LLM call for the MVP to guarantee speed and stability,
        # or use LLM if preferred. The instructions say "Output plain text only, no JSON", implies LLM.
        # But we can just use a prompt.
        prompt = (
            f"Format a dispatch alert for this incident.\n"
            f"Hazard: {hazard}\nLocation: {location}\nUrgency: {urgency}\n"
            f"Vehicles: {v_str}\nETA: {eta} mins\nTasks: {task_str}\n"
            "Keep it under 100 words. Plain text only."
        )
        
        try:
            # Send prompt to the LLM
            response = self.generate_reply(messages=[{"role": "user", "content": prompt}])
            alert = str(response).strip()
            
            # Remove any markdown wrapping if the LLM added it
            if alert.startswith("```"):
                lines = alert.split("\n")
                if len(lines) > 2:
                    alert = "\n".join(lines[1:-1])
                    
            self.log_action("broadcast_alert", {"hazard": hazard}, {"alert": alert})
            return alert
        except Exception as e:
            fallback = f"DISPATCH ALERT: {hazard} at {location} ({urgency}). Vehicles: {v_str} en route (ETA {eta} min). Tasks: {task_str}. Plan approved by dispatcher."
            self.log_action("broadcast_alert_error", {"error": str(e)}, {"alert": fallback})
            return fallback
