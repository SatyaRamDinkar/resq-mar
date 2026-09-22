"""Tests for LanguageService module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestLanguageService:
    def test_init_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.utils.language_service import LanguageService
            svc = LanguageService(api_key=None)
            assert svc.enabled is False
    def test_detect_language_fallback(self):
        from src.utils.language_service import LanguageService
        svc = LanguageService.__new__(LanguageService)
        svc.enabled = False
        svc._cache = {}
        assert svc.detect_language("Hello") == "en"
