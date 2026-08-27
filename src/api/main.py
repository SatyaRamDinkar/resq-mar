"""
ResQ-MAR FastAPI Main Application.
Provides REST endpoints for the multi-agent emergency response pipeline.
"""
import os
import time
import uuid
import requests
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from src.api.models import (
    IncidentRequest, IncidentResponse, RoutingRequest, RoutingResponse,
    ApprovalRequest, ApprovalResponse, DashboardStatus, AgentLogEntry, HealthCheck
)

# Import the OSRM and Edge routers if they exist
try:
    from src.api.routes_osrm import router as osrm_router
    has_osrm_router = True
except ImportError:
    has_osrm_router = False

try:
    from src.api.edge_routes import router as edge_router
    has_edge_router = True
except ImportError:
    has_edge_router = False

app = FastAPI(
    title="ResQ-MAR API",
    description="AI-Powered Multi-Agent Emergency Response System",
    version="1.0.0"
)

if has_osrm_router:
    app.include_router(osrm_router)

if has_edge_router:
    app.include_router(edge_router)

# Mount static files
if os.path.exists("frontend"):
    app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
if os.path.exists("data"):
    app.mount("/data", StaticFiles(directory="data"), name="data")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State for Mock DashboardAgent and orchestration tracking
SYSTEM_STATE = {
    "start_time": time.time(),
    "ollama_connected": False,
    "incidents": {},       # incident_id -> IncidentResponse dict
    "pending_plans": {},   # plan_id -> RoutingResponse dict
    "logs": []             # list of AgentLogEntry
}

def log_agent_activity(agent: str, status: str, task: str, duration: int = 0):
    """Helper to append agent logs to the global state."""
    entry = AgentLogEntry(
        agent=agent,
        status=status,
        task=task,
        timestamp=datetime.utcnow().isoformat(),
        duration_ms=duration
    )
    SYSTEM_STATE["logs"].append(entry)

