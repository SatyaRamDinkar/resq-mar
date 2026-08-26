# Chapter 4: Implementation

## 4.1 Development Environment
The ResQ-MAR system was developed entirely in Python 3.12 within a virtual environment. Version control was managed via Git and hosted on GitHub. All LLM inference was executed locally using the Ollama application, ensuring zero external API dependencies and adhering to strict privacy protocols. The system was designed to be fully compatible with Windows `cp1252` encoding, strictly utilizing ASCII outputs for all console logging.

## 4.2 Phase 1: Foundation
Phase 1 involved establishing the repository structure and conducting a deep analysis of the primary base paper, ResQConnect. A gap analysis was performed against supplementary literature to identify areas where the original architecture could be extended, specifically noting the absence of offline edge capabilities and dynamic truck-drone routing.

## 4.3 Phase 2: MVP Sprint
The Minimum Viable Product (MVP) established the core agent pipeline. 
- **Step 1**: Intake and Metadata agents were engineered with strict JSON-mode system prompts to prevent free-text hallucinations.
- **Step 2**: The PlannerAgent was integrated with a basic ChromaDB RAG pipeline populated with predefined flood, fire, and earthquake SOPs.
- **Step 3**: The RouterAgent was developed as a wrapper around the Google OR-Tools routing solver, implementing basic distance matrices.
- **Step 4 & 5**: A basic Streamlit dashboard was created, and the `Orchestrator` class was written to manage the sequential handoffs between agents. An early hurdle involved prompt injection vulnerabilities where the LLM generated plans for non-emergencies; this was mitigated by patching the PlannerAgent to strictly return zero resources for "unknown" hazards.

## 4.4 Phase 3: Enhancement
Phase 3 constituted the majority of the novel technical contributions:
- **Agentic RAG**: A dual-agent loop was created inside `src/rag/agentic_rag.py`. The `AssessorAgent` was programmed to enforce a coverage checklist against retrieved context.
- **AET Routing**: The `AETRouter` class was implemented with a state machine tracking `trigger_thresholds`. This logic intercepts routing requests and returns warm-started previous solutions if the geographic center of mass of the incidents has not shifted significantly.
- **Truck-Drone Collaboration**: Data models were updated to include `vehicle_type` and `is_roadblocked`. The solver was modified into a two-tier approach: a primary routing pass for ground vehicles to accessible nodes, and a secondary pass routing drones from the ground vehicle stops to isolated nodes.
- **Edge SLM Integration**: The `EdgeAgent` was mapped to a secondary Ollama port. A Progressive Web App (PWA) skeleton was built (`pwa_offline.html`) featuring JavaScript ping mechanisms to handle automatic failover.
- **Enhanced Dashboard**: The UI was massively expanded using a `DashboardAgent` to manage state asynchronously. Components for human-in-the-loop approvals and a Folium map were integrated.

## 4.5 Code Quality and Testing
Robust testing was a priority throughout development. A comprehensive `pytest` suite was maintained in the `/tests` directory. Integration tests validated the OR-Tools mathematical constraints and ensuring the Agentic RAG loop terminated correctly. All Python code adheres to strict type hinting (`typing` module) to ensure structural integrity across complex agent data handoffs.

## 4.6 GitHub Repository
The complete source code is open-source and publicly available. The repository is organized logically into `src/`, `tests/`, `data/`, `frontend/`, and `docs/` directories. A comprehensive README provides installation instructions, architecture diagrams, and quick-start scripts. 
Link: https://github.com/SatyaRamDinkar/resq-mar

## 4.7 Summary
The implementation phase successfully translated the theoretical architecture into a functioning, tested software suite. Phase 3 introduced critical innovations over the base paper, establishing the foundation for quantitative evaluation in the following chapter.
