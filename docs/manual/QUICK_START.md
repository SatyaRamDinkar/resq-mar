# ResQ-MAR Quick Start Guide

Welcome to the Quick Start guide for ResQ-MAR. This guide is for first-time users who want to get the system running locally within 5 minutes without reading the full, detailed manual.

## 1. Install Ollama
The system requires a local AI engine.
1. Download the installer from https://ollama.com
2. Run the installer and ensure the background service starts.

## 2. Pull Required Models
Open your terminal and download the specific LLMs used by the agents:
```bash
ollama pull llama3.1
ollama pull phi3:mini
```

## 3. Clone the Repository
Download the ResQ-MAR source code to your machine:
```bash
git clone https://github.com/SatyaRamDinkar/resq-mar.git
cd resq-mar
```

## 4. Install Dependencies
It is recommended to use a virtual environment. Install the Python packages:
```bash
python -m venv venv

# Activate on Linux/Mac:
# source venv/bin/activate
# Activate on Windows:
venv\Scripts\activate

pip install -r requirements.txt
```

## 5. Run the Automated Demo
Test the core agent pipeline without starting the web servers:
```bash
python scripts/run_full_demo.py
```
Expected output at the end of the script: `3 scenarios complete, report saved`

## 6. Open the Dashboard
To interact with the live system, start the FastAPI backend and Streamlit UI in two separate terminals.
Terminal 1:
```bash
python -m uvicorn src.api.main:app --reload
```
Terminal 2:
```bash
streamlit run frontend/streamlit_app_enhanced.py
```
Your browser will automatically open to `http://localhost:8501`.

---

## Troubleshooting Quick Fixes

1. Issue: "Connection refused" when starting the dashboard.
   Fix: You must ensure the FastAPI server (Terminal 1) is running before launching Streamlit.

2. Issue: Agents return an "error" status or fail to parse JSON.
   Fix: The Ollama service may have timed out. Verify it is running by typing `ollama list` in a new terminal.

3. Issue: OSRM is unavailable, defaulting to Haversine.
   Fix: To use real road data, you must install Docker and run `bash scripts/setup_osrm.sh` (or `setup_osrm.bat` on Windows). If you skip this, the system safely falls back to straight-line math.

## Next Steps
For a complete understanding of system configurations, dispatcher operations, and developer API references, please read the full `USER_MANUAL.md`.
