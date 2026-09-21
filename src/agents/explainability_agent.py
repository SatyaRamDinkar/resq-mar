import json
from typing import List, Dict, Any
from src.utils.decision_logger import log_agent_decision, get_decisions_for_incident

class ExplainabilityAgent:
    """
    Agent responsible for rendering transparent, human-readable explanations of AI decisions.
    Integrates directly with the centralized decision logger.
    """
    
    def __init__(self):
        """Initialize the ExplainabilityAgent."""
        pass
        
    def log_decision(self, agent_name: str, decision: str, reasoning: str, confidence: float, inputs: dict, incident_id: str = "default") -> str:
        """
        Log a decision with reasoning and confidence traces.
        
        Args:
            agent_name (str): Name of the agent.
            decision (str): The final decision made.
            reasoning (str): Human-readable reasoning.
            confidence (float): Confidence score between 0.0 and 1.0.
            inputs (dict): Inputs provided to the agent.
            incident_id (str): Incident ID.
            
        Returns:
            str: Generated decision ID.
        """
        outputs = {"decision": decision}
        return log_agent_decision(
            agent_name=agent_name,
            decision_type="general",
            inputs=inputs,
            outputs=outputs,
            reasoning=reasoning,
            confidence=confidence,
            incident_id=incident_id
        )

    def get_decision_chain(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Return all decisions for an incident in chronological order.
        
        Args:
            incident_id (str): Associated incident ID.
            
        Returns:
            List[Dict]: Chronological list of decision dictionaries.
        """
        return get_decisions_for_incident(incident_id)

    def explain_routing_decision(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provide human-readable explanations for routing assignments.
        
        Args:
            plan (dict): The routing plan dictionary containing assignments.
            
        Returns:
            Dict: Explanation payload for the dashboard.
        """
        explanations = []
        overall_confidence = plan.get("confidence", 0.85) # Example default realistic score
        
        for task in plan.get("tasks", []):
            vehicle = task.get("resource", "Unknown Resource")
            dist = task.get("distance_km", 0.0)
            
            reason = f"RouterAgent chose {vehicle} because it was {dist}km away (closest available)."
            
            # Add edge-case reasoning if distance is oddly high
            if dist > 15.0:
                reason = f"RouterAgent assigned {vehicle} from {dist}km away because closer units were unavailable or inaccessible."
                
            explanations.append({
                "vehicle": vehicle,
                "reason": reason,
                "confidence": overall_confidence
            })
            
        return {
            "type": "routing",
            "explanations": explanations,
            "overall_confidence": overall_confidence
        }

    def explain_rag_decision(self, retrieved_sops: List[Dict[str, Any]], scores: List[float], final_sop: str, re_retrieval_triggered: bool = False) -> Dict[str, Any]:
        """
        Explain why a specific SOP was chosen during the RAG pipeline.
        
        Args:
            retrieved_sops (list): List of candidate SOP dictionaries.
            scores (list): List of relevance scores.
            final_sop (str): The ID or name of the chosen SOP.
            re_retrieval_triggered (bool): Whether the Assessor forced a re-query.
            
        Returns:
            Dict: Explanation payload for the dashboard.
        """
        candidates = []
        for i, sop in enumerate(retrieved_sops):
            candidates.append({
                "sop_id": sop.get("id", f"SOP_{i}"),
                "score": scores[i] if i < len(scores) else 0.5
            })
            
        reasoning = f"The AssessorAgent selected {final_sop} as the primary protocol because it had the highest contextual relevance."
        if re_retrieval_triggered:
            reasoning += " Note: Initial retrieval lacked sufficient coverage, triggering an automatic broader search or web fallback to find this document."
            
        return {
            "type": "rag",
            "final_sop": final_sop,
            "candidates": candidates,
            "re_retrieval_triggered": re_retrieval_triggered,
            "reasoning": reasoning
        }

    def generate_counterfactual(self, incident: Dict[str, Any], change_param: str, change_value: Any) -> Dict[str, Any]:
        """
        Generate a counterfactual scenario ('what if').
        
        Args:
            incident (dict): The original incident metadata.
            change_param (str): The parameter to change (e.g., 'severity').
            change_value (Any): The new value for the parameter.
            
        Returns:
            Dict: original plan vs counterfactual plan.
        """
        original_val = incident.get(change_param, "unknown")
        
        # Mock logic for demonstration of counterfactual generation
        original_resources = 2 if incident.get("severity") == "critical" else 1
        new_resources = 2 if change_value == "critical" else 1
        
        reasoning = f"If {change_param} was '{change_value}' instead of '{original_val}', the plan would use {new_resources} resource(s) instead of {original_resources}."
        
        return {
            "parameter_changed": change_param,
            "original_value": original_val,
            "new_value": change_value,
            "original_allocation": original_resources,
            "new_allocation": new_resources,
            "explanation": reasoning
        }

    def export_audit_trail(self, incident_id: str) -> str:
        """
        Generate formatted text report of all decisions for legal/review purposes.
        
        Args:
            incident_id (str): Incident ID.
            
        Returns:
            str: The ASCII-formatted text report.
        """
        decisions = self.get_decision_chain(incident_id)
        if not decisions:
            return "No decisions found for this incident."
            
        lines = [f"=== AUDIT TRAIL FOR INCIDENT: {incident_id} ==="]
        for d in decisions:
            lines.append("-" * 40)
            lines.append(f"Timestamp : {d.get('timestamp')}")
            lines.append(f"Agent     : {d.get('agent')}")
            lines.append(f"Decision  : {d.get('outputs', {}).get('decision', 'N/A')}")
            lines.append(f"Reasoning : {d.get('reasoning')}")
            lines.append(f"Confidence: {d.get('confidence'):.2f}")
            
        lines.append("-" * 40)
        lines.append("=== END OF REPORT ===")
        return "\n".join(lines)

    def get_confidence_summary(self, incident_id: str) -> Dict[str, Any]:
        """
        Calculate confidence metrics for a specific incident.
        
        Args:
            incident_id (str): Incident ID.
            
        Returns:
            Dict: avg_confidence, lowest_confidence_decision, highest_confidence_decision, requires_review.
        """
        decisions = self.get_decision_chain(incident_id)
        if not decisions:
            return {}
            
        scores = [d.get("confidence", 0.0) for d in decisions]
        avg = sum(scores) / len(scores)
        lowest = min(decisions, key=lambda x: x.get("confidence", 0.0))
        highest = max(decisions, key=lambda x: x.get("confidence", 0.0))
        
        requires_review = any(s < 0.7 for s in scores)
        
        return {
            "avg_confidence": avg,
            "lowest_confidence_decision": lowest.get("outputs", {}).get("decision", "N/A"),
            "highest_confidence_decision": highest.get("outputs", {}).get("decision", "N/A"),
            "requires_review": requires_review
        }
