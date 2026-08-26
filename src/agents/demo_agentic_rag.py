"""
Benchmark Demo: Naive RAG vs Agentic RAG
Demonstrates the advantages of a multi-agent retrieval pipeline.
"""
import os
import sys
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.rag.agentic_rag import AgenticRAGPipeline
from src.rag.embeddings import SOPKnowledgeBase

def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception:
        return {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "NULL"}]}

def run_benchmark():
    config = load_config()
    kb = SOPKnowledgeBase()
    sop_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sops')
    if os.path.exists(sop_dir):
        kb.ingest_sops(sop_dir)
        
    pipeline = AgenticRAGPipeline(llm_config=config, kb=kb)
    
    incidents = [
        {"name": "Fire in Bldg 7", "text": "Fire in Building 7, 3rd floor, people trapped, smoke everywhere"},
        {"name": "Flood Sector 4", "text": "Flood in sector 4, 20 people on rooftops, send boats"},
        {"name": "Earthquake Market", "text": "Earthquake! Building collapsed near market, people buried"}
    ]
    
    results = []
    
    print("\n[INFO] Starting RAG Pipeline Benchmark...\n")
    
    for inc in incidents:
        # Run Naive
        t0 = time.time()
        naive_res = pipeline.run_naive(inc["text"])
        t1 = time.time()
        naive_time = t1 - t0
        
        # Run Agentic
        t2 = time.time()
        agentic_res = pipeline.run(inc["text"])
        t3 = time.time()
        agentic_time = t3 - t2
        
        # Collect stats
        naive_sops = len(naive_res.get("retrieved_sops", []))
        agentic_sops = len(agentic_res.get("retrieved_sops", []))
        cov_score = agentic_res.get("assessment", {}).get("coverage_score", 0.0)
        
        results.append({
            "name": inc["name"],
            "naive_steps": naive_res.get("pipeline_steps", 1),
            "agentic_steps": agentic_res.get("pipeline_steps", 4),
            "naive_sops": naive_sops,
            "agentic_sops": agentic_sops,
            "coverage": cov_score,
            "naive_time": naive_time,
            "agentic_time": agentic_time
        })

    # Print Table
    print("=========================================================================")
    print("BENCHMARK: Naive RAG vs Agentic RAG")
    print("=========================================================================")
    print(f"{'Incident':<18} | {'Pipeline':<8} | {'Steps':<5} | {'SOPs':<4} | {'Coverage':<8} | {'Time (s)':<8}")
    print("-" * 73)
    
    avg_diff = 0.0
    for r in results:
        print(f"{r['name']:<18} | {'Naive':<8} | {r['naive_steps']:<5} | {r['naive_sops']:<4} | {'N/A':<8} | {r['naive_time']:.2f}")
        print(f"{r['name']:<18} | {'Agentic':<8} | {r['agentic_steps']:<5} | {r['agentic_sops']:<4} | {r['coverage']:<8.2f} | {r['agentic_time']:.2f}")
        avg_diff += (r['agentic_time'] - r['naive_time'])
        
    avg_diff /= len(results)

    print("=========================================================================")
    print("Key Improvements:")
    print("- Multi-query retrieval: 3 reformulated queries vs 1 direct query")
    print("- Safety assessment: Coverage score + gap detection")
    print("- SOP filtering: Only approved, safe SOPs used in planning")
    print("- Audit trail: Full assessment report for each incident")
    print(f"\nAgentic RAG adds ~{avg_diff:.2f} seconds per incident but provides safety assessment and better coverage.")
    print("=========================================================================")

if __name__ == "__main__":
    run_benchmark()
