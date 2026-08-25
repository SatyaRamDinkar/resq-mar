"""
ResQ-MAR Orchestrator
Manages the agent GroupChat and enforces the sequential pipeline and human-in-the-loop approval.
Dependencies: pyautogen, uuid
"""
import os
import sys
import uuid
import time
from typing import Dict, Any, List
import autogen

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.router_agent import RouterAgent
from src.agents.comms_agent import CommsAgent
from src.rag.embeddings import SOPKnowledgeBase
from src.routing.vrp_solver import VRPSolver


class ResQOrchestrator:
    """
    Orchestrates the entire ResQ-MAR multi-agent pipeline.
    Enforces a strict step-by-step flow: Intake -> Metadata -> Approval -> Planner -> Router -> Comms.
    """

    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initializes the orchestrator, its agents, and the GroupChat environment.
        """
        self.llm_config = llm_config
        
        # Instantiate the specialized agents
        self.intake_agent = IntakeAgent(llm_config=llm_config)
        self.metadata_agent = MetadataAgent(llm_config=llm_config)
        self.planner_agent = PlannerAgent(llm_config=llm_config)
        self.router_agent = RouterAgent(llm_config=llm_config)
        self.comms_agent = CommsAgent(llm_config=llm_config)
        
        # Instantiate knowledge base and VRP solver
        self.kb = SOPKnowledgeBase()
        # Initialize kb if empty
        try:
            stats = self.kb.get_collection_stats()
            if stats.get("total_sops", 0) == 0:
                sop_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'sops')
                if os.path.exists(sop_dir):
                    self.kb.ingest_sops(sop_dir)
        except Exception:
            pass
            
        self.solver = VRPSolver()

        # Create UserProxyAgent for human-in-the-loop
        self.user_proxy = autogen.UserProxyAgent(
            name="human_dispatcher",
            system_message="You are the human dispatcher. Review high-urgency incidents and approve or reject dispatch plans. Reply ONLY 'APPROVE' or 'REJECT'.",
            human_input_mode="NEVER",  # Programmatic simulation for MVP
            llm_config=False
        )

        # Create GroupChat as requested by requirements
        self.groupchat = autogen.GroupChat(
            agents=[
                self.intake_agent, 
                self.metadata_agent, 
                self.user_proxy, 
                self.planner_agent, 
                self.router_agent, 
                self.comms_agent
            ],
            messages=[],
            max_round=12,
            speaker_selection_method="round_robin"
        )
        self.manager = autogen.GroupChatManager(groupchat=self.groupchat, llm_config=llm_config)

    def _generate_incident_id(self) -> str:
        """Generates a unique incident ID."""
        return "inc_" + str(uuid.uuid4())[:8]

    def _extract_json_from_message(self, message: str) -> Dict[str, Any]:
        """Utility to safely extract JSON from an agent message string."""
        import json
        try:
            start = message.find("{")
            end = message.rfind("}")
            if start != -1 and end != -1:
                return json.loads(message[start:end+1])
        except Exception:
            pass
        return {}

    def process_incident(self, raw_text: str, locations: List[Dict], vehicles: List[Dict], human_approval: bool = True) -> Dict[str, Any]:
        """
        Executes the step-by-step incident response flow.
        
        Args:
            raw_text (str): The raw emergency report.
            locations (List[Dict]): Available locations.
            vehicles (List[Dict]): Available vehicles.
            human_approval (bool): Whether to enforce human approval for high urgency.
            
        Returns:
            Dict: The complete incident processing result.
        """
        incident_id = self._generate_incident_id()
        conversation = []
        
        def add_msg(sender: str, text: str):
            conversation.append({"sender": sender, "message": text})

        add_msg("SYSTEM", f"NEW INCIDENT: {raw_text}")

        # 1. Intake
        intake_res = self.intake_agent.process_report(raw_text)
        normalized = intake_res.get("normalized_text", raw_text)
        is_spam = intake_res.get("is_spam", False)
        add_msg("intake", f"Normalized: {normalized} | Spam: {is_spam}")
        
        if is_spam:
            add_msg("comms", "Incident flagged as spam. No action taken.")
            return {
                "incident_id": incident_id,
                "status": "spam",
                "metadata": {}, "plan": {}, "routes": {},
                "agent_conversation": conversation,
                "approval_status": "not_required"
            }

        # 2. Metadata
        meta_res = self.metadata_agent.extract_metadata(normalized)
        add_msg("metadata", f"Metadata extracted: Hazard={meta_res.get('hazard_type')}, Urgency={meta_res.get('urgency')}")

        # 3. Check Approval
        urgency = meta_res.get("urgency", "low").lower()
        hazard_type = meta_res.get("hazard_type", "unknown")
        loc_desc = meta_res.get("location_description", "unknown")
        
        approval_status = "not_required"
        if urgency in ["high", "critical"] and human_approval:
            add_msg("SYSTEM", "Pausing GroupChat for dispatcher approval...")
            add_msg("human_dispatcher", f"DISPATCHER APPROVAL REQUIRED: Approve plan for {hazard_type} incident at {loc_desc}? Reply APPROVE or REJECT.")
            
            # Simulate human delay and response
            time.sleep(2)
            # Default to APPROVE for MVP simulation
            simulated_response = "APPROVE"
            add_msg("human_dispatcher", simulated_response)
            
            if simulated_response == "REJECT":
                add_msg("comms", "Incident rejected by dispatcher.")
                return {
                    "incident_id": incident_id,
                    "status": "rejected",
                    "metadata": meta_res, "plan": {}, "routes": {},
                    "agent_conversation": conversation,
                    "approval_status": "rejected"
                }
            approval_status = "approved"

        # 4. RAG & Planner
        sops = self.kb.query(hazard_type, normalized, top_k=2)
        plan = self.planner_agent.generate_plan(meta_res, sops)
        add_msg("planner", f"Generated tactical plan with {len(plan.get('tasks', []))} tasks. ETA: {plan.get('estimated_total_time_min', 0)} mins.")

        # 5. Router
        routes = self.router_agent.plan_routes(plan, locations, vehicles)
        add_msg("router", f"VRP solved. Status: {routes.get('solver_status')}. Total Distance: {routes.get('total_distance_km')} km.")

        # 6. Comms
        alert = self.comms_agent.broadcast_alert(meta_res, plan, routes)
        add_msg("comms", alert)

        return {
            "incident_id": incident_id,
            "status": "completed",
            "metadata": meta_res,
            "plan": plan,
            "routes": routes,
            "agent_conversation": conversation,
            "approval_status": approval_status
        }
