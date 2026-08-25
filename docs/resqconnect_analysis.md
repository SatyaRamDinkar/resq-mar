Generated for ResQ-MAR Capstone Project | Base Paper Analysis | Date: 2026-08-26

# ResQConnect: An AI-Powered Multi-Agentic Platform for Human-Centered and Resilient Disaster Response - Deep Analysis

## SECTION 1: BIBLIOGRAPHIC INFO
- **Full Citation (APA):** Aththanayake, S., Mallikarachchi, C., Wickramasinghe, J., Kugarajah, S., Meedeniya, D., & Pradhan, B. (2026). ResQConnect: An AI-Powered Multi-Agentic Platform for Human-Centered and Resilient Disaster Response. *Sustainability*, 18(2), 1014. https://doi.org/10.3390/su18021014
- **Journal:** Sustainability
- **Volume / Issue / Page:** Volume 18, Issue 2, Page 1014
- **DOI:** 10.3390/su18021014
- **Publication Date:** 19 January 2026
- **Authors and Affiliations:** 
  - Savinu Aththanayake, Chemini Mallikarachchi, Janeesha Wickramasinghe, Sajeev Kugarajah, Dulani Meedeniya (Department of Computer Science & Engineering, University of Moratuwa, Sri Lanka)
  - Biswajeet Pradhan (Centre for Advanced Modelling and Geospatial Information Systems, Faculty of Engineering and IT, University of Technology Sydney, Australia)
- **Open Access Status:** Open access distributed under the Creative Commons Attribution (CC BY) license.

---

## SECTION 2: ABSTRACT SUMMARY
The paper presents **ResQConnect**, a multimodal, multi-agent AI platform designed to transform fragmented citizen disaster reports into actionable field operations. It combines an agentic Retrieval-Augmented Generation (RAG) system with a hazard-specific knowledge base to produce reliable task plans, while an adaptive event-triggered (AET) routing algorithm dynamically allocates multi-commodity relief resources. Furthermore, a compressed small language model (SLM) is deployed on mobile edge devices to guarantee continuous, policy-aligned guidance for victims even when cloud networks fail.
- **Key Contribution:** Structuring an Agentic RAG for operational correctness and safety, proposing an adaptive event-triggered multi-commodity routing algorithm, and deploying a compressed, domain-specific edge LLM for offline mobile guidance.
- **Problem Addressed:** The "last-mile" challenge of disaster response—transforming unstructured multimodal citizen data into timely, accountable field actions under dynamic conditions and severe network disruptions.
- **Solution Proposed:** The integration of three components: a multi-agent RAG workflow for task generation, an AET routing engine for resource distribution, and a local SLM for offline execution on edge devices.
- **Results Claimed:** The system improved overall task-quality scores from 61.4 to 82.9 (+21.5 points) over a standard RAG baseline. The routing algorithm reduced solver calls by up to 85% compared to continuous re-optimization, while remaining within 7–12% of optimal response time. The edge deployment delivered fully offline guidance with sub-500 ms response latency and 54 tokens/s throughput on commodity smartphones.

---

## SECTION 3: RESEARCH GAP / MOTIVATION
- **Identified Gap:** The operational "last mile" of disaster response is severely underserved. Existing multi-agent simulation models are primarily used offline for preparedness planning, rather than mediating real-time data flows. Standard RAG systems retrieve semantically similar but operationally inappropriate or unverified responses. Moreover, routing models either rely on rigid periodic schedules or computationally prohibitive continuous re-optimization.
- **Evidence Used:** The authors note that the escalation of natural hazards due to climate change (e.g., floods in South and Southeast Asia) puts immense pressure on emergency services, demanding tools that do more than just provide situational awareness or post-hoc planning.
- **Insufficiency of Existing Tech:** Traditional rule-based Decision Support Systems (DSS) fail to decompose noisy, multifaceted help requests into sub-tasks. Monolithic LLM pipelines lack explicit mechanisms for ensuring accountability, safety, and SOP grounding. 
- **Real-World Event:** The system and dataset were driven by real-world citizen help requests observed during the 2025 Sri Lanka floods and landslide crisis.

---

## SECTION 4: SYSTEM ARCHITECTURE (DETAILED)
The ResQConnect platform integrates three core sub-systems:

**1. Agentic RAG Workflow (7 Nodes/Agents):**
- **Meta Node:** Infers structured metadata (disaster type, location, urgency) from the user request.
- **Filtered Retriever Node:** Uses metadata to retrieve relevant chunks from hazard-specific vector databases.
- **General Retriever Node:** Fallback retriever for unconstrained search across all domains.
- **Assessor Node:** Evaluates contextual adequacy and safety of retrieved chunks. Routes back to Reformulator if context is inadequate.
- **Reformulator Node:** Rewrites the user request into a guideline-oriented query for a better vector search.
- **Web Search Node:** Escalates to web retrieval via Tavily API if internal DB fails.
- **Task Generator Node:** Synthesizes the retrieved context into an ordered, field-executable task breakdown for specific agencies.

