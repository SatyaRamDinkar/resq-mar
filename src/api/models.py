"""
Pydantic models for ResQ-MAR FastAPI backend.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class IncidentRequest(BaseModel):
    """Schema for incoming 911 incident requests."""
    id: Optional[str] = Field(None, description="Optional incident ID. Auto-generated if not provided.", example="INC-001")
    description: str = Field(..., description="Raw 911-style text describing the emergency.", example="Flood waters rising rapidly on Main St. Families trapped.")
    location: Dict[str, float] = Field(..., description="Dictionary containing lat and lon coordinates.", example={"lat": 6.8774, "lon": 79.8653})
    type: Optional[str] = Field(None, description="Type of incident (flood, fire, earthquake, medical).", example="flood")
    severity: Optional[str] = Field(None, description="Severity level (low, medium, high, critical).", example="critical")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO format timestamp.")

class IncidentResponse(BaseModel):
    """Schema for incident creation and status responses."""
    incident_id: str = Field(..., description="Unique ID of the incident.")
    status: str = Field(..., description="Current status: received, processing, routed, dispatched, completed.")
    message: str = Field(..., description="Human-readable status message.")
    agents_involved: List[str] = Field(default_factory=list, description="List of agents that have processed this incident.")
    estimated_response_time_min: Optional[int] = Field(None, description="Estimated time until arrival in minutes.")
    created_at: str = Field(..., description="ISO format timestamp of creation.")

class RoutingRequest(BaseModel):
    """Schema for requesting a routing plan for an incident."""
    incident_id: str = Field(..., description="ID of the incident to route resources for.")
    resource_types: List[str] = Field(..., description="List of resource types needed (e.g., ambulance, drone).", example=["ambulance", "drone"])
    max_wait_min: int = Field(30, description="Maximum acceptable wait time in minutes.")

class RoutingResponse(BaseModel):
    """Schema for the generated routing plan."""
    incident_id: str = Field(..., description="Associated incident ID.")
    plan_id: str = Field(..., description="Unique ID for this routing plan.")
    routes: List[Dict[str, Any]] = Field(..., description="List of vehicle assignments and ETAs.")
    total_distance_km: float = Field(..., description="Total route distance in kilometers.")
    estimated_time_min: int = Field(..., description="Estimated completion time in minutes.")
    requires_approval: bool = Field(True, description="Flag indicating if a human dispatcher must approve this plan.")
    status: str = Field(..., description="Status of the plan (pending_approval, approved, rejected).")

class ApprovalRequest(BaseModel):
    """Schema for dispatcher approval actions."""
    plan_id: str = Field(..., description="ID of the routing plan to approve or reject.")
    decision: str = Field(..., description="Decision: 'approve' or 'reject'.", example="approve")
    reason: Optional[str] = Field(None, description="Optional reason for the decision, mandatory if rejected.")

class ApprovalResponse(BaseModel):
    """Schema for approval action outcomes."""
    plan_id: str = Field(..., description="ID of the routed plan.")
    decision: str = Field(..., description="The decision that was recorded.")
    executed: bool = Field(..., description="True if the plan was successfully approved and dispatched.")
    message: str = Field(..., description="Human-readable result message.")

class DashboardStatus(BaseModel):
    """Schema for high-level system metrics."""
    active_incidents: int = Field(..., description="Number of currently active incidents.")
    pending_approvals: int = Field(..., description="Number of plans awaiting human approval.")
    active_agent: str = Field(..., description="Name of the agent currently executing a task.")
    system_health: str = Field(..., description="Overall system health status.")
    last_update: str = Field(..., description="ISO format timestamp of last metric update.")

class AgentLogEntry(BaseModel):
    """Schema for individual agent activity logs."""
    agent: str = Field(..., description="Name of the agent.")
    status: str = Field(..., description="Task status (started, completed, error).")
    task: str = Field(..., description="Description of the task.")
    timestamp: str = Field(..., description="ISO format timestamp.")
    duration_ms: int = Field(..., description="Execution duration in milliseconds.")

class HealthCheck(BaseModel):
    """Schema for API health status."""
    status: str = Field(..., description="API operational status.")
    ollama_connected: bool = Field(..., description="True if local Ollama server is reachable.")
    version: str = Field(..., description="API version string.")
    uptime_seconds: int = Field(..., description="Server uptime in seconds.")
