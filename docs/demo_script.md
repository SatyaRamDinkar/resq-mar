# ResQ-MAR 5-Minute Demo Video Script

## 1. Video Opening (15 sec)
**On Screen:**
Project logo, title card: "ResQ-MAR: Multi-Agent Emergency Response", name of presenter. Transition to the VS Code terminal.

**Narrator:**
"Hi, my name is Satya Ram Dinkar, and this is ResQ-MAR. When natural disasters strike, emergency dispatch systems are often overwhelmed. Today, I'll demonstrate how our AI-powered, multi-agent architecture resolves complex incidents faster and safer than traditional static pipelines."

## 2. Scenario 1 Walkthrough: Flood Response (90 sec)
**On Screen:**
Terminal running `python scripts/run_full_demo.py`. The "SCENARIO 1: COLOMBO FLOOD RESPONSE" banner appears. Steps 1-7 unfold slowly.

**Narrator:**
"Let's look at a critical flood in Colombo. Our Intake Agent parses the raw 911 description, instantly extracting the severity and location. 
In Step 2, the Metadata Agent enriches the data, noting high population density.
Step 3 is where ResQ-MAR shines: Agentic RAG. Unlike naive RAG, our Assessor Agent iteratively checks the retrieved SOPs. It noticed medical protocols were missing, requested a re-retrieval, and boosted our coverage score to 92%.
For Routing in Step 4, we use Adaptive Event-Triggered logic. Instead of re-solving the massive Vehicle Routing Problem from scratch every time, AET smartly batches changes, saving massive amounts of compute. 
Finally, our Human-in-the-Loop dashboard captures the plan. A dispatcher approves it, the Comms Agent sends it out, and our dashboard updates live."

## 3. Scenario 2 Walkthrough: Fire Response (90 sec)
**On Screen:**
Terminal continues to "SCENARIO 2: DEHIWALA FACTORY FIRE". Steps unfold. The mouse highlights the AET Routing calls compared to Continuous.

**Narrator:**
"Next, a chemical factory fire. Watch the routing step. In traditional Continuous routing, this new event would trigger an expensive recalculation of all active trucks. Our AET router simply adapts the existing routes—requiring only 1 solver call compared to 8 in the baseline.
Furthermore, if our cloud LLM goes down due to internet outages, our system seamlessly falls back to a quantized offline edge model, Phi-3-mini, ensuring that the agents never stop functioning when seconds count."

## 4. Scenario 3 Walkthrough: Earthquake Aftershock (60 sec)
**On Screen:**
Terminal continues to "SCENARIO 3: GAMPAHA EARTHQUAKE". Mouse highlights the "Truck-Drone coverage: 100%".

**Narrator:**
"In this earthquake scenario, roads are blocked by debris. Standard truck-only routing fails to reach the victims, capping coverage at 50%.
ResQ-MAR solves this using a collaborative Truck-Drone Optimization solver. Trucks drive to the edge of the blockage, and deploy drones for the final mile. This guarantees 100% geographic coverage even in completely severed urban grids."

## 5. System Comparison (30 sec)
**On Screen:**
The `DEMO SUMMARY` table prints at the end of the script. Highlight the columns comparing ResQ-MAR vs Baselines. Then switch tabs to show the Streamlit Dashboard (Heatmap).

**Narrator:**
"To quantify these benefits, we ran a 50-incident benchmark suite. ResQ-MAR dramatically outperforms naive baselines: a 69% boost in protocol coverage, an 82% reduction in solver calls, and 100% guaranteed routing reach via drones, all while retaining human oversight."

## 6. Closing (15 sec)
**On Screen:**
Final title card / Thank you slide.

**Narrator:**
"By uniting Agentic RAG, Adaptive Routing, and Edge computing, ResQ-MAR delivers an emergency system built for the realities of modern crises. Thank you."
