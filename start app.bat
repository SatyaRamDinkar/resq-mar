@echo off
title ResQ-MAR Startup
color 0B

echo ===================================================
echo      Starting ResQ-MAR AI Command Center...
echo ===================================================
echo.

echo [1/4] Starting Ollama Local LLM Server...
start "Ollama Server" /MIN ollama serve

echo [2/4] Checking Docker Status for OSRM Router...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo   -[WARNING] Docker Desktop is not running!
    echo   - Please open Docker Desktop manually for OSRM Routing to work.
) else (
    echo   -[OK] Docker is running. Starting OSRM container...
    docker start osrm-router >nul 2>&1
    if %errorlevel% neq 0 (
        docker run -d -p 5000:5000 --name osrm-router -v "%~dp0data\osrm:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/india-southern-zone-latest.osrm >nul 2>&1
    )
)

echo.
echo [3/4] Initializing ChromaDB...
echo   -[OK] Embedded Vector Database will start automatically with Python.

echo.
echo [4/4] Launching Streamlit Dashboard...
echo   -[INFO] The browser will open automatically. Press Ctrl+C in this window to stop.
echo ===================================================
echo.

python -m streamlit run frontend/streamlit_app_enhanced.py

pause
