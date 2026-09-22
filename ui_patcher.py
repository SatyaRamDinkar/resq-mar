import os
import re

ROOT = "d:/Projects & Internships/resq-mar"

def patch_file(rel_path, replacements):
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        if isinstance(old, re.Pattern):
            content = old.sub(new, content)
        else:
            content = content.replace(old, new)
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {rel_path}")

# 1. Update Metrics Panel (st.bar_chart -> plotly)
metrics_content = """import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, Any

def render_performance_metrics(metrics: Dict[str, Any]) -> None:
    st.subheader('System Performance')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Avg Response Time', f"{metrics.get('avg_response_time_ms', 0)} ms", '-15%')
    c2.metric('Total Incidents Handled', metrics.get('total_incidents_handled', 0))
    c3.metric('Incidents Today', metrics.get('incidents_today', 0), '+2')
    c4.metric('Solver Calls Saved', metrics.get('solver_calls_saved', 0), 'AET enabled')
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric('Coverage %', f"{metrics.get('coverage_percentage', 100):.1f}%")
    c6.metric('Route Quality (0-1)', f"{metrics.get('avg_route_quality', 1.0):.2f}")
    c7.metric('Human Decisions Req', metrics.get('human_decisions_required', 0))
    c8.metric('Human Decisions Made', metrics.get('human_decisions_made', 0))

def render_benchmark_chart(benchmark_data: Dict[str, Any]) -> None:
    st.subheader('RAG Coverage Benchmark')
    df = pd.DataFrame({
        'Stage': benchmark_data.get('labels', []),
        'Naive RAG': benchmark_data.get('naive_rag_coverage', []),
        'Agentic RAG': benchmark_data.get('agentic_rag_coverage', [])
    })
    df_melted = df.melt(id_vars='Stage', var_name='Method', value_name='Coverage')
    fig = px.bar(df_melted, x='Stage', y='Coverage', color='Method', barmode='group', template='plotly_dark',
                 color_discrete_sequence=['#3b82f6', '#10b981'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

def render_routing_efficiency_chart(aet_data: Dict[str, Any], continuous_data: Dict[str, Any]) -> None:
    st.subheader('Routing Efficiency (Solver Calls)')
    df = pd.DataFrame({
        'Strategy': [aet_data.get('label', 'AET'), continuous_data.get('label', 'Continuous')],
        'Solver Calls': [aet_data.get('solver_calls', 0), continuous_data.get('solver_calls', 0)]
    })
    fig = px.bar(df, x='Strategy', y='Solver Calls', color='Strategy', template='plotly_dark',
                 color_discrete_sequence=['#10b981', '#ef4444'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

def get_mock_metrics() -> Dict[str, Any]:
    return {
        'avg_response_time_ms': 1250, 'total_incidents_handled': 142,
        'incidents_today': 12, 'solver_calls_saved': 45,
        'coverage_percentage': 96.5, 'avg_route_quality': 0.92,
        'human_decisions_required': 8, 'human_decisions_made': 8
    }

def get_mock_benchmark_data() -> Dict[str, Any]:
    return {
        'naive_rag_coverage': [0.4, 0.5, 0.45, 0.55, 0.42],
        'agentic_rag_coverage': [0.85, 0.9, 0.88, 0.92, 0.86],
        'labels': ['S1', 'S2', 'S3', 'S4', 'S5']
    }
"""
with open(os.path.join(ROOT, "frontend/components/metrics_panel.py"), "w", encoding="utf-8") as f:
    f.write(metrics_content)
print("Updated metrics_panel.py")

# 2. Update Agent Monitor (st.dataframe -> Terminal logs)
monitor_content = """import streamlit as st
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
    terminal_html = '<div style="background-color: #0f172a; color: #10b981; font-family: \\'JetBrains Mono\\', monospace; padding: 15px; border-radius: 8px; border: 1px solid #334155; height: 300px; overflow-y: auto; font-size: 0.85rem; box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);">'
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
"""
with open(os.path.join(ROOT, "frontend/components/agent_monitor.py"), "w", encoding="utf-8") as f:
    f.write(monitor_content)
