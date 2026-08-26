"""
EdgeAgent module for ResQ-MAR.
Handles deployment of small language models (SLMs) like Phi-3-mini
for offline and edge emergency response.
"""
import time
import requests
from typing import List, Dict, Any

class EdgeAgent:
    """
    Agent running a quantized SLM (e.g., phi3:mini) on an edge device.
    Uses a separate port to isolate from main cloud models.
    """
    
    def __init__(self, model_name: str = "phi3:mini", port: int = 11435):
        """
        Initializes the EdgeAgent.
        """
        self.model_name = model_name
        self.port = port
        self.base_url = f"http://localhost:{self.port}/api"
        self._check_model()
        
    def _check_model(self):
        """Checks if Ollama is running on the port and if the model is available."""
        try:
            res = requests.get(f"{self.base_url}/tags", timeout=2)
            if res.status_code == 200:
                models = [m["name"] for m in res.json().get("models", [])]
                if self.model_name not in models and f"{self.model_name}:latest" not in models:
                    print(f"[!] Model {self.model_name} not found. Run: ollama pull {self.model_name}")
        except requests.exceptions.RequestException:
            print(f"[!] Ollama not reachable on port {self.port}.")
            print(f"    Start it with: OLLAMA_HOST=0.0.0.0:{self.port} ollama serve")

    def query(self, question: str, category: str = "general") -> Dict[str, Any]:
        """
        Queries the edge SLM with a disaster-specific prompt.
        """
        system_prompt = "You are an emergency response assistant. Provide concise, actionable guidance for disaster situations. Keep answers under 100 words. Be direct and practical."
        payload = {
            "model": self.model_name,
            "prompt": question,
            "system": system_prompt,
            "stream": False
        }
        
        start = time.time()
        try:
            res = requests.post(f"{self.base_url}/generate", json=payload, timeout=30)
            res.raise_for_status()
            answer = res.json().get("response", "")
        except requests.exceptions.RequestException as e:
            answer = f"Error: Unable to reach Edge Model ({str(e)})"
            
        latency = int((time.time() - start) * 1000)
        
        return {
            "question": question,
            "answer": answer.strip(),
            "latency_ms": latency,
            "model": self.model_name,
            "mode": "edge"
        }
        
    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Runs a batch of questions through the edge model.
        """
        results = []
        total = len(questions)
        for i, q in enumerate(questions, 1):
            res = self.query(q)
            results.append(res)
            print(f"Processed {i}/{total} questions")
        return results
        
    def benchmark(self, test_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Benchmarks the edge model against the provided test questions.
        Simulates a cloud baseline of 2000ms avg.
        """
        latencies = []
        total = len(test_questions)
        
        for q_dict in test_questions:
            res = self.query(q_dict["question"])
            latencies.append(res["latency_ms"])
            
        if not latencies:
            return {"error": "No questions provided"}
            
        avg_latency = sum(latencies) / total
        max_latency = max(latencies)
        min_latency = min(latencies)
        
        return {
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": max_latency,
            "min_latency_ms": min_latency,
            "total_questions": total,
            "cloud_baseline_ms": 2000
        }
        
    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns hardcoded structural info about the current model.
        """
        # Simulated model info mapping
        sizes = {
            "phi3:mini": {"size_gb": 1.6, "ram_usage_mb": 2000},
            "qwen2:1.5b": {"size_gb": 1.1, "ram_usage_mb": 1500}
        }
        info = sizes.get(self.model_name, {"size_gb": 0.0, "ram_usage_mb": 0})
        return {
            "model": self.model_name,
            "size_gb": info["size_gb"],
            "ram_usage_mb": info["ram_usage_mb"],
            "port": self.port
        }

if __name__ == "__main__":
    agent = EdgeAgent()
    print("Testing Edge Agent...")
    questions = [
        "What to do if trapped in a flooded building?",
        "How to use a fire extinguisher?",
        "What is drop, cover, and hold on?"
    ]
    for q in questions:
        print(f"\nQ: {q}")
        ans = agent.query(q)
        print(f"A: {ans['answer']}")
        print(f"[Latency: {ans['latency_ms']}ms]")
