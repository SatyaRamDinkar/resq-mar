"""
ResQ-MAR JSON Mode Verification Demo
Demonstrates the Intake, Metadata, and Planner agents using Ollama's native JSON mode.
"""
import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent
from src.rag.embeddings import SOPKnowledgeBase

def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "NULL"}]}

def print_separator(char="-", length=60):
    print(char * length)

def run_json_demo():
    print_separator("=")
    print("ResQ-MAR JSON Mode Fix Verification")
    print_separator("=")
    
    config = load_config()
    
    print("[INFO] Initializing Agents with JSON Mode...")
    intake = IntakeAgent(llm_config=config)
    meta = MetadataAgent(llm_config=config)
    planner = PlannerAgent(llm_config=config)
    
    print("[INFO] Loading ChromaDB Knowledge Base...")
    kb = SOPKnowledgeBase()
    sop_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sops')
    if os.path.exists(sop_dir):
        kb.ingest_sops(sop_dir)
        
    incidents = [
        "MAJOR FIRE! Building 7, 3rd floor, 15 people trapped, smoke everywhere",
        "Flood waters rising in sector 4, 20 people on rooftops, send boats",
        "Earthquake! Building collapsed near the market, people buried under rubble"
    ]
    
    perfect_parses = 0
    total_parses = 0
    
    for idx, text in enumerate(incidents, 1):
        print(f"\n[SCENARIO {idx}] {text}")
        print_separator("-")
        
        # 1. Intake
        intake_res = intake.process_report(text)
        total_parses += 1
        if "error" not in intake_res:
            print("[IntakeAgent] Parsed Successfully: YES")
            perfect_parses += 1
        else:
            print("[IntakeAgent] Parsed Successfully: NO")
            
        normalized = intake_res.get("normalized_text", text)
        
        # 2. Metadata
        meta_res = meta.extract_metadata(normalized)
        total_parses += 1
        if "error" not in meta_res:
            print("[MetadataAgent] Parsed Successfully: YES")
            perfect_parses += 1
        else:
            print("[MetadataAgent] Parsed Successfully: NO")
            
        # 3. Planner
        hazard = meta_res.get("hazard_type", "unknown")
        sops = kb.query(hazard, normalized, top_k=2) if hazard != "unknown" else []
        plan_res = planner.generate_plan(meta_res, sops)
        total_parses += 1
        if "error" not in plan_res:
            print("[PlannerAgent] Parsed Successfully: YES")
            perfect_parses += 1
        else:
            print("[PlannerAgent] Parsed Successfully: NO")
            
        print_separator("-")

    print("\n[DONE] Demo Completed")
    print(f"Success rate: {perfect_parses}/{total_parses} agent calls had perfect JSON parsing.")
    print("Before fix: frequent fallback plans. After fix: strict JSON mode.")
    print_separator("=")

if __name__ == "__main__":
    run_json_demo()
