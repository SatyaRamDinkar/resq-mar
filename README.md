# ResQ-MAR 🚨
**Multi-Agent Emergency Response & Orchestration System**

![ResQ-MAR Dashboard](https://img.shields.io/badge/UI-Streamlit_Enhanced-3b82f6?style=for-the-badge)
![AI Framework](https://img.shields.io/badge/AI-Microsoft_AutoGen-10b981?style=for-the-badge)
![Local LLM](https://img.shields.io/badge/LLM-Ollama_Llama3-f59e0b?style=for-the-badge)

ResQ-MAR is a state-of-the-art, autonomous emergency management platform designed specifically for **Visakhapatnam, Andhra Pradesh**. By orchestrating a swarm of specialized AI agents, ResQ-MAR processes multi-modal civilian emergency inputs and dynamically routes resources in real-time, minimizing response delays during critical disasters.

---

## 🌟 Key Features

*   **🤖 Multi-Agent Swarm (AutoGen):** A specialized team of AI agents (Intake, Assessor, Planner, Router, and Comms) that collaborate to assess, plan, and execute emergency responses without human bottlenecks.
*   **🎙️ Multi-Modal Intake:** 
    *   **Voice (Whisper AI):** Automatically transcribes and parses raw 911 audio recordings.
    *   **Vision (Gemini/Llava):** Assesses structural damage and incident severity from citizen-uploaded disaster photos.
*   **🌍 Live Situational Awareness:** Integrates DuckDuckGo Search and Groq to inject real-time weather and news context into the AI's tactical planning window.
*   **🗺️ Geospatial Routing (OSRM):** Solves the Vehicle Routing Problem (VRP) to optimize ambulance and fire truck deployment across the Andhra Pradesh road network.
*   **🗣️ Multi-Language Dispatch:** Automatically translates emergency alerts and dispatcher instructions into **Telugu (తెలుగు)** and **Hindi (हिंदी)** for local responders.
*   **🔍 Explainable AI (XAI):** Features a dedicated Explainability Dashboard with MermaidJS flowcharts that trace the exact logical steps the AI took to reach a routing decision.

---

## 🛠️ Technology Stack

*   **Frontend:** Streamlit (Custom Glassmorphism CSS, Plotly, MermaidJS)
*   **AI Orchestration:** Microsoft AutoGen
*   **Local Inference:** Ollama (Llama 3.1)
*   **Routing Engine:** OSRM (Open Source Routing Machine) via Docker
*   **Testing:** Pytest (Full component and integration coverage)

---

## 🚀 Quick Start Guide

### 1. Prerequisites
*   Python 3.10+
*   [Ollama](https://ollama.ai/) installed locally.
*   [Docker Desktop](https://www.docker.com/) (required for OSRM).
*   FFmpeg (required for Whisper audio processing).

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/SatyaRamDinkar/resq-mar.git
cd resq-mar
pip install -r requirements.txt
```

### 3. Environment Setup
Copy the example environment file and add your API keys (for Gemini Vision and Groq Live Awareness):
```bash
cp .env.example .env
```

### 4. Start Local Services
Start Ollama and pull the required model:
```bash
ollama serve
ollama pull llama3.1
```

Start the OSRM Routing Engine (Ensure Docker is running):
```bash
docker run -d -p 5000:5000 --name osrm-router -v "${PWD}/data/osrm:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-southern-zone-latest.osrm
```

### 5. Launch the Command Center
```bash
python -m streamlit run frontend/streamlit_app_enhanced.py
```
Navigate to `http://localhost:8501` to view the live dashboard!

---

## 🧪 Testing
ResQ-MAR includes a robust test suite ensuring maximum reliability of the autonomous agents. To run the tests:
```bash
pytest tests/ -v
```

---
*Developed as a Capstone Project demonstrating the integration of Multi-Agent Systems in real-world disaster management.*
