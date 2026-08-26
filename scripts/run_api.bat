@echo off
echo =========================================
echo ResQ-MAR FastAPI Backend
echo =========================================
echo Checking Python environment...
python --version
echo Starting API server...
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
echo =========================================
echo API Docs: http://localhost:8000/docs
echo Health:  http://localhost:8000/health
echo =========================================
pause
