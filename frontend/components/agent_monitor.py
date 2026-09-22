import streamlit as st
import pandas as pd
from typing import List, Dict, Any

def render_agent_monitor(agent_logs: List[Dict[str, Any]]) -> None:
    if not agent_logs:
        st.info('No agent activity recorded yet.')
        return
        
    active_agents = len(set(log['agent'] for log in agent_logs if log.get('status') == 'running'))
    completed = len([log for log in agent_logs if log.get('status') == 'completed'])
    errors = len([log for log in agent_logs if log.get('status') == 'error'])
    
    st.markdown(f'**Active agents: {active_agents} &nbsp;|&nbsp; Completed: {completed} &nbsp;|&nbsp; Errors: {errors}**')
    
    # Terminal-style output
    terminal_html = '<div style="background-color: #0f172a; color: #10b981; font-family: \'JetBrains Mono\', monospace; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 300px; overflow-y: auto; font-size: 0.85rem; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">'
    for log in reversed(agent_logs):
        time_str = log.get('timestamp', '')[:19].replace('T', ' ')
        agent_name = log.get('agent', 'SYSTEM').upper()
        status = log.get('status', 'INFO').upper()
        task = log.get('task', '')
        
        color = "#10b981" if status == "COMPLETED" else "#f59e0b" if status == "RUNNING" else "#ef4444"
        
        terminal_html += f'<div style="margin-bottom: 6px;"><span style="color:#64748b;">[{time_str}]</span> <span style="color:{color}; font-weight:bold;">[{agent_name}]</span> {task} <span style="color:#64748b; font-size:0.75rem;">({log.get("duration_ms", 0)}ms)</span></div>'
    
    terminal_html += '</div>'
    st.markdown(terminal_html, unsafe_allow_html=True)

def render_agent_flow_diagram(current_agent: str) -> None:
    pass

def get_mock_agent_logs() -> List[Dict[str, Any]]:
    from datetime import datetime, timedelta
    now = datetime.now()
    return [
        {'agent': 'IntakeAgent', 'status': 'completed', 'task': 'Parsed raw 911 text', 'timestamp': (now - timedelta(minutes=5)).isoformat(), 'duration_ms': 120},
        {'agent': 'MetadataAgent', 'status': 'completed', 'task': 'Extracted hazard: flood', 'timestamp': (now - timedelta(minutes=4)).isoformat(), 'duration_ms': 300},
        {'agent': 'PlannerAgent', 'status': 'completed', 'task': 'Generated tactical plan', 'timestamp': (now - timedelta(minutes=3)).isoformat(), 'duration_ms': 4500},
        {'agent': 'RouterAgent', 'status': 'running', 'task': 'Solving VRP for 5 locations', 'timestamp': now.isoformat(), 'duration_ms': 0},
    ]
