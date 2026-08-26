"""
Tests for benchmark_runner.py
"""
import os
import json
import pytest
from src.benchmark.benchmark_runner import BenchmarkRunner

@pytest.fixture
def mock_files(tmp_path):
    inc = [{"id": "B1", "type": "flood", "severity": "low", "required_resources": ["boat"]}]
    res = [{"id": "R1", "type": "boat"}]
    
    inc_file = tmp_path / "incidents.json"
    inc_file.write_text(json.dumps(inc))
    
    res_file = tmp_path / "resources.json"
    res_file.write_text(json.dumps(res))
    
    out_dir = tmp_path / "out"
    return str(inc_file), str(res_file), str(out_dir)

def test_benchmark_runner_init(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    assert len(runner.incidents) == 1
    assert len(runner.resources) == 1
    assert os.path.exists(mock_files[2])

def test_run_single_incident(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    res = runner.run_single_incident(runner.incidents[0], "resqmar")
    assert "incident_id" in res
    assert "coverage_score" in res
    assert res["config"] == "resqmar"

def test_run_benchmark(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    results = runner.run_benchmark("baseline_a")
    assert len(results) == 1
    assert results[0]["config"] == "baseline_a"

def test_calculate_statistics(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    mock_res = [
        {"coverage_score": 0.8, "latency_ms": 1000, "solver_calls": 2, "route_quality": 0.9, "success": True},
        {"coverage_score": 0.6, "latency_ms": 2000, "solver_calls": 4, "route_quality": 0.7, "success": False}
    ]
    stats = runner.calculate_statistics(mock_res)
    assert stats["avg_coverage_score"] == 0.7
    assert stats["avg_latency_ms"] == 1500
    assert stats["avg_solver_calls"] == 3.0
    assert stats["success_rate"] == 50.0

def test_deterministic_results(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    res1 = runner.run_single_incident(runner.incidents[0], "resqmar")
    res2 = runner.run_single_incident(runner.incidents[0], "resqmar")
    assert res1["coverage_score"] == res2["coverage_score"]
    
def test_save_results(mock_files):
    runner = BenchmarkRunner(mock_files[0], mock_files[1], mock_files[2])
    results = runner.run_all_benchmarks()
    report = runner.generate_report(results)
    runner.save_results(results, report)
    
    assert os.path.exists(os.path.join(mock_files[2], "benchmark_results.json"))
    assert os.path.exists(os.path.join(mock_files[2], "benchmark_report.txt"))
    assert os.path.exists(os.path.join(mock_files[2], "benchmark_comparison.json"))
