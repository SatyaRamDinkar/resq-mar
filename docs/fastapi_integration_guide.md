# FastAPI Integration Guide

## 1. What Changed
**Before:** The Streamlit dashboard (`frontend/streamlit_app_enhanced.py`) tightly coupled the UI with the AI logic by invoking the Python agent classes directly.
**After:** A robust `FastAPI` layer has been inserted. The Streamlit dashboard now utilizes `api_client.py` to make HTTP calls to the backend, which in turn orchestrates the agents.

**Benefits:**
- **Decoupling:** Frontend and backend can scale independently.
- **Mobile Ready:** External applications (Flutter, React Native) can now hook directly into the system.
- **External Integration:** IoT sensors (e.g., flood gauges) can POST incidents directly to `/incidents` without needing a human to type them in.

## 2. Architecture Update
```text
[Streamlit Dashboard] <--HTTP--> [FastAPI API] <--Python--> [Agents]
[Mobile App]        <--HTTP--> [FastAPI API] <--Python--> [Ollama]
[IoT Sensor]        <--HTTP--> [FastAPI API]
```

## 3. Running the Full Stack
To launch the complete ResQ-MAR distributed architecture, open three separate terminal windows:

**Terminal 1 (AI Server):**
```bash
ollama serve
```

**Terminal 2 (API Backend):**
```bash
scripts/run_api.bat
# or: scripts/run_api.sh
```

**Terminal 3 (Frontend Dashboard):**
```bash
streamlit run frontend/streamlit_app_enhanced.py
```

## 4. Updating the Dashboard
If you are modifying the Streamlit frontend, replace direct agent function calls with the `api_client.py` module.

*Before (Tightly Coupled):*
```python
from src.agents.orchestrator import run_pipeline
result = run_pipeline(text_input)
```

*After (Decoupled API):*
```python
from frontend.api_client import create_incident, request_routing
response = create_incident(text_input, 6.9, 79.8)
route_plan = request_routing(response["incident_id"], ["ambulance"])
```

## 5. Future Mobile App
Because the API strictly adheres to OpenAPI/Swagger standards, generating a mobile app client is trivial. 
- A Flutter app can be generated automatically using Swagger Codegen.
- Endpoints like `GET /dashboard/status` map directly to standard mobile dashboard screens.
- Webhooks or WebSockets (Phase 5) could easily be added to push notifications to first responders' phones when `POST /approvals` marks a plan as dispatched.
