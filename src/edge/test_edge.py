"""
Tests for Edge SLM deployment module.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.edge.edge_agent import EdgeAgent
from src.edge.offline_client import OfflineClient

@patch('requests.get')
def test_model_info(mock_get):
    """Verify get_model_info returns expected size info."""
    agent = EdgeAgent(model_name="phi3:mini", port=11435)
    info = agent.get_model_info()
    assert info["model"] == "phi3:mini"
    assert info["size_gb"] == 1.6
    assert info["port"] == 11435

@patch('requests.get')
@patch('requests.post')
def test_edge_agent_query(mock_post, mock_get):
    """Verify EdgeAgent query returns dict with proper keys."""
    mock_post_res = MagicMock()
    mock_post_res.json.return_value = {"response": "Mocked answer"}
    mock_post_res.status_code = 200
    mock_post.return_value = mock_post_res
    
    agent = EdgeAgent()
    res = agent.query("Test question?")
    
    assert res["question"] == "Test question?"
    assert res["answer"] == "Mocked answer"
    assert "latency_ms" in res
    assert res["mode"] == "edge"

@patch('requests.get')
@patch('requests.post')
def test_offline_client_online_mode(mock_post, mock_get):
    """Verify OfflineClient routes to cloud when online."""
    # Mock GET to return 200 (Online)
    mock_get_res = MagicMock()
    mock_get_res.status_code = 200
    mock_get.return_value = mock_get_res
    
    # Mock POST for answer
    mock_post_res = MagicMock()
    mock_post_res.json.return_value = {"response": "Cloud answer"}
    mock_post.return_value = mock_post_res
    
    client = OfflineClient()
    res = client.ask("Test?")
    
    assert res["mode"] == "online"
    assert res["source"] == "cloud"
    assert res["answer"] == "Cloud answer"

@patch('requests.get')
@patch('requests.post')
def test_offline_client_offline_mode(mock_post, mock_get):
    """Verify OfflineClient routes to edge when cloud is unavailable."""
    # Mock GET to raise exception (Offline)
    import requests
    mock_get.side_effect = requests.exceptions.ConnectionError("Offline")
    
    # Mock POST for edge answer
    mock_post_res = MagicMock()
    mock_post_res.json.return_value = {"response": "Edge answer"}
    mock_post.return_value = mock_post_res
    
    client = OfflineClient()
    res = client.ask("Test?")
    
    assert res["mode"] == "offline"
    assert res["source"] == "edge"
    assert res["answer"] == "Edge answer"

@patch('requests.get')
@patch('requests.post')
def test_benchmark_runs(mock_post, mock_get):
    """Verify benchmark returns stats dict."""
    mock_post_res = MagicMock()
    mock_post_res.json.return_value = {"response": "Mocked answer"}
    mock_post.return_value = mock_post_res
    
    agent = EdgeAgent()
    test_q = [{"question": "Q1"}, {"question": "Q2"}]
    stats = agent.benchmark(test_q)
    
    assert "avg_latency_ms" in stats
    assert "max_latency_ms" in stats
    assert stats["total_questions"] == 2
