<!-- Page 1 -->
# System Design Document (SAD) — ResQ-MAR

## 1. DOCUMENT CONTROL
- **Title:** System Design Document (SAD) — ResQ-MAR: AI-Powered Multi-Agent Emergency Response System
- **Version:** 1.0
- **Date:** 2026-08-26
- **Author:** Antigravity AI
- **Status:** Draft for First Review
- **Revision History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-08-26 | Antigravity AI | Initial Draft covering all subsystems, APIs, database schemas, and agent architectures. |

---

## 2. EXECUTIVE SUMMARY
ResQ-MAR is an AI-powered, multi-agent disaster management platform designed to operate 100% locally using open-source technologies. It provides a cohesive ecosystem where specialized AI agents orchestrate emergency response, plan actionable tasks grounded in official guidelines, and compute adaptive delivery routes. 

The system solves the profound "last-mile" challenge of emergency management, where fragmented citizen distress signals fail to be translated into immediate, accountable field actions. ResQ-MAR delivers three key technical contributions: (1) a multi-hazard agentic Retrieval-Augmented Generation (RAG) pipeline that guarantees task safety and operational relevance; (2) an Adaptive Event-Triggered (AET) truck-drone collaborative routing engine powered by OR-Tools to bypass destroyed infrastructure; and (3) an offline-resilient edge Small Language Model (SLM) ensuring field responders and citizens maintain AI guidance during complete telecommunication blackouts. 

Primary users include stranded citizens (reporting incidents), human dispatchers (reviewing and overriding AI plans), and field responders (executing tasks). The platform spans a responsive web dashboard for command centers, a mobile Progressive Web App (PWA) for citizens, and an edge device deployment package for responders operating offline.

---

## 3. SYSTEM OVERVIEW

### 3.1 Purpose
The primary purpose of ResQ-MAR is to coordinate autonomous AI agents to parse, analyze, and respond to emergency incidents in real-time under the supervision of human dispatchers. Secondary purposes include predictive risk assessment through historical incident logging, offline procedural guidance via mobile SLMs, and post-incident analysis for performance auditing.

### 3.2 Scope
- **IN SCOPE:** 
  - Multi-hazard incident handling (floods, fires, earthquakes, medical emergencies).
  - Agentic RAG task planning using local vector databases.
  - Adaptive truck-drone collaborative routing with OR-Tools.
  - Real-time Streamlit command dashboard.
  - Edge SLM deployment for disconnected field use.
  - Explicit Human-in-the-Loop (HITL) approval workflows.
- **OUT OF SCOPE:** 
  - Actual hardware control or telemetry of physical drones.
  - Real-time satellite imagery or GIS raster processing.
  - Live video or drone-camera streaming capabilities.
  - Direct integration with proprietary government legacy systems.

### 3.3 Definitions & Acronyms

| Term | Definition |
|------|------------|
| **RAG** | Retrieval-Augmented Generation. Grounding LLM responses in external knowledge bases. |
| **SLM** | Small Language Model. A highly compressed language model (typically <3B parameters) designed for edge devices. |
| **VRP** | Vehicle Routing Problem. A mathematical optimization problem seeking the best routes for a fleet of vehicles. |
| **AET** | Adaptive Event-Triggered. A re-optimization strategy that updates routes only when disruption crosses a threshold. |
| **SOP** | Standard Operating Procedure. Official manuals and guidelines for emergency handling. |
| **MDMCVRPTW** | Multi-Depot Multi-Commodity Vehicle Routing Problem with Time Windows. |
| **GGUF** | GPT-Generated Unified Format. A binary format for distributing compressed/quantized LLMs optimized for CPU execution. |
| **PWA** | Progressive Web App. A web application that acts like a native app with offline caching capabilities. |
| **OR-Tools** | Google's open-source software suite for optimization, used for routing. |
| **AutoGen** | Microsoft's framework for developing multi-agent LLM applications. |
| **ChromaDB** | An open-source vector database for storing and retrieving embeddings. |
| **Ollama** | A lightweight, extensible framework for running local LLMs. |
| **GroupChat** | An AutoGen orchestrator paradigm where agents converse in a shared virtual room. |
| **UserProxyAgent** | An AutoGen agent acting as a proxy for human inputs (enabling HITL). |

### 3.4 References
- Aththanayake et al. (2026). *ResQConnect: An AI-Powered Multi-Agentic Platform for Human-Centered and Resilient Disaster Response*.
- *Literature Review: Multi-Agent AI Systems for Disaster Response* (ResQ-MAR Internal Document).
- Microsoft AutoGen Documentation (v0.2.x).
- Google OR-Tools Routing Library Documentation.

