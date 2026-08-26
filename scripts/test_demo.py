"""
Tests for the demo script.
"""
import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Allow imports from scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.run_full_demo import run_scenario, SCENARIOS, print_system_banner, print_comparison_summary, generate_demo_report, check_ollama

@pytest.fixture(autouse=True)
def mock_sleep():
    """Mock time.sleep to make tests fast."""
    with patch("time.sleep", return_value=None):
        yield

def test_run_scenario_structure():
    res = run_scenario(SCENARIOS[0], 1, use_mock=True)
    assert res["id"] == "DEMO_001"
    assert len(res["steps"]) == 7
    assert "total_time_ms" in res
    assert "coverage" in res

def test_system_banner(capsys):
    print_system_banner()
    captured = capsys.readouterr()
    assert "RESQ-MAR: AI-Powered Multi-Agent" in captured.out
    assert "Version: 1.0" in captured.out

def test_comparison_summary(capsys):
    mock_results = [{"coverage": 0.9, "total_time_ms": 1000}, {"coverage": 0.8, "total_time_ms": 1200}]
    print_comparison_summary(mock_results)
    captured = capsys.readouterr()
    assert "DEMO SUMMARY: ResQ-MAR vs Baselines" in captured.out
    assert "Agentic RAG" in captured.out
    assert "AET Routing" in captured.out

def test_demo_report_generation(tmp_path):
    out_file = tmp_path / "report.json"
    mock_results = [{"id": "1", "coverage": 0.9, "total_time_ms": 100}]
    generate_demo_report(mock_results, str(out_file))
    assert out_file.exists()
    data = json.loads(out_file.read_text())
    assert data["system_version"] == "1.0"
    assert len(data["results"]) == 1

@patch("urllib.request.urlopen")
def test_ollama_check_success(mock_urlopen):
    mock_urlopen.return_value = MagicMock()
    assert check_ollama() is True

@patch("urllib.request.urlopen")
def test_ollama_check_fail(mock_urlopen):
    mock_urlopen.side_effect = Exception("Connection Refused")
    assert check_ollama() is False
