"""
Pytest suite for the FastAPI backend.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add project root to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.api.main import app, SYSTEM_STATE

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    """Reset global state before each test."""
    SYSTEM_STATE["incidents"].clear()
    SYSTEM_STATE["pending_plans"].clear()
    SYSTEM_STATE["logs"].clear()
    yield

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data
    assert "ollama_connected" in data

def test_create_incident():
    payload = {
        "description": "Flood trapped 3 people",
        "location": {"lat": 1.0, "lon": 2.0}
    }
    response = client.post("/incidents", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "incident_id" in data
    assert data["status"] == "processing"

def test_get_incident():
    # First create
    payload = {"description": "Test", "location": {"lat": 1.0, "lon": 2.0}}
    res = client.post("/incidents", json=payload)
    inc_id = res.json()["incident_id"]
    
    # Then get
    response = client.get(f"/incidents/{inc_id}")
    assert response.status_code == 200
    assert response.json()["incident_id"] == inc_id

def test_get_incident_not_found():
    response = client.get("/incidents/BAD-ID")
    assert response.status_code == 404

def test_route_incident():
    payload = {"description": "Test", "location": {"lat": 1.0, "lon": 2.0}}
    res = client.post("/incidents", json=payload)
    inc_id = res.json()["incident_id"]
    
    route_payload = {"incident_id": inc_id, "resource_types": ["truck"]}
    response = client.post(f"/incidents/{inc_id}/route", json=route_payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "plan_id" in data
    assert data["requires_approval"] is True

def test_approve_plan():
    # Create incident -> route -> approve
    res = client.post("/incidents", json={"description": "Test", "location": {"lat": 1.0, "lon": 2.0}})
    inc_id = res.json()["incident_id"]
    
    route_res = client.post(f"/incidents/{inc_id}/route", json={"incident_id": inc_id, "resource_types": ["truck"]})
    plan_id = route_res.json()["plan_id"]
    
    appr_res = client.post("/approvals", json={"plan_id": plan_id, "decision": "approve"})
    assert appr_res.status_code == 200
    assert appr_res.json()["executed"] is True

def test_reject_plan():
    # Create incident -> route -> reject
    res = client.post("/incidents", json={"description": "Test", "location": {"lat": 1.0, "lon": 2.0}})
    inc_id = res.json()["incident_id"]
    
    route_res = client.post(f"/incidents/{inc_id}/route", json={"incident_id": inc_id, "resource_types": ["truck"]})
    plan_id = route_res.json()["plan_id"]
    
    appr_res = client.post("/approvals", json={"plan_id": plan_id, "decision": "reject", "reason": "Too risky"})
    assert appr_res.status_code == 200
    assert appr_res.json()["executed"] is False

def test_dashboard_status():
    response = client.get("/dashboard/status")
    assert response.status_code == 200
    assert "active_incidents" in response.json()

def test_dashboard_logs():
    client.post("/incidents", json={"description": "Test", "location": {"lat": 1.0, "lon": 2.0}})
    response = client.get("/dashboard/logs?limit=5")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_simulate_endpoint():
    response = client.post("/simulate", json={"scenario_type": "flood"})
    assert response.status_code == 200
    assert "flood" in response.json()["message"].lower()

def test_cors_headers():
    response = client.options("/health", headers={"Origin": "http://localhost:8501", "Access-Control-Request-Method": "GET"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "*"
