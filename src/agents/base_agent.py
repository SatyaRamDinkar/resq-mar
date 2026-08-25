"""
Dependencies: pyautogen
"""
import autogen
from typing import Dict, Any
import json
import logging

class ResQAgent(autogen.ConversableAgent):
    """
    Base agent class for all ResQ-MAR agents.
    Inherits from autogen.ConversableAgent and adds standard logging and validation.
    """
    
    def __init__(self, name: str, system_message: str, llm_config: Dict[str, Any]):
        """
        Initialize the ResQAgent.
        
        Args:
            name (str): The name of the agent.
            system_message (str): The system prompt defining the agent's behavior.
            llm_config (Dict[str, Any]): The LLM configuration dictionary.
        """
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            human_input_mode="NEVER"
        )
        self.logger = logging.getLogger(name)
        
    def log_action(self, action: str, input_data: Dict[str, Any], output_data: Dict[str, Any]) -> None:
        """
        Logs an action performed by the agent.
        
        Args:
            action (str): Description of the action.
            input_data (Dict[str, Any]): The data provided to the agent.
            output_data (Dict[str, Any]): The data produced by the agent.
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
        
        Args:
            output (Dict[str, Any]): The generated output from the LLM.
            schema (Dict[str, type]): A dictionary mapping expected keys to their expected types.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        for key, expected_type in schema.items():
            if key not in output:
                return False
            # Allow some flexibility with typing, especially for floats/ints and None
            val = output[key]
            if val is not None and not isinstance(val, expected_type):
                # If expected float but got int, that's acceptable
                if expected_type == float and isinstance(val, int):
                    continue
                return False
        return True

# Example Usage:
# llm_config = {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]}
# agent = ResQAgent(name="TestAgent", system_message="You are a test agent.", llm_config=llm_config)
# agent.log_action("test", {"in": "hello"}, {"out": "world"})