**2. Communication and Orchestration:**
The agents do not communicate via unconstrained natural language banter. They use a deterministic execution order enforced by strict guardrails and state-passing. The Assessor Node explicitly dictates the control flow (looping back to the Reformulator) based on a rubric-style prompt evaluation.

**3. Knowledge Base:**
Curated disaster-response documents (SOPs, Sphere guidelines, incident reports, technical advisories). Data is segmented into 120-300 word procedural units and stored in two separate vector collections (Floods and Landslides) tagged with extensive metadata.

**4. LLM & Deployment:**
- **Cloud/Backend:** Uses GPT-4o for the Agentic RAG workflow and reasoning.
- **Edge/Mobile:** Uses a compressed `Qwen2.5-0.5B` Small Language Model (SLM) running natively on the user's mobile device for offline support.

**Architecture Diagram (ASCII):**
```text
[ Citizen Help Requests ]
          │
          ▼
+-------------------------------------------------+
|               Agentic RAG Workflow              |
|                                                 |
|  [Meta Node] (Extracts Metadata)                |
|       │                                         |
|       ▼                                         |
|  [Filtered Retriever] ──(Fallback)─► [General Retriever]
|       │                                         |
|       ▼                                         |
|  [Assessor Node] ◄─────┐                        |
|       │                │ (Inadequate)           |
|  (Adequate)            |                        |
|       │                |                        |
|       │         [Reformulator Node]             |
|       │                ▲                        |
|       │                │                        |
|       │           [Web Search]                  |
|       ▼                                         |
|  [Task Generator Node]                          |
+-------------------------------------------------+
          │
          ▼ Task Breakdown & Resource Requirements
          │
+-------------------------------------------------+
|          Resource Distributor Workflow          |
|                                                 |
| Inputs: Inventory, Demands, Vehicle Status      |
| Engine: AET Multi-Commodity Routing             |
| Output: Resource Distribution Plan & Routes     |
+-------------------------------------------------+
          │
          ▼
+-------------------------------------------------+
|             Edge Deployed Chatbot               |
|                                                 |
| [Dual Mode: Online (Cloud) / Offline (Edge)]    |
| Edge Model: Qwen2.5-0.5B (Quantized)            |
| Output: Query Responses / Safety Guidance       |
+-------------------------------------------------+
```

---

## SECTION 5: KEY ALGORITHMS & METHODS

### 1. Agentic RAG Pipeline
- **Steps:** 7 interconnected nodes (as detailed in Section 4).
- **Execution:** Follows a bounded iterative loop. A request passes through the Meta Node and Retriever. The Assessor checks the context. If it fails the safety/adequacy threshold, the Reformulator re-writes the query. If it fails repeatedly, it hits the Web Search fallback. Finally, it reaches the Task Generator.
- **Models:** GPT-4o.
- **Safety:** Ensured through "Constraint Anchoring"—the system enforces rule sets where output is rejected (or regenerated) if it fails structural validation. The Assessor explicitly checks for SOP compliance and operational safety before task generation.

### 2. Adaptive Event-Triggered (AET) Routing
- **Problem Solved:** Balances the need to quickly re-route vehicles for urgent requests against the computational cost and operational chaos ("nervousness") of continuous re-planning.
- **Trigger Condition:** A new global optimization is triggered only when the Disruption Score `D(t)` exceeds an adaptive, decaying threshold `Θ(t)`. 
- **Solver:** Solves a deterministic static MD-CVRP-MCD (Multi-Depot Capacitated Vehicle Routing Problem with Multi-Commodity Demand) using Google OR-Tools.
- **Constraints:** Atomic fulfillment (entire request filled by one vehicle), multi-commodity capacity, time windows, and subtour elimination.
- **Objective Function:** Minimizes a composite cost `Z = T + S + L + R`, where `T` is total travel time, `S` is priority-weighted response time, `L` penalizes unserved nodes, and `R` penalizes route instability/deviations from previous commitments.

### 3. Edge-Deployed SLM
- **Model:** `Qwen2.5-0.5B`.
- **Quantization:** Converted using Google MediaPipe into a `.task` format with dynamic-range and 4-bit weight quantization, avoiding aggressive pruning to retain generative fidelity.
- **Target Hardware:** Commodity mobile devices (tested on Samsung Galaxy S23 Ultra, Snapdragon 8 Gen 2).
- **Latency & Performance:** Achieves ~412 ms end-to-end latency (18.4 ms/token) and throughput of 54.3 tokens/second.
- **Offline Handling:** Bounded to procedural guidance and general safety. Defaults to conservative advice to mitigate hallucination risks when disconnected from the cloud.

