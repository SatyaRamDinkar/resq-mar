"""
ResQ-MAR Enhanced Command Dashboard
====================================
Redesigned with a professional emergency-ops dark theme,
glassmorphism cards, gradient accents, and polished UX.
"""
import streamlit as st
import time
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
import atexit
def _cleanup_temp_files():
    import os
    import streamlit as st
    for f in st.session_state.get("temp_files", []):
        try: os.unlink(f)
        except: pass
atexit.register(_cleanup_temp_files)

if "temp_files" not in st.session_state:
    st.session_state.temp_files = []


from dotenv import load_dotenv
load_dotenv()

from src.agents.dashboard_agent import DashboardAgent
from frontend.components.approval_panel import render_approval_panel, render_decision_history
from frontend.components.agent_monitor import render_agent_monitor, render_agent_flow_diagram, get_mock_agent_logs
from frontend.components.heatmap_view import render_incident_heatmap, render_coverage_stats, get_mock_incidents, get_mock_resources, HAS_ST_FOLIUM
from frontend.components.metrics_panel import render_performance_metrics, render_benchmark_chart, render_routing_efficiency_chart, get_mock_metrics, get_mock_benchmark_data

st.set_page_config(
    page_title='ResQ-MAR | AI Command Center',
    page_icon=':rotating_light:',
    layout='wide',
    initial_sidebar_state='expanded'
)

