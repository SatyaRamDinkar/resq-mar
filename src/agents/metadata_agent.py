"""
Dependencies: pyautogen
"""
import json
from typing import Dict, Any
from src.agents.base_agent import ResQAgent

class MetadataAgent(ResQAgent):
    """
    MetadataAgent is responsible for extracting structured fields (hazard_type, urgency, location)
    from a normalized incident report.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the MetadataAgent.
        
        Args:
            llm_config (Dict[str, Any]): The LLM configuration.
        """
        system_message = (
            "You are the Metadata Extraction Agent for an emergency response system. "
            "Given a normalized incident report, extract structured metadata. "
            "Identify the hazard_type (flood, fire, earthquake, medical, or unknown), "
            "urgency level (low, medium, high, critical), and location if mentioned. "
            "Output ONLY a JSON object with these exact keys: 'hazard_type', 'urgency', 'location_description', 'extracted_entities' (list of strings)."
        )
        super().__init__(name="MetadataAgent", system_message=system_message, llm_config=llm_config)
        self.output_schema = {
            "hazard_type": str,
            "urgency": str,
            "location_description": str,
            "extracted_entities": list
        }
        self.valid_hazards = ["flood", "fire", "earthquake", "medical", "unknown"]
        self.valid_urgencies = ["low", "medium", "high", "critical"]

    def extract_metadata(self, normalized_text: str) -> Dict[str, Any]:
        """
        Extracts metadata from normalized text.
        
        Args:
            normalized_text (str): The cleansed incident text.
            
        Returns:
            Dict[str, Any]: Parsed JSON metadata containing hazard_type and urgency.
        """
        prompt = (
            f"Extract metadata from the following text:\n\n'{normalized_text}'\n\n"
            "Return ONLY a JSON object with keys: 'hazard_type', 'urgency', 'location_description', 'extracted_entities'."
        )
        
        reply = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        if isinstance(reply, dict):
            content = reply.get("content", "")
        else:
            content = str(reply)
            
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            parsed = json.loads(content)
            
            if self.validate_output(parsed, self.output_schema):
                # Validate enum fields
                if parsed["hazard_type"].lower() not in self.valid_hazards:
                    parsed["hazard_type"] = "unknown"
                else:
                    parsed["hazard_type"] = parsed["hazard_type"].lower()
                    
                if parsed["urgency"].lower() not in self.valid_urgencies:
                    parsed["urgency"] = "medium"
                else:
                    parsed["urgency"] = parsed["urgency"].lower()
                    
                self.log_action("extract_metadata", {"normalized_text": normalized_text}, parsed)
                return parsed
        except Exception:
            pass
            
        # Fallback handling
        fallback = {
            "hazard_type": "unknown",
            "urgency": "medium",
            "location_description": "unknown",
            "extracted_entities": [],
            "error": "extraction_failed"
        }
        self.log_action("extract_metadata_failed", {"normalized_text": normalized_text}, fallback)
        return fallback

# Test cases:
# 1. "Fire in Building 7, 3rd floor, people trapped" -> hazard_type="fire", urgency="critical"
# 2. "Water rising in sector 4, 20 people on rooftops" -> hazard_type="flood", urgency="high"
# 3. "Someone fell and is bleeding at the market entrance" -> hazard_type="medical", urgency="high"
