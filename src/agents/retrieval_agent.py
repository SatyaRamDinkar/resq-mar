"""
RetrievalAgent: Responsible for reformulating queries and retrieving optimal SOPs.
Dependencies: pyautogen
"""
from typing import Dict, Any, List
from src.agents.base_agent import ResQAgent
from src.rag.embeddings import SOPKnowledgeBase

class RetrievalAgent(ResQAgent):
    """
    RetrievalAgent reformulates incident metadata into multiple targeted search queries,
    and executes them against the SOP Knowledge Base to maximize retrieval relevance.
    """
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize the RetrievalAgent.
        """
        system_message = (
            "You are the Knowledge Retrieval Agent for an emergency response system. "
            "Given structured incident metadata, reformulate the query to maximize retrieval relevance "
            "from a vector database of disaster SOPs. Consider synonyms, related hazards, and escalation scenarios. "
            "Output ONLY a JSON object."
        )
        super().__init__(name="RetrievalAgent", system_message=system_message, llm_config=llm_config, use_json_mode=True)

    def reformulate_query(self, metadata: Dict[str, Any], normalized_text: str) -> Dict[str, Any]:
        """
        Reformulates the incident into 3 targeted search queries.
        
        Args:
            metadata (Dict): Extracted metadata.
            normalized_text (str): The normalized incident text.
            
        Returns:
            Dict: A dictionary containing the reformulated queries.
        """
        prompt = (
            f"Given this incident: {normalized_text}\n"
            f"Metadata: hazard={metadata.get('hazard_type')}, urgency={metadata.get('urgency')}, "
            f"location={metadata.get('location_description')}\n"
            "Reformulate 3 search queries that will retrieve the most relevant disaster SOPs.\n"
            "Query 1: Direct match on hazard type\n"
            "Query 2: Broader hazard category (e.g., 'building collapse' for earthquake)\n"
            "Query 3: Escalation scenario (e.g., 'mass casualty' for high-urgency medical)\n"
            "Output JSON ONLY with this exact format:\n"
            '{"queries": [{"query": "string", "hazard_filter": "string", "rationale": "string"}]}'
        )
        
        required_keys = ["queries"]
        parsed = self._send_json_prompt(prompt, required_keys)
        
        if "error" not in parsed:
            self.log_action("reformulate_query", {"hazard_type": metadata.get("hazard_type")}, {"query_count": len(parsed.get("queries", []))})
            return parsed
            
        # Fallback if LLM fails
        fallback = {
            "queries": [
                {"query": normalized_text, "hazard_filter": metadata.get("hazard_type", "unknown"), "rationale": "Fallback direct query"}
            ],
            "error": "parse_failed"
        }
        self.log_action("reformulate_query_failed", {"normalized_text": normalized_text}, fallback)
        return fallback

    def retrieve_sops(self, queries: List[Dict[str, Any]], kb: SOPKnowledgeBase) -> List[Dict[str, Any]]:
        """
        Executes reformulated queries against the KB and aggregates unique results.
        
        Args:
            queries (List[Dict]): The reformulated queries.
            kb (SOPKnowledgeBase): The ChromaDB knowledge base instance.
            
        Returns:
            List[Dict]: The top 5 unique retrieved SOPs.
        """
        unique_sops = {}
        
        for q in queries:
            hazard = q.get("hazard_filter", "unknown")
            text = q.get("query", "")
            
            # Execute query on the KB
            results = kb.query(hazard_type=hazard, query_text=text, top_k=2)
            
            for res in results:
                sop_id = res["id"]
                # Keep the instance with the lowest (best) distance
                if sop_id not in unique_sops or res.get("distance", 999.0) < unique_sops[sop_id].get("distance", 999.0):
                    unique_sops[sop_id] = res
                    
        # Sort by distance (ascending) and take top 5
        sorted_sops = sorted(unique_sops.values(), key=lambda x: x.get("distance", 999.0))
        top_sops = sorted_sops[:5]
        
        self.log_action("retrieve_sops", {"total_queries": len(queries)}, {"retrieved_unique": len(top_sops)})
        return top_sops

# Test Case 1: Fire
# input_metadata = {"hazard_type": "fire", "urgency": "critical", "location_description": "Building 7"}
# output = {"queries": [{"query": "Building fire critical", ...}, ...]}

# Test Case 2: Medical
# input_metadata = {"hazard_type": "medical", "urgency": "high", "location_description": "Downtown"}
# output = {"queries": [{"query": "Mass casualty downtown", ...}, ...]}