# =============================================================================
# MASTER CSS THEME
# =============================================================================
st.markdown("""
<style>
    /* --- Import Professional Font --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

    /* --- Root Variables --- */
    :root {
        --bg-primary: #0a0e1a;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --border-glass: rgba(255, 255, 255, 0.08);
        --accent-red: #ef4444;
        --accent-blue: #3b82f6;
        --accent-green: #22c55e;
        --accent-amber: #f59e0b;
        --accent-purple: #a855f7;
        --accent-cyan: #06b6d4;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --gradient-red: linear-gradient(135deg, #ef4444, #dc2626);
        --gradient-blue: linear-gradient(135deg, #3b82f6, #2563eb);
        --gradient-green: linear-gradient(135deg, #22c55e, #16a34a);
        --gradient-amber: linear-gradient(135deg, #f59e0b, #d97706);
        --gradient-purple: linear-gradient(135deg, #a855f7, #7c3aed);
        --gradient-header: linear-gradient(135deg, #1e3a5f 0%, #0f172a 50%, #1a0a2e 100%);
    }

    /* --- Global Styles --- */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp > header { background: transparent !important; }

    /* --- Sidebar --- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
    }
    section[data-testid="stSidebar"] .stRadio label span {
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }

    /* --- Main Content --- */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    /* --- Metric Cards --- */
    div[data-testid="stMetric"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        backdrop-filter: blur(10px) !important;
        transition: transform 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
    }
    div[data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }

    /* --- Buttons --- */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
    }

    /* --- Expanders --- */
    details[data-testid="stExpander"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    details[data-testid="stExpander"] summary {
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    /* --- DataFrames --- */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* --- Tab Container --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px !important;
        padding: 8px 20px !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(59,130,246,0.2), rgba(168,85,247,0.2)) !important;
        border-color: rgba(59, 130, 246, 0.4) !important;
        color: white !important;
    }

    /* --- Alerts --- */
    .stAlert {
        border-radius: 10px !important;
        border: none !important;
    }

    /* --- Download Button --- */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #22c55e, #16a34a) !important;
        box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3) !important;
    }

    /* --- File Uploader --- */
    section[data-testid="stFileUploader"] {
        border: 2px dashed var(--border-glass) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* --- Selectbox / Input --- */
    .stSelectbox > div > div,
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-glass) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: 10px !important;
        color: var(--text-primary) !important;
    }

    /* --- Custom Classes --- */
    .hero-header {
        background: var(--gradient-header);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0; right: 0;
        width: 300px; height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
        border-radius: 50%;
        transform: translate(30%, -50%);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f1f5f9, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        color: var(--text-muted);
        font-size: 0.95rem;
        font-weight: 400;
        margin: 0;
    }

    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-online { background: rgba(34,197,94,0.15); color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
    .badge-critical { background: rgba(239,68,68,0.15); color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }
    .badge-warning { background: rgba(245,158,11,0.15); color: #f59e0b; border: 1px solid rgba(245,158,11,0.3); }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, var(--accent-blue), var(--accent-purple), transparent) 1;
    }

    .glass-card {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(10px);
        margin-bottom: 16px;
    }

    .stat-row {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 0;
        border-bottom: 1px solid var(--border-glass);
    }
    .stat-label { color: var(--text-secondary); font-size: 0.85rem; flex: 1; }
    .stat-value { color: var(--text-primary); font-weight: 600; font-size: 0.95rem; }

    .pipeline-step {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 2px;
    }
    .step-active {
        background: linear-gradient(135deg, rgba(59,130,246,0.3), rgba(168,85,247,0.3));
        border: 1px solid rgba(59,130,246,0.5);
        color: white;
        animation: pulse-glow 2s ease-in-out infinite;
    }
    .step-idle {
        background: var(--bg-glass);
        border: 1px solid var(--border-glass);
        color: var(--text-secondary);
    }
    .step-arrow { color: var(--text-muted); font-size: 1rem; margin: 0 2px; }

    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 5px rgba(59,130,246,0.2); }
        50% { box-shadow: 0 0 20px rgba(59,130,246,0.4); }
    }

    .live-dot {
        display: inline-block;
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #22c55e;
        margin-right: 6px;
        animation: blink 1.5s ease-in-out infinite;
    }
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* --- Scrollbar --- */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border-glass); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

    /* --- Hide Streamlit Branding --- */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SESSION STATE
# =============================================================================
if 'dash_agent' not in st.session_state:
    st.session_state.dash_agent = DashboardAgent()
    st.session_state.dash_agent.metrics = get_mock_metrics()
    st.session_state.dash_agent.agent_logs = get_mock_agent_logs()
    st.session_state.dash_agent.pending_approvals.append({
        'plan_id': 'PLAN-AP-20260922-001',
        'incident_details': 'Critical Flood - Visakhapatnam Beach Road',
        'proposed_routes': 'Rescue Unit 1 -> Beach Road (ETA 8m)',
        'timestamp': datetime.now().isoformat()
    })

agent = st.session_state.dash_agent

# =============================================================================
# SIDEBAR NAVIGATION
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 16px 0 8px 0;">
        <div style="font-size: 2rem; font-weight: 900; 
                    background: linear-gradient(135deg, #3b82f6, #a855f7);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            ResQ-MAR
        </div>
        <div style="color: #64748b; font-size: 0.75rem; font-weight: 600; 
                    text-transform: uppercase; letter-spacing: 0.15em;">
            AI Command Center
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    page = st.radio(
        'Navigation',
        [
            'Command Center',
            'Incident Heatmap',
            'Human Approval',
            'Agent Pipeline',
            'Performance',
            'XAI Dashboard'
        ],
        label_visibility='collapsed'
    )

    st.markdown("---")

    # System Status Panel
    st.markdown('<div class="section-header" style="font-size:1rem;">System Status</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 8px 0;">
</div>
""", unsafe_allow_html=True)

    # --- Live System Health Checks ---
    import requests as _req

    def _check_service(url, timeout=2):
        try:
            _req.get(url, timeout=timeout)
            return True
        except Exception:
            return False

    _ollama_ok = _check_service("http://127.0.0.1:11434/api/tags")
    _osrm_ok   = _check_service("http://127.0.0.1:5000/")
    _chroma_ok = True

    def _badge(ok):
        return '<span class="status-badge badge-online">ONLINE</span>' if ok else '<span class="status-badge badge-critical">OFFLINE</span>'

    def _dot(ok):
        color = "#22c55e" if ok else "#ef4444"
        return f'<span class="live-dot" style="background:{color};"></span>'

    st.markdown(f"""
    <div style="padding: 8px 0;">
      <div class="stat-row"><span class="stat-label">{_dot(_ollama_ok)}Ollama LLM</span>{_badge(_ollama_ok)}</div>
      <div class="stat-row"><span class="stat-label">{_dot(_chroma_ok)}ChromaDB</span>{_badge(_chroma_ok)}</div>
      <div class="stat-row"><span class="stat-label">{_dot(_osrm_ok)}OSRM Router</span>{_badge(_osrm_ok)}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    auto_refresh = st.checkbox('Auto-Refresh (5s)', value=False)
    st.caption(f"Session: {datetime.now().strftime('%H:%M:%S')}")


# =============================================================================
# PAGE: COMMAND CENTER
# =============================================================================
if page == 'Command Center':
    # Hero Header
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Live Command Center</p>
        <p class="hero-subtitle">Multi-Agent Emergency Response Orchestration -- Andhra Pradesh, India</p>
    </div>
    """, unsafe_allow_html=True)

    # Alert Banner
    if len(agent.pending_approvals) > 0:
        st.error('**[ACTION REQUIRED]** A routing plan is awaiting human approval. Navigate to the Human Approval panel.')

    # --- KPI Row ---
    summary = agent.get_status_summary()
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric('Active Incidents', len(get_mock_incidents()))
    with k2:
        st.metric('Pending Approvals', summary['pending_approval_count'])
    with k3:
        st.metric('System Health', summary['system_health'].upper())
    with k4:
        st.metric('Active Agent', summary['active_agent'].upper())

    st.markdown("")

    # --- Agent Pipeline Visualization ---
    st.markdown('<div class="section-header">Agent Pipeline Status</div>', unsafe_allow_html=True)
    
    pipeline_stages = ['Intake', 'Metadata', 'RAG Retrieval', 'Assessor', 'Planner', 'Router', 'Comms']
    active_stage = summary.get('active_agent', '').lower()
    
    pipeline_html = '<div style="display:flex; flex-wrap:wrap; align-items:center; gap:4px; padding:12px 0;">'
    for i, stage in enumerate(pipeline_stages):
        is_active = stage.lower().replace(' ', '') in active_stage.replace(' ', '') or (stage == 'RAG Retrieval' and 'rag' in active_stage)
        cls = 'step-active' if is_active else 'step-idle'
        pipeline_html += f'<span class="pipeline-step {cls}">{stage}</span>'
        if i < len(pipeline_stages) - 1:
            pipeline_html += '<span class="step-arrow">&#8594;</span>'
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)

    st.markdown("")

    # --- Active Incidents Table ---
    tab_incidents, tab_voice, tab_vision = st.tabs([
        "Active Incidents",
        "Voice Intake (Whisper)",
        "Vision Assessment"
    ])

    with tab_incidents:
        incidents = get_mock_incidents()
        if incidents:
            import pandas as pd
            df = pd.DataFrame(incidents)
            df.columns = [c.replace('_', ' ').title() for c in df.columns]
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        if st.button('Simulate New Incident'):
            agent.log_agent_activity('IntakeAgent', 'completed', 'Simulated incident')
            st.success('[OK] Simulated incident processed successfully.')

    with tab_voice:
        st.markdown('<div class="section-header">Emergency Voice Intake</div>', unsafe_allow_html=True)
        st.caption("Upload an emergency call recording or record live. Whisper AI will transcribe and extract metadata automatically.")
        
        from frontend.components.voice_input import render_voice_uploader, render_microphone_input, render_transcription_result
        
        vc1, vc2 = st.columns(2)
        with vc1:
            audio_file_path = render_voice_uploader()
        with vc2:
            mic_audio_path = render_microphone_input()

        active_audio_path = audio_file_path or mic_audio_path

        if active_audio_path:
            if 'voice_intake' not in st.session_state:
                with st.spinner("Loading Whisper AI model (Base)..."):
                    from src.agents.voice_intake import VoiceIntake
                    st.session_state.voice_intake = VoiceIntake(model_size="base")

            v_intake = st.session_state.voice_intake
            if hasattr(v_intake, 'model') and v_intake.model:
                with st.spinner("Transcribing audio..."):
                    result = v_intake.process_voice_emergency(active_audio_path)
                render_transcription_result(result)
            else:
                st.error("Whisper model is not available. Please install `openai-whisper` and `ffmpeg`.")

    with tab_vision:
        st.markdown('<div class="section-header">Visual Damage Assessment</div>', unsafe_allow_html=True)
        st.caption("Upload a disaster photo for AI-powered structural damage analysis and severity classification.")
        
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
                st.error("Vision AI disabled. Please configure GEMINI_API_KEY.")


