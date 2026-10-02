import pytest
from src.utils.geo_lookup import get_state_language

def test_geo_lookup_metros():
    # Test 10 metros mapping
    assert get_state_language(13.08, 80.27)[0] == "Tamil Nadu"
    assert get_state_language(13.08, 80.27)[2] == "Tamil"
    
    assert get_state_language(19.07, 72.87)[0] == "Maharashtra"
    assert get_state_language(19.07, 72.87)[2] == "Marathi"
    
    assert get_state_language(22.57, 88.36)[0] == "West Bengal"
    assert get_state_language(22.57, 88.36)[2] == "Bengali"
    
    assert get_state_language(12.97, 77.59)[0] == "Karnataka"
    assert get_state_language(12.97, 77.59)[2] == "Kannada"
    
    assert get_state_language(28.61, 77.20)[0] == "Delhi"
    assert get_state_language(28.61, 77.20)[2] == "Hindi"
    
    assert get_state_language(17.38, 78.48)[0] == "Telangana"
    assert get_state_language(17.38, 78.48)[2] == "Telugu"
    
    assert get_state_language(23.02, 72.57)[0] == "Gujarat"
    assert get_state_language(23.02, 72.57)[2] == "Gujarati"
    
    assert get_state_language(18.52, 73.85)[0] == "Maharashtra"
    assert get_state_language(26.91, 75.78)[0] == "Rajasthan"
    assert get_state_language(26.84, 80.94)[0] == "Uttar Pradesh"

def test_comms_agent_auto_language():
    from src.agents.comms_agent import CommsAgent
    agent = CommsAgent.__new__(CommsAgent)
    
    # We mock generate_reply and log_action
    agent.generate_reply = lambda **kwargs: "Mock English Alert"
    
    logs = []
    agent.log_action = lambda action, context, payload: logs.append((action, context, payload))
    
    # Test Chennai (Tamil)
    metadata_chennai = {"lat": 13.08, "lon": 80.27}
    agent.broadcast_alert(metadata_chennai, {}, {})
    
    # Verify log contains language tag
    assert any("Tamil" in log[1].get("languages", "") for log in logs if log[0] == "broadcast_alert")
    
    logs.clear()
    
    # Test Delhi (Hindi)
    metadata_delhi = {"lat": 28.61, "lon": 77.20}
    agent.broadcast_alert(metadata_delhi, {}, {})
    assert any("Hindi" in log[1].get("languages", "") for log in logs if log[0] == "broadcast_alert")
    # Verify no duplicate Hindi/Hindi
    delhi_log = next(log for log in logs if log[0] == "broadcast_alert")
    assert "English, Hindi, Hindi" not in delhi_log[1].get("languages", "")
