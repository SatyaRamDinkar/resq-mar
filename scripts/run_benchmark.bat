@echo off
echo =========================================
echo ResQ-MAR Full Benchmark Suite
echo =========================================
echo Checking Python environment...
python --version
echo Running benchmark (this may take a few minutes)...

:: Ensure dataset exists
python generate_bench_data.py

:: Run benchmark
set PYTHONPATH=%cd%;%PYTHONPATH%
python src\benchmark\benchmark_runner.py

echo =========================================
echo Benchmark complete. Check data\benchmark_results\
echo =========================================
pause
