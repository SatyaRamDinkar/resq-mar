"""
AgenticRAGPipeline: Orchestrates the 4-step advanced RAG pipeline.
Dependencies: pyautogen
"""
import os
import sys
import time
import logging
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.retrieval_agent import RetrievalAgent
from src.agents.assessor_agent import AssessorAgent
from src.agents.planner_agent import PlannerAgent
from src.rag.embeddings import SOPKnowledgeBase

class AgenticRAGPipeline:
    """
    Orchestrates the 4-step Agentic RAG pipeline:
    1. Normalize/Metadata Extraction
    2. Multi-query Retrieval
    3. Safety and Context Assessment
    4. SOP-Grounded Planning
    """
    
    def __init__(self, llm_config: Dict[str, Any], kb: SOPKnowledgeBase):
        """
        Initialize all agents and reference the knowledge base.
        """
        self.kb = kb
        self.intake_agent = IntakeAgent(llm_config=llm_config)
        self.metadata_agent = MetadataAgent(llm_config=llm_config)
        self.retrieval_agent = RetrievalAgent(llm_config=llm_config)
        self.assessor_agent = AssessorAgent(llm_config=llm_config)
        self.planner_agent = PlannerAgent(llm_config=llm_config)
        self.logger = logging.getLogger("AgenticRAG")

    def run(self, raw_text: str) -> Dict[str, Any]:
        """
        Executes the advanced 4-step Agentic RAG pipeline.
        """
        # STEP 1: METADATA EXTRACTION
        intake = self.intake_agent.process_report(raw_text)
        if intake.get("is_spam", False):
            return {"status": "spam", "reason": "Flagged as non-emergency"}
            
        normalized_text = intake.get("normalized_text", raw_text)
        metadata = self.metadata_agent.extract_metadata(normalized_text)
        print(f"[RAG Orchestrator] Step 1 complete. Hazard: {metadata.get('hazard_type')}, Urgency: {metadata.get('urgency')}")

        # STEP 2: RETRIEVAL
        queries_dict = self.retrieval_agent.reformulate_query(metadata, normalized_text)
        queries = queries_dict.get("queries", [{"query": normalized_text, "hazard_filter": metadata.get("hazard_type")}])
        retrieved_sops = self.retrieval_agent.retrieve_sops(queries, self.kb)
        print(f"[RAG Orchestrator] Step 2 complete. Retrieved {len(retrieved_sops)} unique SOPs")

        # STEP 3: ASSESSMENT
        assessment = self.assessor_agent.assess_context(metadata, retrieved_sops)
        print(f"[RAG Orchestrator] Step 3 complete. Assessment: {assessment.get('assessment')}, Coverage: {assessment.get('coverage_score')}")
        
        recommendation = assessment.get("recommendation", "proceed")
        
        if recommendation == "manual_review":
            return {
                "status": "needs_review",
                "incident": intake,
                "metadata": metadata,
                "assessment": assessment,
                "pipeline_steps": 3
            }
            
        if recommendation == "retrieve_more":
            print("[RAG Orchestrator] Assessment requested more context. Retrieving fallback SOPs...")
            # Fallback broader query
            fallback_results = self.kb.query("unknown", metadata.get("hazard_type", "emergency"), top_k=3)
            # Combine and deduplicate
            for res in fallback_results:
                if not any(s.get("id") == res.get("id") for s in retrieved_sops):
                    retrieved_sops.append(res)
            # Re-assess
            assessment = self.assessor_agent.assess_context(metadata, retrieved_sops)
            print(f"[RAG Orchestrator] Re-assessment complete. Coverage: {assessment.get('coverage_score')}")

        # Filter SOPs to only those approved by the Assessor
        approved_ids = assessment.get("approved_sop_ids", [])
        filtered_sops = [sop for sop in retrieved_sops if sop.get("id") in approved_ids]
        
        # If no SOPs were approved, proceed with empty list to force general fallback planning
        if not filtered_sops:
            print("[RAG Orchestrator] WARNING: No SOPs approved. Proceeding with general planning fallback.")

        # STEP 4: PLANNING
        plan = self.planner_agent.generate_plan(metadata, filtered_sops)
        print(f"[RAG Orchestrator] Step 4 complete. Plan generated with {len(plan.get('tasks', []))} tasks")
        
        return {
            "status": "completed",
            "incident": intake,
            "metadata": metadata,
            "retrieved_sops": retrieved_sops,
            "assessment": assessment,
            "plan": plan,
            "pipeline_steps": 4
        }

    def run_naive(self, raw_text: str) -> Dict[str, Any]:
        """
        Executes the OLD basic pipeline for benchmarking comparison.
        Intake -> Metadata -> Direct Query -> Plan.
        """
        intake = self.intake_agent.process_report(raw_text)
        if intake.get("is_spam", False):
            return {"status": "spam"}
            
        normalized_text = intake.get("normalized_text", raw_text)
        metadata = self.metadata_agent.extract_metadata(normalized_text)
        
        # Naive direct query
        sops = self.kb.query(metadata.get("hazard_type", "unknown"), normalized_text, top_k=2)
        
        # Naive plan generation without assessment filtering
        plan = self.planner_agent.generate_plan(metadata, sops)
        
        return {
            "status": "completed",
            "incident": intake,
            "metadata": metadata,
            "retrieved_sops": sops,
            "assessment": {},
            "plan": plan,
            "pipeline_steps": 1
        }