---

## 4. SYSTEM ARCHITECTURE (THE CORE)

### 4.1 High-Level Architecture
```text
┌─────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Streamlit   │  │ Mobile PWA  │  │ Edge Device (Termux)│  │
│  │ Dashboard   │  │ (Citizen)   │  │ (Field Responder)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         └─────────────────┴────────────────────┘            │
│                           │                                 │
│                    ┌──────┴──────┐                          │
│                    │  FastAPI    │                          │
│                    │  Gateway    │                          │
│                    └──────┬──────┘                          │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │   ORCHESTRATION LAYER │                        │
│              │  (AutoGen GroupChat)│                        │
│              └──────────┬──────────┘                        │
│                         │                                   │
│    ┌────────┬───────────┼───────────┬────────┐              │
│    ▼        ▼           ▼           ▼        ▼              │
│ ┌─────┐  ┌─────┐   ┌─────────┐   ┌─────┐  ┌─────┐           │
│ │Intake│  │Meta │   │Planner  │   │Route│  │Comms│           │
│ │Agent │  │Data │   │Agent    │   │Agent│  │Agent│           │
│ └─────┘  └─────┘   └────┬────┘   └─────┘  └─────┘           │
│                         │                                   │
│                    ┌────┴────┐                              │
│                    │  RAG    │                              │
│                    │ Pipeline│                              │
│                    └────┬────┘                              │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │   KNOWLEDGE LAYER   │                        │
│              │  ChromaDB + SOPs +  │                        │
│              │  Historical Data    │                        │
│              └─────────────────────┘                        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              EDGE / OFFLINE LAYER                   │    │
│  │  ┌─────────────┐  ┌─────────────────────────────┐   │    │
│  │  │ Edge Agent  │  │ Phi-3-mini (GGUF Q4_K_M)    │   │    │
│  │  │ (Local API) │  │ <2GB · <1.5GB RAM · <1s lat │   │    │
│  │  └─────────────┘  └─────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Component Descriptions

**Streamlit Dashboard**
- **Purpose:** Primary interface for human dispatchers and command center operators.
- **Responsibilities:**
  - Visualize live incidents on an interactive map.
  - Review and approve/reject AI-generated task plans.
  - Monitor vehicle and drone routing in real-time.
  - Provide a conversational interface to the orchestrator.
- **Technology Used:** Streamlit, Folium, Pandas.
- **Input/Output:** Consumes JSON from FastAPI; outputs HTTP requests.

**Mobile PWA**
- **Purpose:** Interface for affected citizens to report emergencies.
- **Responsibilities:**
  - Collect text, images, and geolocation data.
  - Work under poor connectivity using service workers.
  - Provide offline caching of critical safety advice.
- **Technology Used:** HTML5, JavaScript, Service Workers.
- **Input/Output:** Accepts user input; outputs JSON to FastAPI.

**Edge Device Client**
- **Purpose:** Provide offline guidance for field responders when cellular networks fail.
- **Responsibilities:**
  - Host a local API server.
  - Execute inference on a highly compressed SLM.
  - Synchronize queued reports when connectivity returns.
- **Technology Used:** Termux (Android), llama.cpp.
- **Input/Output:** Local text queries; outputs local text responses.

**FastAPI Gateway**
- **Purpose:** The central entry point for all presentation layer requests.
- **Responsibilities:**
  - Route HTTP requests to the Orchestration Layer.
  - Provide asynchronous endpoints to prevent blocking.
  - Expose Server-Sent Events (SSE) for real-time dashboard updates.
- **Technology Used:** FastAPI, Uvicorn.
- **Input/Output:** Accepts HTTP requests; outputs JSON responses.

**AutoGen GroupChat Orchestrator**
- **Purpose:** Manages agent conversation and task delegation.
- **Responsibilities:**
  - Maintain conversation history.
  - Select the next speaker based on LLM routing.
  - Trigger human-in-the-loop pauses via UserProxyAgent.
- **Technology Used:** Microsoft AutoGen.
- **Input/Output:** Raw strings/JSON; outputs agent dialogue.

**IntakeAgent**
- **Purpose:** Ingests the raw citizen report and normalizes it.
- **Responsibilities:**
  - Filter spam and non-emergencies.
  - Standardize text format.
- **Technology Used:** AutoGen ConversableAgent (Llama 3.1).
- **Input/Output:** Raw text; outputs normalized text.

**MetadataAgent**
- **Purpose:** Extracts structured fields from the normalized report.
- **Responsibilities:**
  - Identify hazard type, urgency, location.
  - Output strict JSON payload.
- **Technology Used:** AutoGen (Llama 3.1) with JSON mode.
- **Input/Output:** Normalized text; outputs JSON metadata.

**PlannerAgent**
- **Purpose:** Generates actionable task sequences grounded in official SOPs.
- **Responsibilities:**
  - Call the RAG pipeline tool.
  - Synthesize retrieved knowledge into tasks.
  - Estimate resource requirements.
- **Technology Used:** AutoGen + RAG Tool.
- **Input/Output:** Metadata JSON; outputs structured Task Plan JSON.

**RouterAgent**
- **Purpose:** Solves the physical logistics of the task plan.
- **Responsibilities:**
  - Formulate the OR-Tools VRP model.
  - Calculate truck and drone trajectories.
  - Compute AET disruption scores.
- **Technology Used:** Python, Google OR-Tools.
- **Input/Output:** Task Plan JSON; outputs Route GeoJSON.

**CommsAgent**
- **Purpose:** Dispatches final plans to field teams.
- **Responsibilities:**
  - Format routes and tasks into human-readable alerts.
  - Push data to the dashboard and PWA.
- **Technology Used:** AutoGen.
- **Input/Output:** GeoJSON and Plans; outputs Alert JSON.

**EdgeAgent**
- **Purpose:** Acts as a standalone offline advisor.
- **Responsibilities:**
  - Provide procedural safety advice.
  - Decline complex routing requests (fail-safe).
- **Technology Used:** llama.cpp, Phi-3-mini.
- **Input/Output:** User queries; outputs text responses.

**RAG Pipeline**
- **Purpose:** Provide factual grounding for the PlannerAgent.
- **Responsibilities:**
  - Embed queries.
  - Perform top-k vector search.
  - Assess retrieved chunks for relevance.
- **Technology Used:** Sentence-Transformers, ChromaDB.
- **Input/Output:** Text query; outputs verified text chunks.

**ChromaDB Knowledge Base**
- **Purpose:** Persistent storage for vector embeddings of SOPs.
- **Responsibilities:**
  - Store chunked markdown files.
  - Execute rapid cosine similarity searches.
- **Technology Used:** ChromaDB.
- **Input/Output:** Floats/Embeddings; outputs Document Chunks.

**Edge SLM Service**
- **Purpose:** Highly compressed LLM inference engine.
- **Responsibilities:**
  - Run efficiently on mobile CPU.
  - Keep RAM usage under 1.5GB.
- **Technology Used:** llama.cpp (GGUF).
- **Input/Output:** Tokens; outputs tokens.

### 4.3 Agent Interaction Flow
1. Citizen submits report via PWA → `POST /incident`
2. FastAPI validates the payload and forwards it to the Orchestrator.
3. Orchestrator spawns an AutoGen GroupChat with relevant agents.
4. **IntakeAgent** receives raw report and cleanses it.
5. **MetadataAgent** extracts structured data (hazard, lat/lon, urgency).
6. If urgency == HIGH → Orchestrator triggers `UserProxyAgent` to request human approval on the dashboard.
7. **PlannerAgent** receives metadata and queries the RAG Pipeline.
8. RAG Pipeline: retrieves top-k SOPs → assesses safety → passes context back.
9. **PlannerAgent** synthesizes the SOPs and returns a JSON task plan.
10. **RouterAgent** ingests the plan, formulates a VRP model, and solves it with OR-Tools.
11. **CommsAgent** translates the Route GeoJSON into field alerts.
12. All agents log decisions to the `agent_logs` SQLite table.
13. FastAPI broadcasts the final JSON to the Dashboard via Server-Sent Events (SSE).

---

## 5. DATA DESIGN

### 5.1 Data Flow Diagram
```text
 Citizen Report 
      │
      ▼
   [ JSON ]
      │
      ▼
   FastAPI 
      │
      ▼
 Orchestrator
      │
      ▼
 Agent Messages ──► RAG Query ──► ChromaDB
      │
      ▼
  [ Plan JSON ]
      │
      ▼
 Router Input
      │
      ▼
 [ Route GeoJSON ]
      │
      ▼
    Comms
      │
      ▼
 [ Alert JSON ]
      │
      ▼
  Dashboard
