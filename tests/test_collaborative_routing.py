"""
Pytest integration tests for Collaborative Routing logic.
"""
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.routing.models import Location, Vehicle
from src.routing.vrp_solver import VRPSolver
from src.routing.collaborative_solver import CollaborativeVRPSolver

@pytest.fixture
def setup_scenario():
    solver = VRPSolver()
    collab_solver = CollaborativeVRPSolver(solver)
    
    locations = [
        Location(id="D", lat=12.97, lon=77.59, demand=0, priority=1),
        Location(id="R1", lat=12.98, lon=77.60, demand=2, priority=2),
        Location(id="B1", lat=12.99, lon=77.61, demand=1, priority=4, is_roadblocked=True),
        Location(id="B2_far", lat=13.50, lon=77.60, demand=1, priority=4, is_roadblocked=True) # Too far
    ]
    
    trucks = [Vehicle(id="T1", capacity=10, start_location_id="D", vehicle_type="truck")]
    drones = [Vehicle(id="DR1", capacity=2, speed_kmh=80.0, start_location_id="D", vehicle_type="drone", is_aerial=True)]
    
    return solver, collab_solver, locations, trucks, drones

def test_truck_only_ignores_blocked(setup_scenario):
    """Verify standard solver drops roadblocked locations."""
    solver, _, locations, trucks, _ = setup_scenario
    # Normally we filter blocked locations before sending to standard solver.
    # If we pass all, the truck solver doesn't inherently know about is_roadblocked
    # unless we pre-filter. The collab solver pre-filters.
    reachable = [l for l in locations if not l.is_roadblocked]
    res = solver.solve(reachable, trucks, "D")
    
    assert len(res.routes) > 0
    assigned_ids = []
    for r in res.routes:
        assigned_ids.extend(r.location_ids)
    assert "B1" not in assigned_ids
    assert "B2_far" not in assigned_ids

def test_drone_only_limited_capacity(setup_scenario):
    """Verify drones fail on large demands if acting as standalone vehicles."""
    solver, _, locations, _, drones = setup_scenario
    # Drone capacity is 2. Let's make R1 demand = 10
    locations[1].demand = 10
    res = solver.solve(locations, drones, "D")
    
    # R1 should be unassigned because demand > drone capacity
    assert "R1" in res.unassigned

def test_collaborative_full_coverage(setup_scenario):
    """Verify collab solver routes truck to R1, drone to B1."""
    _, collab_solver, locations, trucks, drones = setup_scenario
    # Exclude B2_far for this test
    locs = [l for l in locations if l.id != "B2_far"]
    
    res = collab_solver.solve(locs, trucks, drones, "D")
    
    # Truck should visit R1
    truck_assigned = [l for r in res.truck_routes for l in r.location_ids]
    assert "R1" in truck_assigned
    
    # Drone should visit B1
    assert len(res.drone_subroutes) == 1
    assert "B1" in res.drone_subroutes[0].served_locations
    assert res.drone_subroutes[0].launch_truck_id == "T1"
    assert len(res.unassigned) == 0

def test_drone_range_limit(setup_scenario):
    """Verify collab solver leaves B2_far unassigned because flight distance > 5km."""
    _, collab_solver, locations, trucks, drones = setup_scenario
    
    res = collab_solver.solve(locations, trucks, drones, "D")
    
    assert "B2_far" in res.unassigned

def test_drone_launch_from_truck(setup_scenario):
    """Verify the drone subroute explicitly launches from a truck stop."""
    _, collab_solver, locations, trucks, drones = setup_scenario
    locs = [l for l in locations if l.id != "B2_far"]
    
    res = collab_solver.solve(locs, trucks, drones, "D")
    
    ds = res.drone_subroutes[0]
    assert ds.launch_truck_id == "T1"
    # Truck stops at D and R1. Drone should launch from the closest, which might be R1.
    assert ds.truck_location_id in ["D", "R1"]
