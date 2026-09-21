import pytest
import os
from unittest.mock import patch, MagicMock
from src.rag.web_search import fetch_web_results, summarize_results, web_search_fallback

@patch("src.rag.web_search.DDGS")
def test_fetch_web_results(mock_ddgs):
    """Test DuckDuckGo search fetching."""
    mock_ddgs_instance = MagicMock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Test Disaster", "body": "This is a summary of the test disaster.", "href": "http://test.com"}
    ]
    mock_ddgs.return_value = mock_ddgs_instance
    
    result = fetch_web_results("test emergency")
    assert "Test Disaster" in result
    assert "This is a summary" in result
    assert "http://test.com" in result

@patch("src.rag.web_search.genai")
def test_summarize_results_gemini(mock_genai, monkeypatch):
    """Test Gemini summarization fallback when API key is present."""
    monkeypatch.setenv("GEMINI_API_KEY", "fake_key")
    
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "This is a Gemini summary."
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    summary = summarize_results("test query", "test context")
    assert "[Summarized via Gemini API]" in summary
    assert "This is a Gemini summary" in summary

@patch("src.rag.web_search.requests.post")
def test_summarize_results_ollama(mock_post, monkeypatch):
    """Test Ollama summarization fallback when API key is MISSING."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This is an Ollama summary."}
    mock_post.return_value = mock_response
    
    summary = summarize_results("test query", "test context")
    assert "[Summarized via Local Llama 3.1]" in summary
    assert "This is an Ollama summary" in summary

@patch("src.rag.web_search.summarize_results")
@patch("src.rag.web_search.fetch_web_results")
def test_web_search_fallback_integration(mock_fetch, mock_summarize):
    """Test the main fallback endpoint."""
    mock_fetch.return_value = "Result 1: Aliens attacked."
    mock_summarize.return_value = "Summary: Aliens attacked."
    
    result = web_search_fallback("alien attack")
    assert result == "Summary: Aliens attacked."
    mock_fetch.assert_called_once_with("alien attack")
    mock_summarize.assert_called_once_with("alien attack", "Result 1: Aliens attacked.")
