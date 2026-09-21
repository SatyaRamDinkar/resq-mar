import pytest
import os
import json
from src.agents.explainability_agent import ExplainabilityAgent
from src.utils.decision_logger import LOG_FILE_PATH, clear_old_decisions

@pytest.fixture(autouse=True)
def setup_teardown():
    """Ensure clean log state before and after tests."""
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)
    yield
    if os.path.exists(LOG_FILE_PATH):
        os.remove(LOG_FILE_PATH)

def test_log_decision():
    """Verify decision is stored with all fields."""
    agent = ExplainabilityAgent()
    dec_id = agent.log_decision(
        agent_name="TestAgent",
        decision="Go Left",
        reasoning="Because it is closer",
        confidence=0.9,
        inputs={"distance": 5},
        incident_id="TEST-123"
    )
    
    assert dec_id.startswith("dec_")
    
    chain = agent.get_decision_chain("TEST-123")
    assert len(chain) == 1
    
    stored = chain[0]
    assert stored["agent"] == "TestAgent"
    assert stored["outputs"]["decision"] == "Go Left"
    assert stored["reasoning"] == "Because it is closer"
    assert stored["confidence"] == 0.9
    assert stored["incident_id"] == "TEST-123"

def test_get_decision_chain():
    """Verify chronological ordering."""
    agent = ExplainabilityAgent()
    agent.log_decision("Agent1", "A", "Reason A", 0.5, {}, "TEST-456")
    agent.log_decision("Agent2", "B", "Reason B", 0.6, {}, "TEST-456")
    
    chain = agent.get_decision_chain("TEST-456")
    assert len(chain) == 2
    assert chain[0]["agent"] == "Agent1"
    assert chain[1]["agent"] == "Agent2"

def test_explain_routing():
    """Verify explanation contains 'because'."""
    agent = ExplainabilityAgent()
    plan = {"tasks": [{"resource": "Drone X", "distance_km": 4.5}]}
    exp = agent.explain_routing_decision(plan)
    
    assert exp["type"] == "routing"
    assert len(exp["explanations"]) == 1
    assert "because" in exp["explanations"][0]["reason"].lower()
    assert "Drone X" in exp["explanations"][0]["reason"]

def test_explain_rag():
    """Verify relevance scores included."""
    agent = ExplainabilityAgent()
    sops = [{"id": "SOP_A"}, {"id": "SOP_B"}]
    scores = [0.99, 0.45]
    
    exp = agent.explain_rag_decision(sops, scores, "SOP_A", True)
    assert exp["type"] == "rag"
    assert exp["final_sop"] == "SOP_A"
    assert exp["re_retrieval_triggered"] is True
    assert len(exp["candidates"]) == 2
    assert exp["candidates"][0]["score"] == 0.99

def test_counterfactual():
    """Verify change param affects output."""
    agent = ExplainabilityAgent()
    incident = {"severity": "critical", "type": "fire"}
    
    cf = agent.generate_counterfactual(incident, "severity", "medium")
    assert cf["parameter_changed"] == "severity"
    assert cf["original_value"] == "critical"
    assert cf["new_value"] == "medium"
    assert cf["original_allocation"] != cf["new_allocation"]

def test_audit_trail():
    """Verify export contains all decisions."""
    agent = ExplainabilityAgent()
    agent.log_decision("TestAgent", "A", "Reason", 0.9, {}, "TEST-789")
    
    audit = agent.export_audit_trail("TEST-789")
    assert "=== AUDIT TRAIL FOR INCIDENT: TEST-789 ===" in audit
    assert "TestAgent" in audit
    assert "Decision  : A" in audit
    assert "Reasoning : Reason" in audit

def test_confidence_flagging():
    """Verify sub-0.7 decisions flagged."""
    agent = ExplainabilityAgent()
    agent.log_decision("Agent1", "A", "R", 0.9, {}, "TEST-FLAG")
    
    sum1 = agent.get_confidence_summary("TEST-FLAG")
    assert sum1["requires_review"] is False
    
    agent.log_decision("Agent2", "B", "R", 0.5, {}, "TEST-FLAG")
    sum2 = agent.get_confidence_summary("TEST-FLAG")
    assert sum2["requires_review"] is True
