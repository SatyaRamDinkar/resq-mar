"""
Live Vehicle Tracking with High-Precision Telemetry Simulator
============================================================
Enhances live tracking with smooth bearing-oriented markers,
telemetry stats (speed, distance, ETA), and dynamic re-routing.
"""

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import random
from src.routing.osrm_client import OSRMClient
from src.utils.telemetry_simulator import TelemetrySimulator


def render_live_tracking_panel(agent_instance):
    """
    Renders high-precision dynamic GPS telemetry streaming on a dark-matter map.
    """
    st.markdown('<div class="section-header">Live GPS Telemetry & Fleet Tracking</div>', unsafe_allow_html=True)

    # Initialize state
    if 'sim_active' not in st.session_state:
        st.session_state.sim_active = False
    if 'sim_road_blocked' not in st.session_state:
        st.session_state.sim_road_blocked = False
    if 'sim_progress' not in st.session_state:
        st.session_state.sim_progress = 0.0

    # Auto-detect language
    from src.utils.geo_lookup import get_state_language
    incidents = st.session_state.get('incidents', [])
    if incidents:
        lat, lon = incidents[0].get('lat', 17.6868), incidents[0].get('lon', 83.2185)
    else:
        lat, lon = 17.6868, 83.2185

    state_name, lang_code, lang_name = get_state_language(lat, lon)
    langs = ["English", "Hindi"]
    if lang_code != "hi" and lang_name not in langs:
        langs.append(lang_name)

    st.caption(f"Connected to AP-State Emergency Dispatch Gateway | Coverage: {' + '.join(langs)} ({state_name})")

    # Action Controls
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with c1:
        if st.button("Start Live Telemetry", disabled=st.session_state.sim_active, use_container_width=True):
            st.session_state.sim_active = True
            st.session_state.sim_progress = 0.0
            st.session_state.sim_road_blocked = False
            st.rerun()

    with c2:
        if st.button("Simulate Road Hazard", disabled=not st.session_state.sim_active or st.session_state.sim_road_blocked, use_container_width=True):
            st.session_state.sim_road_blocked = True
            agent_instance.log_agent_activity("LiveAwarenessAgent", "alert", "HAZARD ALERT: Coastal flood inundation detected on primary arterial road!")
            agent_instance.log_agent_activity("RouterAgent", "planning", "Dynamic reroute engaged: computing safe bypass via inland corridor.")
            st.rerun()

    with c3:
        if st.button("Reset Telemetry", disabled=not st.session_state.sim_active, use_container_width=True):
            st.session_state.sim_active = False
            st.session_state.sim_progress = 0.0
            st.session_state.sim_road_blocked = False
            st.rerun()

    with c4:
        if st.button("Dispatch Ping (SMS)", use_container_width=True):
            from src.services.notifier import send_sms
            msg = f"ResQ-MAR: Emergency Unit AMB-01 dispatched to Vizag Coast. Active ETA 8.5m."
            send_sms("+91-RESPONDER", msg, logger=agent_instance.log_agent_activity)
            st.success("Telemetry ping broadcasted to response unit.")

    # Telemetry metrics row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    speed_metric = m_col1.empty()
    dist_metric = m_col2.empty()
    eta_metric = m_col3.empty()
    status_metric = m_col4.empty()

    map_container = st.empty()
    status_container = st.empty()

    # Route coords for simulation (Vizag Coastal to King George Hospital or Inland bypass)
    primary_route = [
        (17.6868, 83.2185),
        (17.6950, 83.2350),
        (17.7020, 83.2550),
        (17.7120, 83.2850),
        (17.7180, 83.3050),
        (17.7042, 83.3005),
    ]

    detour_route = [
        (17.6868, 83.2185),
        (17.6920, 83.2100),
        (17.7150, 83.2300),
        (17.7300, 83.2700),
        (17.7200, 83.2950),
        (17.7042, 83.3005),
    ]

    active_route = detour_route if st.session_state.sim_road_blocked else primary_route
    route_color = "#f59e0b" if st.session_state.sim_road_blocked else "#3b82f6"

    sim = TelemetrySimulator(
        vehicle_id="AMB-01 (ALS Unit)",
        route_coordinates=active_route,
        target_hospital="King George Hospital Trauma Center",
        average_speed_kmh=52.0 if not st.session_state.sim_road_blocked else 42.0,
    )

    if st.session_state.sim_active:
        steps = 40
        start_step = int(st.session_state.sim_progress * steps)

        for step in range(start_step, steps + 1):
            prog = step / float(steps)
            frame = sim.get_position_at_progress(prog)

            # Update live KPIs
            speed_metric.metric("Vehicle Speed", f"{frame['speed_kmh']} km/h")
            dist_metric.metric("Remaining Dist", f"{frame['remaining_distance_km']} km")
            eta_metric.metric("Dynamic ETA", f"{frame['eta_minutes']} min")
            status_metric.metric("Bearing", f"{frame['bearing']} deg")

            # Build map
            fig = go.Figure()

            # Polyline route
            lats = [c[0] for c in active_route]
            lons = [c[1] for c in active_route]
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lat=lats,
                lon=lons,
                line=dict(width=5, color=route_color),
                name="Detour Bypass" if st.session_state.sim_road_blocked else "Active Route",
            ))

            # Start point (Emergency Origin)
            fig.add_trace(go.Scattermapbox(
                mode="markers",
                lat=[active_route[0][0]],
                lon=[active_route[0][1]],
                marker=dict(size=10, color="orange"),
                name="Incident Origin",
            ))

            # Destination (Hospital)
            fig.add_trace(go.Scattermapbox(
                mode="markers",
                lat=[active_route[-1][0]],
                lon=[active_route[-1][1]],
                marker=dict(size=12, color="green"),
                name="Target Hospital",
            ))

            # Real-time Moving Ambulance Marker
            curr_lat, curr_lon = frame["current_coords"]
            fig.add_trace(go.Scattermapbox(
                mode="markers+text",
                lat=[curr_lat],
                lon=[curr_lon],
                marker=dict(size=16, color="#ef4444"),
                text=["AMB-01"],
                textposition="top right",
                name="AMB-01 (Active)",
            ))

            fig.update_layout(
                mapbox=dict(
                    style="carto-darkmatter",
                    center=dict(lat=curr_lat, lon=curr_lon),
                    zoom=12.2,
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=450,
                showlegend=True,
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(15,23,42,0.8)", font=dict(color="white")),
            )

            map_container.plotly_chart(fig, use_container_width=True)
            status_container.info(
                f"STATUS: **{frame['status']}** | Destination: **{frame['destination']}** | Completed: **{frame['progress_percent']}%**"
            )

            st.session_state.sim_progress = prog
            time.sleep(0.12)

        st.session_state.sim_active = False
        st.session_state.sim_progress = 0.0
        status_container.success("UNIT ARRIVED SAFELY AT HOSPITAL EMERGENCY TRAUMA WARD.")
    else:
        # Static preview map before launch
        fig = go.Figure()
        lats = [c[0] for c in active_route]
        lons = [c[1] for c in active_route]
        fig.add_trace(go.Scattermapbox(
            mode="lines+markers",
            lat=lats,
            lon=lons,
            line=dict(width=4, color=route_color),
            marker=dict(size=8, color="#38bdf8"),
            name="Route Waypoints",
        ))
        fig.update_layout(
            mapbox=dict(
                style="carto-darkmatter",
                center=dict(lat=(active_route[0][0] + active_route[-1][0]) / 2,
                            lon=(active_route[0][1] + active_route[-1][1]) / 2),
                zoom=11.5,
            ),
            margin=dict(l=0, r=0, t=0, b=0),
            height=420,
            showlegend=False,
        )
        map_container.plotly_chart(fig, use_container_width=True)
        status_container.info("Click **'Start Live Telemetry'** to stream GPS coordinate progression in real-time.")
