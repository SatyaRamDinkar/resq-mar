"""
Dependencies: pyautogen
"""
from typing import Dict, Any
from src.agents.base_agent import ResQAgent

class MetadataAgent(ResQAgent):
    """
    MetadataAgent extracts structured metadata (hazard type, urgency, location, entities) 
    from the normalized incident text.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the MetadataAgent.
        """
        system_message = (
            "You are the Metadata Extraction Agent for an emergency response system. "
            "Given a clear incident report, extract the key metadata. "
            "Hazard types must be one of: fire, flood, earthquake, medical, unknown. "
            "Urgency must be one of: low, medium, high, critical. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="MetadataAgent", system_message=system_message, llm_config=llm_config, use_json_mode=True)
        self.output_schema = {
            "hazard_type": str,
            "urgency": str,
            "location_description": str,
            "extracted_entities": list
        }

    def extract_metadata(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts structured metadata from normalized text.
        """
        prompt = (
            f"Extract metadata from the following report:\n\n'{normalized_text}'\n\n"
            "Return ONLY a JSON object with the exact keys: "
            "'hazard_type' (string), 'urgency' (string), "
            "'location_description' (string), 'extracted_entities' (list of strings)."
        )
        
        required_keys = ["hazard_type", "urgency", "location_description", "extracted_entities"]
        parsed = self._send_json_prompt(prompt, required_keys)
        
        if "error" not in parsed:
            self.log_action("extract_metadata", {"normalized_text": normalized_text}, parsed)
            return parsed
            
        # Fallback
        fallback = {
            "hazard_type": "unknown",
            "urgency": "medium",
            "location_description": "unknown",
            "extracted_entities": [],
            "error": "parse_failed"
        }
        self.log_action("extract_metadata_failed", {"normalized_text": normalized_text}, fallback)
        return fallback
