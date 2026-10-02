import os
import json
import pytest
from evaluation.run_benchmarks import run_benchmarks

def test_benchmark_runner_mocked(tmp_path):
    # Ensure the script handles mocked execution and writes output
    summary = run_benchmarks(mocked=True)
    
    assert summary["total_cases"] == 20
    assert "precision" in summary
    assert "avg_latency_s" in summary
    
    # Check outputs
    assert os.path.exists("evaluation/results/benchmark_report.json")
    assert os.path.exists("evaluation/results/latency_histogram.html")
    assert os.path.exists("evaluation/results/routing_comparison.html")

    # Verify JSON structure
    with open("evaluation/results/benchmark_report.json", "r") as f:
        data = json.load(f)
        assert "summary" in data
        assert "results" in data
        assert len(data["results"]) == 20
