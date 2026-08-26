"""
Dependencies: pyautogen
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import ResQAgent

class PlannerAgent(ResQAgent):
    """
    PlannerAgent takes the metadata and retrieved SOPs to generate a structured,
    step-by-step task plan for incident response.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the PlannerAgent.
        """
        system_message = (
            "You are the Tactical Planner Agent for an emergency response system. "
            "Given incident metadata and relevant Standard Operating Procedures (SOPs), "
            "you must generate a structured step-by-step tactical plan. "
            "Adhere strictly to the SOPs provided. If no SOPs match, use general emergency best practices. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="PlannerAgent", system_message=system_message, llm_config=llm_config, use_json_mode=True)

    def generate_plan(self, metadata: Dict[str, Any], retrieved_sops: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a step-by-step tactical plan grounded in SOPs.
        """
        sops_text = json.dumps(retrieved_sops, indent=2) if retrieved_sops else "None"
        metadata_text = json.dumps(metadata, indent=2)
        
        prompt = (
            f"INCIDENT METADATA:\n{metadata_text}\n\n"
            f"RETRIEVED SOPs:\n{sops_text}\n\n"
            "If the hazard_type is 'unknown' or this is a non-emergency (e.g., lost pet), generate a single "
            "task advising the user to contact non-emergency services, and require 0 resources.\n\n"
            "Output ONLY a JSON object with these exact keys: tasks (array), resources_needed (object), "
            "estimated_total_time_min (number), sops_referenced (array). Each task must have: "
            "step (number), action (string), resource (string), estimated_time_min (number)."
        )
        
        required_keys = ["tasks", "resources_needed", "estimated_total_time_min", "sops_referenced"]
        parsed = self._send_json_prompt(prompt, required_keys)
        
        if "error" not in parsed:
            self.log_action("generate_plan", {"hazard_type": metadata.get("hazard_type")}, parsed)
            return parsed
            
        # Fallback plan if parsing totally fails
        fallback_plan = {
            "tasks": [
                {"step": 1, "action": f"Assess safety for {metadata.get('hazard_type', 'unknown')} event", "resource": "Recon Team", "estimated_time_min": 15},
                {"step": 2, "action": "Establish communication with victims", "resource": "Comms Unit", "estimated_time_min": 10},
                {"step": 3, "action": "Deploy rescue operatives to location", "resource": "Rescue Squad", "estimated_time_min": 45}
            ],
            "resources_needed": {"Recon Team": 1, "Comms Unit": 1, "Rescue Squad": 1},
            "estimated_total_time_min": 70,
            "sops_referenced": [],
            "error": "json_parse_failed_used_fallback"
        }
        self.log_action("generate_plan_failed", {"hazard_type": metadata.get("hazard_type")}, fallback_plan)
        return fallback_plan
