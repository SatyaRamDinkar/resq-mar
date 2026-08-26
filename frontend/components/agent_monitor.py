"""
Agent Monitor Component for live activity tracking.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

def render_agent_monitor(agent_logs: List[Dict[str, Any]]) -> None:
    """Render the live agent activity table."""
    if not agent_logs:
        st.info('No agent activity recorded yet.')
        return
        
    active_agents = len(set(log['agent'] for log in agent_logs if log.get('status') == 'running'))
    completed = len([log for log in agent_logs if log.get('status') == 'completed'])
    errors = len([log for log in agent_logs if log.get('status') == 'error'])
    
    st.write(f'**Active agents: {active_agents} | Completed today: {completed} | Errors: {errors}**')
    
    df = pd.DataFrame(reversed(agent_logs))
    st.dataframe(df, use_container_width=True)

def render_agent_flow_diagram(current_agent: str) -> None:
    """Render a text-based pipeline diagram."""
    pipeline = ['Intake', 'Metadata', 'Planner', '[Retrieval + Assessor]', 'Router', 'Comms']
    
    flow_str = ''
    for step in pipeline:
        is_active = step.lower() in current_agent.lower() or (step == '[Retrieval + Assessor]' and 'rag' in current_agent.lower())
        if is_active:
            flow_str += f' >>> {step} <<< -> '
        else:
            flow_str += f' {step} -> '
            
    flow_str = flow_str.rstrip(' -> ')
    st.code(flow_str, language='text')

def get_mock_agent_logs() -> List[Dict[str, Any]]:
    """Return mock agent logs."""
    from datetime import datetime, timedelta
    now = datetime.now()
    return [
        {'agent': 'IntakeAgent', 'status': 'completed', 'task': 'Parsed raw 911 text', 'timestamp': (now - timedelta(minutes=5)).isoformat(), 'duration_ms': 120},
        {'agent': 'MetadataAgent', 'status': 'completed', 'task': 'Extracted hazard: flood', 'timestamp': (now - timedelta(minutes=4)).isoformat(), 'duration_ms': 300},
        {'agent': 'PlannerAgent', 'status': 'completed', 'task': 'Generated tactical plan', 'timestamp': (now - timedelta(minutes=3)).isoformat(), 'duration_ms': 4500},
        {'agent': 'RouterAgent', 'status': 'running', 'task': 'Solving VRP for 5 locations', 'timestamp': now.isoformat(), 'duration_ms': 0},
    ]
