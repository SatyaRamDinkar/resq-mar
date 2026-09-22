# ResQ-MAR 🚨 
**Multi-Agent Routing & Emergency Response Orchestration**

![ResQ-MAR Dashboard](https://img.shields.io/badge/UI-Streamlit_Enhanced-3b82f6?style=for-the-badge)
![AI Framework](https://img.shields.io/badge/AI-Microsoft_AutoGen-10b981?style=for-the-badge)
![Local LLM](https://img.shields.io/badge/LLM-Ollama_Llama3-f59e0b?style=for-the-badge)
![Cost](https://img.shields.io/badge/Cost-100%25_Free_%26_Open_Source-success?style=for-the-badge)

ResQ-MAR is a fully autonomous, cost-free, multi-modal emergency management platform tailored for **Visakhapatnam, Andhra Pradesh**. Built as a capstone research project, it leverages a Microsoft AutoGen swarm to process complex civilian emergencies, perform visual/audio triage, and optimize geospatial routing in real-time.

---

## 🔬 Academic Novelty & Differentiation from Base Papers

Traditional disaster response research (e.g., Li et al.) often proposes standalone AI models for specific tasks (like image classification). ResQ-MAR fundamentally differs by integrating these isolated capabilities into a **unified, autonomous Multi-Agent System (MAS)**.

| Feature / Domain | Standard Base Paper Approaches | ResQ-MAR Novelty & Innovation |
| :--- | :--- | :--- |
| **Damage Assessment** | Standalone computer vision models (requires human to review and manually dispatch). | **Integrated Vision-to-Routing:** Vision AI assesses severity and *autonomously* passes data to the Router Agent to prioritize ambulances. |
| **Situational Awareness** | Static RAG (Retrieval-Augmented Generation) based on pre-trained disaster datasets. | **Live News Injection:** Uses DuckDuckGo + Groq to scrape real-time weather/flood news and dynamically inject ground-truth into the Planner Agent. |
| **Language & Accessibility** | English-only dispatch protocols. | **Native Indian Localization:** Automatically translates final tactical plans into **Hindi (हिंदी)** and **Telugu (తెలుగు)** for local responders. |
| **System Architecture** | Single-LLM bottleneck (monolithic prompting). | **Swarm Intelligence:** 8 specialized AutoGen agents conversing and debating internally to reach a consensus before acting. |
| **Explainability** | Black-box routing decisions. | **XAI Flowcharts:** Dynamically generated MermaidJS diagrams proving *why* the AI made a specific routing choice. |

---

## 💸 100% Cost-Free & Localized Architecture

A major limitation in deploying AI in developing regions is the prohibitive cost of enterprise API calls (OpenAI, Google Maps, etc.). **ResQ-MAR is designed to be 100% cost-free to operate in production.**

| System Requirement | Traditional Enterprise Solution | ResQ-MAR Zero-Cost Alternative |
| :--- | :--- | :--- |
| **Core LLM Reasoning** | GPT-4o / Claude 3.5 (Pay-per-token) | **Ollama + Llama 3.1** (Runs 100% locally) |
| **Geospatial Routing** | Google Maps / Mapbox API (Paid) | **OSRM Docker Container** (Self-hosted OpenStreetMap data) |
| **Audio Transcription** | OpenAI Whisper API (Paid) | **Local Whisper Model** (Runs on CPU/GPU locally) |
| **Live Web Context** | SerpAPI / Bing Search API (Paid) | **DuckDuckGo-Search** (Free python scraper) |
| **Vision & Translation** | Google Cloud Vision / Translate | **Gemini Free Tier** (Zero-cost API usage) |

---

## 🧠 The Agent Pipeline & Work Phases

Developing ResQ-MAR required a phased engineering approach to build the 8-agent swarm and the surrounding infrastructure.

### Phase 1: Swarm Foundation & Core RAG
*   Implemented **Microsoft AutoGen** to create a conversational swarm architecture.
*   Developed the **Intake Agent**, **Metadata Agent**, and **Planner Agent**.
*   Built the Agentic RAG system with ChromaDB to fetch Standard Operating Procedures (SOPs).

### Phase 2: Geographic Localization & Routing
*   Shifted all mock data and coordinate systems to focus heavily on **Visakhapatnam, Andhra Pradesh** (RK Beach, Gajuwaka, etc.).
*   Integrated the Open Source Routing Machine (**OSRM**) to solve complex Vehicle Routing Problems (VRP) without cloud APIs.

### Phase 3: Multi-Modal Capabilities (Audio & Vision)
*   **Voice Intake:** Built a `VoiceIntake` pipeline using Whisper AI to convert raw civilian 911 audio recordings into text metadata.
*   **Vision Assessment:** Implemented the `VisionAgent` to allow citizens to upload disaster photos. The AI analyzes structural integrity and passes severity scores directly to the router.

### Phase 4: Real-Time Novelty Features
*   **LiveAwarenessAgent:** Built a real-time web crawler using DuckDuckGo to pull breaking news on the incident to prevent the AI from hallucinating weather conditions.
*   **LanguageService:** Implemented the `CommsAgent` to translate the final dispatch manifest into Telugu and Hindi.

### Phase 5: Faculty-Ready UI/UX Redesign
*   Overhauled the generic Streamlit interface into a stunning **Glassmorphism Dark-Mode Dashboard**.
*   Added **Plotly** interactive analytics, **MermaidJS** decision-tree flowcharts for Explainable AI (XAI), and a live hacker-style **Agent Chatter Terminal** to visualize backend operations.

---

## 🖥️ System Requirements & Setup

### 1. Prerequisites
*   **Python 3.10+**
*   **[Ollama](https://ollama.ai/)** (For running Llama 3.1 locally)
*   **[Docker Desktop](https://www.docker.com/)** (Required for the OSRM Routing Engine)
*   **FFmpeg** (Required for Whisper Audio processing)

### 2. Installation
```bash
git clone https://github.com/SatyaRamDinkar/resq-mar.git
cd resq-mar
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the root directory and add your free-tier API keys:
```env
GEMINI_API_KEY="your_free_gemini_key_here"
GROQ_API_KEY="your_free_groq_key_here"
```

### 4. Start Backend Services
Launch the local LLM:
```bash
ollama serve
ollama pull llama3.1
```
Launch the OSRM Routing Engine:
```bash
docker run -d -p 5000:5000 --name osrm-router -v "${PWD}/data/osrm:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-southern-zone-latest.osrm
```

### 5. Launch the Dashboard
```bash
python -m streamlit run frontend/streamlit_app_enhanced.py
```
Open `http://localhost:8501` to access the AI Command Center.

---

## 🧪 Testing & Reliability
To ensure the multi-agent swarm operates flawlessly without endless loops or crashes, the system is backed by a comprehensive test suite (37+ tests):
```bash
pytest tests/ -v
```
*(Tests cover AutoGen schemas, API fallbacks, routing assertions, and multi-language encodings).*
