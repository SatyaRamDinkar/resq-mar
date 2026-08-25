# Phase 2 MVP Summary

**Date:** 2026-08-26

## What Was Built
- `src/agents/comms_agent.py`: Generates concise human-readable dispatch alerts.
- `src/agents/orchestrator.py`: Manages strict sequential execution of agents with human-in-the-loop approval.
- `tests/test_integration.py`: Integration tests for full pipeline execution.
- `src/agents/demo_orchestrator.py`: Final MVP demo script covering 3 key scenarios (Fire, Flood, Spam).
- `README_UPDATE.md`: Patch notes for the main README.

## Architecture Diagram

```
+---------------+      +------------------+
|   User Input  | ---> |   IntakeAgent    | (Normalizes, Detects Spam)
+---------------+      +--------+---------+
                                |
                                v
                       +------------------+
                       |  MetadataAgent   | (Extracts hazard, urgency)
                       +--------+---------+
                                |
                                v
                       +------------------+
                       | Human Dispatcher | (Approves high/critical incidents)
                       +--------+---------+
                                |
                                v
+---------------+      +------------------+
|   ChromaDB    | <--- |   PlannerAgent   | (RAG SOP retrieval, generates JSON plan)
+---------------+      +--------+---------+
                                |
                                v
+---------------+      +------------------+
|   OR-Tools    | <--- |   RouterAgent    | (VRP solver, assigns locations/vehicles)
+---------------+      +--------+---------+
                                |
                                v
                       +------------------+
                       |    CommsAgent    | (Formats broadcast alert)
                       +--------+---------+
                                |
                                v
                       +------------------+
                       | Streamlit Dash   | (Visualizes map, feed, logs)
                       +------------------+
```

## Test Results
- All tests passing. The integration suite runs under 5 seconds using mocked LLM outputs.

## Known Limitations
- JSON parsing from LLMs can occasionally fail on very long prompts; currently handled with fallback logic.
- Single-trip VRP: vehicles cannot return to depot and make a second trip in the current MVP formulation.
- No real-time streaming: incidents are processed statically.

## Next Steps for Phase 3
- Agentic RAG: Add an assessment step before planning.
- Multi-trip / Multi-depot routing.
- Truck-drone collaborative routing (AET routing).
- Full live real-time dashboard.
