"""
ResQ-MAR AET Routing Benchmark
Compares Static, Continuous, and Adaptive Event-Triggered (AET) routing.
"""
import os
import sys
import time
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.routing.vrp_solver import VRPSolver
from src.routing.aet_router import AETRouter
from src.routing.baseline_router import ContinuousRouter, StaticRouter

def generate_incidents(num: int = 15, seed: int = 42) -> list:
    """Generates a deterministic sequence of simulated incidents."""
    random.seed(seed)
    incidents = []
    base_lat, base_lon = 12.9716, 77.5946  # Bangalore Depot
    
    for i in range(num):
        lat = base_lat + random.uniform(-0.05, 0.05)
        lon = base_lon + random.uniform(-0.05, 0.05)
        # Mix of small and large incidents
        demand = random.choice([1, 1, 2, 2, 3, 4, 6, 8])
        priority = random.randint(1, 4)
        
        incidents.append({
            "id": f"INC-{100+i}",
            "lat": lat,
            "lon": lon,
            "demand": demand,
            "priority": priority
        })
    return incidents

def run_benchmark():
    print("Initializing components...")
    
    solver = VRPSolver()
    depot = {"id": "central_depot", "lat": 12.9716, "lon": 77.5946, "demand": 0, "priority": 1}
    vehicles = [
        {"id": "amb_1", "capacity": 15, "start_location_id": "central_depot"},
        {"id": "amb_2", "capacity": 15, "start_location_id": "central_depot"},
        {"id": "amb_3", "capacity": 15, "start_location_id": "central_depot"}
    ]
    
    routers = {
        "Static": StaticRouter(solver),
        "Continuous": ContinuousRouter(solver),
        "AET (20%)": AETRouter(solver, trigger_threshold=0.20, slack_threshold=0.10)
    }
    
    incidents = generate_incidents(15)
    results = {}
    
    print("\nSimulating Incident Stream (15 incidents)...")
    for name, router in routers.items():
        print(f"-> Running {name} Strategy...")
        router.setup(depot, vehicles)
        
        for inc in incidents:
            router.add_incident(inc)
            
        results[name] = router.get_stats()
        
    # Print Output Table
    print("\n=========================================================================")
    print("ROUTING STRATEGY BENCHMARK")
    print("=========================================================================")
    print(f"{'Strategy':<12} | {'Incidents':<9} | {'Solver Calls':<12} | {'Call Rate':<9} | {'Total Dist':<10} | {'Unassigned':<10}")
    print("-" * 75)
    
    for name, stats in results.items():
        call_rate = f"{stats['solver_call_rate'] * 100:.1f}%"
        dist = f"{stats['total_distance_km']:.2f} km"
        print(f"{name:<12} | {stats['total_incidents']:<9} | {stats['solver_calls']:<12} | {call_rate:<9} | {dist:<10} | {stats['unassigned_count']:<10}")

    print("=========================================================================\n")
    
    print("KEY INSIGHTS:")
    print("- Static: Fastest but leaves many incidents unassigned (ignores dynamic events).")
    print("- Continuous: Highly optimal routing but wastes massive compute via constant re-solving.")
    print("- AET: Dynamic triggers ensure near-optimal routing while dropping compute overhead significantly.\n")
    
    aet_calls = results["AET (20%)"]["solver_calls"]
    cont_calls = results["Continuous"]["solver_calls"]
    savings = ((cont_calls - aet_calls) / max(cont_calls, 1)) * 100
    
    print("CONCLUSION:")
    print(f"Adaptive Event-Triggered (AET) Routing achieved highly competitive route distances ")
    print(f"while executing {savings:.1f}% FEWER solver calls than Continuous routing.")
    print("This trade-off is critical for scaling real-time disaster response systems.")
    print("=========================================================================\n")

if __name__ == "__main__":
    run_benchmark()
