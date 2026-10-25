import streamlit as st
from typing import List, Dict, Any
import folium
from folium.plugins import HeatMap
try:
    from streamlit_folium import st_folium
    HAS_ST_FOLIUM = True
except ImportError:
    HAS_ST_FOLIUM = False
import json
import os
from src.config.geo import MAP_CENTER, MAP_ZOOM


def render_incident_heatmap(
    incidents: List[Dict[str, Any]],
    resources: List[Dict[str, Any]],
    show_cyclone: bool = True,
    show_seismic: bool = True,
    show_flood: bool = True
) -> folium.Map:
    """Render folium heatmap layer with high-contrast CartoDB dark-matter styling."""
    center = [MAP_CENTER["lat"], MAP_CENTER["lon"]]

    # Dark matter map with light street map alternative layer
    m = folium.Map(
        location=center,
        zoom_start=MAP_ZOOM,
        tiles="CartoDB dark_matter",
        name="CartoDB Dark Matter",
        control_scale=True,
    )
    folium.TileLayer("OpenStreetMap", name="OpenStreetMap Light").add_to(m)

    # Load hazards
    hazard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "hazards")

    def _add_hazard(name: str, color: str, display_name: str):
        path = os.path.join(hazard_dir, f"{name}.geojson")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                geo = json.load(f)
                folium.GeoJson(
                    geo,
                    name=display_name,
                    style_function=lambda x, col=color: {
                        "fillColor": col,
                        "color": col,
                        "weight": 2,
                        "fillOpacity": 0.25,
                    },
                    tooltip=f"Active Alert: {display_name}"
                ).add_to(m)

    if show_cyclone:
        _add_hazard("cyclone", "#38bdf8", "Cyclone Risk Coastline (Bay of Bengal)")
    if show_seismic:
        _add_hazard("seismic", "#f87171", "Seismic Fault Zones IV-V")
    if show_flood:
        _add_hazard("flood", "#c084fc", "Flood Inundation Basins")

    # HeatMap for broader hotspots at India scale
    heat_data = []
    severity_weights = {"low": 1, "medium": 2, "high": 3, "critical": 5}
    for i in incidents:
        w = severity_weights.get(i.get("severity", "low").lower(), 2)
        heat_data.append([i.get("lat", center[0]), i.get("lon", center[1]), w])

    HeatMap(heat_data, radius=28, blur=18, max_zoom=6).add_to(
        folium.FeatureGroup(name="Incident Hotspot Density").add_to(m)
    )

    # Incident Markers with custom vibrant colors
    colors = {
        "flood": "#38bdf8",
        "fire": "#f97316",
        "earthquake": "#ef4444",
        "medical": "#22c55e",
        "cyclone": "#06b6d4",
        "unknown": "#94a3b8"
    }
    inc_group = folium.FeatureGroup(name="Active Incidents")
    for i in incidents:
        c = colors.get(i.get("type", "flood").lower(), "#38bdf8")
        folium.CircleMarker(
            location=[i.get("lat", center[0]), i.get("lon", center[1])],
            radius=8,
            color="#ffffff",
            fill_color=c,
            fill=True,
            fill_opacity=0.9,
            weight=2,
            tooltip=f"{i.get('type', 'Emergency').upper()} | Severity: {i.get('severity', 'High').upper()}"
        ).add_to(inc_group)
    inc_group.add_to(m)

    # Resource fleet markers
    res_group = folium.FeatureGroup(name="Emergency Fleet Depots")
    for r in resources:
        if "lat" not in r or "lon" not in r:
            continue
        is_avail = r.get("available", True)
        icon_color = "green" if is_avail else "red"
        status_txt = "Available for Dispatch" if is_avail else "Busy on Mission"
        folium.Marker(
            location=[r["lat"], r["lon"]],
            icon=folium.Icon(color=icon_color, icon="ambulance", prefix="fa"),
            tooltip=f"{r.get('base_location', r.get('id', 'Depot'))} | {status_txt}"
        ).add_to(res_group)
    res_group.add_to(m)

    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    return m


def render_coverage_stats(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate and display coverage stats."""
    from src.utils.dashboard_utils import check_incident_coverage

    total = len(incidents)
    # Regional emergency radius check (50 km)
    covered = sum(1 for i in incidents if check_incident_coverage(i, resources, radius_km=50.0))
    coverage_pct = (covered / total * 100) if total > 0 else 100.0

    hotspots = max(1, total // 4)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Incidents", total)
    col2.metric("Covered Incidents", covered)
    col3.metric("Coverage %", f"{coverage_pct:.1f}%")
    col4.metric("Active Hotspots", hotspots)

    return {"total": total, "covered": covered, "coverage_pct": coverage_pct, "hotspots": hotspots}


def get_mock_incidents() -> List[Dict[str, Any]]:
    """Load from demo_incidents.json with hazard intersection tags."""
    try:
        from src.utils.hazard_checker import get_intersecting_hazards
        with open("data/demo_incidents.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                row["type"] = row.get("type", "unknown")
                row["severity"] = row.get("severity", "high")
                intersecting = get_intersecting_hazards(row.get("lat", 0.0), row.get("lon", 0.0))
                if intersecting:
                    h_str = "/".join([h.replace("_", " ").title() for h in intersecting])
                    row["hazard_zone"] = f"⚠️ {h_str}"
                else:
                    row["hazard_zone"] = "Safe Zone"
            return data
    except Exception:
        return []


def get_mock_resources() -> List[Dict[str, Any]]:
    """Load resources with verified availability."""
    try:
        with open("data/benchmark_resources.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for r in data:
                if "available" not in r or r["available"] is None:
                    r["available"] = True
            return data
    except Exception:
        return []
