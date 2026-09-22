"""Tests for VisionAgent module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestVisionAgent:
    def test_vision_agent_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.agents.vision_agent import VisionAgent
            va = VisionAgent(api_key=None)
            assert va.enabled is False
    def test_analyze_missing_image(self):
        from src.agents.vision_agent import VisionAgent
        va = VisionAgent.__new__(VisionAgent)
        va.enabled = True
        va.model = MagicMock()
        result = va.analyze_damage("/nonexistent.jpg")
        assert "error" in result
