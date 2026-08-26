# Phase 4 Step 1: Benchmark Methodology

## 1. Benchmark Objectives
The objective of this full benchmark suite is to empirically validate the advantages of the ResQ-MAR multi-agent emergency response system compared to traditional baselines. We measure system capability across five distinct disaster scenarios to prove that Agentic Retrieval-Augmented Generation (RAG), Adaptive Event-Triggered (AET) routing, and Collaborative Truck-Drone dispatch provide statistically significant improvements in emergency response metrics.

## 2. Dataset Description
To ensure ecological validity, the benchmark utilizes a dataset of 50 simulated incidents modeled after real 911 dispatch calls in the Colombo, Sri Lanka region (Lat: 6.85 to 6.95, Lon: 79.80 to 79.90). 
- **Flood Incidents**: 15 (requiring boats and high-clearance vehicles)
- **Fire Incidents**: 12 (requiring multi-station fire truck deployment)
- **Earthquake Incidents**: 10 (requiring structural collapse units)
- **Medical Incidents**: 8 (requiring ambulances)
- **Complex Incidents**: 5 (requiring multi-modal drone and truck collaboration)
Additionally, 15 emergency resources are simulated across strategic base locations.

## 3. System Configurations
The benchmark runs identically on three architectural configurations:
- **ResQ-MAR**: The complete system proposed in this capstone. Employs 4-step Agentic RAG for planning, AET heuristics for routing batching, and Truck-Drone modeling.
- **Baseline-A (Naive RAG + Continuous Routing)**: Employs standard 1-step retrieval for planning, and re-runs the standard Vehicle Routing Problem (VRP) solver continuously upon every new incident without batching.
- **Baseline-B (Static Rules)**: Employs no language model. Extracts keywords and dispatches the geographically closest resource regardless of traffic, SOP compliance, or road blockages.

## 4. Metrics Definition
We track five primary metrics for each configuration:
- **Coverage Score (0-1)**: Ratio of critical SOP requirements successfully met by the generated plan.
- **Avg Latency (ms)**: End-to-end processing time from incident intake to dispatch communication.
- **Solver Calls**: Number of times the OR-Tools optimization engine was invoked.
- **Route Quality (0-1)**: Optimality of the route regarding travel time and resource constraints.
- **Success Rate (%)**: Percentage of incidents where Coverage Score > 0.40.

## 5. Experimental Setup
Due to local computing constraints, LLM responses and exact OR-Tools distance matrices are deterministically simulated using seeded random distributions bound by individual component benchmarks identified in Phase 3. The random seed utilizes the `incident_id` to guarantee 100% reproducible execution runs.

## 6. Expected Results
Extrapolating from Phase 3 isolated module testing, we expect:
- **Coverage**: ResQ-MAR outperforms Baseline-A by roughly 50% due to the AssessorAgent's iterative refinement.
- **Compute Efficiency**: AET routing will reduce solver calls by 60-70% compared to Baseline-A.
- **Latency**: ResQ-MAR will be marginally slower than Baseline-B (Static) due to LLM overhead, but dramatically faster than Baseline-A due to solver batching.

## 7. Limitations
- Simulations rely on bounded random walk estimations for exact latencies rather than live API calls (to facilitate rapid execution under 2 minutes).
- Real-time traffic variables are abstracted into static distance calculations.
- Small Local Models (Phi-3) exhibit slightly lower baseline reasoning compared to production cloud models (GPT-4), though relative improvements hold.

## 8. Reproducibility
All source code for the benchmark execution, including the synthetic datasets and deterministic seeds, are open-source and included within the project repository under `src/benchmark/` and `data/benchmark_incidents.json`.