```

### 5.2 Database Schema
The system uses SQLite for lightweight, file-based persistence.

```sql
CREATE TABLE incidents (
    id TEXT PRIMARY KEY,
    raw_text TEXT NOT NULL,
    hazard_type TEXT CHECK(hazard_type IN ('flood', 'fire', 'earthquake', 'medical', 'unknown')),
    location_lat REAL NOT NULL,
    location_lon REAL NOT NULL,
    urgency TEXT CHECK(urgency IN ('low', 'medium', 'high', 'critical')),
    status TEXT CHECK(status IN ('received', 'planning', 'routing', 'dispatched', 'resolved')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE task_plans (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    retrieved_sops TEXT NOT NULL,
    quality_score REAL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_by TEXT,
    FOREIGN KEY(incident_id) REFERENCES incidents(id)
);

CREATE TABLE routes (
    id TEXT PRIMARY KEY,
    incident_id TEXT NOT NULL,
    vehicle_id TEXT NOT NULL,
    vehicle_type TEXT CHECK(vehicle_type IN ('ambulance', 'fire_truck', 'relief_truck', 'drone')),
    route_geojson TEXT NOT NULL,
    estimated_time_min INTEGER,
    status TEXT CHECK(status IN ('planned', 'active', 'completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(incident_id) REFERENCES incidents(id)
);

CREATE TABLE agent_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    action TEXT NOT NULL,
    input_data TEXT,
    output_data TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(incident_id) REFERENCES incidents(id)
);

CREATE TABLE sops (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    hazard_type TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding_id TEXT NOT NULL,
    source TEXT NOT NULL
);
```

### 5.3 Data Dictionary

**Table: incidents**
- `id` (TEXT): UUID primary key. Ex: `inc_1234`
- `raw_text` (TEXT): Original user text. Ex: "Flood waters rising in sector 4."
- `hazard_type` (TEXT): Categorical hazard type. Ex: `flood`
- `location_lat` (REAL): Latitude. Ex: `6.9271`
- `location_lon` (REAL): Longitude. Ex: `79.8612`
- `urgency` (TEXT): Priority level. Ex: `critical`
- `status` (TEXT): Lifecycle status. Ex: `received`
- `created_at` (TIMESTAMP): Time of submission.
- `resolved_at` (TIMESTAMP): Time incident closed.

**Table: task_plans**
- `id` (TEXT): UUID primary key.
- `incident_id` (TEXT): FK to incidents.
- `plan_json` (TEXT): Array of actionable tasks.
- `retrieved_sops` (TEXT): Array of ChromaDB UUIDs.
- `quality_score` (REAL): Confidence score of RAG.
- `generated_at` (TIMESTAMP): Time generated.
- `approved_by` (TEXT): Dispatcher ID.

**Table: routes**
- `id` (TEXT): UUID primary key.
- `incident_id` (TEXT): FK to incidents.
- `vehicle_id` (TEXT): Identifier for physical vehicle.
- `vehicle_type` (TEXT): drone or truck.
- `route_geojson` (TEXT): Spatial route path.
- `estimated_time_min` (INTEGER): ETA in minutes.
- `status` (TEXT): Current state.
- `created_at` (TIMESTAMP): Time planned.

**Table: agent_logs**
- `id` (INTEGER): Auto-increment PK.
- `incident_id` (TEXT): FK to incidents.
- `agent_name` (TEXT): Ex: `PlannerAgent`.
- `action` (TEXT): Ex: `retrieve_sops`.
- `input_data` (TEXT): Input JSON.
- `output_data` (TEXT): Output JSON.
- `timestamp` (TIMESTAMP): Time of action.

**Table: sops**
- `id` (TEXT): Document UUID.
- `title` (TEXT): Ex: "Flood Evacuation Guidelines".
- `hazard_type` (TEXT): Ex: `flood`.
- `content` (TEXT): Raw markdown text.
- `embedding_id` (TEXT): FK linking to ChromaDB vectors.
- `source` (TEXT): Ex: "NDRSC Sri Lanka".

---

## 6. API SPECIFICATIONS

The FastAPI Gateway exposes the following 10 REST endpoints. All request/response bodies are application/json.

### 1. POST `/incident`
**Description:** Submit a new emergency incident from the PWA.
**Status Codes:** 201 Created, 400 Bad Request
**REQUEST:**
```json
{
  "reporter_id": "citizen_001",
  "raw_text": "Fire in Building 7, 3rd floor, people trapped",
  "location": {"lat": 12.9716, "lon": 77.5946},
  "media_urls": [],
  "timestamp": "2026-09-15T10:30:00Z"
}
```
**RESPONSE:**
```json
{
  "incident_id": "inc_550e8400",
  "status": "received",
  "estimated_processing_time": "15s",
  "message": "Incident received. Agents are analyzing."
}
```

### 2. GET `/incident/{id}`
**Description:** Fetch status and details of a specific incident.
**Status Codes:** 200 OK, 404 Not Found
**REQUEST:** `GET /incident/inc_550e8400`
**RESPONSE:**
```json
{
  "id": "inc_550e8400",
  "status": "planning",
  "hazard_type": "fire",
  "urgency": "critical",
  "location_lat": 12.9716,
  "location_lon": 77.5946
}
```

### 3. GET `/incidents`
**Description:** List all active incidents for the dashboard map.
**Status Codes:** 200 OK
**REQUEST:** `GET /incidents?status=active`
**RESPONSE:**
```json
[
  {
    "id": "inc_550e8400",
    "location": [12.9716, 77.5946],
    "urgency": "critical"
  }
]
```

### 4. POST `/incident/{id}/approve`
**Description:** Human dispatcher explicitly approves the AI-generated task/route plan.
**Status Codes:** 200 OK, 403 Forbidden
**REQUEST:**
```json
{
  "dispatcher_id": "disp_99",
  "approval_status": "approved",
  "override_notes": ""
}
```
**RESPONSE:**
```json
{
  "status": "dispatched",
  "message": "Units successfully mobilized."
}
```

### 5. GET `/plan/{incident_id}`
**Description:** Retrieve the detailed Task Plan JSON generated by the PlannerAgent.
**Status Codes:** 200 OK
**REQUEST:** `GET /plan/inc_550e8400`
**RESPONSE:**
```json
{
  "incident_id": "inc_550e8400",
  "tasks": [
    {"step": 1, "action": "Deploy aerial drone for fire assessment", "resource": "drone"},
    {"step": 2, "action": "Dispatch Engine 4", "resource": "fire_truck"}
  ],
  "sops_referenced": ["sop_fire_01"]
}
```

### 6. GET `/route/{incident_id}`
**Description:** Retrieve the OR-Tools optimized Route GeoJSON for map rendering.
**Status Codes:** 200 OK
**REQUEST:** `GET /route/inc_550e8400`
**RESPONSE:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "LineString",
        "coordinates": [[77.5900, 12.9700], [77.5946, 12.9716]]
      },
      "properties": {"vehicle": "drone_alpha"}
    }
  ]
}
```

### 7. GET `/dashboard/stream`
**Description:** Server-Sent Events (SSE) endpoint providing real-time pushes of agent states.
**Status Codes:** 200 OK (Stream)
**REQUEST:** `GET /dashboard/stream`
**RESPONSE:**
```text
data: {"agent": "PlannerAgent", "event": "retrieving_sops", "incident": "inc_550e8400"}
```

### 8. GET `/edge/query`
**Description:** Endpoint on the local Edge Device API to query the offline SLM.
**Status Codes:** 200 OK
**REQUEST:**
```json
{
  "query": "How do I perform CPR on a drowning victim?"
}
```
**RESPONSE:**
```json
{
  "response": "Ensure the scene is safe. Check responsiveness. If no breathing, begin chest compressions...",
  "source": "Offline Model (Phi-3-mini)"
}
```

### 9. GET `/health`
**Description:** Liveness probe for system components.
**Status Codes:** 200 OK
**REQUEST:** `GET /health`
**RESPONSE:**
```json
{
  "api": "healthy",
  "database": "connected",
  "chromadb": "connected",
  "ollama_server": "running"
}
```

### 10. GET `/agents/status`
**Description:** View current activity status of all AutoGen agents.
**Status Codes:** 200 OK
**REQUEST:** `GET /agents/status`
**RESPONSE:**
```json
{
  "IntakeAgent": "idle",
  "MetadataAgent": "idle",
  "PlannerAgent": "processing_inc_550e8400",
  "RouterAgent": "idle"
}
```

---

## 7. AGENT DESIGN (DETAILED)

The orchestration layer relies on a team of 6 primary agents built on Microsoft AutoGen.

### 7.1 IntakeAgent
- **Class Name:** `IntakeAgent`
- **Base Class:** `ConversableAgent`
- **System Message:** "You are the Intake Agent. Your job is to read raw, panicked citizen reports, filter out non-emergency spam, and rewrite the report into clear, professional, objective English. Do not add information that is not present."
- **Input Schema:** `{"raw_text": str}`
- **Output Schema:** `{"normalized_text": str, "is_spam": bool}`
- **Processing Logic:** Analyzes semantics. If `is_spam` is true, terminates flow. Else, passes `normalized_text` to MetadataAgent.
- **Error Handling:** If text is incomprehensible, tags `is_spam: false` but adds an `unclear` flag.

### 7.2 MetadataAgent
- **Class Name:** `MetadataAgent`
- **Base Class:** `ConversableAgent`
- **System Message:** "Extract structured metadata from the normalized report. You must identify hazard_type (flood, fire, earthquake, medical), estimate the urgency (low, medium, high, critical), and extract coordinates if mentioned."
- **Input Schema:** `{"normalized_text": str}`
- **Output Schema:** `{"hazard_type": str, "urgency": str, "lat": float, "lon": float}`
- **Processing Logic:** Uses few-shot prompting to strictly format output as JSON.
- **Error Handling:** If coordinates are missing, returns default `[0.0, 0.0]` to trigger fallback geo-IP location.

### 7.3 PlannerAgent
- **Class Name:** `PlannerAgent`
- **Base Class:** `ConversableAgent`
- **System Message:** "You are the Tactical Planner. You must query the RAG Pipeline for official SOPs based on the metadata. Once retrieved, synthesize a step-by-step, actionable task plan including exact resource requirements."
- **Input Schema:** `{"metadata": dict}`
- **Output Schema:** `{"tasks": list, "resources_needed": dict}`
- **Processing Logic:** 
  1. Calls `query_rag(hazard_type)` tool.
  2. Receives assessed SOP chunks.
  3. Writes JSON plan mapping tasks to resource capacities.
- **Error Handling:** If RAG returns no data, uses generic fallback logic based on universal safety protocols.

### 7.4 RouterAgent
- **Class Name:** `RouterAgent`
- **Base Class:** `ConversableAgent`
- **System Message:** "You are the Logistics Router. Take the required resources and map them to physical vehicles (Trucks and Drones). You will formulate the constraints and invoke the OR-Tools Python solver to generate GeoJSON routes."
- **Input Schema:** `{"resources_needed": dict, "target_location": list}`
- **Output Schema:** `{"routes": list}`
- **Processing Logic:** Acts as a code-execution agent. Formulates the MDMCVRPTW arrays, calls the local OR-Tools script, and parses the output.
- **Error Handling:** If OR-Tools fails to find a feasible solution, it relaxes the time window constraints and retries.

### 7.5 CommsAgent
- **Class Name:** `CommsAgent`
- **Base Class:** `ConversableAgent`
- **System Message:** "You are the Communications Officer. Translate the final task plan and routing GeoJSON into a brief, human-readable alert for the field responders."
- **Input Schema:** `{"tasks": list, "routes": list}`
- **Output Schema:** `{"alert_text": str}`
- **Processing Logic:** Synthesizes technical JSON into a military-style dispatch briefing.
- **Error Handling:** Truncates excessive text to ensure rapid transmission over low-bandwidth radios.

### 7.6 EdgeAgent
- **Class Name:** `EdgeAgent`
- **Base Class:** N/A (llama.cpp integration via LangChain)
- **System Message:** "You are an offline disaster survival assistant running on a mobile device. Provide safe, conservative procedural advice. You do not have internet access."
- **Input Schema:** `{"query": str}`
- **Output Schema:** `{"response": str}`
- **Processing Logic:** Loads a highly quantized GGUF model (`Phi-3-mini-4k-instruct-q4_K_M.gguf`, ~1.8GB) into RAM and processes the user string directly.
- **Error Handling:** If the prompt is too long, truncates to 1024 tokens.

### 7.7 Orchestrator (GroupChat)
- **Configuration:** AutoGen `GroupChat` with `GroupChatManager`.
- **Selection Strategy:** Strict round-robin enforced (Intake → Meta → Planner → Router → Comms) to prevent non-deterministic loops.
- **Human-in-the-Loop:** A `UserProxyAgent` intercepts the flow after the PlannerAgent if `urgency == "critical"`. It waits via WebSockets for the Streamlit dashboard to send an approval signal.
- **Termination:** Stops when CommsAgent emits the final alert.

---

## 8. RAG PIPELINE DESIGN

### 8.1 Architecture
```text
User Query 
   │
   ▼
Embedding Model (all-MiniLM-L6-v2)
   │
   ▼
ChromaDB Retrieval (top-k=5)
   │
   ▼
Context Assembly + Assessor Prompt
   │
   ▼
Local LLM (Llama 3.1)
   │
   ▼
Structured Output (Pydantic Plan)
```

### 8.2 Knowledge Base
- **SOPs Included:** 
  - Flood Evacuation Protocols (NDRSC)
  - Wildfire Mitigation Guidelines (Sphere)
  - Earthquake Structural Assessment 
  - Triage Medical Handbooks
- **Chunking Strategy:** Paragraph-level chunking (approx. 250-300 words) with 50-word overlap to preserve procedural context.
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2`. It outputs 384-dimensional vectors, balancing extreme speed with high semantic accuracy on local CPU.
- **Vector Store:** ChromaDB running in persistent mode (`./chroma_data`).

### 8.3 Agentic RAG Flow (4 Steps)
1. **Normalize:** MetadataAgent converts raw input ("Help water rising fast") into a structured search query ("Flood, rising water evacuation").
2. **Retrieve:** PlannerAgent's tool queries ChromaDB for the top 5 chunks matching the query.
3. **Assess:** An internal Assessor prompt evaluates the chunks. If they are generic (e.g., "Water is wet"), the Assessor rejects them and reformulates the query (e.g., "Vertical evacuation procedures").
4. **Plan:** The accepted chunks are appended to the system prompt, forcing the PlannerAgent to ground its generated tasks strictly in the provided text.

---

## 9. ROUTING ENGINE DESIGN

### 9.1 Problem Formulation
The problem is mathematically framed as a **Multi-Depot Multi-Commodity Vehicle Routing Problem with Time Windows (MDMCVRPTW)**.
- **Objective:** Minimize a composite score: `Z = Total Travel Time + Priority-Weighted Delay + Route Instability Penalty`.
- **Constraints:**
  - Vehicle capacity constraints per commodity (e.g., water, medkits).
  - Time windows ensuring critical nodes are reached before conditions worsen.
  - Subtour elimination.

### 9.2 Adaptive Event-Triggered (AET) Re-optimization
To prevent extreme computational overhead, ResQ-MAR implements an AET strategy based on the ResQConnect paper.
- **Trigger Condition:** The system calculates a disruption score `D(t)` based on the urgency of a new request and spatial deviation from existing routes. 
- If `D(t)` exceeds a decaying threshold, OR-Tools performs a global re-optimization. Otherwise, a simple greedy insertion is used.

### 9.3 OR-Tools Model Pseudocode
```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def solve_vrp(data):
    # 1. Create Routing Index Manager and Model
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    # 2. Add Distance Callback and Dimension
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    routing.AddDimension(transit_callback_index, 0, 3000, True, "Distance")

    # 3. Add Capacity Constraints
    # (Implementation of multi-commodity capacities...)

    # 4. Set Search Parameters (GLD)
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.time_limit.seconds = 5 # Force quick solution for dynamic routing

    # 5. Solve and Extract Routes
    solution = routing.SolveWithParameters(search_parameters)
    return extract_geojson(solution, routing, manager)
```

### 9.4 Truck-Drone Collaboration
Taking inspiration from Peng et al. (2025), ResQ-MAR models truck-drone collaboration.
- **Modeled As:** A heterogeneous fleet. Trucks traverse the road graph network. Drones traverse a Euclidean (straight-line) graph. 
- **Collaboration Constraint:** Drone routes are constrained to start and end at specific "rendezvous nodes" that intersect with the truck's route, simulating the truck acting as a mobile launching depot to bypass impassable roads.

---

## 10. EDGE / OFFLINE DESIGN

### 10.1 Edge Architecture
```text
  Field Device (Android/iOS Tablet)
         │
         ▼
      [ Termux ]
         │
         ▼
[ llama.cpp server ] ◄── Phi-3-mini (GGUF)
         │
         ▼
  [ Local API ] ──► Mobile PWA UI
```

### 10.2 Model Selection
- **Base Model:** `microsoft/Phi-3-mini-4k-instruct`. It has 3.8B parameters and exhibits exceptional reasoning capabilities relative to its size.
- **Quantization:** Converted to GGUF format with `Q4_K_M` (4-bit) quantization via `llama.cpp`.
- **Performance targets:** 
  - Size on disk: ~2.2 GB.
  - VRAM/RAM required: < 1.5 GB.
  - Latency: < 1s per token generation on a standard mobile CPU (Snapdragon 8 Gen 2).

### 10.3 Offline Mode Logic
The PWA frequently sends lightweight ping requests to the FastAPI Gateway. If a timeout occurs (network drop), the PWA seamlessly routes inference requests to the local `localhost:8080` API hosted by Termux. The EdgeAgent answers queries based on its pre-trained disaster knowledge. Any incident reports submitted offline are cached in IndexedDB and pushed as a batch queue once the ping to FastAPI succeeds.

### 10.4 PWA Design
- **Service Worker:** Caches the HTML, CSS, JS, and essential UI assets.
- **IndexedDB:** Stores queued JSON incident reports.
- **Responsive Design:** Optimized for touch interfaces on 6-inch to 10-inch screens.

---

## 11. DEPLOYMENT ARCHITECTURE

### 11.1 Development Environment
- **OS:** Cross-platform (Windows, macOS, Linux).
- **Python:** 3.10+ in a virtual environment (`venv`).
- **Local Services:** Ollama running `llama3.1` on port 11434.

### 11.2 Production Environment (Demo Deployment)
Because ResQ-MAR is designed for low-resource EOCs, the production deployment avoids complex Kubernetes or cloud clusters.
- **Backend:** Uvicorn serving FastAPI.
- **Frontend:** Streamlit running as a single local process.
- **Database:** SQLite (file-based).
- **Vector DB:** ChromaDB (persistent local storage).
- **LLM:** Ollama framework.

### 11.3 Deployment Diagram
```text
  [ Command Center Laptop ]
             │
   ┌─────────┼─────────┐
   │                   │
[Ollama]   [FastAPI]  [Streamlit]
(11434)      (8000)     (8501)
   │           │           │
   └───────────┼───────────┘
               │ (Localhost loopback)
               ▼
        [ SQLite Database ]
        [ ChromaDB Store  ]
```

---

## 12. SECURITY & SAFETY CONSIDERATIONS

### 12.1 Human-in-the-Loop (HITL)
Autonomous action is inherently dangerous in emergency scenarios. ResQ-MAR enforces HITL through an explicit trigger. If `urgency >= "high"`, the Orchestrator stalls the workflow, alerting the Streamlit dashboard. The system blocks deployment until a dispatcher POSTs to `/incident/{id}/approve`. A 5-minute timeout forces auto-rejection if unaddressed, defaulting to standard human protocols.

### 12.2 Data Privacy
All infrastructure is strictly self-hosted. Citizen reports contain anonymous `reporter_id` strings. Because the system avoids external APIs (like OpenAI), sensitive geolocation and emergency data never leave the command center's local area network.

### 12.3 Fail-Safe Design
- **PlannerAgent Failure:** Falls back to hardcoded JSON templates for basic tasks.
- **RouterAgent / OR-Tools Failure:** Defaults to a Greedy nearest-neighbor spatial assignment.
- **Ollama / LLM Crash:** FastAPI queues all incidents and alerts the dashboard to switch to manual entry mode.

---

## 13. TECHNOLOGY JUSTIFICATION

**AutoGen vs. CrewAI vs. LangGraph**
AutoGen was chosen because its `GroupChat` orchestration and `UserProxyAgent` natively support structured state-passing and seamless Human-in-the-Loop integration. While CrewAI is simpler, it lacks AutoGen's deterministic control over multi-agent workflows necessary for strict disaster guidelines.

**Ollama/Llama3.1 vs. GPT-4o vs. Claude**
Llama 3.1 8B running via Ollama was selected because it delivers GPT-3.5 level reasoning while running entirely offline on consumer hardware. GPT-4o violates our strict requirement for cloud independence and data privacy during infrastructure collapse.

**ChromaDB vs. Pinecone vs. Weaviate**
ChromaDB runs locally, natively supports Python, and uses a persistent file structure. Pinecone is a cloud-only SaaS, which makes it useless in offline disaster environments.

**OR-Tools vs. DRL vs. Custom Heuristics**
Google OR-Tools provides mathematically optimal, deterministic, and highly explainable routing solutions. Deep Reinforcement Learning (DRL) requires massive offline training, is computationally heavy, and acts as a "black box," making it unsuitable for dispatchers who need to trust and explain routing decisions.

**SQLite vs. PostgreSQL vs. MongoDB**
SQLite was chosen for its zero-configuration, serverless nature. Disaster command centers often run off standard laptops; running a massive PostgreSQL daemon introduces unnecessary points of failure.

**Streamlit vs. React vs. Flask**
Streamlit allows rapid development of data-rich Python dashboards with built-in mapping (Folium) without requiring a separate front-end JavaScript stack, perfectly aligning with a data-science capstone timeline.

**Phi-3-mini vs. Llama-3.1-8B for Edge**
Phi-3-mini (3.8B) can be quantized down to under 2GB, fitting into the RAM of standard Android phones. Llama 3.1 8B requires at least 4-5GB of RAM, which crashes smaller field devices and aggressively drains batteries.

---

## 14. APPENDIX

**A. Glossary Updates**
- *HitL:* Human-in-the-Loop.
- *GLD:* Guided Local Search, a metaheuristic used by OR-Tools to escape local minima.
- *GeoJSON:* An open standard format designed for representing simple geographical features.

**B. Change Log**
- *v1.0 (2026-08-26):* Complete document generated aligning ResQConnect base research with local LLM, OR-Tools, and multi-source RAG extensions.

<!-- End of Document -->
