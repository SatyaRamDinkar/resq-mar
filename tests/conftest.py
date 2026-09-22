"""Shared pytest fixtures."""
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture
def dummy_llm_config():
    return {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]}

@pytest.fixture(autouse=True)
def mock_env_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
