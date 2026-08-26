# Chapter 2: Literature Review

## 2.1 Emergency Response Systems
Traditional emergency response logistics heavily rely on Computer-Aided Dispatch (CAD) systems. These platforms utilize static, rule-based logic to assign the closest available resource to an incident. However, during large-scale disasters, the operational environment becomes highly dynamic. Roads become impassable, and multiple emergencies compete for limited resources. Rule-based systems lack the semantic understanding to prioritize complex, multi-hazard scenarios effectively, highlighting a shift toward AI-assisted dispatching.

## 2.2 Multi-Agent Systems in Disaster Management
The application of Multi-Agent Systems (MAS) in disaster management has gained traction with the advent of Large Language Models (LLMs). Frameworks such as CrewAI, LangGraph, and AutoGen facilitate collaborative AI problem-solving. ResQ-MAR utilizes AutoGen AG2 due to its superior handling of complex group chats, native support for human-in-the-loop interventions, and robust code-execution sandboxing. Unlike monolithic LLM approaches, multi-agent architectures separate concerns, reducing hallucinations and improving overall system reliability.

## 2.3 Retrieval-Augmented Generation for Emergency Protocols
Standard Operating Procedures (SOPs) dictate emergency response protocols. Extracting actionable steps from SOPs using LLMs traditionally relies on Naive Retrieval-Augmented Generation (RAG). Naive RAG performs a single vector search, often missing critical peripheral context. ResQConnect (Aththanayake et al., 2026) utilized basic RAG powered by cloud-based GPT-4o. ResQ-MAR enhances this by introducing an Agentic RAG pipeline: a 4-step process where a dedicated AssessorAgent evaluates retrieved context for completeness and triggers iterative re-retrievals if critical medical or hazmat protocols are absent.

## 2.4 Vehicle Routing in Disaster Logistics
Disaster routing is a variation of the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). Solvers like Google OR-Tools are industry standards for computing optimal paths. A significant gap in existing literature is the computational cost of continuous re-routing. When new incidents arrive sequentially, continuously re-solving the VRP wastes computational resources. Adaptive Event-Triggered (AET) routing offers a heuristic alternative, batching route recalculations only when specific threshold criteria are met, thereby saving critical compute cycles.

## 2.5 Truck-Drone Collaborative Delivery
The integration of Unmanned Aerial Vehicles (UAVs) with ground vehicles has revolutionized logistics. Peng et al. (2026) proposed a collaborative truck-drone routing model for package delivery. Adapting this for emergency response allows trucks to transport heavy equipment to the edge of road blockages, while drones deploy for the "last mile" to deliver critical medical supplies or establish communication links. This hybrid approach circumvents ground-level infrastructure failures that plague pure truck-based routing models.

## 2.6 Edge AI and Offline Operation
Dependence on cloud infrastructure is a critical vulnerability. In disasters where fiber lines and cellular towers are destroyed, systems relying on OpenAI or Google APIs cease to function. The emergence of Small Language Models (SLMs) such as Microsoft's Phi-3-mini and Alibaba's Qwen2-1.5B allows for sophisticated reasoning directly on edge hardware. Coupling SLMs with Progressive Web Apps (PWAs) enables fully offline, resilient command centers that maintain operational continuity.

## 2.7 Gap Analysis
Table 2.1 compares prominent recent architectures against ResQ-MAR.

| Feature | ResQConnect (2026) | Peng et al. (2026) | DisastRAG (Li et al.) | ResQ-MAR (Proposed) |
|---|---|---|---|---|
| Multi-Agent | Yes | No | Yes | Yes |
| Agentic RAG | No | No | Yes | Yes |
| Adaptive Routing | No | Yes | No | Yes |
| Truck-Drone | No | Yes | No | Yes |
| Edge SLM | No | No | No | Yes |
| Human-in-Loop | Limited | No | No | Yes |
| Open Source | No | Yes | Yes | Yes |

As illustrated, ResQ-MAR is the only system integrating multi-agent reasoning, agentic RAG, AET routing, truck-drone collaboration, and offline edge capabilities within a single, open-source, zero-cost framework.

## 2.8 Summary
This review highlights the limitations of current disaster response systems, particularly regarding cloud dependency, static routing, and single-pass retrieval methods. The next chapter details the architectural design of ResQ-MAR to address these specific gaps.
