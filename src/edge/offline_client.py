"""
Offline Client module for ResQ-MAR.
Simulates a PWA backend that seamlessly routes between Cloud and Edge models.
"""
import requests
from typing import Dict, Any

class OfflineClient:
    """
    Client that detects connectivity and routes queries to either
    the cloud model (llama3.1) or edge model (phi3:mini).
    """
    
    def __init__(self, edge_url: str = "http://localhost:11435", cloud_url: str = "http://localhost:11434"):
        """
        Initializes the OfflineClient with both URLs.
        """
        self.edge_url = edge_url
        self.cloud_url = cloud_url
        self.mode = "online"
        
    def check_connectivity(self) -> bool:
        """
        Pings the cloud URL to determine if we are online.
        """
        try:
            res = requests.get(f"{self.cloud_url}/api/tags", timeout=2)
            if res.status_code == 200:
                self.mode = "online"
                return True
        except requests.exceptions.RequestException:
            pass
            
        self.mode = "offline"
        return False
        
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Routes the question to the appropriate model based on connectivity.
        """
        is_online = self.check_connectivity()
        
        url = f"{self.cloud_url}/api/generate" if is_online else f"{self.edge_url}/api/generate"
        model = "llama3.1" if is_online else "phi3:mini"
        source = "cloud" if is_online else "edge"
        mode_str = "online" if is_online else "offline"
        
        payload = {
            "model": model,
            "prompt": question,
            "stream": False,
            "system": "You are an emergency response assistant."
        }
        
        try:
            res = requests.post(url, json=payload, timeout=10)
            res.raise_for_status()
            answer = res.json().get("response", "")
        except requests.exceptions.RequestException as e:
            answer = f"Error: {str(e)}"
            
        return {
            "mode": mode_str,
            "answer": answer.strip(),
            "source": source
        }
        
    def sync_queue(self):
        """
        Syncs any locally cached requests when transitioning offline -> online.
        """
        # MVP: just print, no actual queue implementation needed yet
        print("Syncing offline queue...")
