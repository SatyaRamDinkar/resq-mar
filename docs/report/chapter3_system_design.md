# Chapter 3: System Design and Architecture

## 3.1 Design Philosophy
The core design philosophy of ResQ-MAR revolves around modularity, resilience, and human-AI collaboration. By strictly separating concerns, the system ensures that distinct tasks (e.g., semantic extraction vs. spatial optimization) are handled by specialized agents. A "local-first" philosophy ensures that the system incurs zero API costs and inherently preserves data privacy by processing all 911 transcripts on local hardware.

## 3.2 System Architecture
The ResQ-MAR pipeline operates as a sequential, agent-driven workflow orchestrated by a central controller. The data flow is structured as follows:
1. User Input (raw emergency text) is received by the IntakeAgent.
2. The IntakeAgent parses the text into structured JSON and passes it to the MetadataAgent.
3. The MetadataAgent enriches the data with geographic and hazard tags.
4. The PlannerAgent initiates the Agentic RAG pipeline to retrieve relevant Standard Operating Procedures (SOPs).
5. The RouterAgent receives the plan and calculates optimal paths using OR-Tools, incorporating truck-drone logic.
6. The DashboardAgent captures the generated plan and halts execution, presenting a GUI for Human-in-the-Loop approval.
7. Upon human approval, the CommsAgent dispatches the final instructions.
8. If cloud connectivity is lost, the offline PWA client seamlessly routes requests to the EdgeAgent.

## 3.3 Agent Design
Each agent in the system inherits from a robust `BaseAgent` abstraction, standardizing input/output formats.

| Agent Name | Role | Input | Output | LLM Used |
|---|---|---|---|---|
| IntakeAgent | Parses raw text | Raw string | Structured JSON | Llama-3.1-8B |
| MetadataAgent | Context enrichment | JSON Incident | Augmented JSON | Llama-3.1-8B |
| PlannerAgent | Tactical strategy | Augmented JSON | Task list | Llama-3.1-8B |
| RetrievalAgent | Vector DB querying | Query string | SOP Context | Llama-3.1-8B |
| AssessorAgent | Context evaluation | SOP Context | Pass/Fail boolean | Llama-3.1-8B |
| RouterAgent | VRP parameterization | Task list | Optimized Routes | Llama-3.1-8B |
| CommsAgent | Field instruction | Optimized Routes | Dispatch messages | Llama-3.1-8B |
| DashboardAgent | State management | Pipeline events | UI State Dict | Python native |
| EdgeAgent | Offline fallback | Raw string | Localized guidance | Phi-3-mini |

## 3.4 Knowledge Base and RAG Pipeline
The knowledge base utilizes ChromaDB as a local vector store, embedding SOPs using the `all-MiniLM-L6-v2` model. To overcome the limitations of naive retrieval, ResQ-MAR implements a 4-step Agentic RAG loop. The RetrievalAgent queries the database; the AssessorAgent critically evaluates the output against the incident's metadata. If safety-critical data is missing, the AssessorAgent reformulates the query and forces a re-retrieval, ensuring comprehensive operational safety.

## 3.5 Routing Engine
The spatial optimization engine leverages the Google OR-Tools CP-SAT solver. The routing module is enhanced with two distinct features:
- **AET Adaptive Routing**: Instead of solving the VRP upon every incident, the router batches incidents based on spatial distance and temporal thresholds, drastically reducing computational overhead.
- **Truck-Drone Collaborative Model**: Ground vehicles are modeled as mobile depots. When a target node is tagged as `is_roadblocked=True`, the solver restricts trucks to proximal safe nodes and dispatches drones to complete the final segment, bounded by a 5km flight radius constraint.

## 3.6 Edge Deployment
Resilience is achieved by hosting a quantized SLM (Phi-3-mini, 1.6GB) on a dedicated port (11435) via Ollama. A Progressive Web App (PWA) continuously pings the primary port (11434). If the primary model fails or network connectivity drops, the client automatically re-routes API calls to the EdgeAgent, preserving core QA capabilities using a highly targeted disaster dataset.

## 3.7 Dashboard and Human-in-the-Loop
The user interface is built using Streamlit. It features a real-time auto-refreshing command center, an interactive Folium-based heatmap displaying coverage metrics, and a vital Approval Panel. The system is hard-coded to pause execution at the routing phase, requiring a human dispatcher to click "Approve" or "Reject", thus preventing AI hallucinations from manifesting in physical resource deployments.

## 3.8 Technology Stack

| Component | Technology | Version | Purpose |
|---|---|---|---|
| AI Framework | AutoGen AG2 | 0.2.35 | Multi-agent orchestration |
| Local LLM Server | Ollama | Latest | Hosting local models |
| Large Language Model | Llama 3.1 | 8B | Complex reasoning |
| Small Language Model | Phi-3 | mini | Edge computing |
| Vector Database | ChromaDB | Latest | SOP embeddings |
| Optimization Solver| OR-Tools | Latest | Vehicle routing |
| Frontend | Streamlit | Latest | Dispatch dashboard |

## 3.9 Summary
The architecture of ResQ-MAR is specifically designed for disaster resilience. By compartmentalizing tasks among intelligent agents and backing the system with a hard-coded VRP solver and an edge-fallback mechanism, the system guarantees robust performance even in degraded environments.
