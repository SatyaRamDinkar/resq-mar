import streamlit as st
from typing import List, Dict, Any
from src.agents.explainability_agent import ExplainabilityAgent

def render_explainability_panel(incident_id: str, decision_chain: List[Dict[str, Any]]) -> None:
    """
    Show incident timeline with decision nodes and confidence badges.
    
    Args:
        incident_id (str): The current incident ID.
        decision_chain (List[Dict]): The list of decision dicts from ExplainabilityAgent.
    """
    st.subheader(f"Decision Reasoning Trace (Incident: {incident_id})")
    
    if not decision_chain:
        st.info("No decisions logged for this incident yet.")
        return
        
    for idx, d in enumerate(decision_chain):
        conf = d.get("confidence", 0.0)
        if conf >= 0.8:
            color = "green"
            label = "High Confidence"
        elif conf >= 0.6:
            color = "orange"
            label = "Medium Confidence"
        else:
            color = "red"
            label = "Low Confidence - REVIEW REQUIRED"
            
        with st.expander(f"[{d.get('agent')}] {d.get('type', 'Decision').upper()} - {label} ({conf:.2f})"):
            st.write(f"**Decision:** {d.get('outputs', {}).get('decision', 'N/A')}")
            st.write(f"**Reasoning:** {d.get('reasoning', 'No reasoning provided.')}")
            st.caption(f"Timestamp: {d.get('timestamp')}")

def render_decision_history(decisions: List[Dict[str, Any]]) -> None:
    """Render a chronological list of agent decisions."""
    st.markdown("### Agent Decision Trace")
    if not decisions:
        st.info("No decisions recorded yet.")
        return
        
    # Generate Mermaid Flowchart
    mermaid_code = "graph TD\n"
    for i, dec in enumerate(decisions):
        agent = dec.get("agent_name", "Agent").replace(" ", "")
        action = dec.get("action", "Action")
        # sanitize action for mermaid
        action = action.replace('"', '').replace("'", "")
        mermaid_code += f"    Node{i}[{agent}] -->|{action}| Node{i+1}[Outcome]\n"
    
    st.markdown(f"```mermaid\n{mermaid_code}\n```")

def render_confidence_chart(decisions: List[Dict[str, Any]]) -> None:
    """
    Render a bar chart of confidence scores across agents.
    
    Args:
        decisions (List[Dict]): The decision chain.
    """
    if not decisions:
        return
        
    import pandas as pd
    
    data = []
    for d in decisions:
        data.append({
            "Agent": d.get("agent", "Unknown"),
            "Confidence": d.get("confidence", 0.0)
        })
        
    df = pd.DataFrame(data)
    if not df.empty:
        st.write("**Confidence Trends by Agent**")
        st.bar_chart(df.set_index("Agent"))
        
        low_conf = df[df["Confidence"] < 0.7]
        if not low_conf.empty:
            st.error(f"Warning: {len(low_conf)} decision(s) fell below the 0.7 confidence safety threshold.")

def render_rag_explanation(explanation: Dict[str, Any]) -> None:
    """
    Show why a specific SOP was chosen during retrieval.
    
    Args:
        explanation (Dict): Output from ExplainabilityAgent.explain_rag_decision.
    """
    st.markdown("#### RAG Protocol Selection")
    st.write(f"**Final SOP Chosen:** {explanation.get('final_sop')}")
    st.info(f"**Reasoning:** {explanation.get('reasoning')}")
    
    if explanation.get("re_retrieval_triggered"):
        st.warning("[WARNING] This decision required re-retrieval or Web Search Fallback due to insufficient initial context.")
        
    cands = explanation.get("candidates", [])
    if cands:
        st.write("**Candidate Scores:**")
        import pandas as pd
        df = pd.DataFrame(cands)
        st.dataframe(df)

def render_routing_explanation(explanation: Dict[str, Any]) -> None:
    """
    Show vehicle assignments with explicit explanations.
    
    Args:
        explanation (Dict): Output from ExplainabilityAgent.explain_routing_decision.
    """
    st.markdown("#### Routing Assignments")
    for exp in explanation.get("explanations", []):
        st.success(f"**{exp.get('vehicle')}**: {exp.get('reason')}")

def render_counterfactual_panel(incident: Dict[str, Any], explainability_agent: ExplainabilityAgent) -> None:
    """
    Interactive 'what-if' counterfactual generator.
    
    Args:
        incident (dict): The original incident.
        explainability_agent (ExplainabilityAgent): The initialized agent.
    """
    st.markdown("### Counterfactual Analysis (What-If)")
    
    new_severity = st.selectbox(
        "What if severity was...", 
        options=["low", "medium", "high", "critical"], 
        index=3 if incident.get("severity") == "critical" else 1
    )
    
    if new_severity != incident.get("severity"):
        counter = explainability_agent.generate_counterfactual(incident, "severity", new_severity)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Original Allocation", counter.get("original_allocation", 0))
        with col2:
            st.metric("New Allocation", counter.get("new_allocation", 0), 
                      delta=counter.get("new_allocation", 0) - counter.get("original_allocation", 0))
            
        st.info(counter.get("explanation", ""))

def render_audit_trail_download(incident_id: str, audit_text: str) -> None:
    """
    Provide a downloadable ASCII text file of the full audit trail.
    
    Args:
        incident_id (str): Incident ID.
        audit_text (str): Pre-generated ASCII text from ExplainabilityAgent.
    """
    if audit_text and audit_text != "No decisions found for this incident.":
        st.download_button(
            label="[DOWNLOAD] Download Official Audit Trail",
            data=audit_text,
            file_name=f"audit_{incident_id}.txt",
            mime="text/plain"
        )
