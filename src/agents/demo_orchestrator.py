"""
ResQ-MAR Phase 2 MVP Demo
Demonstrates the full Orchestrator pipeline across 3 scenarios.
"""
import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.orchestrator import ResQOrchestrator


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        # Fallback if running without real Ollama for tests
        return {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "NULL"}]}


def print_separator(char="=", length=65):
    print(char * length)


def run_demo():
    print_separator("=")
    print("ResQ-MAR Phase 2 MVP Demo")
    print("Initializing Orchestrator...")
    print_separator("=")
    
    start_time = time.time()
    config = load_config()
    orchestrator = ResQOrchestrator(llm_config=config)
    
    scenarios = [
        {
            "name": "SCENARIO 1: Critical Fire (requires approval)",
            "text": "MAJOR FIRE! Building 7, 3rd floor, 15 people trapped, smoke everywhere",
            "locations": [
                {"id": "fire_station", "lat": 12.9716, "lon": 77.5946, "demand": 0, "priority": 1},
                {"id": "bldg7", "lat": 12.9720, "lon": 77.5950, "demand": 15, "priority": 4},
                {"id": "city_hospital", "lat": 12.9700, "lon": 77.5930, "demand": 0, "priority": 1},
            ],
            "vehicles": [
                {"id": "fire_truck_1", "capacity": 12, "start_location_id": "fire_station"},
                {"id": "ambulance_1", "capacity": 4, "start_location_id": "fire_station"},
            ]
        },
        {
            "name": "SCENARIO 2: High-priority Flood (auto-approved for demo)",
            "text": "Flood waters rising in sector 4, 20 people on rooftops, send boats",
            "locations": [
                {"id": "rescue_depot", "lat": 13.0827, "lon": 80.2707, "demand": 0, "priority": 1},
                {"id": "sector4_north", "lat": 13.0830, "lon": 80.2710, "demand": 10, "priority": 4},
                {"id": "sector4_south", "lat": 13.0820, "lon": 80.2700, "demand": 10, "priority": 4},
            ],
            "vehicles": [
                {"id": "rescue_boat_1", "capacity": 10, "start_location_id": "rescue_depot"},
                {"id": "rescue_boat_2", "capacity": 10, "start_location_id": "rescue_depot"},
            ]
        },
        {
            "name": "SCENARIO 3: Spam / Non-emergency",
            "text": "Hey I found a lost dog near the park",
            "locations": [{"id": "depot", "lat": 12.9, "lon": 77.5, "demand": 0, "priority": 1}],
            "vehicles": [{"id": "van", "capacity": 2, "start_location_id": "depot"}]
        }
    ]

    successes = 0
    
    for s in scenarios:
        print(f"\n[INFO] Starting {s['name']}")
        print(f"INPUT: {s['text']}")
        print_separator("-")
        
        try:
            result = orchestrator.process_incident(s["text"], s["locations"], s["vehicles"])
            
            print(f"1. Incident ID: {result['incident_id']}")
            print(f"2. Agent Conversation:")
            for msg in result["agent_conversation"]:
                print(f"   [{msg['sender'].upper()}] {msg['message']}")
            
            print(f"3. Metadata: {result.get('metadata', {})}")
            print(f"4. Approval: {result.get('approval_status')}")
            
            plan = result.get("plan", {})
            tasks = plan.get("tasks", [])
            print(f"5. Plan: {len(tasks)} tasks | ETA {plan.get('estimated_total_time_min', 0)} mins")
            
            routes = result.get("routes", {})
            r_list = routes.get("routes", [])
            print(f"6. Routing: {len(r_list)} vehicles assigned | Status: {routes.get('solver_status')}")
            
            print(f"7. Final Comms Alert:")
            comms_alert = next((m['message'] for m in reversed(result['agent_conversation']) if m['sender'] == 'comms'), "None")
            print(f"   {comms_alert}")
            
            successes += 1
        except Exception as e:
            print(f"[WARN] Scenario failed: {e}")
            
        print_separator("=")

    end_time = time.time()
    avg_time = (end_time - start_time) / len(scenarios)
    
    print("\n[DONE] Demo Completed")
    print(f"Total incidents processed: {len(scenarios)}")
    print(f"Average pipeline time: {avg_time:.2f} seconds")
    print(f"Success rate: {(successes/len(scenarios))*100:.1f}%")

if __name__ == "__main__":
    run_demo()
