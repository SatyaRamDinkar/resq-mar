"""Tests for LiveAwarenessAgent module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestLiveAwarenessAgent:
    def test_agent_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.agents.live_awareness_agent import LiveAwarenessAgent
            agent = LiveAwarenessAgent(api_key=None)
            assert agent.enabled is False
    def test_fetch_returns_string(self):
        from src.agents.live_awareness_agent import LiveAwarenessAgent
        agent = LiveAwarenessAgent.__new__(LiveAwarenessAgent)
        agent.enabled = False
        result = agent.fetch_live_context("flood", "Vizag")
        assert isinstance(result, str)