# =============================================================================
# PAGE: INCIDENT HEATMAP
# =============================================================================
elif page == 'Incident Heatmap':
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Incident Heatmap</p>
        <p class="hero-subtitle">Real-time geospatial visualization of active incidents and resource deployment across Andhra Pradesh</p>
    </div>
    """, unsafe_allow_html=True)

    incidents = get_mock_incidents()
    resources = get_mock_resources()

    render_coverage_stats(incidents, resources)
    
    st.markdown("")
    m = render_incident_heatmap(incidents, resources)

    if HAS_ST_FOLIUM:
        from streamlit_folium import st_folium
        st_folium(m, width=None, height=550, use_container_width=True, returned_objects=[])
    else:
        import streamlit.components.v1 as components
        components.html(m._repr_html_(), height=550)


# =============================================================================
# PAGE: HUMAN APPROVAL
# =============================================================================
elif page == 'Human Approval':
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Human-in-the-Loop Approval</p>
        <p class="hero-subtitle">Review, approve, or reject AI-proposed emergency routing plans before execution</p>
    </div>
    """, unsafe_allow_html=True)

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

    st.markdown("")
    st.markdown('<div class="section-header">Decision History</div>', unsafe_allow_html=True)
    all_decisions = agent.approved_plans + agent.rejected_plans
    render_decision_history(all_decisions)