@app.on_event("startup")
async def startup_event():
    """Startup routine: Check Ollama connectivity."""
    print("[OK] ResQ-MAR API starting...")
    try:
        res = requests.get("http://localhost:11434/api/tags", timeout=2.0)
        if res.status_code == 200:
            SYSTEM_STATE["ollama_connected"] = True
            print("[OK] Ollama connected. Full AI mode active.")
    except Exception:
        SYSTEM_STATE["ollama_connected"] = False
        print("[WARN] Ollama unavailable. Mock mode active.")
    SYSTEM_STATE["start_time"] = time.time()

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Returns the operational status of the API and LLM backend."""
    return HealthCheck(
        status="operational",
        ollama_connected=SYSTEM_STATE["ollama_connected"],
        version="1.0.0",
        uptime_seconds=int(time.time() - SYSTEM_STATE["start_time"])
    )

@app.post("/incidents", response_model=IncidentResponse)
async def create_incident(req: IncidentRequest):
    """Ingests a new emergency incident and triggers the Intake and Metadata agents."""
    incident_id = req.id if req.id else f"INC-{uuid.uuid4().hex[:6].upper()}"
    
    start_t = time.time()
    log_agent_activity("IntakeAgent", "started", f"Parsing incident {incident_id}")
    
    # Mock logic based on Ollama connectivity
    incident_type = req.type or "unknown"
    severity = req.severity or "medium"
    
    if not SYSTEM_STATE["ollama_connected"]:
        # Mock enrichment
        text_lower = req.description.lower()
        if "flood" in text_lower or "water" in text_lower: incident_type = "flood"
        elif "fire" in text_lower or "smoke" in text_lower: incident_type = "fire"
        
        if "trapped" in text_lower or "critical" in text_lower: severity = "critical"
    
    log_agent_activity("MetadataAgent", "completed", f"Enriched incident {incident_id}", int((time.time() - start_t)*1000))
    
    response = IncidentResponse(
        incident_id=incident_id,
        status="processing",
        message=f"Incident parsed as {severity} {incident_type}. Awaiting routing.",
        agents_involved=["IntakeAgent", "MetadataAgent"],
        estimated_response_time_min=None,
        created_at=datetime.utcnow().isoformat()
    )
    
    SYSTEM_STATE["incidents"][incident_id] = response
    return response

@app.get("/incidents/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: str):
    """Retrieve the current status of an incident."""
    if incident_id not in SYSTEM_STATE["incidents"]:
        raise HTTPException(status_code=404, detail="Incident not found")
    return SYSTEM_STATE["incidents"][incident_id]

@app.post("/incidents/{incident_id}/route", response_model=RoutingResponse)
async def request_routing(incident_id: str, req: RoutingRequest):
    """Triggers the Planner and Router agents to generate a dispatch plan."""
    if incident_id not in SYSTEM_STATE["incidents"]:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    start_t = time.time()
    log_agent_activity("PlannerAgent", "started", f"Planning for {incident_id}")
    log_agent_activity("RouterAgent", "started", f"Routing {req.resource_types}")
    
    plan_id = f"PLAN-{uuid.uuid4().hex[:6].upper()}"
    
    routes = [{"vehicle": r, "eta_min": 10, "node": "target"} for r in req.resource_types]
    
    plan = RoutingResponse(
        incident_id=incident_id,
        plan_id=plan_id,
        routes=routes,
        total_distance_km=15.5,
        estimated_time_min=10,
        requires_approval=True,
        status="pending_approval"
    )
    
    log_agent_activity("RouterAgent", "completed", f"Plan {plan_id} generated", int((time.time() - start_t)*1000))
    
    SYSTEM_STATE["pending_plans"][plan_id] = plan
    
    # Update incident status
    SYSTEM_STATE["incidents"][incident_id].status = "routed"
    SYSTEM_STATE["incidents"][incident_id].agents_involved.extend(["PlannerAgent", "RouterAgent"])
    
    return plan

@app.post("/approvals", response_model=ApprovalResponse)
async def submit_approval(req: ApprovalRequest):
    """Human-in-the-loop endpoint to approve or reject a routing plan."""
    if req.plan_id not in SYSTEM_STATE["pending_plans"]:
        raise HTTPException(status_code=404, detail="Plan not found or already processed")
        
    plan = SYSTEM_STATE["pending_plans"][req.plan_id]
    incident_id = plan.incident_id
    
    log_agent_activity("DashboardAgent", "completed", f"Human decision: {req.decision} for {req.plan_id}")
    
    if req.decision.lower() == "approve":
        plan.status = "approved"
        SYSTEM_STATE["incidents"][incident_id].status = "dispatched"
        SYSTEM_STATE["incidents"][incident_id].agents_involved.append("CommsAgent")
        log_agent_activity("CommsAgent", "completed", f"Dispatched resources for {incident_id}")
        
        executed = True
        msg = "Plan approved and resources dispatched."
    else:
        plan.status = "rejected"
        executed = False
        msg = f"Plan rejected. Reason: {req.reason or 'None provided'}"
        
    del SYSTEM_STATE["pending_plans"][req.plan_id]
    
    return ApprovalResponse(
        plan_id=req.plan_id,
        decision=req.decision,
        executed=executed,
        message=msg
    )

@app.get("/dashboard/status", response_model=DashboardStatus)
async def get_dashboard_status():
    """Retrieve global system metrics."""
    return DashboardStatus(
        active_incidents=len(SYSTEM_STATE["incidents"]),
        pending_approvals=len(SYSTEM_STATE["pending_plans"]),
        active_agent="Idle" if not SYSTEM_STATE["logs"] else SYSTEM_STATE["logs"][-1].agent,
        system_health="Healthy" if SYSTEM_STATE["ollama_connected"] else "Degraded (Mock Mode)",
        last_update=datetime.utcnow().isoformat()
    )

@app.get("/dashboard/incidents", response_model=List[IncidentResponse])
async def list_active_incidents():
    """List all tracked incidents."""
    return list(SYSTEM_STATE["incidents"].values())

@app.get("/dashboard/logs", response_model=List[AgentLogEntry])
async def get_agent_logs(agent: Optional[str] = None, limit: int = 50):
    """Fetch recent activity logs from all agents."""
    logs = SYSTEM_STATE["logs"]
    if agent:
        logs = [log for log in logs if log.agent == agent]
    return logs[-min(limit, 100):]

@app.get("/dashboard/approvals/pending", response_model=List[RoutingResponse])
async def list_pending_approvals():
    """Retrieve all plans awaiting human dispatcher approval."""
    return list(SYSTEM_STATE["pending_plans"].values())

@app.post("/simulate", response_model=IncidentResponse)
async def simulate_scenario(scenario: dict):
    """End-to-End simulation trigger for a specific hazard scenario."""
    scenario_type = scenario.get("scenario_type", "flood")
    req = IncidentRequest(
        description=f"Simulated {scenario_type} emergency triggered via API.",
        location={"lat": 6.9271, "lon": 79.8612},
        type=scenario_type,
        severity="high"
    )
    return await create_incident(req)

if __name__ == "__main__":
    import uvicorn
    print("=========================================")
    print("[OK] ResQ-MAR API running at http://localhost:8000")
    print("[OK] API docs at http://localhost:8000/docs")
    print("=========================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)
