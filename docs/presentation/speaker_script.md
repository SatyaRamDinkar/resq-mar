# ResQ-MAR Final Review Speaker Script

This is the word-for-word narration script for the final capstone review.

---

**SLIDE 1: Title**
- **TIME:** 30 seconds
- **SCRIPT:** "Good morning everyone. I am Satya Ram Dinkar from the Department of Computer Science. Today, I am presenting ResQ-MAR -- an AI-powered multi-agent emergency response system that is completely free, completely local, and completely open-source."
- **KEY POINTS:**
  - Name and affiliation
  - Project name and core promise
  - Differentiator: zero cost, local deployment
- **TRANSITION:** "Let's start by understanding why this matters."

**SLIDE 2: The Problem**
- **TIME:** 45 seconds
- **SCRIPT:** "Natural disasters are on the rise globally. When infrastructure collapses, existing cloud-based systems like ResQConnect fail because they require constant internet to reach APIs like GPT-4o. Furthermore, static routing algorithms break down when roads are suddenly blocked. We need a system that operates locally, adapts dynamically, and remains completely free."
- **KEY POINTS:**
  - Infrastructure collapse
  - Cloud dependency is a flaw
  - Static routing fails
- **TRANSITION:** "This led us to four primary research questions."

**SLIDE 3: Research Questions**
- **TIME:** 40 seconds
- **SCRIPT:** "We structured our research around four questions: How to improve protocol retrieval via Agentic RAG; How to save compute using Adaptive Routing; How to ensure geographic coverage with Truck-Drone collaboration; and how to maintain uptime using Edge SLMs."
- **KEY POINTS:**
  - Agentic RAG
  - Adaptive Routing
  - Truck-Drone Collaboration
  - Edge SLM
- **TRANSITION:** "Let's see how current literature addresses these."

**SLIDE 4: Literature Review**
- **TIME:** 50 seconds
- **SCRIPT:** "If we look at the landscape, some systems handle routing, others handle retrieval, but none unify them. ResQConnect was a great base, but it lacks offline edge support and agentic intelligence. ResQ-MAR is the first framework to integrate all these capabilities into a single, zero-cost open-source package."
- **KEY POINTS:**
  - Fragmentation in current solutions
  - ResQConnect's limitations
  - ResQ-MAR unifies all features
- **TRANSITION:** "So, how did we build it? Here is the architecture."

**SLIDE 5: System Architecture**
- **TIME:** 45 seconds
- **SCRIPT:** "Our architecture separates concerns. Instead of one massive LLM doing everything, we have 6 specialized agents. Intake parses data, Planner strategizes, and Router handles math. AutoGen orchestrates the handoffs. The entire stack runs on Python, Ollama, and OR-Tools."
- **KEY POINTS:**
  - Separation of concerns
  - AutoGen orchestration
  - Local tech stack
- **TRANSITION:** "Let's dive into our first major innovation: Agentic RAG."

**SLIDE 6: Agentic RAG**
- **TIME:** 50 seconds
- **SCRIPT:** "Naive RAG often pulls the wrong manuals if keywords overlap. We introduced a 4-step Agentic RAG loop. An AssessorAgent acts as a quality filter, rejecting bad pulls and forcing a re-query. This bumped our standard operating procedure coverage from 47% to 82% -- a massive 74% improvement in safety."
- **KEY POINTS:**
  - AssessorAgent quality filter
  - Iterative re-query
  - 74% improvement
- **TRANSITION:** "Once we have the plan, we need to route vehicles."

**SLIDE 7: AET Adaptive Routing**
- **TIME:** 45 seconds
- **SCRIPT:** "Standard systems re-run complex math solvers every single time a new call comes in. This crashes servers during mass disasters. Our Adaptive Event-Triggered (AET) routing holds routes steady unless a major threshold is crossed. This reduced solver calls by 66.7%, preserving vital CPU cycles."
- **KEY POINTS:**
  - Avoid re-solving constantly
  - Event-triggered thresholds
  - 66.7% reduction
- **TRANSITION:** "But what happens when roads are physically destroyed?"

**SLIDE 8: Truck-Drone Collaboration**
- **TIME:** 50 seconds
- **SCRIPT:** "If an earthquake blocks a road, ambulances cannot reach the victims. Drones can, but they have short battery lives. We built a collaborative solver where trucks act as mobile launchpads. The truck drives to the blockage edge, and the drone handles the final mile. This guarantees 100% geographic coverage."
- **KEY POINTS:**
  - Blocked roads stall trucks
  - Drones solve the final mile
  - 100% coverage
- **TRANSITION:** "To run all this intelligence reliably, we need offline capabilities."

