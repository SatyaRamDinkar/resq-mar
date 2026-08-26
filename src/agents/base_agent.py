"""
Dependencies: pyautogen
"""
import os
import sys
import autogen
from typing import Dict, Any, List
import json
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.json_utils import safe_json_loads


class ResQAgent(autogen.ConversableAgent):
    """
    Base agent class for all ResQ-MAR agents.
    Inherits from autogen.ConversableAgent and adds standard logging, validation, and JSON mode support.
    """
    
    def __init__(self, name: str, system_message: str, llm_config: Dict[str, Any], use_json_mode: bool = False):
        """
        Initialize the ResQAgent.
        
        Args:
            name (str): The name of the agent.
            system_message (str): The system prompt defining the agent's behavior.
            llm_config (Dict[str, Any]): The LLM configuration dictionary.
            use_json_mode (bool): If True, configures the agent to use Ollama's native JSON mode.
        """
        final_config = llm_config
        if use_json_mode and "config_list" in llm_config:
            # Filter for config with "json" tag
            json_configs = [c for c in llm_config["config_list"] if "json" in c.get("tags", [])]
            if json_configs:
                final_config = {"config_list": json_configs}
            else:
                # Fallback: manually inject response_format to the first config
                modified_list = list(llm_config["config_list"])
                if modified_list:
                    modified_list[0] = dict(modified_list[0])
                    modified_list[0]["response_format"] = {"type": "json_object"}
                final_config = {"config_list": modified_list}
                
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=final_config,
            human_input_mode="NEVER"
        )
        self.logger = logging.getLogger(name)
        
    def log_action(self, action: str, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """
        Logs an action performed by the agent.
        """
        log_entry = {
            "agent": self.name,
            "action": action,
            "input": input_data,
            "output": output_data
        }
        print(f"[{self.name}] LOG: {json.dumps(log_entry, indent=2)}")

    def validate_output(self, output: Dict[str, Any], schema: Dict[str, type]) -> bool:
        """
        Validates if the output dictionary contains the expected keys and types.
        """
        for key, expected_type in schema.items():
            if key not in output:
                return False
            val = output[key]
            if val is not None and not isinstance(val, expected_type):
                if expected_type == float and isinstance(val, int):
                    continue
                return False
        return True

    def _send_json_prompt(self, prompt: str, required_keys: List[str]) -> dict:
        """
        Sends a prompt to the LLM and reliably extracts JSON.
        Retries once if parsing fails.
        
        Args:
            prompt (str): The prompt to send.
            required_keys (list): The keys required in the resulting JSON.
            
        Returns:
            dict: The parsed JSON dictionary, or an empty dict with error if it fails.
        """
        # First attempt
        reply = self.generate_reply(messages=[{"role": "user", "content": prompt}])
        content = reply.get("content", "") if isinstance(reply, dict) else str(reply)
        
        data, success = safe_json_loads(content, required_keys)
        if success:
            return data
            
        # Second attempt (stricter prompt)
        retry_prompt = prompt + "\n\nYou MUST output ONLY valid JSON. No markdown, no explanations. JSON:"
        reply_retry = self.generate_reply(messages=[{"role": "user", "content": retry_prompt}])
        content_retry = reply_retry.get("content", "") if isinstance(reply_retry, dict) else str(reply_retry)
        
        data_retry, success_retry = safe_json_loads(content_retry, required_keys)
        if success_retry:
            return data_retry
            
        # All failed
        return {"error": "parse_failed"}
