# ResQ-MAR User Manual

Version: 1.0.0
Date: November 2026
Authors: Satya Ram Dinkar
Target Audiences: Dispatcher, Administrator, Developer

## Table of Contents
1. [CHAPTER 1: SYSTEM OVERVIEW](#chapter-1-system-overview)
2. [CHAPTER 2: INSTALLATION AND SETUP](#chapter-2-installation-and-setup)
3. [CHAPTER 3: STARTING THE SYSTEM](#chapter-3-starting-the-system)
4. [CHAPTER 4: DISPATCHER GUIDE - USING THE DASHBOARD](#chapter-4-dispatcher-guide---using-the-dashboard)
5. [CHAPTER 5: EMERGENCY OPERATIONS](#chapter-5-emergency-operations)
6. [CHAPTER 6: ADMINISTRATOR GUIDE - CONFIGURATION AND MAINTENANCE](#chapter-6-administrator-guide---configuration-and-maintenance)
7. [CHAPTER 7: TROUBLESHOOTING](#chapter-7-troubleshooting)
8. [CHAPTER 8: DEVELOPER GUIDE - EXTENDING THE SYSTEM](#chapter-8-developer-guide---extending-the-system)
9. [APPENDIX A: QUICK REFERENCE CARD](#appendix-a-quick-reference-card)
10. [APPENDIX B: GLOSSARY](#appendix-b-glossary)
11. [APPENDIX C: CHANGE LOG](#appendix-c-change-log)

---

## CHAPTER 1: SYSTEM OVERVIEW

### 1.1 What is ResQ-MAR?
ResQ-MAR is a comprehensive, open-source, AI-powered Multi-Agent Emergency Response System designed to revolutionize how emergency dispatch centers handle incoming distress calls, allocate resources, and route emergency vehicles. Built as a capstone project extending the ResQConnect architecture, ResQ-MAR integrates local large language models (LLMs) via Ollama, agentic retrieval-augmented generation (RAG), and physical road network routing via Open Source Routing Machine (OSRM). By keeping all AI processing local, the system guarantees 100% data privacy and maintains operational capability even when disconnected from the broader internet.

Key differentiators include:
- Open-Source and Local: No reliance on paid cloud APIs (e.g., OpenAI or Google Cloud).
- Multi-Agent Architecture: Six specialized AI agents handle distinct phases of the emergency response pipeline.
- Human-in-the-Loop: Critical decisions, especially regarding hazardous materials or complex resource allocation, require explicit human dispatcher approval before execution.
- Physical Routing: Uses real street-level data for Colombo, Sri Lanka, factoring in one-way streets and driving durations.

### 1.2 Who Should Read This Manual?
This manual is comprehensive and designed for three distinct audiences. You do not need to read the entire document unless you are responsible for all aspects of the system.
- Dispatcher: The primary end-user operating the dashboard. Read Chapters 1, 4, 5, and 7.
- Administrator: The IT professional responsible for deploying, configuring, and backing up the system. Read Chapters 1, 2, 3, 6, and 7.
- Developer: The software engineer tasked with maintaining or extending the codebase. Read Chapters 1, 2, 3, 6, and 8.

### 1.3 System Architecture at a Glance
The ResQ-MAR system operates on a pipeline model where an incident flows through multiple intelligent agents before arriving at a final dispatch plan.

[ Incident Data ] -> [ Intake Agent ] -> [ Metadata Agent ] -> [ Planner Agent ] <-> [ Agentic RAG ] -> [ Router Agent ] -> [ Approval Panel ] -> [ Comms Agent ] -> [ Dashboard ]

1. Intake Agent: Parses raw emergency text and categorizes the incident.
2. Metadata Agent: Extracts exact geolocation coordinates and timestamps.
3. Planner Agent: Determines required resources (e.g., Firetrucks, Ambulances) and queries the SOP database via RAG.
4. Router Agent: Calculates the optimal path using OSRM or Haversine distance.
5. Approval Panel: Human dispatcher reviews the plan.
6. Comms Agent: Generates plain-text instructions for field responders.

### 1.4 Key Features Summary
- Multi-Agent Pipeline: Autonomous handling of incident classification and routing.
- Edge SLM Fallback: Utilizes Phi-3-mini for low-resource or offline environments.
- Agentic RAG: Dynamically retrieves Standard Operating Procedures (SOPs) based on incident context.
- OSRM Integration: Real-world road physics and drive-time calculations.
- Truck-Drone Collaboration: Advanced routing allowing drones to scout ahead of heavy trucks.
- AET Adaptive Routing: Reduces computational solver calls by 66.7% through intelligent thresholding.
- Real-Time Heatmap: Interactive Folium maps rendering live incident data.
- RESTful API Backend: FastAPI integration allowing external sensors to trigger the pipeline.

---

## CHAPTER 2: INSTALLATION AND SETUP

### 2.1 Prerequisites
Before attempting to install ResQ-MAR, ensure your system meets the following minimum and recommended requirements.

Hardware Requirements:
- Minimum: 8GB RAM, 4-core CPU, 50GB available disk space.
- Recommended: 16GB RAM (or higher), 8-core CPU, 100GB available disk space, dedicated GPU for faster LLM inference.
- Internet connection is required during the initial setup to download models and map data.

Software Requirements:
- Operating System: Windows 10/11, Ubuntu 22.04 LTS, or macOS 13+ (Apple Silicon supported).
- Python: Version 3.12 or higher.
- Git: For version control and repository cloning.
- Docker: Required for running the OSRM routing engine locally.
- Ollama: The local LLM engine.

### 2.2 Step-by-Step Installation

Step 1: Clone the repository
Open your terminal or command prompt and run the following commands to download the source code:
```bash
git clone https://github.com/SatyaRamDinkar/resq-mar.git
cd resq-mar
```

Step 2: Create a virtual environment
It is highly recommended to isolate Python dependencies.
For Linux/macOS:
```bash
python -m venv venv
source venv/bin/activate
```
For Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

Step 3: Install dependencies
With your virtual environment activated, install all required Python packages:
```bash
pip install -r requirements.txt
```

Step 4: Install and start Ollama
- Download the installer for your OS from https://ollama.com
- Install the application and ensure the background service is running.
- Pull the required local models by executing:
```bash
ollama pull llama3.1
ollama pull phi3:mini
```
- Verify the models are available:
```bash
ollama list
```

Step 5: Set up OSRM (Optional but highly recommended)
To use real street-level routing instead of straight-line distances, you must compile the local map data using Docker.
For Windows:
```powershell
scripts\setup_osrm.bat
```
For Linux/macOS:
```bash
bash scripts/setup_osrm.sh
```
[NOTE] This process will download the Sri Lanka map (approx. 137MB) and compile it. It may take up to 10 minutes. 
Verify it is running:
```bash
curl http://localhost:5000/route/v1/driving/79.8612,6.9271;79.8650,6.9300?overview=false
```

Step 6: Verify installation
Run the built-in verification script to ensure all components are configured correctly:
```bash
python scripts/verify.py
```
Expected output: "[OK] All checks passed"

### 2.3 Configuration
System configurations are stored in JSON files and environment variables.
- LLM Settings: Edit `src/config/llm_config.json` to change the default models, ports, or temperature settings for the agents.
- Environment Variables: You can override defaults by setting the following environment variables:
  - RESQMAR_OLLAMA_URL=http://localhost:11434
  - RESQMAR_OSRM_URL=http://localhost:5000
  - RESQMAR_API_PORT=8000
  - RESQMAR_DASHBOARD_PORT=8501

### 2.4 First-Time Setup Checklist
- [ ] Ollama running with llama3.1 and phi3:mini
- [ ] OSRM Docker container running (optional, falls back to Haversine if offline)
- [ ] Python Virtual environment activated
- [ ] Dependencies from requirements.txt installed
- [ ] verify.py passes all connectivity checks

---

## CHAPTER 3: STARTING THE SYSTEM

### 3.1 Starting All Services (Full Stack)
To run the complete ResQ-MAR system, you need to launch its core components in separate terminal windows. Ensure your Python virtual environment is activated in every terminal.

Terminal 1 (AI Engine):
```bash
ollama serve
```
(If you are using the desktop application, this may already be running in the background).

Terminal 2 (API Backend):
```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 3 (Dashboard UI):
```bash
streamlit run frontend/streamlit_app_enhanced.py
```

Terminal 4 (Routing Engine - If not started by the setup script):
```bash
docker start <osrm_container_id>
```

Expected ports in use:
- 11434: Ollama LLM Service
- 5000: OSRM Routing Service
- 8000: FastAPI Backend
- 8501: Streamlit User Dashboard

### 3.2 Starting Individual Components
If you only need to run specific parts of the system for testing or maintenance:
- API only: `python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000`
- Dashboard only: `streamlit run frontend/streamlit_app_enhanced.py`
- Command-Line Demo script: `python scripts/run_full_demo.py`
- Automated Benchmark: `bash scripts/run_benchmark.sh`

### 3.3 Verifying Services Are Running
You can quickly check the health of the system using standard HTTP requests:
- API Health: `curl http://localhost:8000/health` (Expected response: {"status": "healthy"})
- OSRM Health: `curl http://localhost:5000/route/v1/driving/...`
- Dashboard: Open your web browser and navigate to `http://localhost:8501`.

### 3.4 Stopping the System
To gracefully shut down ResQ-MAR:
1. Go to Terminal 3 (Streamlit) and press Ctrl+C.
2. Go to Terminal 2 (FastAPI) and press Ctrl+C.
3. To stop the routing engine, run `docker stop <osrm_container_id>`.
4. To stop Ollama, close the desktop application or press Ctrl+C in Terminal 1.

---

## CHAPTER 4: DISPATCHER GUIDE - USING THE DASHBOARD

### 4.1 Logging In
Open your standard web browser (Chrome, Firefox, or Edge recommended) and navigate to `http://localhost:8501`. For this local V1.0 deployment, no username or password is required. You will be placed immediately into the main Command Center. Future versions may add authentication via reverse proxy configurations.

### 4.2 The Command Center (Home Page)
The Command Center is your primary workspace. It features a modern, clean layout divided into three main sections:
- Top Bar: Quick statistics showing total active incidents, available resources, and overall system health.
- Left Sidebar: Navigation links to the Heatmap, Agent Monitor, and Performance Metrics.
- Main Incident Feed: A live-updating table of all emergencies.

How to read the incident table:
- ID: Unique identifier for the emergency.
- Type: The classification (e.g., Medical, Fire, Flood).
- Severity: The critical level determined by the AI.
- Status: Pending, Processing, Waiting for Approval, or Dispatched.

Severity Color Coding:
- Low (Gray): Non-life-threatening, standard response time acceptable.
- Medium (Yellow): Urgent but contained situations.
- High (Orange): Life-threatening or rapidly escalating emergencies.
- Critical (Red): Mass casualty events or severe structural threats.

### 4.3 Submitting a New Incident
During normal operations, incidents will automatically populate the dashboard via the API. However, you can manually input an emergency:
1. Click the "Simulate New Incident" button on the sidebar.
2. Type the emergency details exactly as reported by the caller.
3. Click "Submit".
What happens next: The text is sent to the Intake Agent, which extracts the location and severity, then passes it down the pipeline until a routing plan is generated.

### 4.4 The Approval Panel
[WARNING] The Approval Panel is the most critical component for a human dispatcher. It ensures AI accountability.

When it appears: 
If the AI determines an incident is "High" or "Critical" severity (such as a hazardous material spill), it will pause the pipeline and generate an Approval Panel at the top of your dashboard.

How to review:
Read the "Incident Details" summary, examine the "Proposed Routes," and review the "Resource Allocation" (e.g., 2 Firetrucks, 1 Drone). Check the retrieved SOPs to ensure the AI followed protocol.

How to approve:
If the plan is sound, click the green "APPROVE" button. The system will immediately dispatch the vehicles and notify field teams.

How to reject:
If the plan is flawed (e.g., sending an ambulance into a flood zone without a boat), type your reasoning into the text box and click the red "REJECT" button. The plan is logged as rejected, and the system resets, awaiting a new manual or adjusted AI plan.

### 4.5 The Incident Heatmap
Navigate to the Heatmap page via the sidebar to view spatial data.
- How to read: The map uses Folium to render geographic data. Red zones indicate high incident density, blue icons indicate flood events, and orange icons indicate earthquakes or fires.
- Filters: Use the dropdown menus at the top to filter by incident type, severity, or a specific date range.
- Coverage statistics: The map displays a "Covered Incidents" metric, which calculates the percentage of active incidents located within a 5km radius of an available depot or responding unit.

### 4.6 The Agent Monitor
This page provides transparency into the AI's "thought process."
- Reading the table: Each of the 6 agents will display a status: Active (currently processing), Running (online but idle), Completed (task finished), or Error.
- Flow Diagram: A visual flowchart highlights which agent currently possesses the incident data.
- What to do if an agent shows "error": This usually indicates a timeout with the Ollama service. Navigate to the Troubleshooting chapter for resolution steps.

### 4.7 Performance Metrics
This dashboard provides analytics on system efficiency.
- How to interpret: Look at the "Coverage %" (higher is better), "Route Quality" (average deviation from optimal), and "Solver Calls Saved" (metrics proving the AET router is working).
- Exporting reports: Click the "Export Report" button to download a CSV file of the day's metrics for administrative review.

### 4.8 Common Dispatcher Tasks
To ensure smooth operations, follow this daily routine:
- Task 1: Check system health at the start of your shift (look for green indicators on all agents).
- Task 2: Continuously review and approve pending routing plans in the Approval Panel.
- Task 3: Monitor active incidents on the heatmap to identify emerging disaster clusters.
- Task 4: Export the daily performance report at the end of your shift.

---

## CHAPTER 5: EMERGENCY OPERATIONS

### 5.1 Handling a Flood Emergency
Floods present unique routing challenges due to submerged roads.
- Step 1: Receive the incident via auto-ingestion or manual entry.
- Step 2: Verify the Planner Agent successfully retrieved the flood_evacuation SOP from the knowledge base.
- Step 3: Review the routing plan carefully. Ensure the AI has allocated boats for submerged coordinates and heavy trucks only for dry staging areas.
- Step 4: Approve the plan in the dashboard.
- Step 5: Monitor the dispatch on the heatmap, watching for bottleneck congestion.

### 5.2 Handling a Fire Emergency
Fires, especially those involving chemicals, trigger strict protocols.
- Hazmat considerations: The AI should detect keywords like chemical, spill, or toxic fumes and elevate the severity to Critical.
- Truck-drone coordination: Ensure the proposed plan utilizes collaborative routing (trucks establish a perimeter while a drone provides thermal imaging).
- [IMPORTANT] Human approval is MANDATORY for all hazmat incidents. The system is hardcoded to never auto-dispatch these events.

### 5.3 Handling an Earthquake
Earthquakes cause widespread, simultaneous incidents.
- Building collapse scenarios require heavy rescue equipment routing.
- The AET router will drastically reduce solver calls during an earthquake to prevent system overload, processing incidents in micro-batches.
- Dispatchers must monitor aftershocks and manually reject routes that cross bridges or known fault lines if the OSRM data has not yet updated to reflect destroyed infrastructure.

### 5.4 When the System Goes Offline
ResQ-MAR is designed for resilience.
- Edge mode activates automatically if the connection to the primary LLM (llama3.1) is lost.
- The system will fall back to the smaller Phi-3-mini model, which requires fewer resources and provides basic, critical guidance without relying on cloud internet.
- During offline mode, OSRM falls back to Haversine (straight-line) distance calculations.
- The queue will sync with the central server automatically when the connection is restored.

---

## CHAPTER 6: ADMINISTRATOR GUIDE - CONFIGURATION AND MAINTENANCE

### 6.1 Adding New SOPs to the Knowledge Base
To update the Agentic RAG database with new Standard Operating Procedures:
1. Create a new markdown file in the `data/sops/` directory.
2. Follow the strict formatting guidelines: `# Title`, `## Steps`, `## Equipment`, `## Safety Notes`.
3. Open a terminal and run the ingestion script:
```bash
python src/rag/embeddings.py --ingest data/sops/new_sop.md
```
4. Verify the ingestion by querying the database via the API or testing a related incident in the dashboard.

### 6.2 Updating LLM Models
Administrators can configure which models the agents use.
1. Open `src/config/llm_config.json` in a text editor.
2. Change the `model_name` attribute for any specific agent (e.g., changing "llama3.1" to "mistral").
3. Ensure the new model is pulled locally via `ollama pull <model_name>`.
4. Restart the FastAPI server.
5. Verify changes by running `curl http://localhost:8000/health`.

### 6.3 Managing OSRM Data
Road networks change over time. To keep routing accurate:
- Updating road network: Re-run the `scripts/setup_osrm.sh` script to download the latest OpenStreetMap extract.
- Switching regions: Edit the `wget` URL inside the setup script to point to a different Geofabrik region (e.g., changing Sri Lanka to a specific US State).
- Performance tuning: For massive maps, you can change the algorithm parameter in the docker run command from `--algorithm mld` to `--algorithm ch` (Contraction Hierarchies) for faster queries at the cost of longer build times.

### 6.4 Backup and Restore
Regular backups are critical for disaster recovery.
- What to backup: The vector database (`data/chroma_db/`), benchmark logs (`data/benchmark_results/`), and configuration files.
- Backup command (Linux/macOS):
```bash
tar -czf resqmar_backup_$(date +%Y%m%d).tar.gz data/ src/config/
```
- Restore: Simply extract the tar archive into the project root directory, overwriting the existing folders.

### 6.5 Log Files
Monitoring logs is essential for system auditing.
- API logs: Available in the terminal output running Uvicorn, or can be redirected to a file (`> api.log`).
- Dashboard logs: Printed directly to the Streamlit console.
- Agent logs: Accessible programmatically via the `/dashboard/logs` REST endpoint.
- Log rotation: On Linux production servers, use `logrotate` to prevent log files from consuming all disk space. On Windows, schedule a PowerShell script to clean files older than 30 days.

### 6.6 Security Considerations
V1.0 is designed for local, trusted-network deployment.
- Local deployment: Ensure Windows Defender or `ufw` firewall rules allow inbound traffic on ports 8000 and 8501 only from trusted internal IP addresses.
- Authentication: There is no built-in login screen in v1.0. For production deployment, you MUST place the Streamlit and FastAPI servers behind a secure reverse proxy (like Nginx or Traefik) equipped with Basic Auth, OAuth2, or SAML.
- Ollama API: Ensure Ollama is bound to `localhost` (127.0.0.1) to prevent external actors from exploiting your GPU resources.

---

## CHAPTER 7: TROUBLESHOOTING

### 7.1 Ollama Issues
Symptom: The dashboard or API health check reports "Ollama unavailable" or agents return empty responses.
- Check: Run `ollama list` in the terminal. It should list `llama3.1` and `phi3:mini`.
- Fix 1: If models are missing, run `ollama pull llama3.1`.
- Fix 2: If the service is dead, run `ollama serve` to restart the background daemon.

### 7.2 OSRM Issues
Symptom: The terminal logs show "OSRM unavailable, using haversine fallback".
- Check: Run `docker ps` and verify the OSRM container is running.
- Check: Run `curl http://localhost:5000/route/v1/driving/79.86,6.92;79.87,6.93?overview=false`.
- Fix 1: If the container is stopped, run `docker start <container_id>`.
- Fix 2: If the map data is corrupted, delete the `data/osrm/` folder and re-run `scripts/setup_osrm.bat`.

### 7.3 API Server Issues
Symptom: The dashboard fails to load data and reports "Connection refused" on port 8000.
- Check (Linux): `netstat -tlnp | grep 8000`
- Check (Windows): `netstat -ano | findstr 8000`
- Fix 1: Kill any orphaned Python processes blocking port 8000 and restart Uvicorn.
- Fix 2: If port 8000 is used by another application, change the port in the Uvicorn command and update `RESQMAR_API_PORT`.

### 7.4 Dashboard Issues
Symptom: Streamlit hangs indefinitely on a "Please wait..." spinner.
- Check: Is the FastAPI server running? The dashboard depends entirely on the API.
- Check: Open your browser's Developer Tools (F12) and check the Console for JavaScript errors.
- Fix: Perform a hard refresh (Ctrl+F5) or restart the Streamlit terminal process.

### 7.5 Agent Errors
Symptom: The Agent Monitor displays an "error" status for a specific agent (e.g., Planner Agent).
- Check: Review the detailed agent logs via the `/dashboard/logs` endpoint or the FastAPI terminal.
- Check: Ensure the Ollama response format is valid. The agents expect JSON objects. If the LLM hallucinates plain text, the JSON parser will fail.
- Fix: Restart the API server. If the issue persists, ensure you are using a highly capable model like llama3.1 rather than a heavily quantized small model that struggles with JSON formatting.

### 7.6 Performance Issues
Symptom: System response times exceed 5-10 seconds per incident.
- Check: Monitor system RAM and GPU VRAM usage. Local LLMs require significant memory (llama3.1 requires at least 4-8GB of free RAM).
- Check: Note that OSRM routing is computationally heavier than Haversine math.
- Fix 1: Close unnecessary desktop applications (Chrome tabs, IDEs) to free up memory for Ollama.
- Fix 2: Downgrade the configuration to use `phi3:mini` across all agents for a massive speed boost at a slight cost to reasoning accuracy.

### 7.7 Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `ConnectionRefusedError: [Errno 111]` | A backend service is down. | Restart Uvicorn or Docker. |
| `JSONDecodeError: Expecting value` | LLM failed to output valid JSON. | Retry the incident; check model config. |
| `KeyError: 'routes'` | OSRM failed to find a valid road path. | Verify coordinates are on land; fallback to haversine. |
| `ModuleNotFoundError: No module named 'src'` | Python path is incorrect. | Run commands from the project root directory. |
| `Docker Desktop is unable to start` | WSL2 is not installed or configured. | Run `wsl --install` as Administrator and reboot. |
| `Validation Error for Pydantic Model` | API received badly formatted data. | Ensure dashboard matches API schemas. |
| `ChromaDB: Could not connect to database` | Corrupted vector database. | Delete `data/chroma_db/` and re-ingest SOPs. |
| `Ollama: model not found` | The specified model isn't downloaded. | Run `ollama pull <model_name>`. |

---

## CHAPTER 8: DEVELOPER GUIDE - EXTENDING THE SYSTEM

### 8.1 Adding a New Agent
ResQ-MAR is highly modular. To add a new agent (e.g., a "Weather Agent"):
1. Create a new Python file in `src/agents/weather_agent.py`.
2. Create a class that inherits from `BaseAgent`.
3. Implement the required `process()` method to handle the logic.
4. Register the new agent in `src/agents/orchestrator.py` by adding it to the pipeline sequence.
5. Write corresponding unit tests in the `tests/` directory to ensure reliability.

### 8.2 Adding a New Routing Algorithm
To implement a custom routing logic (e.g., an Ant Colony Optimization solver):
1. Create a new file in `src/routing/aco_solver.py`.
2. Implement a `solve()` method that conforms to the existing interface.
3. It must accept a `distance_matrix` (from OSRM or Haversine) and a list of demands.
4. It must return a standardized `routes` dictionary mapping vehicle IDs to path coordinates.
5. Add the new algorithm to `scripts/run_benchmark.sh` to compare its performance against the existing VRP OR-Tools solver.

### 8.3 Adding Dashboard Components
To expand the user interface:
1. Create a new component script in `frontend/components/`.
2. Utilize standard Streamlit widgets (`st.metric`, `st.dataframe`, `st.plotly_chart`).
3. Import the component into `frontend/streamlit_app_enhanced.py`.
4. Add the component to the appropriate page section or create a new sidebar navigation link.

### 8.4 API Endpoint Extensions
To expose new functionality to external clients:
1. Create a new router file in `src/api/` (e.g., `routes_weather.py`).
2. Define the endpoints using `APIRouter` from FastAPI.
3. Register the router in `src/api/main.py` using `app.include_router()`.
4. Define any necessary data validation schemas using Pydantic in `src/api/models.py`.
5. Add integration tests to `src/api/test_api.py`.

### 8.5 Contributing Guidelines
We welcome contributions from the open-source community.
1. Fork the official repository.
2. Create a feature branch (`git checkout -b feature/new-solver`).
3. Write comprehensive unit tests for your additions.
4. Submit a Pull Request with a clear description of the changes.
5. Code Style: Adhere to PEP 8 standards. Ensure all terminal output and documentation is strictly ASCII-only. Docstrings are required for all public classes and methods.

---

## APPENDIX A: QUICK REFERENCE CARD

Ports and Services:
- 11434: Ollama LLM Service
- 5000: OSRM Docker Routing Server
- 8000: FastAPI Backend
- 8501: Streamlit Dashboard UI

File Locations:
- Config: `src/config/llm_config.json`
- Logs: Terminal stdout or `data/benchmark_results/`
- Map Data: `data/osrm/`
- Vector DB: `data/chroma_db/`

Environment Variables:
- `RESQMAR_OLLAMA_URL`
- `RESQMAR_OSRM_URL`
- `RESQMAR_API_PORT`
- `RESQMAR_DASHBOARD_PORT`

Emergency Commands:
- Restart API: `Ctrl+C` then `python -m uvicorn src.api.main:app`
- Check Health: `curl http://localhost:8000/health`
- Backup Data: `tar -czf backup.tar.gz data/ src/config/`

---

## APPENDIX B: GLOSSARY
- Agent: An autonomous AI component designed to handle a specific task in the pipeline.
- SOP: Standard Operating Procedure. Official protocols for handling specific emergencies.
- RAG: Retrieval-Augmented Generation. A technique allowing LLMs to search a database for facts before answering.
- VRP: Vehicle Routing Problem. The mathematical challenge of finding optimal routes for a fleet of vehicles.
- AET: Adaptive Evaluation Threshold. ResQ-MAR's proprietary algorithm to skip solver calls for simple routes.
- OSRM: Open Source Routing Machine. A C++ routing engine using real map data.
- Ollama: A lightweight tool for running large language models locally.
- OR-Tools: Google's optimization software suite used for solving the VRP.
- CP-SAT: Constraint Programming - Boolean Satisfiability. The specific solver engine used by OR-Tools.
- Edge SLM: Small Language Model (like Phi-3) deployed on low-power "edge" devices without internet.
- PWA: Progressive Web App. Web applications providing native-like experiences.
- Folium: A Python library used for rendering interactive Leaflet maps.
- Streamlit: The Python framework used to build the dispatcher dashboard.
- FastAPI: The high-performance Python framework powering the backend REST API.
- ChromaDB: The vector database used to store and retrieve embedded SOP documents.
- Haversine: A mathematical formula used to calculate the straight-line, "as-the-crow-flies" distance between two GPS coordinates.
- Dispatcher: The human operator responsible for overseeing the system and approving critical plans.
- ETA: Estimated Time of Arrival.
- Coverage: A performance metric indicating the percentage of emergencies within range of a responder.
- Route Quality: A metric evaluating how close a proposed route is to the mathematical optimum.

---

## APPENDIX C: CHANGE LOG

v1.0.0 (November 2026): Initial release
- Implemented 6 autonomous AI agents (Intake, Metadata, Planner, Router, Comms, Orchestrator).
- Integrated Agentic RAG for dynamic SOP retrieval.
- Developed AET adaptive routing and Truck-Drone collaborative solvers.
- Validated Edge SLM capabilities using offline Phi-3-mini fallback.
- Deployed a highly concurrent FastAPI REST backend.
- Built the interactive Streamlit dashboard with Folium heatmap integration.
- Integrated OSRM via Docker for real-world road network physics.
- Completed full 50-incident benchmark suite, demonstration videos, and complete documentation.
