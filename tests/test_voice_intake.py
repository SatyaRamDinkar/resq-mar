"""Tests for VoiceIntake module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestVoiceIntake:
    def test_voice_intake_no_whisper(self):
        with patch.dict("sys.modules", {"whisper": None}):
            from src.agents.voice_intake import VoiceIntake
            vi = VoiceIntake(model_size="base")
            assert vi.model is None
    def test_transcribe_missing_file(self):
        from src.agents.voice_intake import VoiceIntake
        vi = VoiceIntake.__new__(VoiceIntake)
        vi.model = None
        result = vi.process_voice_emergency("/nonexistent.wav")
        assert "status" in result
