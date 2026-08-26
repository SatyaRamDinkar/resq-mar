"""
ResQ-MAR API Client for Frontend Integration.
Wraps the FastAPI endpoints into accessible Python functions for Streamlit.
"""
import requests
from typing import Dict, List, Any

def get_api_base_url() -> str:
    """Returns the base URL of the FastAPI backend."""
    return "http://localhost:8000"

def _handle_request(method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
    """Helper to execute requests and catch connection errors."""
    url = f"{get_api_base_url()}{endpoint}"
    try:
        response = requests.request(method, url, timeout=10.0, **kwargs)
        if response.status_code in [200, 201]:
            return response.json()
        return {"error": f"HTTP {response.status_code}", "detail": response.text}
    except requests.exceptions.RequestException as e:
        return {"error": "API unavailable", "detail": str(e)}

def health_check() -> Dict[str, Any]:
    """Check API and LLM backend health."""
    return _handle_request("GET", "/health")

def create_incident(description: str, lat: float, lon: float) -> Dict[str, Any]:
    """Submit a new emergency incident."""
    payload = {
        "description": description,
        "location": {"lat": lat, "lon": lon}
    }
    return _handle_request("POST", "/incidents", json=payload)

def get_incident(incident_id: str) -> Dict[str, Any]:
    """Retrieve the current status of a specific incident."""
    return _handle_request("GET", f"/incidents/{incident_id}")

def request_routing(incident_id: str, resource_types: List[str]) -> Dict[str, Any]:
    """Request a routing plan from the AI for an incident."""
    payload = {
        "incident_id": incident_id,
        "resource_types": resource_types
    }
    return _handle_request("POST", f"/incidents/{incident_id}/route", json=payload)

def submit_approval(plan_id: str, decision: str, reason: str = "") -> Dict[str, Any]:
    """Submit a human-in-the-loop dispatch decision."""
    payload = {
        "plan_id": plan_id,
        "decision": decision,
        "reason": reason
    }
    return _handle_request("POST", "/approvals", json=payload)

def get_dashboard_status() -> Dict[str, Any]:
    """Fetch global dashboard metrics."""
    return _handle_request("GET", "/dashboard/status")

def get_agent_logs(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch recent AI agent activity logs."""
    res = _handle_request("GET", f"/dashboard/logs?limit={limit}")
    return res if isinstance(res, list) else []

def simulate_scenario(scenario_type: str) -> Dict[str, Any]:
    """Trigger an end-to-end simulated incident."""
    payload = {"scenario_type": scenario_type}
    return _handle_request("POST", "/simulate", json=payload)
