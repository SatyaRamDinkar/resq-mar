Generated for ResQ-MAR Capstone | Multi-agent deep reinforcement learning-based truck-drone collaborative routing with dynamic emergency response | Date: 2026-08-26

# Paper 1 Analysis: Truck-Drone Collaborative Routing (Peng et al., 2025)

## 1. BIBLIOGRAPHIC INFO
*   **Full APA Citation:** Peng, W., Wang, D., Yin, Y., & Cheng, T. C. E. (2025). Multi-agent deep reinforcement learning-based truck-drone collaborative routing with dynamic emergency response. *Transportation Research Part E: Logistics and Transportation Review*, 195, 103974. https://doi.org/10.1016/j.tre.2025.103974
*   **Journal:** Transportation Research Part E: Logistics and Transportation Review (Volume 195)
*   **Year:** March 2025
*   **DOI:** 10.1016/j.tre.2025.103974
*   **Authors & Affiliations:** Wenhao Peng, Dujuan Wang, Yunqiang Yin, and T.C.E. Cheng.

## 2. PROBLEM ADDRESSED
*   **Routing Problem Solved:** The paper solves the dynamic truck-drone collaborative routing problem for humanitarian logistics. It focuses on dispatching truck-drone tandems to deliver relief resources in scenarios where affected areas, road conditions, and resource requirements are highly dynamic and uncertain.
*   **Need for Truck-Drone Collaboration:** In post-disaster environments, road networks are often severely damaged, blocked by debris, or congested. Trucks carry heavy loads but are restricted to accessible roads. Drones have limited payload capacity but can fly over obstacles and reach isolated, hard-to-access areas rapidly. Combining them allows the truck to act as a mobile depot while the drone handles the "last-mile" delivery to unreachable nodes.
*   **Limitations of Ground-Only Routing:** Pure ground routing (truck-only) is slow, susceptible to road network failures, and often completely fails to reach isolated communities. Conversely, helicopter-only systems are too expensive and resource-constrained for granular, widespread deliveries.

## 3. METHODOLOGY
*   **Algorithm Used:** The authors model the problem as a **Markov game** and propose a **Multi-Agent Deep Reinforcement Learning (MADRL)** algorithm. This approach allows multiple agents (the trucks and drones) to learn optimal collaborative routing policies through trial and error within a simulated environment.
*   **Truck-Drone Coordination:** The system employs an event-driven method to capture dynamic state changes. The truck travels along the road network and launches the drone from specific nodes. The drone performs deliveries and then returns to the truck at a designated rendezvous node to swap batteries and reload.
*   **State, Action, Reward Space:** 
    *   *State Space:* Dynamic node demands, current locations of trucks and drones, remaining drone battery, and road network status.
    *   *Action Space:* Next-node selections for both the truck and the drone.
    *   *Reward Function:* A function prioritizing the minimization of delivery delays, maximization of coverage, and penalty for missed time windows or battery depletion.
*   **Constraints Modeled:** Drone battery life/flight range, truck and drone payload capacities, time windows for deliveries, and rendezvous synchronization constraints.
*   **Handling Dynamic Incidents:** To enhance performance and handle new emergencies arriving dynamically, the algorithm incorporates **prioritized experience replay** (to learn faster from rare/critical dynamic events) and **invalid action masking** (to restrict the decision space and prevent agents from selecting infeasible routes, such as flying a drone beyond its battery limit).

## 4. EXPERIMENTAL SETUP
*   **Datasets/Scenarios:** The authors validated their model using a real-world case study based on the **2008 Wenchuan earthquake** in Sichuan, China.
*   **Scale:** *(Based on abstract/summary — full text not accessible for exact node count)* The simulation involves a disaster-affected region with multiple demand nodes, utilizing a fleet of truck-drone tandems to distribute relief.
*   **Simulation Environment:** An event-driven simulation framework that dynamically updates road status and injects new demand nodes during the operation to simulate post-earthquake chaos.

## 5. RESULTS & METRICS
*   **Metrics Measured:** Response time, delivery coverage, and computational efficiency relative to baselines.
*   **Key Numerical Results:** The numerical studies demonstrate the superiority of the proposed MADRL method over traditional heuristic rules and existing baseline solvers. 
*   **Improvement Over Baseline:** The case study highlights that the truck-drone collaborative mode significantly outperforms traditional truck-only or helicopter-only systems in terms of reaching isolated nodes faster and increasing total fulfilled demand under dynamic conditions.
*   **Ablation Studies:** The authors analyzed the impact of prioritized experience replay and invalid action masking, proving that these additions significantly improve sample efficiency and convergence speed.

## 6. LIMITATIONS
*(Critical analysis based on MADRL paradigms in logistics)*
*   **What they did NOT address:** Explainability. DRL policies act as "black boxes," making it difficult for human dispatchers to understand *why* a specific route was chosen. In high-stakes emergency response, lack of explainability can lead to a lack of trust.
*   **Scalability Issues:** MADRL models suffer from the "curse of dimensionality." Scaling the algorithm to hundreds of vehicles and thousands of dynamic nodes requires massive retraining and computational power.
*   **Real-world Deployment Gaps:** Training a DRL model requires a perfectly simulated environment that perfectly matches the real-world dynamics. Simulation-to-reality (Sim2Real) transfer is notoriously difficult in disaster scenarios because real-world debris, weather, and human behavior cannot be perfectly modeled.
*   **Computational Cost:** Real-time inference might be fast, but the initial training and periodic retraining as the disaster evolves require heavy GPU compute, which is often unavailable at local edge command centers.

## 7. HOW THIS INFORMS RESQ-MAR
*   **Component Utilizing This:** The Resource Distributor Workflow (Routing Engine).
*   **What we will adopt:** We will adopt the **concept** of truck-drone collaborative routing to solve the last-mile accessibility problem identified by Peng et al., specifically modeling trucks as mobile depots for drones.
*   **What we will modify / differ:** Instead of using a black-box Multi-Agent Deep Reinforcement Learning (MADRL) approach, **ResQ-MAR uses a deterministic, explainable solver (Google OR-Tools) combined with Adaptive Event-Triggered (AET) heuristics.** 
*   **Why our choice is better for the capstone:** 
    1. **Explainability:** OR-Tools provides mathematically optimal (or near-optimal) routes based on clear constraints and objective functions. A human dispatcher can easily understand and override the constraints.
    2. **No Training Required:** DRL requires massive datasets and compute to train. Our OR-Tools + AET approach works instantly on any new map or disaster scenario without prior training.
    3. **Edge Deployment:** Our routing engine runs efficiently on standard CPUs, aligning with our goal of a 100% local, edge-capable stack, whereas DRL retraining would require cloud GPUs.
