"""
Tests for JSON extraction utilities and agent JSON mode.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.json_utils import extract_json, safe_json_loads
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent

DUMMY_LLM_CONFIG = {"config_list": [{"model": "dummy", "api_key": "dummy"}]}


def test_extract_json_direct():
    """Verify direct parsing works."""
    text = '{"a": 1, "b": "test"}'
    res = extract_json(text)
    assert res == {"a": 1, "b": "test"}


def test_extract_json_markdown():
    """Verify extraction from ```json blocks."""
    text = 'Here is your output:\n```json\n{"status": "ok"}\n```\nDone.'
    res = extract_json(text)
    assert res == {"status": "ok"}


def test_extract_json_braces():
    """Verify extraction from raw text using braces."""
    text = 'The agent output is {"some": "value"} and that is all.'
    res = extract_json(text)
    assert res == {"some": "value"}


def test_metadata_agent_json():
    """Verify MetadataAgent correctly parses JSON."""
    agent = MetadataAgent(llm_config=DUMMY_LLM_CONFIG)
    # Mock the LLM reply
    agent.generate_reply = MagicMock(return_value={
        "content": '{"hazard_type": "fire", "urgency": "high", "location_description": "downtown", "extracted_entities": ["building"]}'
    })
    
    res = agent.extract_metadata("Fire downtown")
    
    assert res["hazard_type"] == "fire"
    assert "error" not in res
    agent.generate_reply.assert_called_once()


def test_planner_agent_json():
    """Verify PlannerAgent correctly parses JSON even with markdown."""
    agent = PlannerAgent(llm_config=DUMMY_LLM_CONFIG)
    # Mock LLM reply wrapped in markdown
    mock_reply = '```json\n{"tasks": [{"step": 1, "action": "test", "resource": "x", "estimated_time_min": 5}], "resources_needed": {}, "estimated_total_time_min": 5, "sops_referenced": []}\n```'
    agent.generate_reply = MagicMock(return_value={"content": mock_reply})
    
    res = agent.generate_plan({"hazard_type": "test"}, [])
    
    assert len(res["tasks"]) == 1
    assert res["tasks"][0]["action"] == "test"
    assert "error" not in res
