"""
Dependencies: pytest, pyautogen
"""
import pytest
import sys
import os

# Ensure src module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent

@pytest.fixture
def test_llm_config():
    """
    Fixture providing a dummy LLM configuration for agent instantiation in tests.
    """
    return {
        "config_list": [{"model": "dummy", "api_key": "dummy"}],
        "temperature": 0.0
    }

# =======================
# Test IntakeAgent
# =======================
def test_process_report_normal(test_llm_config, monkeypatch):
    """Verify that a normal emergency report is parsed correctly."""
    agent = IntakeAgent(llm_config=test_llm_config)
    mock_reply = '{"normalized_text": "Fire in building 7, people trapped.", "is_spam": false, "confidence": 0.95}'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.process_report("Fire in building 7! People trapped help!!!")
    assert result["normalized_text"] == "Fire in building 7, people trapped."
    assert result["is_spam"] is False
    assert result["confidence"] == 0.95

def test_process_report_spam(test_llm_config, monkeypatch):
    """Verify that spam is correctly flagged."""
    agent = IntakeAgent(llm_config=test_llm_config)
    mock_reply = '{"normalized_text": "Buy cheap watches now 50% off", "is_spam": true, "confidence": 0.99}'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.process_report("Buy cheap watches now 50% off")
    assert result["is_spam"] is True

def test_process_report_invalid_json(test_llm_config, monkeypatch):
    """Verify that the agent gracefully handles invalid JSON fallback."""
    agent = IntakeAgent(llm_config=test_llm_config)
    mock_reply = 'This is not valid JSON.'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.process_report("Some raw text")
    assert result.get("error") == "parse_failed"
    assert result["normalized_text"] == "Some raw text"
    assert result["is_spam"] is False

# =======================
# Test MetadataAgent
# =======================
def test_extract_metadata_fire(test_llm_config, monkeypatch):
    """Verify hazard extraction for a fire incident."""
    agent = MetadataAgent(llm_config=test_llm_config)
    mock_reply = '{"hazard_type": "fire", "urgency": "critical", "location_description": "Building 7, 3rd floor", "extracted_entities": ["Building 7", "people"]}'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.extract_metadata("Fire in Building 7, 3rd floor, people trapped")
    assert result["hazard_type"] == "fire"
    assert result["urgency"] == "critical"
    
def test_extract_metadata_flood(test_llm_config, monkeypatch):
    """Verify hazard extraction for a flood incident."""
    agent = MetadataAgent(llm_config=test_llm_config)
    mock_reply = '{"hazard_type": "flood", "urgency": "high", "location_description": "sector 4", "extracted_entities": ["sector 4", "20 people", "rooftops"]}'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.extract_metadata("Water rising in sector 4, 20 people on rooftops")
    assert result["hazard_type"] == "flood"
    assert result["urgency"] == "high"
    
def test_extract_metadata_unknown(test_llm_config, monkeypatch):
    """Verify that invalid enum outputs fallback to default safe values."""
    agent = MetadataAgent(llm_config=test_llm_config)
    mock_reply = '{"hazard_type": "alien_invasion", "urgency": "super_high", "location_description": "sky", "extracted_entities": []}'
    monkeypatch.setattr(agent, "generate_reply", lambda messages, **kwargs: mock_reply)
    
    result = agent.extract_metadata("UFOs in the sky")
    assert result["hazard_type"] == "unknown"  # Fallback triggered
    assert result["urgency"] == "medium"     # Fallback triggered
