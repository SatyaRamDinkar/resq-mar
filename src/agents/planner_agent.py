"""
Dependencies: pyautogen
"""
import json
from typing import Dict, Any, List
from src.agents.base_agent import ResQAgent

class PlannerAgent(ResQAgent):
    """
    PlannerAgent takes structured metadata and retrieved SOPs to generate
    an actionable, step-by-step disaster response task plan.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the PlannerAgent.
        
        Args:
            llm_config (Dict[str, Any]): The LLM configuration.
        """
        system_message = (
            "You are the Tactical Planner for an emergency response system. "
            "Given structured incident metadata and relevant Standard Operating Procedures (SOPs), "
            "generate a step-by-step task plan. Each task must specify: step number, action description, "
            "required resources, and estimated time. Ground your plan STRICTLY in the provided SOPs. "
            "Do NOT invent procedures not mentioned in the SOPs. Output ONLY a JSON object."
        )
        super().__init__(name="PlannerAgent", system_message=system_message, llm_config=llm_config)
        self.output_schema = {
            "tasks": list,
            "resources_needed": dict,
            "estimated_total_time_min": int,
            "sops_referenced": list
        }

    def generate_plan(self, metadata: Dict[str, Any], retrieved_sops: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a step-by-step task plan grounded in retrieved SOPs.
        
        Args:
            metadata (Dict[str, Any]): Incident metadata (hazard, urgency, etc.)
            retrieved_sops (List[Dict[str, Any]]): Relevant SOPs retrieved from ChromaDB.
            
        Returns:
            Dict[str, Any]: A JSON dictionary containing the task plan.
        """
        # Format the retrieved SOPs into the prompt
        sop_text = ""
        if retrieved_sops:
            for sop in retrieved_sops:
                sop_text += f"SOP [{sop['id']}]: {sop['title']}\n{sop['content']}\n\n"
        else:
            sop_text = "No specific SOPs found. Use general emergency safety guidelines."
            
        prompt = (
            "Generate a tactical plan for the following incident.\n\n"
            f"=== INCIDENT METADATA ===\n{json.dumps(metadata, indent=2)}\n\n"
            f"=== RETRIEVED SOPs ===\n{sop_text}\n"
            "Return ONLY a JSON object with the following keys:\n"
            "- 'tasks' (list of objects with keys: 'step' [int], 'action' [str], 'resource' [str], 'estimated_time_min' [int])\n"
            "- 'resources_needed' (dict mapping resource name to quantity)\n"
            "- 'estimated_total_time_min' (int)\n"
            "- 'sops_referenced' (list of SOP IDs used)\n"
            "Ensure the output is strictly valid JSON."
        )
        
        reply = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        if isinstance(reply, dict):
            content = reply.get("content", "")
        else:
            content = str(reply)
            
        # Try to parse the JSON
        parsed = self._parse_json(content)
        if parsed and self.validate_output(parsed, self.output_schema):
            self.log_action("generate_plan", metadata, parsed)
            return parsed
            
        # Retry once
        retry_prompt = prompt + "\n\nCRITICAL: YOU MUST OUTPUT VALID JSON ONLY. NO MARKDOWN TEXT."
        reply = self.generate_reply(messages=[{"role": "user", "content": retry_prompt}])
        if isinstance(reply, dict):
            content = reply.get("content", "")
        else:
            content = str(reply)
            
        parsed = self._parse_json(content)
        if parsed and self.validate_output(parsed, self.output_schema):
            self.log_action("generate_plan_retry", metadata, parsed)
            return parsed
            
        # Fallback plan if JSON parsing completely fails
        fallback = {
            "tasks": [
                {"step": 1, "action": f"Assess safety for {metadata.get('hazard_type')} event", "resource": "Recon Team", "estimated_time_min": 15},
                {"step": 2, "action": "Establish communication with victims", "resource": "Comms Unit", "estimated_time_min": 10},
                {"step": 3, "action": "Deploy rescue operatives to location", "resource": "Rescue Squad", "estimated_time_min": 45}
            ],
            "resources_needed": {"Recon Team": 1, "Comms Unit": 1, "Rescue Squad": 1},
            "estimated_total_time_min": 70,
            "sops_referenced": [],
            "error": "json_parse_failed_used_fallback"
        }
        self.log_action("generate_plan_failed", metadata, fallback)
        return fallback

    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Helper to strip markdown wrapping and parse JSON."""
        try:
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:-3].strip()
            elif text.startswith("```"):
                text = text[3:-3].strip()
            return json.loads(text)
        except json.JSONDecodeError:
            return None

# Test cases (Mental Check):
# 1. Fire in building with trapped people -> plan should include rescue, evacuation, medical
# 2. Flood with people on rooftops -> plan should include boat deployment, aerial assessment
# 3. Unknown hazard -> plan should include generic safety assessment
