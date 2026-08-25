"""
Dependencies: pyautogen
"""
import os
import json
import sys

# Ensure src module can be imported from the root directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent

def load_config():
    """Loads the LLM config file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def run_demo():
    """Runs a demonstration of the Intake and Metadata agents."""
    print("=============================================")
    print("ResQ-MAR Pipeline Demo: Intake & Metadata")
    print("=============================================")
    
    # 1. Initialize config and agents
    config = load_config()
    intake = IntakeAgent(llm_config=config)
    meta = MetadataAgent(llm_config=config)
    
    # 2. Define test incidents
    incidents = [
        "FIRE! Building 7, 3rd floor, people trapped, send help now!!!",
        "Water rising fast in sector 4, about 20 people stuck on rooftops, very urgent",
        "Hey I found a lost dog near the park, can someone help?"
    ]
    
    results = []
    
    # 3. Process incidents through pipeline
    for i, raw_text in enumerate(incidents, 1):
        print(f"\n--- Incident {i} ---")
        print(f"RAW: {raw_text}")
        
        # Intake Phase
        intake_res = intake.process_report(raw_text)
        print(f"NORMALIZED: {intake_res.get('normalized_text')}")
        print(f"IS SPAM: {intake_res.get('is_spam')}")
        
        # Metadata Phase (Skip if spam)
        if not intake_res.get("is_spam", False):
            meta_res = meta.extract_metadata(intake_res.get("normalized_text", raw_text))
            print(f"METADATA: Hazard: {meta_res.get('hazard_type')} | Urgency: {meta_res.get('urgency')} | Loc: {meta_res.get('location_description')}")
            results.append({
                "raw": raw_text,
                "intake": intake_res,
                "meta": meta_res
            })
        else:
            print("METADATA: Skipped (Flagged as spam)")
            results.append({
                "raw": raw_text,
                "intake": intake_res,
                "meta": None
            })

    # 4. Print Summary Table
    print("\n=========================================================================")
    print("SUMMARY TABLE")
    print(f"{'Hazard':<12} | {'Urgency':<10} | {'Spam?':<6} | {'Location'}")
    print("-" * 73)
    for res in results:
        spam = str(res['intake'].get('is_spam', False))
        if res['meta']:
            hazard = res['meta'].get('hazard_type', 'N/A')
            urgency = res['meta'].get('urgency', 'N/A')
            loc = res['meta'].get('location_description', 'N/A')
        else:
            hazard = "N/A"
            urgency = "N/A"
            loc = "N/A"
        print(f"{hazard:<12} | {urgency:<10} | {spam:<6} | {loc}")
    print("=========================================================================")

if __name__ == "__main__":
    run_demo()
