import os
from typing import Dict, Any

try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    DDGS = None
    HAS_DDGS = False

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

class LiveAwarenessAgent:
    """
    Live Situational Awareness Agent.
    Monitors live news feeds dynamically based on incident location and hazard.
    Summarizes the context using Groq's high-speed inference to inject real-time
    ground truth into the PlannerAgent's context window.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize the LiveAwarenessAgent."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = None
        self.enabled = False
        
        if self.api_key and HAS_GROQ:
            try:
                self.client = Groq(api_key=self.api_key)
                self.enabled = True
                print("[OK] LiveAwarenessAgent initialized with Groq API.")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Groq client: {e}")
        else:
            print("[WARN] Groq API key missing or package not installed.")
            print("[WARN] Live context will be passed as raw DuckDuckGo text.")

    def fetch_live_context(self, hazard: str, location: str) -> str:
        if not HAS_DDGS: return "Live awareness unavailable: duckduckgo-search not installed."
        """
        Fetch and summarize live news updates for a given hazard and location.
        
        Args:
            hazard (str): The type of emergency (e.g., 'flood', 'fire').
            location (str): The geographic location (e.g., 'Vizag', 'Andhra Pradesh').
            
        Returns:
            str: A synthesized, tactical situational awareness report.
        """
        query = f"{location} {hazard} today live news updates"
        print(f"[*] Fetching live awareness for: '{query}'")
        
        try:
            # Fetch live news using DuckDuckGo
            ddgs = DDGS()
            results = list(ddgs.news(query, max_results=4))
            
            # Fallback to standard web text if news is empty
            if not results:
                results = list(ddgs.text(query, max_results=3))
                
            if not results:
                return f"No live web updates found for {hazard} in {location}."
                
            raw_context = ""
            for idx, r in enumerate(results):
                title = r.get("title", "")
                body = r.get("body", "")
                date = r.get("date", "recent")
                raw_context += f"[{date}] {title}: {body}\n"
                
            # Summarize via Groq if available
            if self.enabled and self.client:
                prompt = (
                    "You are a tactical situational awareness AI for an emergency command center. "
                    f"Summarize the following live news feeds regarding a '{hazard}' in '{location}' "
                    "into a concise, 2-sentence tactical report for emergency responders. "
                    "Focus only on ground conditions, road closures, or immediate threats.\n\n"
                    f"Raw News:\n{raw_context}"
                )
                
                # Using Llama-3-8b on Groq for ultra-fast, free inference
                completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama3-8b-8192",
                    temperature=0.2,
                    max_tokens=150
                )
                
                summary = completion.choices[0].message.content.strip()
                return summary
            else:
                # Return raw context if Groq is disabled
                return f"Raw Live Context:\n{raw_context}"
                
        except Exception as e:
            print(f"[ERROR] Live Awareness retrieval failed: {e}")
            return f"Live awareness temporarily unavailable: {e}"
