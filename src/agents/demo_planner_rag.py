"""
Dependencies: pyautogen, chromadb, sentence-transformers
"""
import os
import sys
import json

# Ensure src module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent
from src.rag.embeddings import SOPKnowledgeBase

def load_config():
    """Loads the LLM config file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def run_pipeline_demo():
    print("=========================================================")
    print("ResQ-MAR Complete Pipeline Demo: Intake -> Metadata -> RAG -> Planner")
    print("=========================================================")
    
    print("\n[1/4] Loading configurations and initializing agents...")
    config = load_config()
    intake = IntakeAgent(llm_config=config)
    meta = MetadataAgent(llm_config=config)
    planner = PlannerAgent(llm_config=config)
    
    print("[2/4] Initializing ChromaDB Knowledge Base...")
    kb = SOPKnowledgeBase()
    print("Ingesting SOPs from data/sops/ (This might take a moment if first time)...")
    kb.ingest_sops(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sops'))
    print(f"Knowledge Base Stats: {kb.get_collection_stats()}")
    
    print("\n[3/4] Ready to process incidents.\n")
    
    incidents = [
        "FIRE! Building 7, 3rd floor, people trapped, send help now!!!",
        "Water rising fast in sector 4, about 20 people stuck on rooftops, very urgent",
        "Earthquake! Building collapsed near the market, people buried under rubble"
    ]
    
    for i, raw_text in enumerate(incidents, 1):
        print(f"\n==================== INCIDENT {i} ====================")
        print(f"RAW INPUT: {raw_text}")
        
        # 1. Intake
        print("\n--> Running IntakeAgent...")
        intake_res = intake.process_report(raw_text)
        print(f"NORMALIZED: {intake_res.get('normalized_text')}")
        
        if intake_res.get("is_spam", False):
            print("Skipping - Flagged as SPAM")
            continue
            
        # 2. Metadata
        print("\n--> Running MetadataAgent...")
        meta_res = meta.extract_metadata(intake_res.get("normalized_text", raw_text))
        print(f"METADATA: Hazard: {meta_res.get('hazard_type')} | Urgency: {meta_res.get('urgency')}")
        
        # 3. RAG Query
        print("\n--> Querying Knowledge Base (RAG)...")
        hazard = meta_res.get('hazard_type', 'unknown')
        retrieved_sops = kb.query(hazard, intake_res.get("normalized_text", raw_text), top_k=2)
        print(f"RETRIEVED {len(retrieved_sops)} SOPs:")
        for sop in retrieved_sops:
            print(f"  - [{sop['id']}] {sop['title']}")
            
        # 4. Planner
        print("\n--> Running PlannerAgent...")
        plan_res = planner.generate_plan(meta_res, retrieved_sops)
        print("\n--- GENERATED TACTICAL PLAN ---")
        if plan_res.get("tasks"):
            for task in plan_res["tasks"]:
                print(f"  Step {task.get('step')}: {task.get('action')} (Resource: {task.get('resource')}, {task.get('estimated_time_min')}m)")
        print(f"\n  Resources Needed: {json.dumps(plan_res.get('resources_needed', {}))}")
        print(f"  SOPs Referenced: {plan_res.get('sops_referenced', [])}")
        print(f"  Estimated Total Time: {plan_res.get('estimated_total_time_min')} mins")

    print("\n=========================================================")
    print("[4/4] Pipeline Demo Complete.")
    print("=========================================================")

if __name__ == "__main__":
    run_pipeline_demo()
