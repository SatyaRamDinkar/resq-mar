# Live Situational Awareness (DuckDuckGo + Groq)

## 1. Context and Novelty
Existing disaster response systems (e.g., ResQConnect, DisastRAG) assume the world is static. They retrieve static Standard Operating Procedures (SOPs) based on incoming emergency reports. However, disaster environments are highly dynamic (e.g., roads close rapidly, flood waters rise). 

**ResQ-MAR is the first system to integrate Live Situational Awareness into the multi-agent pipeline.**

## 2. How It Works
Before the `PlannerAgent` generates an execution plan, the orchestrator triggers the `LiveAwarenessAgent` (Step 3.5 in the pipeline).

1. **Information Retrieval:** Uses the `duckduckgo_search` pip package to silently fetch live news feeds and web alerts tailored exactly to the incident's `location` and `hazard_type` (e.g., "Vizag flood today live news").
2. **High-Speed Synthesis:** The raw, noisy web results are passed to the **Groq API** (using the `llama3-8b-8192` model) to synthesize a concise, 2-sentence tactical summary of ground conditions.
3. **Context Injection:** This hyper-current tactical summary is injected directly into the `PlannerAgent`'s system prompt alongside the retrieved SOPs.

## 3. The Free-Tier Architecture
We achieve this dynamic awareness with **100% Zero Cost**:
- **Scraping:** DuckDuckGo Search (`duckduckgo-search`) is completely free and requires no API keys, bypassing expensive providers like Tavily or SerpApi.
- **Inference:** Groq provides lightning-fast inference on LPU architectures with generous free tiers, ideal for low-latency emergency routing loops. 

## 4. Example Output
**Incident:** Flood reported in Visakhapatnam.
**Live Context Injected:** *"Heavy rains have inundated low-lying areas of Vizag, with the local meteorological department issuing a red alert. Major traffic diversions are in place along Beach Road due to severe waterlogging, and citizens are advised to stay indoors."*

The `PlannerAgent` reads this and dynamically updates routing tasks to avoid Beach Road, a decision no static SOP could ever make.
