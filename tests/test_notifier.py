import pytest
from unittest.mock import patch, MagicMock
from src.services.notifier import send_sms, send_email

class TestNotifier:
    def test_sms_fallback_logging(self):
        """Test SMS falls back to logging when keys are missing."""
        logger_mock = MagicMock()
        with patch.dict('os.environ', clear=True):
            result = send_sms("+919999999999", "Test Chennai ETA 10m", logger=logger_mock)
            
            assert result is True
            logger_mock.assert_called_once()
            args = logger_mock.call_args[0]
            assert args[0] == "CommsAgent"
            assert "MOCK SMS" in args[2]
            assert "Chennai ETA 10m" in args[2]

    def test_email_fallback_logging(self):
        """Test Email falls back to logging when keys are missing."""
        logger_mock = MagicMock()
        with patch.dict('os.environ', clear=True):
            result = send_email("test@example.com", "Alert", "Delhi ETA 5m", logger=logger_mock)
            
            assert result is True
            logger_mock.assert_called_once()
            args = logger_mock.call_args[0]
            assert "MOCK EMAIL" in args[2]
            assert "Delhi ETA 5m" in args[2]
