"""
Pytest integration tests for AET Routing mechanisms.
"""
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.routing.vrp_solver import VRPSolver
from src.routing.aet_router import AETRouter
from src.routing.baseline_router import ContinuousRouter, StaticRouter

@pytest.fixture
def setup_components():
    solver = VRPSolver()
    depot = {"id": "depot", "lat": 12.97, "lon": 77.59, "demand": 0, "priority": 1}
    vehicles = [{"id": "v1", "capacity": 100, "start_location_id": "depot"}]
    return solver, depot, vehicles

def test_aet_trigger_threshold(setup_components):
    """A small incident should NOT trigger re-optimization in AET."""
    solver, depot, vehicles = setup_components
    router = AETRouter(solver, trigger_threshold=0.20, slack_threshold=0.10)
    router.setup(depot, vehicles)
    
    # 1st incident always triggers
    res1 = router.add_incident({"id": "inc1", "lat": 12.98, "lon": 77.60, "demand": 50, "priority": 4})
    assert res1["triggered"] is True
    
    # 2nd incident is tiny (1 demand out of 100 total) -> NO trigger (1/100 = 0.01 < 0.20)
    res2 = router.add_incident({"id": "inc2", "lat": 12.99, "lon": 77.61, "demand": 1, "priority": 1})
    assert res2["triggered"] is False
    assert router.solver_call_count == 1

def test_aet_trigger_fires(setup_components):
    """A large incident SHOULD trigger re-optimization in AET."""
    solver, depot, vehicles = setup_components
    router = AETRouter(solver, trigger_threshold=0.20, slack_threshold=0.10)
    router.setup(depot, vehicles)
    
    router.add_incident({"id": "inc1", "lat": 12.98, "lon": 77.60, "demand": 70, "priority": 4})
    
    # 2nd incident is large (30 demand out of 100 total) -> SHOULD trigger (30/100 = 0.30 > 0.20)
    res2 = router.add_incident({"id": "inc2", "lat": 12.99, "lon": 77.61, "demand": 30, "priority": 4})
    assert res2["triggered"] is True
    assert router.solver_call_count == 2

def test_slack_depletion(setup_components):
    """Almost full vehicle should trigger re-optimization on ANY incident."""
    solver, depot, vehicles = setup_components
    router = AETRouter(solver, trigger_threshold=0.99, slack_threshold=0.10) # impossible trigger_threshold
    router.setup(depot, vehicles)
    
    # Fill to 95%
    router.add_incident({"id": "inc1", "lat": 12.98, "lon": 77.60, "demand": 95, "priority": 4})
    
    # Tiny incident, but capacity is heavily depleted (<10% slack)
    res2 = router.add_incident({"id": "inc2", "lat": 12.99, "lon": 77.61, "demand": 1, "priority": 1})
    
    assert res2["triggered"] is True
    assert "slack" in res2["reason"].lower()
    assert router.solver_call_count == 2

def test_continuous_always_reoptimizes(setup_components):
    """ContinuousRouter should solve on every incident."""
    solver, depot, vehicles = setup_components
    router = ContinuousRouter(solver)
    router.setup(depot, vehicles)
    
    for i in range(5):
        router.add_incident({"id": f"inc{i}", "lat": 12.98, "lon": 77.60, "demand": 1, "priority": 1})
        
    assert router.solver_call_count == 5

def test_static_never_reoptimizes(setup_components):
    """StaticRouter should solve exactly once."""
    solver, depot, vehicles = setup_components
    router = StaticRouter(solver)
    router.setup(depot, vehicles)
    
    for i in range(5):
        router.add_incident({"id": f"inc{i}", "lat": 12.98, "lon": 77.60, "demand": 1, "priority": 1})
        
    assert router.solver_call_count == 1
    assert len(router.unassigned) == 4  # The remaining 4 were queued and ignored