---

## SECTION 6: DATASETS & EXPERIMENTS
- **Datasets Used:** 1000+ real citizen help requests collected from a disaster-support portal during the 2025 Sri Lanka floods and landslide crisis, supplemented with manually curated samples.
- **Disaster Types:** Floods and Landslides.
- **Geographic Region:** Sri Lanka.
- **Edge LLM Fine-Tuning Split:** 580 high-quality Q&A pairs (29 categories × 20 samples), split into 486 Training (80%) and 122 Testing (20%).
- **Synthetic Data (Routing):** Generated via a simulation environment modelling a directed graph with time-varying travel times. Demand nodes arrive stochastically via a Poisson process across 13 scenarios covering 4 load conditions (Low, Medium, High, Extreme).

---

## SECTION 7: EVALUATION METRICS & RESULTS

**Comparison Table:**

| Metric | Baseline | ResQConnect | Improvement |
|--------|----------|-------------|-------------|
| **Overall RAG Quality Score** | 61.4 ± 9.6 | 82.9 ± 6.5 | +21.5 points |
| **RAG Relevance Score** | 5.8 | 8.1 | +2.3 points |
| **RAG Safety & Accuracy** | 6.9 | 8.2 | +1.3 points |
| **Routing Solver Calls (High Load)** | 61 (Continuous) | 11 (AET) | 81% reduction |
| **Edge SLM F1 Score** | 10.77 (Base) | 19.79 (Fine-tuned) | +83% |
| **Edge SLM BLEU Score** | 0.70 (Base) | 2.35 (Fine-tuned) | +236% |

- **Task Planning Quality:** Measured by a blind LLM judge across Relevance, Contextual Enrichment, Safety Accuracy, Specificity, and Signal Quality.
- **Response Time / Latency:** 
  - *RAG Latency:* Increased from 4.1s (Baseline) to 14.8s (Agentic RAG) due to the reasoning overhead.
  - *Routing Response Time:* AET stays within 7–12% of the theoretical upper-bound (Continuous re-optimization).
- **Edge Model Performance:** Very low peak RAM usage (612 MB). The model throughput (54.3 tok/s) easily supports real-time dialogue without network access.
- **Ablation Studies:** Showed that the `Assessor Loop` heavily contributed to the safety score jump (from 7.0 to 8.1), while the `Meta Node + Filtered Retriever` provided the biggest jump in Relevance (5.8 to 7.0).

---

## SECTION 8: LIMITATIONS & WEAKNESSES (CRITICAL)
- **Omitted Disaster Types:** The system is explicitly tailored to Floods and Landslides. It has not been tested on unpredictable, fast-moving crises like earthquakes, fires, or chemical spills.
- **Geographic Scope Limitation:** The knowledge base is strictly curated for Sri Lankan SOPs and cultural/operational contexts, limiting immediate plug-and-play global applicability.
- **Tech Stack Limitations:** The core Agentic RAG heavily relies on a proprietary, cloud-hosted LLM (GPT-4o), introducing a severe single point of failure if the command center loses internet access.
- **Scalability Issues:** The current implementation assumes a centralized backend deployment. Large-scale, multi-region disasters would cause bottlenecks and require complex horizontal scaling strategies.
- **Safety / Ethical Concerns:** The routing algorithm relies on strict numerical priority weighting, which the authors admit simplifies "fairness". Vulnerable groups without the means to communicate might be systematically ignored by the platform.
- **Lack of Human Evaluation:** There were no real human dispatchers surveyed for UX, cognitive load, or trust. The quality of tasks was evaluated by an "LLM Judge" rather than human domain experts.
- **Suggested Future Work:** Integration with precipitation now-casting and land-cover data; horizontal scaling through distributed agent orchestration; incorporation of fairness-aware, community-informed priority schemes; explicit human-in-the-loop override mechanisms.

---

## SECTION 9: OUR DIFFERENTIATION STRATEGY
*How ResQ-MAR builds upon and differentiates from ResQConnect:*

1. **ResQConnect:** Relies on cloud-hosted GPT-4o for the heavy Agentic RAG processing.
   **→ ResQ-MAR:** Employs 100% local, open-weights LLMs (Llama 3.1 via Ollama) for *all* agentic workflows, guaranteeing absolute data privacy and offline command center capabilities.
2. **ResQConnect:** Assumes a monolithic, centralized backend deployment for routing and task orchestration.
   **→ ResQ-MAR:** Will utilize a containerized, decentralized microservice architecture allowing individual, disconnected local Emergency Operations Centers (EOCs) to run the stack independently.
3. **ResQConnect:** Routing fairness is rigidly tied to static priority numbers assigned during the intake phase.
   **→ ResQ-MAR:** Features an interactive Streamlit dashboard allowing human dispatchers to visually adjust equity constraints, priorities, and dynamically inject human intuition into the routing engine.
