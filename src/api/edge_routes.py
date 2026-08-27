import json
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import time

router = APIRouter(prefix="/edge", tags=["edge"])

EDGE_AGENT_URL = "http://localhost:11435/api/generate"
EDGE_HEALTH_URL = "http://localhost:11435/api/tags"
DATASET_PATH = "data/edge_dataset.json"

class QueryRequest(BaseModel):
    question: str
    category: str = None

@router.get("/health")
async def check_health():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(EDGE_HEALTH_URL)
            if response.status_code == 200:
                return {"status": "connected", "model": "phi3:mini", "port": 11435}
    except Exception:
        pass
    
    raise HTTPException(status_code=503, detail="Edge model disconnected")

@router.post("/query")
async def query_edge(request: QueryRequest):
    start_time = time.time()
    system_prompt = "You are an emergency response assistant. Provide concise, actionable guidance. Keep under 100 words.\n\n"
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(EDGE_AGENT_URL, json={
                "model": "phi3:mini",
                "prompt": system_prompt + request.question,
                "stream": False,
                "format": "json"
            })
            
            if response.status_code == 200:
                data = response.json()
                latency = int((time.time() - start_time) * 1000)
                
                # Attempt to parse JSON response from LLM, fallback to raw text if model failed json format
                try:
                    parsed = json.loads(data["response"])
                    answer = parsed.get("answer", data["response"])
                except:
                    answer = data["response"]
                
                return {
                    "question": request.question,
                    "answer": answer,
                    "source": "edge",
                    "latency_ms": latency
                }
    except Exception as e:
        # EdgeAgent is down, fallback to reading the dataset file server-side
        pass
        
    # Fallback to local file if Edge model fails
    latency = int((time.time() - start_time) * 1000)
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            dataset = json.load(f)
            
        # Very simple keyword matching for server-side fallback
        words = request.question.lower().split()
        best_match = None
        max_score = 0
        
        for item in dataset:
            score = sum(1 for w in words if len(w) > 3 and w in item["question"].lower())
            if score > max_score:
                max_score = score
                best_match = item
                
        if best_match and max_score >= 1:
            return {
                "question": request.question,
                "answer": best_match["answer"],
                "source": "cache",
                "latency_ms": latency
            }
            
    except Exception:
        pass
        
    return {
        "question": request.question,
        "answer": "No cached guidance matches. Call 119 for immediate help.",
        "source": "fallback",
        "latency_ms": latency
    }

@router.get("/dataset")
async def get_dataset():
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        raise HTTPException(status_code=404, detail="Dataset not found")

@router.post("/benchmark")
async def run_benchmark():
    start_time = time.time()
    success = 0
    
    questions = ["What to do in a flood?", "How to treat a burn?", "Earthquake safety"]
    
    for q in questions:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(EDGE_AGENT_URL, json={
                    "model": "phi3:mini",
                    "prompt": q,
                    "stream": False
                })
                if resp.status_code == 200:
                    success += 1
        except:
            pass
            
    latency = int((time.time() - start_time) * 1000)
    return {
        "success_rate": f"{success}/{len(questions)}",
        "total_latency_ms": latency
    }
