"""
Dependencies: pyautogen
"""
from typing import Dict, Any
from src.agents.base_agent import ResQAgent

class IntakeAgent(ResQAgent):
    """
    IntakeAgent is responsible for parsing raw citizen reports, normalizing the text,
    and classifying if it is spam/non-emergency.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the IntakeAgent.
        """
        system_message = (
            "You are the Intake Agent for an emergency response system. "
            "Your job is to read raw, panicked citizen reports and rewrite them into clear, objective, professional language. "
            "Do NOT add information not present in the original report. Do NOT make up details. "
            "If the report is clearly not an emergency (spam, advertisement, joke), flag it as spam. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="IntakeAgent", system_message=system_message, llm_config=llm_config, use_json_mode=True)
        self.output_schema = {
            "normalized_text": str,
            "is_spam": bool,
            "confidence": float
        }

    def process_report(self, raw_text: str) -> Dict[str, Any]:
        """
        Processes a raw citizen report into normalized text and spam classification.
        """
        prompt = (
            f"Process the following raw report:\n\n'{raw_text}'\n\n"
            "Return ONLY a JSON object with the exact keys: 'normalized_text' (string), 'is_spam' (boolean), and 'confidence' (float between 0 and 1)."
        )
        
        required_keys = ["normalized_text", "is_spam", "confidence"]
        parsed = self._send_json_prompt(prompt, required_keys)
        
        if "error" not in parsed:
            self.log_action("process_report", {"raw_text": raw_text}, parsed)
            return parsed
            
        # Fallback
        fallback = {
            "normalized_text": raw_text,
            "is_spam": False,
            "confidence": 0.5,
            "error": "parse_failed"
        }
        self.log_action("process_report_failed", {"raw_text": raw_text}, fallback)
        return fallback
