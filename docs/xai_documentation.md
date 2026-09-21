# ResQ-MAR Explainable AI (XAI) Documentation

## 1. Why Explainability Matters in Emergency AI
In mission-critical emergency response systems, "black box" AI is unacceptable. Decisions regarding resource allocation, protocol selection, and route optimization involve life-or-death outcomes. 
- **Accountability:** Dispatchers and commanding officers must be able to trace exactly why a drone was deployed instead of an ambulance.
- **Trust:** Faculty, dispatchers, and responders need to trust the system. Transparent reasoning fosters this trust.
- **Regulatory Compliance:** Adding explainability fulfills emerging requirements for AI transparency in public safety domains.

## 2. What ResQ-MAR Explains
ResQ-MAR logs and visualizes reasoning traces for every major decision point:
- **RAG Decisions:** Which SOP was retrieved, why it was chosen over others, and confidence scores based on semantic relevance.
- **Routing Decisions:** Which emergency vehicle was assigned, why (e.g., ETA, distance, availability), and any alternative routes considered.
- **Approval Decisions:** What modifications a human dispatcher made to the AI's proposed plan, and the stated reasoning.

## 3. Confidence Scoring
Every decision output by the agent swarm is accompanied by a confidence score [0.0 - 1.0].
- **High Confidence (> 0.8):** Standard procedures, clear data, high semantic match for SOPs.
- **Medium Confidence (0.6 - 0.8):** Slight ambiguity, moderate distance for routing, or secondary SOP matches.
- **Low Confidence (< 0.6):** High uncertainty, conflicting metadata, or distant routing assignments. These are immediately flagged in the dashboard as `REVIEW REQUIRED`.

## 4. Counterfactual Analysis
The XAI dashboard includes an interactive "what-if" generator. This is crucial for training dispatchers and stress-testing the system.
- **Example:** "What if the severity was Medium instead of Critical?" 
- The system will demonstrate how resource allocations shift based on changes to incident variables, proving that the AI is dynamically responding rather than relying on hardcoded static rules.

## 5. Audit Trail
The system persists all decisions to `data/decision_logs.jsonl`.
- **Post-Incident Review:** An exportable, plain-text Audit Trail can be downloaded directly from the dashboard.
- **Compliance:** This provides a chronological timeline of AI recommendations and human interventions, essential for post-action reports and legal review.
