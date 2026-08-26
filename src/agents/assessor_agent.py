"""
AssessorAgent: Evaluates retrieved SOPs for safety, completeness, and relevance.
Dependencies: pyautogen
"""
from typing import Dict, Any, List
from src.agents.base_agent import ResQAgent

class AssessorAgent(ResQAgent):
    """
    AssessorAgent evaluates the retrieved context to ensure the pipeline has safe,
    sufficient, and non-conflicting information before proceeding to planning.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the AssessorAgent.
        """
        system_message = (
            "You are the Safety and Context Assessor for an emergency response system. "
            "Given retrieved SOPs and incident metadata, evaluate whether the retrieved context is "
            "sufficient, safe, and appropriate for generating a task plan. "
            "Flag any missing safety procedures, inadequate coverage, or conflicting instructions. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="AssessorAgent", system_message=system_message, llm_config=llm_config, use_json_mode=True)

    def assess_context(self, metadata: Dict[str, Any], retrieved_sops: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluates the retrieved SOPs against the incident.
        
        Args:
            metadata (Dict): Extracted incident metadata.
            retrieved_sops (List[Dict]): The SOPs retrieved from ChromaDB.
            
        Returns:
            Dict: Assessment result including coverage_score, safety_flags, and recommendation.
        """
        hazard_type = metadata.get("hazard_type", "unknown")
        urgency = metadata.get("urgency", "low")
        location = metadata.get("location_description", "unknown")
        
        sop_summaries = []
        for sop in retrieved_sops:
            content_snippet = sop.get("content", "")[:200].replace("\n", " ") + "..."
            sop_summaries.append(f"- ID: {sop.get('id', 'N/A')} | Title: {sop.get('metadata', {}).get('title', 'Unknown')} | Snippet: {content_snippet}")
        
        sops_text = "\n".join(sop_summaries) if sop_summaries else "NO SOPS RETRIEVED"
        
        prompt = (
            f"INCIDENT: {hazard_type} at {location}, urgency={urgency}\n"
            f"RETRIEVED SOPs:\n{sops_text}\n\n"
            "Evaluate:\n"
            "1. COVERAGE: Do these SOPs cover all aspects of this incident? (evacuation, rescue, medical, safety)\n"
            "2. SAFETY: Are there any missing safety protocols for this urgency level?\n"
            "3. CONFLICTS: Do any SOPs contradict each other?\n"
            "4. GAPS: What critical information is missing?\n\n"
            "Output JSON ONLY with these exact keys:\n"
            '{"assessment": "sufficient" | "insufficient" | "partial", '
            '"coverage_score": float (0-1), '
            '"safety_flags": [list of strings], '
            '"gaps": [list of strings], '
            '"approved_sop_ids": [list of SOP IDs that are safe to use], '
            '"rejected_sop_ids": [list of SOP IDs that are unsafe or irrelevant], '
            '"recommendation": "proceed" | "retrieve_more" | "manual_review"}'
        )
        
        required_keys = [
            "assessment", "coverage_score", "safety_flags", "gaps", 
            "approved_sop_ids", "rejected_sop_ids", "recommendation"
        ]
        parsed = self._send_json_prompt(prompt, required_keys)
        
        if "error" not in parsed:
            self.log_action(
                "assess_context", 
                {"hazard": hazard_type, "retrieved_sops": len(retrieved_sops)}, 
                {"score": parsed.get("coverage_score"), "recommendation": parsed.get("recommendation")}
            )
            return parsed
            
        # Fallback if LLM fails
        all_ids = [s.get("id") for s in retrieved_sops if "id" in s]
        fallback = {
            "assessment": "partial",
            "coverage_score": 0.5,
            "safety_flags": ["Assessment parsing failed, proceed with caution"],
            "gaps": ["Unknown due to parse error"],
            "approved_sop_ids": all_ids,
            "rejected_sop_ids": [],
            "recommendation": "proceed",
            "error": "parse_failed"
        }
        self.log_action("assess_context_failed", {"hazard": hazard_type}, fallback)
        return fallback

    def is_safe_to_proceed(self, assessment: Dict[str, Any]) -> bool:
        """
        Determines if the pipeline should proceed to planning based on the assessment.
        """
        return assessment.get("recommendation") == "proceed"

# Test Case 1: Sufficient SOPs
# retrieved_sops = [{"id": "SOP-FLD-001", ...}]
# returns recommendation: "proceed", score: 0.9

# Test Case 2: Conflicting/Irrelevant SOPs
# retrieved_sops = [{"id": "SOP-FIRE-001", ...}] for a flood incident
# returns recommendation: "retrieve_more" or "manual_review", rejected_sop_ids: ["SOP-FIRE-001"]
