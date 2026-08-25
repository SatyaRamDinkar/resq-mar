# 🚨 ResQ-MAR
## AI-Powered Multi-Agent Emergency Response System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/LLM-Ollama-orange.svg" alt="Ollama">
  <img src="https://img.shields.io/badge/Framework-AutoGen-red.svg" alt="AutoGen">
  <img src="https://img.shields.io/badge/Routing-OR--Tools-yellow.svg" alt="OR-Tools">
  <img src="https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg" alt="ChromaDB">
</p>

<p align="center">
  <b>Coordinated Intelligence for Coordinated Response</b><br>
  Multi-agent orchestration · Agentic RAG · Adaptive truck-drone routing · Edge resilience
</p>

## Overview
ResQ-MAR is a comprehensive, AI-powered disaster management platform designed to transform unstructured, panicked citizen distress signals into safe, accountable, and highly coordinated field operations. It solves the profound "last-mile" challenge of emergency response, where traditional static protocols and manual dispatching buckle under the pressure of rapidly compounding crises. Built for emergency management agencies, human dispatchers, and field responders, the platform acts as an intelligent "Disaster Copilot." What sets ResQ-MAR apart is its commitment to absolute operational resilience and data privacy: it runs 100% locally using open-source Large Language Models, supports multi-hazard incidents, and enforces strict Human-in-the-Loop oversight for life-or-death decisions.

## 🎥 Demo
> *Demo video and screenshots will be added after Phase 4 implementation.*

## Key Features
- 🤖 **6 Specialized AI Agents** — Intake, Metadata, Planner, Router, Comms, Edge
- 🔍 **Agentic RAG Pipeline** — 4-step context-aware task planning using disaster SOPs
- 🗺️ **Adaptive Truck-Drone Routing** — Event-triggered re-optimization with OR-Tools
- 🛡️ **Human-in-the-Loop** — Mandatory approval gates for high-urgency dispatches
- 📱 **Edge Resilience** — Offline-capable SLM for field responders via PWA
- 🌐 **Real-Time Dashboard** — Streamlit-based live incident tracking and visualization
- 💰 **100% Free & Open Source** — Zero API costs, zero subscriptions

## Architecture

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
│              │ ORCHESTRATION LAYER │                        │
│              │ (AutoGen GroupChat) │                        │
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
│                    │   RAG   │                              │
│                    │ Pipeline│                              │
│                    └────┬────┘                              │
│                         │                                   │
│              ┌──────────┴──────────┐                        │
│              │   KNOWLEDGE LAYER   │                        │
│              │  ChromaDB + SOPs    │                        │
│              └─────────────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```
*High-level system architecture showing the 3-layer design.*

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Multi-Agent Framework | AutoGen (AG2) | Agent orchestration & conversation |
| Local LLM | Ollama + Llama 3.1 | Zero-cost, offline-capable inference |
| Vector Database | ChromaDB | SOP storage & semantic retrieval |
| Routing Engine | Google OR-Tools | Multi-depot VRP with time windows |
| Dashboard | Streamlit + Folium | Real-time incident visualization |
| Backend API | FastAPI + Uvicorn | RESTful service layer |
| Edge Model | Phi-3-mini (GGUF) | <2GB offline guidance |
| Mobile | Progressive Web App | Offline-first responder client |

## Quick Start

### Prerequisites
- Python 3.10+
- Git
- Ollama (install from https://ollama.com/download)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/resq-mar.git
cd resq-mar

# 2. Run the setup script
chmod +x setup.sh
./setup.sh

# 3. Start Ollama (in a separate terminal)
ollama serve

# 4. Verify everything works
python verify.py

# 5. Run the hello-world demo
python hello_world_agent.py

# 6. Launch the dashboard
streamlit run frontend/streamlit_app.py
```
