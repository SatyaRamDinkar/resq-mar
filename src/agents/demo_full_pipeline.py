"""
Full Pipeline Demo: Intake -> Metadata -> RAG -> Planner -> Router
Dependencies: pyautogen, chromadb, sentence-transformers, ortools
"""
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.router_agent import RouterAgent
from src.rag.embeddings import SOPKnowledgeBase


def load_config() -> dict:
    """Loads the LLM config file from src/config/llm_config.json."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def print_route_summary(routing_result: dict):
    """Pretty-print the routing result."""
    print(f"\n  Solver Status : {routing_result.get('solver_status')}")
    print(f"  Total Distance: {routing_result.get('total_distance_km')} km")
    for route in routing_result.get("routes", []):
        path = " -> ".join(route["location_ids"])
        print(f"  [{route['vehicle_id']}] {path}")
        print(f"    Distance: {route['total_distance_km']} km | "
              f"ETA: {route['estimated_time_min']} min | "
              f"Demand served: {route['total_demand']}")
    if routing_result.get("unassigned"):
        print(f"  ⚠ Unassigned: {routing_result['unassigned']}")


def run_full_pipeline():
    print("=" * 65)
    print("ResQ-MAR FULL PIPELINE DEMO")
    print("Intake -> Metadata -> RAG -> Planner -> Router")
    print("=" * 65)

    # ── Initialization ──────────────────────────────────────────────
    print("\n[INIT] Loading config and initializing all agents...")
    config = load_config()
    intake  = IntakeAgent(llm_config=config)
    meta    = MetadataAgent(llm_config=config)
    planner = PlannerAgent(llm_config=config)
    router  = RouterAgent(llm_config=config)

    print("[INIT] Initializing ChromaDB Knowledge Base...")
    sop_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sops')
    kb = SOPKnowledgeBase()
    kb.ingest_sops(sop_dir=sop_dir)
    print(f"[INIT] KB Stats: {kb.get_collection_stats()}")

    # ── Define Scenarios ────────────────────────────────────────────
    scenarios = [
        {
            "name": "SCENARIO 1 — Building Fire with Trapped Persons",
            "raw_text": "FIRE! Building 7, 3rd floor, people trapped, send help now!!!",
            "locations": [
                {"id": "fire_station",  "lat": 12.9716, "lon": 77.5946, "demand": 0,  "priority": 1},
                {"id": "bldg7",         "lat": 12.9720, "lon": 77.5950, "demand": 8,  "priority": 4},
                {"id": "city_hospital", "lat": 12.9700, "lon": 77.5930, "demand": 0,  "priority": 1},
            ],
            "vehicles": [
                {"id": "fire_truck_1", "capacity": 12, "speed_kmh": 40.0, "start_location_id": "fire_station"},
                {"id": "ambulance_1",  "capacity": 4,  "speed_kmh": 40.0, "start_location_id": "fire_station"},
            ],
        },
        {
            "name": "SCENARIO 2 — Flood with Rooftop Victims",
            "raw_text": "Water rising fast in sector 4, about 20 people stuck on rooftops, very urgent",
            "locations": [
                {"id": "rescue_depot",   "lat": 13.0827, "lon": 80.2707, "demand": 0,  "priority": 1},
                {"id": "sector4_north",  "lat": 13.0830, "lon": 80.2710, "demand": 8,  "priority": 4},
                {"id": "sector4_south",  "lat": 13.0820, "lon": 80.2700, "demand": 12, "priority": 4},
            ],
            "vehicles": [
                {"id": "rescue_boat_1", "capacity": 10, "speed_kmh": 20.0, "start_location_id": "rescue_depot"},
                {"id": "rescue_boat_2", "capacity": 10, "speed_kmh": 20.0, "start_location_id": "rescue_depot"},
            ],
        },
    ]

    pipeline_stats = []

    for scenario in scenarios:
        print(f"\n{'=' * 65}")
        print(f"  {scenario['name']}")
        print(f"{'=' * 65}")
        raw_text  = scenario["raw_text"]
        locations = scenario["locations"]
        vehicles  = scenario["vehicles"]

        print(f"\nRAW INPUT: {raw_text}")

        # ── Stage 1: Intake ─────────────────────────────────────────
        print("\n[1/5] IntakeAgent normalizing report...")
        intake_res = intake.process_report(raw_text)
        normalized = intake_res.get("normalized_text", raw_text)
        print(f"  NORMALIZED: {normalized}")

        if intake_res.get("is_spam"):
            print("  ⚠ Flagged as SPAM — skipping.")
            continue

        # ── Stage 2: Metadata ────────────────────────────────────────
        print("\n[2/5] MetadataAgent extracting structured metadata...")
        meta_res = meta.extract_metadata(normalized)
        hazard   = meta_res.get("hazard_type", "unknown")
        urgency  = meta_res.get("urgency", "medium")
        location_desc = meta_res.get("location_description", "unknown")
        print(f"  Hazard: {hazard} | Urgency: {urgency} | Location: {location_desc}")

        # ── Stage 3: RAG ─────────────────────────────────────────────
        print("\n[3/5] Querying Knowledge Base (RAG)...")
        sops = kb.query(hazard, normalized, top_k=2)
        for sop in sops:
            print(f"  Retrieved: [{sop['id']}] {sop['title']}")

        # ── Stage 4: Planner ─────────────────────────────────────────
        print("\n[4/5] PlannerAgent generating tactical plan...")
        plan = planner.generate_plan(meta_res, sops)
        tasks = plan.get("tasks", [])
        print(f"  Generated {len(tasks)} tasks | "
              f"ETA: {plan.get('estimated_total_time_min')} min | "
              f"SOPs: {plan.get('sops_referenced', [])}")
        for task in tasks[:3]:  # print first 3 tasks only
            print(f"    Step {task.get('step')}: {task.get('action')}")
        if len(tasks) > 3:
            print(f"    ... ({len(tasks) - 3} more tasks)")

        # ── Stage 5: Router ──────────────────────────────────────────
        print("\n[5/5] RouterAgent solving VRP...")
        routing_result = router.plan_routes(plan, locations, vehicles)
        print_route_summary(routing_result)

        pipeline_stats.append({
            "scenario": scenario["name"],
            "hazard": hazard,
            "urgency": urgency,
            "tasks_generated": len(tasks),
            "vehicles_routed": len(routing_result.get("routes", [])),
            "solver_status": routing_result.get("solver_status"),
            "total_distance_km": routing_result.get("total_distance_km"),
        })

    # ── Pipeline Summary ─────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print("PIPELINE SUMMARY")
    print(f"{'=' * 65}")
    print(f"{'Scenario':<35} {'Status':<10} {'Vehicles':<10} {'Dist (km)'}")
    print("-" * 65)
    for s in pipeline_stats:
        name = s["scenario"][:34]
        print(f"{name:<35} {s['solver_status']:<10} {s['vehicles_routed']:<10} {s['total_distance_km']}")
    print("=" * 65)


if __name__ == "__main__":
    run_full_pipeline()