**SLIDE 9: Edge SLM & Human-in-the-Loop**
- **TIME:** 50 seconds
- **SCRIPT:** "We deploy a 1.6GB Phi-3-mini edge model that takes over automatically if the main server loses internet. More importantly, we instituted a Human-in-the-Loop circuit breaker. The AI plans everything, but a human dispatcher must click approve before a real vehicle moves."
- **KEY POINTS:**
  - 1.6GB Phi-3-mini fallback
  - Human circuit breaker
  - AI proposes, human approves
- **TRANSITION:** "Let's see how this looks for the dispatcher."

**SLIDE 10: The Dashboard**
- **TIME:** 40 seconds
- **SCRIPT:** "Our Streamlit dashboard is the nerve center. It features a live Folium heatmap, real-time agent tracking, and the critical approval panel. It auto-refreshes every 5 seconds, providing complete situational awareness to the commander."
- **KEY POINTS:**
  - Folium heatmap
  - Live agent tracking
  - Approval panel
- **TRANSITION:** "Let's walk through a real scenario."

**SLIDE 11: Demo Scenario 1**
- **TIME:** 40 seconds
- **SCRIPT:** "In our first demo scenario, a flood in Colombo triggers a call. Within 1.2 seconds, the multi-agent pipeline parses the text, retrieves the exact evacuation SOP, calculates the optimal route for boats, and places it on the dashboard for approval."
- **KEY POINTS:**
  - Flood scenario
  - Lightning-fast retrieval
  - Dashboard integration
- **TRANSITION:** "Now consider a more complex event."

**SLIDE 12: Demo Scenario 2**
- **TIME:** 45 seconds
- **SCRIPT:** "In a chemical fire, the metadata agent intelligently flags it as a Hazmat situation. The Router realizes it's too dangerous to send humans into the smoke immediately, so it dispatches a drone alongside the trucks for thermal imaging."
- **KEY POINTS:**
  - Hazmat detection
  - Multi-vehicle dispatch
  - Safety first
- **TRANSITION:** "We ran these scenarios across 50 simulated incidents to gather statistical proof."

**SLIDE 13: Benchmark Results**
- **TIME:** 50 seconds
- **SCRIPT:** "Across 50 incidents, ResQ-MAR achieved a 94% success rate compared to 72% for naive AI and 54% for static rules. It achieved the highest route quality, vastly improved coverage, and cut solver calls by 65% compared to continuous AI baselines."
- **KEY POINTS:**
  - 50 incidents
  - 94% success rate
  - Massive improvements over baselines
- **TRANSITION:** "To summarize what we achieved in just 12 weeks..."

**SLIDE 14: Key Achievements**
- **TIME:** 40 seconds
- **SCRIPT:** "In just 12 weeks, we built 6 custom AI agents, enhanced RAG retrieval, implemented mathematical Truck-Drone routing, deployed a local edge model, built a full UI, and open-sourced the entire stack."
- **KEY POINTS:**
  - 6 Agents
  - RAG + Truck-Drone + Edge
  - 100% open source
- **TRANSITION:** "The novel contributions to the field are clear."

**SLIDE 15: Contributions to Knowledge**
- **TIME:** 45 seconds
- **SCRIPT:** "Our contributions bridge a massive gap in literature. We are the first to combine agentic reasoning with drone routing and offline resilience in a single, auditable framework."
- **KEY POINTS:**
  - Bridging the gap
  - Unifying features
  - Auditable framework
- **TRANSITION:** "However, we must be honest about our limitations."

**SLIDE 16: Limitations & Future Work**
- **TIME:** 50 seconds
- **SCRIPT:** "We recognize that our benchmarks used synthetic data and simulated delays to run at scale. Moving forward, we aim to integrate real GPS tracking, voice-to-text via Whisper for audio calls, and native multilingual support to deploy this directly to Sri Lankan municipalities."
- **KEY POINTS:**
  - Synthetic data limitation
  - GPS integration future
  - Whisper and Multilingual support
- **TRANSITION:** "In conclusion..."

**SLIDE 17: Conclusion**
- **TIME:** 35 seconds
- **SCRIPT:** "To conclude: Advanced AI shouldn't just be for the rich. ResQ-MAR proves that with smart architecture, open-source tools, and a human-in-the-loop, any municipality on any budget can deploy a world-class disaster response system."
- **KEY POINTS:**
  - AI for everyone
  - Zero-cost deployment
  - Human oversight
- **TRANSITION:** "Thank you."

**SLIDE 18: Thank You**
- **TIME:** 15 seconds
- **SCRIPT:** "Thank you for your time and attention. I would now like to open the floor to any questions you might have."
- **KEY POINTS:**
  - Open for Q&A
- **TRANSITION:** [End of presentation]
