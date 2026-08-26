"""
Integration tests for the 4-Step Agentic RAG Pipeline.
"""
import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.agentic_rag import AgenticRAGPipeline
from src.rag.embeddings import SOPKnowledgeBase

DUMMY_LLM_CONFIG = {"config_list": [{"model": "dummy", "api_key": "dummy"}]}

@pytest.fixture
def mock_pipeline():
    kb = SOPKnowledgeBase()
    kb.query = MagicMock(return_value=[{"id": "SOP-1", "content": "Test content", "distance": 0.5, "metadata": {"title": "Test"}}])
    pipeline = AgenticRAGPipeline(llm_config=DUMMY_LLM_CONFIG, kb=kb)
    return pipeline

def test_agentic_rag_fire(mock_pipeline):
    """Test full 4-step pipeline on a fire incident."""
    # Mock LLM outputs
    mock_pipeline.intake_agent._send_json_prompt = MagicMock(return_value={"normalized_text": "Fire", "is_spam": False})
    mock_pipeline.metadata_agent._send_json_prompt = MagicMock(return_value={"hazard_type": "fire", "urgency": "high"})
    mock_pipeline.retrieval_agent._send_json_prompt = MagicMock(return_value={"queries": [{"query": "fire", "hazard_filter": "fire"}]})
    mock_pipeline.assessor_agent._send_json_prompt = MagicMock(return_value={
        "assessment": "sufficient", "coverage_score": 0.9, "recommendation": "proceed", "approved_sop_ids": ["SOP-1"], "rejected_sop_ids": []
    })
    mock_pipeline.planner_agent._send_json_prompt = MagicMock(return_value={"tasks": [{"step": 1, "action": "Extinguish"}], "estimated_total_time_min": 60})
    
    res = mock_pipeline.run("Fire in building 7")
    
    assert res["status"] == "completed"
    assert res["pipeline_steps"] == 4
    assert res["assessment"]["coverage_score"] == 0.9
    assert len(res["plan"]["tasks"]) == 1

def test_agentic_rag_flood(mock_pipeline):
    """Test full pipeline on flood incident."""
    mock_pipeline.intake_agent._send_json_prompt = MagicMock(return_value={"normalized_text": "Flood", "is_spam": False})
    mock_pipeline.metadata_agent._send_json_prompt = MagicMock(return_value={"hazard_type": "flood", "urgency": "critical"})
    mock_pipeline.retrieval_agent._send_json_prompt = MagicMock(return_value={"queries": [{"query": "flood evacuation", "hazard_filter": "flood"}]})
    mock_pipeline.assessor_agent._send_json_prompt = MagicMock(return_value={
        "assessment": "partial", "coverage_score": 0.6, "recommendation": "proceed", "approved_sop_ids": ["SOP-1"], "rejected_sop_ids": []
    })
    mock_pipeline.planner_agent._send_json_prompt = MagicMock(return_value={"tasks": [], "estimated_total_time_min": 120})
    
    res = mock_pipeline.run("Flood in sector 4")
    assert res["status"] == "completed"
    assert res["metadata"]["hazard_type"] == "flood"

def test_assessor_rejects_irrelevant(mock_pipeline):
    """Verify AssessorAgent rejects bad SOPs and requests manual review."""
    mock_pipeline.intake_agent._send_json_prompt = MagicMock(return_value={"normalized_text": "Earthquake", "is_spam": False})
    mock_pipeline.metadata_agent._send_json_prompt = MagicMock(return_value={"hazard_type": "earthquake", "urgency": "high"})
    mock_pipeline.retrieval_agent._send_json_prompt = MagicMock(return_value={"queries": []})
    mock_pipeline.assessor_agent._send_json_prompt = MagicMock(return_value={
        "assessment": "insufficient", "coverage_score": 0.1, "recommendation": "manual_review", "approved_sop_ids": [], "rejected_sop_ids": ["SOP-1"]
    })
    
    res = mock_pipeline.run("Earthquake collapse")
    
    assert res["status"] == "needs_review"
    assert res["pipeline_steps"] == 3
    assert res["assessment"]["recommendation"] == "manual_review"

def test_naive_vs_agentic(mock_pipeline):
    """Run both pipelines and verify the agentic one adds assessment data."""
    mock_pipeline.intake_agent._send_json_prompt = MagicMock(return_value={"normalized_text": "Test", "is_spam": False})
    mock_pipeline.metadata_agent._send_json_prompt = MagicMock(return_value={"hazard_type": "test"})
    mock_pipeline.retrieval_agent._send_json_prompt = MagicMock(return_value={"queries": []})
    mock_pipeline.assessor_agent._send_json_prompt = MagicMock(return_value={"assessment": "ok", "recommendation": "proceed", "coverage_score": 1.0, "approved_sop_ids": ["SOP-1"]})
    mock_pipeline.planner_agent._send_json_prompt = MagicMock(return_value={"tasks": []})
    
    naive = mock_pipeline.run_naive("test")
    agentic = mock_pipeline.run("test")
    
    assert naive["pipeline_steps"] == 1
    assert agentic["pipeline_steps"] == 4
    assert not naive["assessment"]
    assert agentic["assessment"]["coverage_score"] == 1.0

def test_spam_handling(mock_pipeline):
    """Verify spam stops at step 1."""
    mock_pipeline.intake_agent._send_json_prompt = MagicMock(return_value={"normalized_text": "Spam", "is_spam": True})
    res = mock_pipeline.run("Buy watches")
    assert res["status"] == "spam"
