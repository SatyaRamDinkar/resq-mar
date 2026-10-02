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

import autogen
from unittest.mock import patch, MagicMock

@pytest.fixture(autouse=True)
def mock_llm_calls():
    with patch('autogen.ConversableAgent.generate_reply', return_value='{"mocked": "json"}'):
        with patch('google.generativeai.GenerativeModel.generate_content') as mock_gemini:
            mock_gemini.return_value = MagicMock(text='Mocked Gemini response')
            try:
                import groq
                with patch('groq.resources.chat.completions.Completions.create') as mock_groq:
                    mock_groq.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content="Mocked Groq"))])
                    yield
            except ImportError:
                yield
