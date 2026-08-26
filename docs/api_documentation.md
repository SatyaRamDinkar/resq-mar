# ResQ-MAR API Documentation

## 1. Overview
The ResQ-MAR API provides a high-performance REST interface to the underlying multi-agent AI pipeline. It enables external clients, mobile applications, and IoT sensors to trigger emergency response protocols, request intelligent vehicle routing, and query live system status.
- **Base URL**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

## 2. Authentication
Currently, the API is designed for local, trusted network deployment and does not require authentication. Future production iterations will implement API Key verification and OAuth2 flows.

## 3. Endpoints Reference

| Method | Path | Description | Request Body | Response |
|---|---|---|---|---|
| GET | `/health` | Check API and LLM connectivity status. | None | `HealthCheck` |
| POST | `/incidents` | Submit a new 911 emergency transcript. | `IncidentRequest` | `IncidentResponse` |
| GET | `/incidents/{id}` | Poll the status of a specific incident. | None | `IncidentResponse` |
| POST | `/incidents/{id}/route` | Request optimal vehicle routing for an incident. | `RoutingRequest` | `RoutingResponse` |
| POST | `/approvals` | Dispatcher human-in-the-loop decision (approve/reject). | `ApprovalRequest` | `ApprovalResponse` |
| GET | `/dashboard/status` | Get global metrics (active incidents, pending approvals). | None | `DashboardStatus` |
| GET | `/dashboard/incidents` | List all tracked incidents. | None | `List[IncidentResponse]` |
| GET | `/dashboard/logs` | Fetch real-time AI agent activity logs. | None (Query params available) | `List[AgentLogEntry]` |
| GET | `/dashboard/approvals/pending` | List all routing plans awaiting human approval. | None | `List[RoutingResponse]` |
| POST | `/simulate` | Automatically inject and process a test scenario. | JSON: `{"scenario_type": "flood"}` | `IncidentResponse` |

## 4. Example Usage

**Create an Incident:**
```bash
curl -X 'POST' \
  'http://localhost:8000/incidents' \
  -H 'Content-Type: application/json' \
  -d '{
  "description": "Massive flooding on Main St, 3 families trapped on roof.",
  "location": {"lat": 6.9, "lon": 79.8}
}'
```

**Get Incident Status:**
```bash
curl -X 'GET' 'http://localhost:8000/incidents/INC-123456'
```

**Approve a Routing Plan:**
```bash
curl -X 'POST' \
  'http://localhost:8000/approvals' \
  -H 'Content-Type: application/json' \
  -d '{
  "plan_id": "PLAN-ABCDEF",
  "decision": "approve"
}'
```

## 5. Error Codes
- **400 Bad Request**: Malformed JSON or invalid parameter types.
- **404 Not Found**: The requested `incident_id` or `plan_id` does not exist in the state tracker.
- **422 Unprocessable Entity**: Missing required fields according to the Pydantic schema.
- **500 Internal Server Error**: Unexpected failure in the agent execution pipeline.

## 6. Integration with Frontend
The `Streamlit` dashboard utilizes the Python `api_client.py` wrapper to communicate with these endpoints, strictly separating UI rendering from AI reasoning. Future mobile apps (e.g., Flutter) can simply execute HTTP POST/GET requests to these same endpoints to receive native JSON structures.

## 7. Mock Mode
ResQ-MAR API features an automatic mock-fallback. On startup, the API pings `localhost:11434` (Ollama). If unreachable, the system automatically falls back to Mock Mode. In Mock Mode, endpoints still return perfectly formatted JSON responses using deterministic logic instead of invoking the heavy LLMs, ensuring UI development and client integration testing can proceed without a massive GPU footprint.
