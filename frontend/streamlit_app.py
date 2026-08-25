"""
ResQ-MAR Command Dashboard
==========================
Main Streamlit application for the ResQ-MAR multi-agent emergency response system.
Run with:  streamlit run frontend/streamlit_app.py

Dependencies: streamlit, folium, streamlit-folium, requests
All agent and RAG imports come from the existing src/ package.

IMPORTANT: All output text in this file is 100% ASCII.
           No Unicode, no emoji, no em-dashes, no box-drawing characters.
           Windows cp1252 safe.
"""
import os
import sys
import json
import time
import random
import datetime
import requests

import streamlit as st
import folium
from streamlit_folium import st_folium

# ---------------------------------------------------------------------------
# Path setup -- allow imports from project root regardless of working dir
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.agents.intake_agent import IntakeAgent
from src.agents.metadata_agent import MetadataAgent
from src.agents.planner_agent import PlannerAgent
from src.agents.router_agent import RouterAgent
from src.rag.embeddings import SOPKnowledgeBase
from src.utils.map_utils import (
    create_depot_marker,
    create_incident_marker,
    create_route_polyline,
    get_map_center,
)


# =========================================================================
#  PAGE CONFIGURATION
# =========================================================================
st.set_page_config(
    page_title="ResQ-MAR Command Dashboard",
    page_icon=":fire:",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================================
#  HELPERS
# =========================================================================

URGENCY_COLORS = {
    "critical": "red",
    "high": "orange",
    "medium": "blue",
    "low": "green",
}

HAZARD_BADGE = {
    "fire": ":red[FIRE]",
    "flood": ":blue[FLOOD]",
    "earthquake": ":orange[EARTHQUAKE]",
    "medical": ":green[MEDICAL]",
    "unknown": ":gray[UNKNOWN]",
}

# Default depot coordinates (Bangalore)
DEFAULT_DEPOT = {"id": "central_depot", "lat": 12.9716, "lon": 77.5946}


def check_ollama_status() -> bool:
    """Return True if the local Ollama server is reachable."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def load_demo_incidents() -> list:
    """Load the pre-defined demo incidents from data/demo_incidents.json."""
    json_path = os.path.join(PROJECT_ROOT, "data", "demo_incidents.json")
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception:
        return []


@st.cache_resource(show_spinner="Loading agents and knowledge base...")
def init_pipeline():
    """
    Initialise all agents and the ChromaDB knowledge base exactly once.
    Cached so Streamlit does not re-create them on every rerun.
    """
    config_path = os.path.join(PROJECT_ROOT, "src", "config", "llm_config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    intake  = IntakeAgent(llm_config=config)
    meta    = MetadataAgent(llm_config=config)
    planner = PlannerAgent(llm_config=config)
    router  = RouterAgent(llm_config=config)

    kb = SOPKnowledgeBase()
    sop_dir = os.path.join(PROJECT_ROOT, "data", "sops")
    kb.ingest_sops(sop_dir=sop_dir)

    return intake, meta, planner, router, kb


def run_pipeline(raw_text: str, lat: float, lon: float):
    """
    Execute the full 5-stage pipeline for a single incident and return
    a structured result dict.
    """
    intake, meta, planner, router, kb = init_pipeline()
    logs = []
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    # --- Stage 1: Intake ---
    intake_res = intake.process_report(raw_text)
    normalized = intake_res.get("normalized_text", raw_text)
    is_spam = intake_res.get("is_spam", False)
    logs.append({
        "agent": "IntakeAgent",
        "action": "process_report",
        "timestamp": timestamp,
        "input": {"raw_text": raw_text},
        "output": intake_res,
    })

    if is_spam:
        return {
            "id": f"INC-{int(time.time())}",
            "raw_text": raw_text,
            "normalized_text": normalized,
            "is_spam": True,
            "metadata": {},
            "plan": {},
            "routing": {},
            "lat": lat,
            "lon": lon,
            "logs": logs,
        }

    # --- Stage 2: Metadata ---
    meta_res = meta.extract_metadata(normalized)
    hazard = meta_res.get("hazard_type", "unknown")
    urgency = meta_res.get("urgency", "medium")
    logs.append({
        "agent": "MetadataAgent",
        "action": "extract_metadata",
        "timestamp": timestamp,
        "input": {"normalized_text": normalized},
        "output": meta_res,
    })

    # --- Stage 3: RAG ---
    sops = kb.query(hazard, normalized, top_k=2)
    logs.append({
        "agent": "RAG",
        "action": "query_sops",
        "timestamp": timestamp,
        "input": {"hazard_type": hazard, "query": normalized},
        "output": {"retrieved": len(sops), "sop_ids": [s["id"] for s in sops]},
    })

    # --- Stage 4: Planner ---
    plan = planner.generate_plan(meta_res, sops)
    logs.append({
        "agent": "PlannerAgent",
        "action": "generate_plan",
        "timestamp": timestamp,
        "input": meta_res,
        "output": plan,
    })

    # --- Stage 5: Router (MVP: 1 depot + 1 incident + 1 vehicle) ---
    locations = [
        {"id": DEFAULT_DEPOT["id"], "lat": DEFAULT_DEPOT["lat"],
         "lon": DEFAULT_DEPOT["lon"], "demand": 0, "priority": 1},
        {"id": f"incident_{int(time.time())}", "lat": lat, "lon": lon,
         "demand": 5, "priority": 4},
    ]
    vehicles = [
        {"id": "rescue_unit_1", "capacity": 10, "speed_kmh": 40.0,
         "start_location_id": DEFAULT_DEPOT["id"]},
    ]
    routing = router.plan_routes(plan, locations, vehicles)
    logs.append({
        "agent": "RouterAgent",
        "action": "plan_routes",
        "timestamp": timestamp,
        "input": {"locations": len(locations), "vehicles": len(vehicles)},
        "output": routing,
    })

    return {
        "id": f"INC-{int(time.time())}",
        "raw_text": raw_text,
        "normalized_text": normalized,
        "is_spam": False,
        "metadata": meta_res,
        "plan": plan,
        "routing": routing,
        "lat": lat,
        "lon": lon,
        "logs": logs,
    }


# =========================================================================
#  SESSION STATE INITIALISATION
# =========================================================================
if "incidents" not in st.session_state:
    st.session_state.incidents = []
if "logs" not in st.session_state:
    st.session_state.logs = []


# =========================================================================
#  SIDEBAR
# =========================================================================
with st.sidebar:
    st.header("Submit Incident")

    incident_text = st.text_area(
        "Describe the emergency...",
        height=120,
        placeholder="E.g.: Fire in Building 7, 3rd floor, people trapped!",
    )

    col_lat, col_lon = st.columns(2)
    with col_lat:
        inc_lat = st.number_input("Latitude", value=12.9720, format="%.4f")
    with col_lon:
        inc_lon = st.number_input("Longitude", value=77.5950, format="%.4f")

    ollama_online = check_ollama_status()

    process_disabled = (not ollama_online) or (not incident_text.strip())
    if st.button("Process Incident", type="primary", disabled=process_disabled,
                 use_container_width=True):
        with st.spinner("Running 5-stage pipeline..."):
            result = run_pipeline(incident_text.strip(), inc_lat, inc_lon)
            st.session_state.incidents.insert(0, result)
            st.session_state.logs = result["logs"] + st.session_state.logs
            # Trim logs to last 20 entries
            st.session_state.logs = st.session_state.logs[:20]
        st.rerun()

    # --- Load Demo Incident ---
    st.divider()
    if st.button("Load Demo Incident", use_container_width=True):
        demos = load_demo_incidents()
        if demos:
            pick = random.choice(demos)
            with st.spinner("Running pipeline on demo incident..."):
                result = run_pipeline(pick["raw_text"], pick["lat"], pick["lon"])
                st.session_state.incidents.insert(0, result)
                st.session_state.logs = result["logs"] + st.session_state.logs
                st.session_state.logs = st.session_state.logs[:20]
            st.rerun()

    # --- System Status ---
    st.divider()
    st.subheader("System Status")

    if ollama_online:
        st.success("Ollama: Online")
    else:
        st.error("Ollama: Offline -- start with 'ollama serve'")

    try:
        _, _, _, _, kb = init_pipeline()
        stats = kb.get_collection_stats()
        st.info(f"ChromaDB: {stats['total_sops']} SOPs loaded")
    except Exception:
        st.warning("ChromaDB: Not initialised")

    st.markdown("**Agent Statuses**")
    for name in ["IntakeAgent", "MetadataAgent", "PlannerAgent", "RouterAgent"]:
        st.markdown(f"- :green[Active] {name}")


# =========================================================================
#  MAIN AREA -- TITLE
# =========================================================================
st.title(":fire: ResQ-MAR Command Dashboard")

if not st.session_state.incidents:
    st.info("Welcome to ResQ-MAR. Submit an incident from the sidebar to begin.")


# =========================================================================
#  MAIN AREA -- THREE COLUMNS
# =========================================================================
col_feed, col_map, col_logs = st.columns([3, 4, 3])


# -------------------------------------------------------------------------
#  LEFT COLUMN: Incident Feed
# -------------------------------------------------------------------------
with col_feed:
    st.subheader("Incident Feed")

    if not st.session_state.incidents:
        st.caption("No incidents yet.")

    for idx, inc in enumerate(st.session_state.incidents):
        hazard = inc.get("metadata", {}).get("hazard_type", "unknown")
        urgency = inc.get("metadata", {}).get("urgency", "medium")
        badge = HAZARD_BADGE.get(hazard, ":gray[UNKNOWN]")
        urg_color = URGENCY_COLORS.get(urgency, "blue")

        with st.container(border=True):
            st.markdown(f"**{inc['id']}** | {badge} | :{urg_color}[{urgency.upper()}]")

            if inc.get("is_spam"):
                st.warning("Flagged as SPAM")
            else:
                loc_desc = inc.get("metadata", {}).get("location_description", "N/A")
                st.caption(f"Location: {loc_desc}")

            with st.expander("Details"):
                st.markdown(f"**Raw:** {inc['raw_text']}")
                st.markdown(f"**Normalized:** {inc.get('normalized_text', 'N/A')}")

                if inc.get("metadata"):
                    st.markdown("**Metadata:**")
                    st.json(inc["metadata"])

                plan = inc.get("plan", {})
                tasks = plan.get("tasks", [])
                if tasks:
                    st.markdown(f"**Plan:** {len(tasks)} tasks, "
                                f"ETA {plan.get('estimated_total_time_min', '?')} min")
                    for t in tasks[:3]:
                        st.markdown(f"- Step {t.get('step')}: {t.get('action')}")
                    if len(tasks) > 3:
                        st.caption(f"... and {len(tasks) - 3} more tasks")

                routing = inc.get("routing", {})
                if routing.get("routes"):
                    st.markdown(f"**Routing:** {routing.get('solver_status')} | "
                                f"{routing.get('total_distance_km')} km")


# -------------------------------------------------------------------------
#  MIDDLE COLUMN: Live Map
# -------------------------------------------------------------------------
with col_map:
    st.subheader("Live Map")

    # Determine map center
    if st.session_state.incidents:
        center = get_map_center(st.session_state.incidents)
    else:
        center = get_map_center()

    m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

    # Add depot marker
    create_depot_marker(
        DEFAULT_DEPOT["lat"], DEFAULT_DEPOT["lon"], "Central Depot"
    ).add_to(m)

    # Add incident markers and route lines
    for inc in st.session_state.incidents:
        hazard = inc.get("metadata", {}).get("hazard_type", "unknown")
        urgency = inc.get("metadata", {}).get("urgency", "medium")

        create_incident_marker(
            inc["lat"], inc["lon"], hazard, urgency, inc["id"]
        ).add_to(m)

        # Draw route polyline from depot to incident if routing exists
        routing = inc.get("routing", {})
        if routing.get("routes"):
            route_color = HAZARD_COLORS.get(hazard, "gray") if hazard != "unknown" else "gray"
            # Simple depot -> incident line
            points = [
                (DEFAULT_DEPOT["lat"], DEFAULT_DEPOT["lon"]),
                (inc["lat"], inc["lon"]),
            ]
            create_route_polyline(points, color=route_color).add_to(m)

    st_folium(m, height=500, use_container_width=True)


# -------------------------------------------------------------------------
#  RIGHT COLUMN: Agent Logs
# -------------------------------------------------------------------------
with col_logs:
    st.subheader("Agent Logs")

    if not st.session_state.logs:
        st.caption("No logs yet. Process an incident to see agent activity.")

    AGENT_COLORS = {
        "IntakeAgent": "gray",
        "MetadataAgent": "blue",
        "RAG": "violet",
        "PlannerAgent": "green",
        "RouterAgent": "orange",
    }

    for log_entry in st.session_state.logs:
        agent = log_entry.get("agent", "Unknown")
        action = log_entry.get("action", "")
        ts = log_entry.get("timestamp", "")
        color = AGENT_COLORS.get(agent, "gray")

        with st.expander(f":{color}[{agent}] -- {action} ({ts})"):
            st.markdown("**Input:**")
            st.json(log_entry.get("input", {}))
            st.markdown("**Output:**")
            st.json(log_entry.get("output", {}))
