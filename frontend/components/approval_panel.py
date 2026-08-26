"""
Approval Panel Component for human-in-the-loop decisions.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
from src.utils.dashboard_utils import format_timestamp

def render_approval_panel(orchestrator_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Render the approval panel for pending routing plans."""
    pending_plans = orchestrator_state.get('pending_approvals', [])
    
    if not pending_plans:
        st.success('[OK] No pending decisions. All systems automated.')
        return None
        
    st.warning(f'[ALERT] {len(pending_plans)} plan(s) awaiting approval.')
    
    plan = pending_plans[0]
    plan_id = plan.get('plan_id', 'UNKNOWN')
    
    with st.expander(f'Review Plan: {plan_id}', expanded=True):
        st.write(f"**Generated:** {format_timestamp(plan.get('timestamp', ''))}")
        st.write(f"**Incident:** {plan.get('incident_details', 'Unknown severity/location')}")
        st.write(f"**Proposed Routes:** {plan.get('proposed_routes', 'N/A')}")
        
        reason = st.text_input('Rejection Reason (required if rejecting):', key=f'reason_{plan_id}')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button('APPROVE', type='primary', key=f'approve_{plan_id}'):
                return {'action': 'approved', 'plan_id': plan_id, 'timestamp': plan.get('timestamp')}
        with col2:
            if st.button('REJECT', key=f'reject_{plan_id}'):
                if not reason.strip():
                    st.error('Please provide a rejection reason.')
                else:
                    return {'action': 'rejected', 'plan_id': plan_id, 'timestamp': plan.get('timestamp'), 'reason': reason}
    return None

def render_decision_history(history: List[Dict[str, Any]]) -> None:
    """Render a table of past decisions."""
    if not history:
        st.info('No decisions recorded yet.')
        return
        
    approved = sum(1 for d in history if d.get('decision', '').lower() in ['approve', 'approved'])
    rejected = len(history) - approved
    
    st.write(f'**Total decisions: {len(history)} | Approved: {approved} | Rejected: {rejected}**')
    
    table_data = []
    for d in history:
        table_data.append({
            'Time': format_timestamp(d.get('decision_time', d.get('timestamp', ''))),
            'Plan ID': d.get('plan_id', 'N/A'),
            'Decision': d.get('decision', 'Unknown').upper(),
            'Reason': d.get('reason', '')
        })
    st.dataframe(table_data, use_container_width=True)
