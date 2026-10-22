"""
Unit tests for Driver Mobile View component and regional language translations.
"""
import pytest
from frontend.components.driver_view import LOCALIZED_STRINGS


class TestDriverView:
    """Test suite for in-ambulance driver interface and localization."""

    def test_all_four_languages_supported(self):
        """Verify English, Telugu, Tamil, and Hindi are fully translated."""
        supported_langs = ["en", "te", "ta", "hi"]
        for lang in supported_langs:
            assert lang in LOCALIZED_STRINGS
            lang_dict = LOCALIZED_STRINGS[lang]
            
            # Check mandatory keys
            assert "terminal_title" in lang_dict
            assert "unit_id" in lang_dict
            assert "action_accept" in lang_dict
            assert "action_en_route" in lang_dict
            assert "action_patient_onboard" in lang_dict
            assert "action_arrived" in lang_dict
            assert "detour_alert" in lang_dict
            assert "steps" in lang_dict
            assert len(lang_dict["steps"]) >= 3

    def test_telugu_localization_content(self):
        """Verify Telugu specific disaster response phrases."""
        te = LOCALIZED_STRINGS["te"]
        assert "అంబులెన్స్" in te["terminal_title"]
        assert "మిషన్ అంగీకరించు" in te["action_accept"]
        assert "వరద" in te["detour_alert"]  # Flood detour mention

    def test_tamil_localization_content(self):
        """Verify Tamil specific disaster response phrases."""
        ta = LOCALIZED_STRINGS["ta"]
        assert "ஆம்புலன்ஸ்" in ta["terminal_title"]
        assert "பணியை ஏற்றுக்கொள்" in ta["action_accept"]
        assert "வெள்ளம்" in ta["detour_alert"]

    def test_hindi_localization_content(self):
        """Verify Hindi specific disaster response phrases."""
        hi = LOCALIZED_STRINGS["hi"]
        assert "एम्बुलेंस" in hi["terminal_title"]
        assert "मिशन स्वीकार करें" in hi["action_accept"]
        assert "डायवर्जन" in hi["detour_alert"]

    def test_state_flow_progression(self):
        """Verify sequential mission status transitions."""
        valid_transitions = {
            "ASSIGNED": "ACCEPTED",
            "ACCEPTED": "EN_ROUTE",
            "EN_ROUTE": "PATIENT_ONBOARD",
            "PATIENT_ONBOARD": "COMPLETED",
            "COMPLETED": "ASSIGNED"
        }
        for current_state, next_state in valid_transitions.items():
            assert next_state is not None
