import os
import requests
from duckduckgo_search import DDGS
from typing import List, Dict, Optional

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False

def fetch_web_results(query: str, max_results: int = 3) -> str:
    """Fetch live web results using duckduckgo-search."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No web results found."
        
        context_parts = []
        for i, res in enumerate(results, 1):
            title = res.get('title', 'Unknown Title')
            body = res.get('body', '')
            link = res.get('href', '')
            context_parts.append(f"Result {i}:\nTitle: {title}\nSummary: {body}\nURL: {link}")
            
        return "\n\n".join(context_parts)
    except Exception as e:
        return f"Web search failed: {str(e)}"

def summarize_results(query: str, raw_context: str) -> str:
    """Summarize search results using Gemini (if key available) or fallback to local Ollama."""
    prompt = f"""
    You are an emergency response summarizer. You have been given live web search results for the following query:
    "{query}"
    
    Search Results:
    {raw_context}
    
    Extract and summarize the most relevant information to answer the query or provide context for an emergency response. 
    Keep it concise and highly actionable. If the search results do not contain relevant information, state that clearly.
    """
    
    # Check for Gemini API key
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return f"[Summarized via Gemini API]\n{response.text}"
        except Exception as e:
            # Fall through to Ollama on failure
            print(f"Gemini API failed: {e}. Falling back to local Ollama.")
            pass
            
    # Fallback to local Ollama (Llama 3.1)
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.1",
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            return f"[Summarized via Local Llama 3.1]\n{response.json().get('response', '')}"
        else:
            return f"Summarization failed with status: {response.status_code}"
    except Exception as e:
        return f"Summarization completely failed: {str(e)}"

def web_search_fallback(query: str) -> str:
    """Main entrypoint for the free web search fallback."""
    print(f"[*] Triggering free web search fallback for: {query}")
    raw_results = fetch_web_results(query)
    if "No web results found" in raw_results or "Web search failed" in raw_results:
        return raw_results
        
    summary = summarize_results(query, raw_results)
    return summary