4. **ResQConnect:** Task quality was evaluated exclusively by an automated LLM Judge.
   **→ ResQ-MAR:** Incorporates explicit human-in-the-loop validation mechanisms in the UI, recording human overrides and rejections to quantitatively measure actual dispatcher trust and cognitive load.
5. **ResQConnect:** The edge chatbot is a static model that cannot adapt to evolving situations without full network connectivity to pull updates.
   **→ ResQ-MAR:** Implements lightweight dynamic prompt injection over local mesh networks or WebSockets (when minimal connectivity exists), pushing real-time global directives to edge agents without updating the model weights.

---

## SECTION 10: CITABLE QUOTES
1. **On the Problem:** "Despite advanced early-warning systems and coordination frameworks, a persistent 'last-mile' challenge undermines response effectiveness: transforming fragmented and unstructured multimodal data into timely and accountable field actions." *(Abstract)*
2. **On Agentic AI Need:** "Traditional rule-based decision-support tools lack the ability to decompose noisy, multi-faceted help requests into sub-tasks, motivating an agentic AI approach..." *(Section 1)*
3. **On Routing Overhead:** "Triggering re-optimization at every event (continuous re-solving) can yield strong solutions but leads to high computational cost and excessive 'nervousness'..." *(Section 4.2.3)*
4. **On RAG Architecture:** "Agentic RAG models treat retrieval and generation as a coordinated multi-agent process rather than a single pipeline..." *(Section 2.1)*
5. **On Edge LLMs:** "The edge-deployed LLM is a core reliability layer within ResQConnect, ensuring uninterrupted assistance during periods of low or zero connectivity which is a frequent condition in disaster situations." *(Section 3.4.3)*
6. **On Latency Trade-offs:** "A marginal increase in processing time is a justifiable price for ensuring that AI-generated support is trustworthy." *(Section 6.1)*
7. **On Human Oversight:** "AI-generated recommendations may influence life-and-death decisions, but human responders must retain ultimate accountability." *(Section 6.6)*

---

## SECTION 11: FIGURES & TABLES SUMMARY

**Key Figures:**
- **Figure 1:** High Level System Overview. Shows the end-to-end architecture (RAG, Routing, Edge).
- **Figure 2:** Agentic Retrieval Workflow. Details the 7-node interaction loop. *(Highly useful for our methodology chapter)*
- **Figure 3:** High-level DataTier. Explains chunking and hazard-specific database ingestion.
- **Figure 4:** Average metric performance radar chart (Standard vs Agentic RAG).
- **Figure 5:** Judgment Decision Transition Matrix.
- **Figure 6:** Mean latency of Standard vs. Agentic RAG.
- **Figure 7:** Priority-Weighted Response Time Across Load Conditions.
- **Figure 8:** Solver Calls Across Policies and Load Conditions. *(Useful to justify our routing approach)*
- **Figure 9:** Comparison of System Nervousness Across Load Conditions.
- **Figure 10 & 11:** Efficiency and Performance of Base SLMs.

**Key Tables:**
- **Table 1:** Comparison of Agentic RAG Frameworks (Self-RAG, Corrective RAG, etc. vs ResQConnect).
- **Table 2:** Comparison of Dynamic and Adaptive Humanitarian Routing Approaches.
- **Table 3:** Comparison of Edge and Compressed LLM Studies.
- **Table 8:** Average Token Usage per Request by Node.
- **Table 9:** Quality metrics across ablation configurations. *(Critical for evaluating RAG design)*
- **Table 11-14:** Routing metrics (Response time, Solver calls, Nervousness).
- **Table 15:** Edge SLM Performance Improvements After Fine-Tuning.

---

## SECTION 12: RELATED WORK MENTIONED
- **Multi-Agent Systems:** Luna-Ramirez and Fasli (2018) [12] - Integration of BDI-style cognitive agents in disaster-rescue simulations.
- **Agentic RAG:** Chang et al. (2025) [19] - MAIN-RAG (Multi-Agent Filtering RAG); Hong et al. (2025) [20] - Dynamic fusion of LLMs for Crisis Communication.
- **Adaptive Routing:** Sheu (2010) [28] - Dynamic relief-demand management; Holguín-Veras et al. (2013) [31] - Deprivation cost models for humanitarian logistics; Peric et al. (2024) [51] - Rolling horizon VRP.
- **Edge / SLM:** Friha et al. (2024) [39] - Survey on LLM-Based Edge Intelligence; Lu et al. (2025) [54] - Demystifying SLMs for Edge Deployment; Jang & Morabito (2025) [55] - Edge-First Language Model Inference.
- **Humanitarian Logistics:** Pescaroli & Alexander (2016) [2] - Cascading disasters vulnerability; Lamos Díaz et al. (2019) [24] - OR/MS research perspectives in disaster operations management.