print("Updated agent_monitor.py")

# 3. Explainability Panel (Mermaid Flowchart)
patch_file("frontend/components/explainability_panel.py", [
    ('def render_decision_history(decisions: List[Dict[str, Any]]) -> None:',
     '''def render_decision_history(decisions: List[Dict[str, Any]]) -> None:
    st.markdown("### Agent Decision Trace")
    if not decisions:
        st.info("No decisions recorded.")
        return
        
    # Generate Mermaid Flowchart
    mermaid_code = "graph TD\\n"
    for i, dec in enumerate(decisions):
        agent = dec.get("agent_name", "Agent").replace(" ", "")
        action = dec.get("action", "Action")
        mermaid_code += f"    Node{i}[{agent}] -->|{action}| Node{i+1}[Outcome]\\n"
    
    st.markdown(f"```mermaid\\n{mermaid_code}\\n```")
    
    for dec in decisions:'''),
])

# 4. streamlit_app_enhanced.py Replacements
patch_file("frontend/streamlit_app_enhanced.py", [
    # Auto-refresh logic
    ('auto_refresh = st.checkbox(\\'Auto-Refresh (5s)\\', value=False)',
     '''from streamlit_autorefresh import st_autorefresh
    auto_refresh = st.checkbox('Auto-Refresh (5s)', value=False)
    if auto_refresh:
        st_autorefresh(interval=5000, limit=None, key="dashboard_autorefresh")'''),
    
    # Remove old time.sleep auto-refresh block
    (re.compile(r'# AUTO-REFRESH.*?if auto_refresh:\s*time\.sleep\(5\)\s*st\.rerun\(\)', re.DOTALL), ''),
    
    # Notifications
    ('st.success(\\'[OK] Simulated incident processed successfully.\\')', "st.toast('[OK] Simulated incident processed successfully.', icon='✅')"),
    ('st.success(f"[OK] Executing approved plan: {action[\\'plan_id\\']}")', 'st.toast(f"[OK] Executing approved plan: {action[\\'plan_id\\']}", icon=\\'✅\\')'),
    ('st.warning(f"[REJECTED] Plan {action[\\'plan_id\\']} rejected.")', 'st.toast(f"[REJECTED] Plan {action[\\'plan_id\\']} rejected.", icon=\\'⚠️\\')'),
    
    # Spinners -> Status
    ('with st.spinner("Loading Whisper AI model (Base)..."):',
     'with st.status("Loading Whisper AI model (Base)...", expanded=True) as status:\\n                    status.update(label="Whisper AI Loaded", state="complete", expanded=False)'),
    ('with st.spinner("Transcribing audio..."):',
     'with st.status("Transcribing audio...", expanded=True) as status:\\n                    status.update(label="Transcription Complete", state="complete", expanded=False)'),
    ('with st.spinner("Initializing VisionAgent..."):',
     'with st.status("Initializing VisionAgent...", expanded=True) as status:\\n                    status.update(label="Vision AI Initialized", state="complete", expanded=False)'),
    ('with st.spinner("AI analyzing structural damage and severity..."):',
     'with st.status("AI analyzing structural damage and severity...", expanded=True) as status:\\n                    status.update(label="Analysis Complete", state="complete", expanded=False)'),
    
    # Pipeline overflow CSS
    ('<div style="display:flex; flex-wrap:wrap; align-items:center; gap:4px; padding:12px 0;">',
     '<div style="display:flex; align-items:center; gap:4px; padding:12px 0; overflow-x:auto; white-space:nowrap; padding-bottom:8px;">'),
    ('<div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:16px; background:rgba(255,255,255,0.02); border-radius:12px; border:1px solid rgba(255,255,255,0.06);">',
     '<div style="display:flex; align-items:center; gap:6px; padding:16px; background:rgba(255,255,255,0.02); border-radius:12px; border:1px solid rgba(255,255,255,0.06); overflow-x:auto; white-space:nowrap; padding-bottom:12px;">')
])
