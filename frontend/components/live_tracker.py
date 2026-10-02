import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from src.routing.osrm_client import OSRMClient
import random

def render_live_tracking_panel(agent_instance):
    """
    Renders the live vehicle tracking view using Plotly and a st.empty() animation loop.
    Includes a deterministic Road Blocked simulation.
    """
    st.markdown('<div class="section-header">Live Vehicle Tracking & Re-Routing</div>', unsafe_allow_html=True)
    
    # For the deterministic demo, we will always show the simulation panel
    # and use the default mock incident coordinate if no live data is present.

    # Deterministic simulation seeds
    random.seed(42)
    
    # Initialize session state for tracking
    if 'sim_active' not in st.session_state:
        st.session_state.sim_active = False
    if 'sim_road_blocked' not in st.session_state:
        st.session_state.sim_road_blocked = False
    if 'sim_step' not in st.session_state:
        st.session_state.sim_step = 0

    # Auto-detect local language for UI indicator
    from src.utils.geo_lookup import get_state_language
    incidents = st.session_state.get('incidents', [])
    if incidents:
        lat, lon = incidents[0].get('lat', 28.6139), incidents[0].get('lon', 77.2090)
    else:
        lat, lon = 28.6139, 77.2090
    state_name, lang_code, lang_name = get_state_language(lat, lon)
    langs = ["English", "Hindi"]
    if lang_code != "hi" and lang_name not in langs:
        langs.append(lang_name)
        
    st.info(f"🌐 **Dispatch Language Coverage:** {' + '.join(langs)} (Auto-detected for {state_name})")

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("Start Live Tracking Simulation", disabled=st.session_state.sim_active):
            st.session_state.sim_active = True
            st.session_state.sim_step = 0
            st.session_state.sim_road_blocked = False
            st.rerun()
            
    with col_btn2:
        if st.button("🚨 Simulate Road Blockage", disabled=not st.session_state.sim_active or st.session_state.sim_road_blocked):
            st.session_state.sim_road_blocked = True
            st.session_state.sim_active = True
            
            # Log to agent chatter
            agent_instance.log_agent_activity("LiveAwarenessAgent", "alert", "CRITICAL: Road blockage detected on primary route!")
            agent_instance.log_agent_activity("RouterAgent", "planning", "Calculating alternative detour via OSRM...")
            st.rerun()

    with col_btn3:
        if st.button("📱 Simulate Dispatch"):
            from src.services.notifier import send_sms, send_email
            
            # Formulate the payload
            incidents = st.session_state.get('incidents', [])
            city = "Chennai" if incidents and incidents[0]['lat'] < 15.0 else "Delhi"
            eta = "14 mins"
            
            msg = f"ResQ-MAR Dispatch: Proceed to {city} incident site. ETA {eta}."
            
            # Trigger dispatch notifications
            send_sms("+91-RESPONDER", msg, logger=agent_instance.log_agent_activity)
            send_email("responder@resq-mar.in", f"Dispatch - {city}", msg, logger=agent_instance.log_agent_activity)
            st.success("Dispatch notifications sent (or mocked). Check Agent Chatter.")

    # The animation container
    map_container = st.empty()
    eta_container = st.empty()
    
    if st.session_state.sim_active:
        osrm = OSRMClient()
        
        # Pick the first route for the demo
        route_demo = agent_instance.last_planned_routes[0]
        # In a real app we'd parse coordinates, here we assume it's just a generic source->dest 
        # But we don't have the exact lat/lon of the route_demo easily if it's a string, 
        # so let's use the first incident and depot.
        from src.config.geo import DEFAULT_DEPOT
        incidents = st.session_state.get('incidents', [])
        if incidents:
            dest_lat, dest_lon = incidents[0]['lat'], incidents[0]['lon']
        else:
            # Fallback
            dest_lat, dest_lon = 19.0983, 72.8267 # Mumbai
            
        src_lat, src_lon = DEFAULT_DEPOT['lat'], DEFAULT_DEPOT['lon']
        
        # Get route geometry
        route_data = osrm.get_route_geometry(src_lat, src_lon, dest_lat, dest_lon, alternatives=True)
        
        if st.session_state.sim_road_blocked and 'alternative' in route_data:
            geom = route_data['alternative']['geometry']
            total_duration = route_data['alternative']['duration_s']
            path_color = 'orange'
        else:
            geom = route_data['primary']['geometry']
            total_duration = route_data['primary']['duration_s']
            path_color = 'blue'
            
        # Ensure we have a geometry array
        if not geom or len(geom) < 2:
            geom = [[src_lon, src_lat], [dest_lon, dest_lat]]

        # Animation Loop
        num_steps = 50
        
        # Smooth interpolation of geometry path to exactly `num_steps` frames
        import numpy as np
        interpolated_geom = []
        if len(geom) > 1:
            total_dist = sum(((geom[k][0]-geom[k-1][0])**2 + (geom[k][1]-geom[k-1][1])**2)**0.5 for k in range(1, len(geom)))
            distances = [0]
            for k in range(1, len(geom)):
                distances.append(distances[-1] + ((geom[k][0]-geom[k-1][0])**2 + (geom[k][1]-geom[k-1][1])**2)**0.5)
            
            for i in range(num_steps):
                target = total_dist * i / max(1, (num_steps - 1))
                # Find segment
                for k in range(1, len(geom)):
                    if distances[k] >= target or k == len(geom) - 1:
                        segment_length = distances[k] - distances[k-1]
                        if segment_length == 0:
                            interpolated_geom.append(geom[k])
                        else:
                            ratio = (target - distances[k-1]) / segment_length
                            lon = geom[k-1][0] + (geom[k][0] - geom[k-1][0]) * ratio
                            lat = geom[k-1][1] + (geom[k][1] - geom[k-1][1]) * ratio
                            interpolated_geom.append([lon, lat])
                        break
        else:
            interpolated_geom = [geom[0]] * num_steps

        start_step = st.session_state.sim_step
        
        for i in range(start_step, num_steps):
            
            current_pos = interpolated_geom[i]
            
            # Remaining ETA
            pct_complete = i / float(num_steps)
            remaining_s = total_duration * (1.0 - pct_complete)
            mins = int(remaining_s // 60)
            secs = int(remaining_s % 60)
            
            # Update ETA
            eta_container.info(f"⏱️ **Live ETA:** {mins}m {secs}s | **Vehicle:** Rescue Unit 1 | **Status:** {'REROUTING (DETOUR)' if st.session_state.sim_road_blocked else 'EN ROUTE'}")
            
            # Build Plotly map
            lons = [p[0] for p in geom]
            lats = [p[1] for p in geom]
            
            fig = go.Figure()
            
            # Route line
            fig.add_trace(go.Scattermapbox(
                mode="lines",
                lon=lons,
                lat=lats,
                marker={'size': 10},
                line=dict(width=4, color=path_color),
                name="Route"
            ))
            
            # Vehicle Marker
            fig.add_trace(go.Scattermapbox(
                mode="markers",
                lon=[current_pos[0]],
                lat=[current_pos[1]],
                marker=dict(size=15, color='red', symbol='circle'),
                name="Ambulance"
            ))
            
            fig.update_layout(
                mapbox=dict(
                    style="carto-darkmatter",
                    center=dict(lat=(src_lat+dest_lat)/2, lon=(src_lon+dest_lon)/2),
                    zoom=4 if abs(src_lat-dest_lat) > 5 else 6
                ),
                margin=dict(l=0, r=0, t=0, b=0),
                height=400,
                showlegend=False
            )
            
            map_container.plotly_chart(fig, use_container_width=True)
            
            st.session_state.sim_step = i
            
            # Break early if button pressed (using a hack: checking query params or just accepting it queues)
            time.sleep(0.15)
            
        # Done
        st.session_state.sim_active = False
        st.session_state.sim_step = 0
        eta_container.success("✅ **Vehicle Arrived on Scene!**")
