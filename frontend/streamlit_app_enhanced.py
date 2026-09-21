"""
Enhanced Streamlit Dashboard for ResQ-MAR.
"""
import streamlit as st
import time
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.dashboard_agent import DashboardAgent
from frontend.components.approval_panel import render_approval_panel, render_decision_history
from frontend.components.agent_monitor import render_agent_monitor, render_agent_flow_diagram, get_mock_agent_logs
from frontend.components.heatmap_view import render_incident_heatmap, render_coverage_stats, get_mock_incidents, get_mock_resources, HAS_ST_FOLIUM
from frontend.components.metrics_panel import render_performance_metrics, render_benchmark_chart, render_routing_efficiency_chart, get_mock_metrics, get_mock_benchmark_data

st.set_page_config(page_title='ResQ-MAR Dashboard', page_icon=':hospital:', layout='wide')

st.markdown("""
<style>
    .reportview-container { background: #1a1a2e; color: white; }
    .stButton>button { background-color: #e94560; color: white; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

if 'dash_agent' not in st.session_state:
    st.session_state.dash_agent = DashboardAgent()
    st.session_state.dash_agent.metrics = get_mock_metrics()
    st.session_state.dash_agent.agent_logs = get_mock_agent_logs()
    st.session_state.dash_agent.pending_approvals.append({
        'plan_id': 'PLAN-20231010-1234',
        'incident_details': 'Critical Fire - Sector 7',
        'proposed_routes': 'T1 -> Sector 7 (ETA 5m)',
        'timestamp': '2023-10-10T10:00:00'
    })

agent = st.session_state.dash_agent

st.sidebar.title('ResQ-MAR Navigation')
page = st.sidebar.radio('Go to', ['Live Command Center', 'Incident Heatmap', 'Approval Panel', 'Agent Monitor', 'Performance Metrics', 'XAI Dashboard'])
auto_refresh = st.sidebar.checkbox('Auto-Refresh (5s)', value=False)

if page == 'Live Command Center':
    st.title('ResQ-MAR Command Center')
    st.write(f"Last Updated: {agent.get_status_summary()['last_update']}")
    
    if len(agent.pending_approvals) > 0:
        st.error('[ACTION REQUIRED] Routing plan awaiting human approval! Check Approval Panel.')
        
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader('Active Incidents')
        st.write(f"Count: {len(get_mock_incidents())}")
        st.dataframe(get_mock_incidents())
    with c2:
        st.subheader('Quick Stats')
        summary = agent.get_status_summary()
        st.metric('Pending Approvals', summary['pending_approval_count'])
        st.metric('System Health', summary['system_health'].upper())
        st.metric('Active Agent', summary['active_agent'].upper())
    with c3:
        st.subheader('Actions')
        if st.button('Simulate New Incident'):
            agent.log_agent_activity('IntakeAgent', 'completed', 'Simulated incident')
            st.success('[OK] Simulated incident processed.')
            
    st.markdown("---")
    st.subheader("Emergency Voice Intake (Whisper AI)")
    from frontend.components.voice_input import render_voice_uploader, render_microphone_input, render_transcription_result
    
    vc1, vc2 = st.columns(2)
    with vc1:
        audio_file_path = render_voice_uploader()
    with vc2:
        mic_audio_path = render_microphone_input()
        
    active_audio_path = audio_file_path or mic_audio_path
    
    if active_audio_path:
        # Initialize VoiceIntake globally if not present
        if 'voice_intake' not in st.session_state:
            with st.spinner("Loading Whisper AI model (Base)... This may take a minute on first run."):
                from src.agents.voice_intake import VoiceIntake
                st.session_state.voice_intake = VoiceIntake(model_size="base")
        
        v_intake = st.session_state.voice_intake
        if hasattr(v_intake, 'model') and v_intake.model:
            with st.spinner("Transcribing audio..."):
                result = v_intake.process_voice_emergency(active_audio_path)
            render_transcription_result(result)
        else:
            st.error("Whisper model is not available. Please ensure `openai-whisper` and `ffmpeg` are installed.")

    st.markdown("---")
    st.subheader("Visual Damage Assessment")
    from frontend.components.vision_input import render_vision_uploader, render_vision_result
    
    image_path = render_vision_uploader()
    
    if image_path:
        if 'vision_agent' not in st.session_state:
            with st.spinner("Initializing VisionAgent..."):
                from src.agents.vision_agent import VisionAgent
                st.session_state.vision_agent = VisionAgent()
                
        v_agent = st.session_state.vision_agent
        if v_agent.enabled:
            with st.spinner("AI analyzing structural damage and severity..."):
                v_result = v_agent.analyze_damage(image_path)
            render_vision_result(v_result)
        else:
            st.error("Vision AI disabled. Please configure GEMINI_API_KEY and install Pillow.")
            
elif page == 'Incident Heatmap':
    st.title('Incident Heatmap')
    incidents = get_mock_incidents()
    resources = get_mock_resources()
    
    render_coverage_stats(incidents, resources)
    m = render_incident_heatmap(incidents, resources)
    
    if HAS_ST_FOLIUM:
        from streamlit_folium import st_folium
        st_folium(m, width=1200, height=600)
    else:
        import streamlit.components.v1 as components
        components.html(m._repr_html_(), height=600)
        
elif page == 'Approval Panel':
    st.title('Approval Panel')
    
    action = render_approval_panel({'pending_approvals': agent.pending_approvals})
    if action:
        if action['action'] == 'approved':
            agent.process_approval(action['plan_id'], 'approve')
            st.success(f"[OK] Executing approved plan: {action['plan_id']}")
        elif action['action'] == 'rejected':
            agent.process_approval(action['plan_id'], 'reject', action.get('reason', ''))
            st.warning(f"[REJECTED] Plan {action['plan_id']} rejected.")
        time.sleep(1)
        st.rerun()
        
    st.markdown('---')
    st.subheader('Decision History')
    all_decisions = agent.approved_plans + agent.rejected_plans
    render_decision_history(all_decisions)

elif page == 'Agent Monitor':
    st.title('Live Agent Monitor')
    
    summary = agent.get_status_summary()
    render_agent_flow_diagram(summary['active_agent'])
    st.markdown('---')
    render_agent_monitor(agent.agent_logs)

elif page == 'Performance Metrics':
    st.title('Performance Metrics')
    
    render_performance_metrics(agent.metrics)
    st.markdown('---')
    c1, c2 = st.columns(2)
    with c1:
        render_benchmark_chart(get_mock_benchmark_data())
    with c2:
        render_routing_efficiency_chart(
            {'solver_calls': 5, 'label': 'AET Adaptive'},
            {'solver_calls': 15, 'label': 'Continuous Re-route'}
        )
        
    if st.button('Export Report'):
        st.text_area('System Report', agent.export_report(), height=300)

elif page == 'XAI Dashboard':
    st.title('XAI (Explainable AI) Dashboard')
    st.markdown("Transparent reasoning, confidence scoring, and audit trails.")
    
    from src.agents.explainability_agent import ExplainabilityAgent
    from frontend.components.explainability_panel import (
        render_explainability_panel, render_confidence_chart, 
        render_rag_explanation, render_routing_explanation, 
        render_counterfactual_panel, render_audit_trail_download
    )
    
    if 'xai_agent' not in st.session_state:
        st.session_state.xai_agent = ExplainabilityAgent()
    xai = st.session_state.xai_agent
    
    # Mock data for demonstration if logs are empty
    incident_id = "INC-2023-999"
    decisions = xai.get_decision_chain(incident_id)
    
    if not decisions:
        # Generate some mock decisions for the demo
        xai.log_decision("IntakeAgent", "Classified as Critical Fire", "Keywords 'fire' and 'trapped' detected.", 0.95, {"text": "fire"}, incident_id)
        xai.log_decision("RetrievalAgent", "Retrieved Fire SOP v2", "Matches hazard 'fire' with 0.89 relevance.", 0.89, {"query": "fire"}, incident_id)
        xai.log_decision("RouterAgent", "Assigned Fire Truck B", "Distance is 2.1km (closest).", 0.92, {"available": ["B", "C"]}, incident_id)
        xai.log_decision("AssessorAgent", "Approved Plan", "All safety constraints met.", 0.88, {"plan": "T"}, incident_id)
        decisions = xai.get_decision_chain(incident_id)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_explainability_panel(incident_id, decisions)
        
        st.markdown("---")
        render_counterfactual_panel({"severity": "critical", "type": "fire"}, xai)
        
    with col2:
        render_confidence_chart(decisions)
        
        st.markdown("---")
        rag_exp = xai.explain_rag_decision([{"id": "Fire SOP v2"}, {"id": "General SOP"}], [0.89, 0.45], "Fire SOP v2", False)
        render_rag_explanation(rag_exp)
        
        st.markdown("---")
        route_exp = xai.explain_routing_decision({"tasks": [{"resource": "Fire Truck B", "distance_km": 2.1}]})
        render_routing_explanation(route_exp)
        
        st.markdown("---")
        audit_text = xai.export_audit_trail(incident_id)
        render_audit_trail_download(incident_id, audit_text)

if auto_refresh:
    time.sleep(5)
    st.rerun()
