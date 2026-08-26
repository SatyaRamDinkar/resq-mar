# ResQ-MAR Demo Guide

Welcome to the ResQ-MAR Capstone Project Demo. This repository contains a full multi-agent emergency response system utilizing Agentic RAG, Adaptive Routing, and Edge LLMs.

## Quick Start
To watch the full 3-scenario automated demo in your console, run:
```bash
python scripts/run_full_demo.py
```
*(This script has timed pauses to allow for live video narration).*

## What You'll See
1. **Scenario 1 (Flood)**: Demonstrates the 4-step Agentic RAG system iteratively correcting missing SOPs.
2. **Scenario 2 (Fire)**: Demonstrates AET (Adaptive Event-Triggered) routing saving massive amounts of compute vs standard routing.
3. **Scenario 3 (Earthquake)**: Demonstrates Truck-Drone collaborative routing bypassing road blockages.

All scenarios conclude with our Human-in-the-Loop decision verification.

## Full UI Dashboard
To run the interactive live dashboard with the geographic folium heatmap:
```bash
streamlit run frontend/streamlit_app_enhanced.py
```

## System Requirements
- Python 3.12+
- (Optional but recommended) Ollama running locally on port 11434 with `phi3:mini` or `llama3.1`. The demo will gracefully mock agent thinking delays if Ollama is absent, ensuring 100% reliability for live presentations.

## Additional Links
- **Demo Video**: [Coming Nov 2026]
- **Full Benchmark Report**: See `data/benchmark_results/benchmark_report.txt`
