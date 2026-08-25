"""
Dependencies: pyautogen
"""
import json
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
        
        Args:
            llm_config (Dict[str, Any]): The LLM configuration.
        """
        system_message = (
            "You are the Intake Agent for an emergency response system. "
            "Your job is to read raw, panicked citizen reports and rewrite them into clear, objective, professional language. "
            "Do NOT add information not present in the original report. Do NOT make up details. "
            "If the report is clearly not an emergency (spam, advertisement, joke), flag it as spam. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="IntakeAgent", system_message=system_message, llm_config=llm_config)
        self.output_schema = {
            "normalized_text": str,
            "is_spam": bool,
            "confidence": float
        }

    def process_report(self, raw_text: str) -> Dict[str, Any]:
        """
        Processes a raw citizen report into normalized text and spam classification.
        
        Args:
            raw_text (str): The raw incident text.
            
        Returns:
            Dict[str, Any]: Parsed JSON containing normalized_text, is_spam, and confidence.
        """
        prompt = (
            f"Process the following raw report:\n\n'{raw_text}'\n\n"
            "Return ONLY a JSON object with the keys: 'normalized_text' (string), 'is_spam' (boolean), and 'confidence' (float between 0 and 1)."
        )
        
        reply = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        if isinstance(reply, dict):
            content = reply.get("content", "")
        else:
            content = str(reply)
            
        # Try parsing JSON
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            parsed = json.loads(content)
            if self.validate_output(parsed, self.output_schema):
                self.log_action("process_report", {"raw_text": raw_text}, parsed)
                return parsed
        except Exception:
            pass

        # Retry once with stricter prompt
        retry_prompt = prompt + "\nCRITICAL: YOU MUST OUTPUT VALID JSON ONLY. NO OTHER TEXT."
        reply = self.generate_reply(messages=[{"role": "user", "content": retry_prompt}])
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
                self.log_action("process_report_retry", {"raw_text": raw_text}, parsed)
                return parsed
        except Exception:
            pass
            
        # Fallback
        fallback = {
            "normalized_text": raw_text,
            "is_spam": False,
            "confidence": 0.5,
            "error": "parse_failed"
        }
        self.log_action("process_report_failed", {"raw_text": raw_text}, fallback)
        return fallback

# Test cases:
# 1. "Fire in building 7! People trapped help!!!" -> should normalize and set is_spam=false
# 2. "Buy cheap watches now 50% off" -> should set is_spam=true
# 3. "Water rising fast in sector 4, 20 people on rooftops, urgent" -> should normalize