# =============================================================================
# PAGE: AGENT PIPELINE
# =============================================================================
elif page == 'Agent Pipeline':
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Agent Pipeline Monitor</p>
        <p class="hero-subtitle">Real-time execution traces of all 10+ autonomous agents in the ResQ-MAR swarm</p>
    </div>
    """, unsafe_allow_html=True)

    # Visual Pipeline
    summary = agent.get_status_summary()
    
    pipeline_stages = ['Intake', 'Metadata', 'RAG Retrieval', 'Assessor', 'Web Search', 'Live Awareness', 'Planner', 'Router', 'Vision', 'XAI', 'Comms']
    active_stage = summary.get('active_agent', '').lower()
    
    pipeline_html = '<div style="display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:16px; background:rgba(255,255,255,0.02); border-radius:12px; border:1px solid rgba(255,255,255,0.06);">'
    for i, stage in enumerate(pipeline_stages):
        is_active = stage.lower().replace(' ', '') in active_stage.replace(' ', '')
        cls = 'step-active' if is_active else 'step-idle'
        pipeline_html += f'<span class="pipeline-step {cls}">{stage}</span>'
        if i < len(pipeline_stages) - 1:
            pipeline_html += '<span class="step-arrow">&#8594;</span>'
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)
    
    st.markdown("")
    
    st.markdown('<div class="section-header">📡 Live Agent Chatter (Backend Operations)</div>', unsafe_allow_html=True)
    render_agent_monitor(agent.agent_logs)


# =============================================================================
# PAGE: PERFORMANCE
# =============================================================================
elif page == 'Performance':
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Performance Analytics</p>
        <p class="hero-subtitle">System KPIs, RAG benchmark comparisons, and routing efficiency metrics</p>
    </div>
    """, unsafe_allow_html=True)

    render_performance_metrics(agent.metrics)
    
    st.markdown("")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">RAG Coverage Benchmark</div>', unsafe_allow_html=True)
        render_benchmark_chart(get_mock_benchmark_data())
    with c2:
        st.markdown('<div class="section-header">Routing Efficiency</div>', unsafe_allow_html=True)
        render_routing_efficiency_chart(
            {'solver_calls': 5, 'label': 'AET Adaptive'},
            {'solver_calls': 15, 'label': 'Continuous Re-route'}
        )

    st.markdown("")
    if st.button('Export Full System Report'):
        st.text_area('System Report', agent.export_report(), height=300)


