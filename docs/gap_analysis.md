Generated for ResQ-MAR Capstone | Combined Gap Analysis | Date: 2026-08-26

# Combined Gap Analysis: Positioning ResQ-MAR

## 1. THE LANDSCAPE

The following table compares the foundational papers in our literature review against the proposed architecture of our capstone project, ResQ-MAR.

| Feature / Aspect | ResQConnect (2026) | Peng et al. (2025) | Li Vision (2025) | DisastRAG (2026) | ResQ-MAR (Our Project) |
|------------------|-------------------|-------------------|------------------|------------------|----------------------|
| **Disaster Types** | Floods, Landslides | Earthquake | General / Concept | General / Mixed | **Multi-Hazard** (Floods, Landslides, Earthquakes, Fires) |
| **Routing** | AET Multi-Commodity | MADRL Truck-Drone | N/A (Concept) | N/A (RAG only) | **OR-Tools AET + Truck-Drone Collaborative** |
| **Agent Count** | 7 (Cloud) + 1 (Edge) | Multi-Agent (RL) | Abstract Hierarchical | Router + Synthesizer | **3+ Core AutoGen Agents (Orchestrator, Planner, Critic)** |
| **Data Sources** | Unstructured (SOPs) | Dynamic Node Demands| Active Digital Twins | Unstructured, SQL, Web | **Multi-Source (ChromaDB + SQLite Inventory + Web)** |
| **Human-in-Loop** | Implied / End User | None (Black Box RL) | High (Core Concept) | None | **High (Interactive Streamlit Dashboard Override)** |
| **Offline/Edge** | Yes (SLM on Mobile) | No | Yes (Concept) | No | **100% Local Stack (Ollama, ChromaDB) + Edge Agents** |
| **Open Source** | No (Relies on GPT-4o) | Yes (Algorithm) | N/A | Tested on Open LLMs| **100% Open-Source (Llama 3.1, AutoGen, OR-Tools)** |
| **Multi-Modal Input**| Text | Numeric State Space | Implied | Text | **Text + Geolocation (Folium Maps)** |
| **Truck-Drone** | No (Trucks only) | Yes | No | No | **Yes (Mobile Depot Routing via OR-Tools)** |

---

## 2. THE GAP

**What ResQConnect achieves:** Our base paper, *ResQConnect*, successfully demonstrates that Agentic RAG provides significantly higher safety and operational accuracy than naive RAG when parsing disaster SOPs. Furthermore, it introduces the Adaptive Event-Triggered (AET) routing policy, proving that we can save massive computational overhead by only recalculating routes when a disruption score crosses a threshold, rather than re-solving continuously. Finally, it pioneers the use of mobile-deployed SLMs to provide offline resilience.

**What the Supplementary Papers Add:** 
*   *Peng et al. (2025)* identifies a critical limitation in ground-only routing during disasters: debris and destroyed infrastructure render isolated nodes unreachable. They introduce truck-drone collaboration to solve the "last-mile" access problem.
*   *Li et al. (2025) [Vision]* provides the theoretical justification for moving away from automated black boxes toward "Collective Human-Machine Intelligence," insisting that AI must act as a *Copilot* to human dispatchers rather than an autonomous replacement.
*   *Li et al. (2026) [DisastRAG]* highlights the flaw in single-source RAG pipelines, demonstrating that operational success requires fusing unstructured text (SOPs) with structured relational data (inventory/records) through a multi-path routing architecture.

**What is STILL MISSING:** 
Despite these rapid advancements, a glaring gap remains at the intersection of these domains. ResQConnect's routing assumes trucks can reach all nodes and relies heavily on proprietary cloud LLMs (GPT-4o), compromising its offline "resilience" claim for the command center. Peng's truck-drone routing uses black-box Deep Reinforcement Learning (DRL) that lacks the explainability and rapid adaptability required by Li's "Human-Machine Teaming" vision. Meanwhile, DisastRAG provides the multi-source data fusion but stops short of plugging that data into a physical routing engine. **There is currently no fully open-source, offline-capable platform that fuses multi-source agentic RAG with explainable, human-in-the-loop truck-drone collaborative routing.**

---

## 3. OUR POSITIONING

**ResQ-MAR occupies the intersection of Agentic RAG, Explainable Truck-Drone Logistics, and Edge Resilience, addressing the gaps left by ResQConnect, Peng's DRL models, and single-source platforms.** 

By replacing black-box DRL with deterministic OR-Tools, transitioning entirely to local Llama 3.1 models via Ollama, integrating structured inventory databases alongside unstructured SOPs, and wrapping the entire system in a human-centric Streamlit dashboard, ResQ-MAR operationalizes the ultimate vision of a resilient, collective human-machine disaster copilot.

---

## 4. CITATION MAP

```text
       [ Li et al. (2025) Vision ]
                  │
                  │ informs: multi-agent justification,
                  │ human-AI teaming, copilot concept
                  ▼
         +-----------------+
         |                 | ◄───── [ Peng et al. (2025) ]
         |                 |        informs: truck-drone 
         |    ResQ-MAR     |        collaborative routing
         |  (Our Project)  |        (last-mile logistics)
         |                 |
         +-----------------+
                  ▲
                  │ informs: multi-source knowledge base,
                  │ structured + unstructured data routing
                  │
       [ Li et al. (2026) DisastRAG ]

                  ▲
                  │
                  │ (Base Architecture)
                  │ informs: Agentic RAG logic,
                  │ AET adaptive routing triggers,
                  │ edge offline resilience
                  │
       [ ResQConnect (2026) Base ]
```
