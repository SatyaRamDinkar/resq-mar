"""
Robust JSON extraction utilities for the ResQ-MAR agents.
"""
import json
import re
from typing import Dict, Any, List, Tuple


def extract_json(text: str) -> dict:
    """
    Try multiple strategies to extract JSON from a text string.
    
    Args:
        text (str): The raw text output from the LLM.
        
    Returns:
        dict: Parsed JSON data or empty dict if parsing fails.
    """
    if not isinstance(text, str):
        return {}
        
    text = text.strip()
    
    # Strategy 1: Direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Strategy 2: Find JSON between ```json and ``` markers using regex
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass
            
    # Strategy 3: Find JSON between first { and last } using regex
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end+1])
        except json.JSONDecodeError:
            pass
            
    return {}


def validate_json_schema(data: dict, required_keys: List[str]) -> bool:
    """
    Check if all required_keys exist in data.
    
    Args:
        data (dict): The parsed JSON dictionary.
        required_keys (list): List of required keys.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    if not isinstance(data, dict):
        return False
    return all(key in data for key in required_keys)


def safe_json_loads(text: str, required_keys: List[str] = None) -> Tuple[dict, bool]:
    """
    Call extract_json, and if required_keys provided, call validate_json_schema.
    
    Args:
        text (str): Raw string.
        required_keys (list): Keys to check.
        
    Returns:
        tuple[dict, bool]: A tuple containing the parsed dictionary and a success flag.
    """
    data = extract_json(text)
    if not data:
        return {}, False
        
    if required_keys:
        is_valid = validate_json_schema(data, required_keys)
        return data, is_valid
        
    return data, True


if __name__ == "__main__":
    t1 = '{"a": 1}'
    t2 = 'Here is the JSON:\n```json\n{"b": 2}\n```'
    t3 = 'Some text before {"c": 3} some text after.'
    print(f"Test 1: {safe_json_loads(t1)}")
    print(f"Test 2: {safe_json_loads(t2)}")
    print(f"Test 3: {safe_json_loads(t3, ['c'])}")
    print(f"Test 3 failure: {safe_json_loads(t3, ['d'])}")