# =============================================================================
# PAGE: XAI DASHBOARD
# =============================================================================
elif page == 'XAI Dashboard':
    st.markdown("""
    <div class="hero-header">
        <p class="hero-title">Explainable AI Dashboard</p>
        <p class="hero-subtitle">Transparent reasoning traces, confidence scoring, counterfactual analysis, and exportable audit trails</p>
    </div>
    """, unsafe_allow_html=True)

    from src.agents.explainability_agent import ExplainabilityAgent
    from frontend.components.explainability_panel import (
        render_explainability_panel, render_confidence_chart,
        render_rag_explanation, render_routing_explanation,
        render_counterfactual_panel, render_audit_trail_download
    )

    if 'xai_agent' not in st.session_state:
        st.session_state.xai_agent = ExplainabilityAgent()
    xai = st.session_state.xai_agent

    incident_id = "INC-AP-2026-001"
    decisions = xai.get_decision_chain(incident_id)

    if not decisions:
        xai.log_decision("IntakeAgent", "Classified as Critical Flood", "Keywords 'flood' and 'trapped' detected in Vizag report.", 0.95, {"text": "flood vizag"}, incident_id)
        xai.log_decision("RetrievalAgent", "Retrieved Flood SOP v3", "Matches hazard 'flood' with 0.91 relevance score.", 0.91, {"query": "flood"}, incident_id)
        xai.log_decision("AssessorAgent", "Approved SOP Coverage", "Coverage score 0.88. All safety constraints met.", 0.88, {"sops": 3}, incident_id)
        xai.log_decision("PlannerAgent", "Generated 4-step tactical plan", "Deployed rescue boats and evacuation teams.", 0.85, {"tasks": 4}, incident_id)
        xai.log_decision("RouterAgent", "Assigned Rescue Boat Alpha", "Distance is 3.1km via navigable waterway.", 0.82, {"available": ["Alpha", "Bravo"]}, incident_id)
        decisions = xai.get_decision_chain(incident_id)

    tab_trace, tab_rag, tab_counterfactual, tab_audit = st.tabs([
        "Decision Trace",
        "RAG Analysis",
        "What-If Scenarios",
        "Audit Trail"
    ])

    with tab_trace:
        col1, col2 = st.columns([3, 2])
        with col1:
            render_explainability_panel(incident_id, decisions)
        with col2:
            render_confidence_chart(decisions)

    with tab_rag:
        col1, col2 = st.columns(2)
        with col1:
            rag_exp = xai.explain_rag_decision(
                [{"id": "Flood SOP v3"}, {"id": "General Evacuation SOP"}, {"id": "Medical Triage SOP"}],
                [0.91, 0.62, 0.45],
                "Flood SOP v3", False
            )
            render_rag_explanation(rag_exp)
        with col2:
            route_exp = xai.explain_routing_decision({"tasks": [
                {"resource": "Rescue Boat Alpha", "distance_km": 3.1},
                {"resource": "Ambulance B", "distance_km": 5.8}
            ]})
            render_routing_explanation(route_exp)

    with tab_counterfactual:
        render_counterfactual_panel({"severity": "critical", "type": "flood"}, xai)

    with tab_audit:
        audit_text = xai.export_audit_trail(incident_id)
        if audit_text:
            st.code(audit_text, language="text")
        render_audit_trail_download(incident_id, audit_text)


# =============================================================================
# AUTO-REFRESH
# =============================================================================
if auto_refresh:
    time.sleep(5)
    st.rerun()
