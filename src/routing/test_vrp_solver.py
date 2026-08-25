"""
Pytest tests for the VRP Solver.
Dependencies: pytest, ortools
"""
import os
import sys
import pytest

# Ensure src module can be imported from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.routing.models import Location, Vehicle
from src.routing.vrp_solver import VRPSolver


@pytest.fixture
def solver():
    """Return a fresh VRPSolver instance for each test."""
    return VRPSolver()


# --- Fixed test data (hardcoded for reproducibility) ---

DEPOT = Location(id="depot", lat=12.9716, lon=77.5946, demand=0, priority=1)

LOC_A = Location(id="site_A", lat=12.9730, lon=77.5960, demand=3, priority=3)
LOC_B = Location(id="site_B", lat=12.9700, lon=77.5920, demand=2, priority=2)
LOC_C = Location(id="site_C", lat=12.9750, lon=77.5940, demand=4, priority=4)
LOC_D = Location(id="site_D", lat=12.9680, lon=77.5970, demand=3, priority=3)
LOC_E = Location(id="site_E", lat=12.9760, lon=77.5910, demand=3, priority=3)

VEH_SMALL = Vehicle(id="amb_1", capacity=10, start_location_id="depot")
VEH_LARGE = Vehicle(id="truck_1", capacity=20, start_location_id="depot")


def test_simple_vrp(solver):
    """
    1 depot, 3 demand locations, 1 vehicle with enough capacity.
    All 3 locations should be assigned.
    """
    locations = [DEPOT, LOC_A, LOC_B, LOC_C]
    vehicles = [VEH_LARGE]

    result = solver.solve(locations, vehicles, depot_id="depot")

    assert result.solver_status in ("OPTIMAL", "FEASIBLE"), f"Unexpected status: {result.solver_status}"
    assert len(result.unassigned) == 0, f"Expected 0 unassigned, got: {result.unassigned}"
    assert len(result.routes) == 1
    # All 3 demand locations should appear in the route
    visited = result.routes[0].location_ids
    for loc in ["site_A", "site_B", "site_C"]:
        assert loc in visited, f"{loc} not found in route: {visited}"


def test_capacity_constraint(solver):
    """
    3 locations with total demand=9, but vehicle capacity=5.
    Expect some locations to be unassigned.
    """
    locations = [DEPOT, LOC_A, LOC_B, LOC_C]  # demands: 3, 2, 4 = total 9
    small_vehicle = Vehicle(id="amb_tiny", capacity=5, start_location_id="depot")
    vehicles = [small_vehicle]

    result = solver.solve(locations, vehicles, depot_id="depot")

    assert result.solver_status in ("OPTIMAL", "FEASIBLE", "FAILED")
    # Total demand (9) > capacity (5), so at least one location must be unassigned
    assert len(result.unassigned) >= 1, "Expected at least 1 unassigned location due to capacity"


def test_multiple_vehicles(solver):
    """
    1 depot, 5 demand locations, 2 vehicles.
    Both vehicles should ideally receive routes, and all locations should be covered.
    """
    locations = [DEPOT, LOC_A, LOC_B, LOC_C, LOC_D, LOC_E]
    vehicles = [VEH_SMALL, Vehicle(id="amb_2", capacity=10, start_location_id="depot")]

    result = solver.solve(locations, vehicles, depot_id="depot")

    assert result.solver_status in ("OPTIMAL", "FEASIBLE"), f"Unexpected status: {result.solver_status}"
    assert len(result.routes) >= 1, "Expected at least 1 active vehicle route"
    assert len(result.unassigned) == 0, f"Expected 0 unassigned, got: {result.unassigned}"


def test_empty_locations(solver):
    """
    No demand locations (only the depot).
    Routes should be empty — no vehicle needs to move.
    """
    locations = [DEPOT]
    vehicles = [VEH_SMALL]

    result = solver.solve(locations, vehicles, depot_id="depot")

    # With no demand, no vehicle should have a non-trivial route
    assert len(result.routes) == 0, f"Expected 0 routes for empty demand, got {len(result.routes)}"
    assert len(result.unassigned) == 0
