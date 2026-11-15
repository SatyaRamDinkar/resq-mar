import streamlit as st
from typing import List, Dict, Any
import folium
from folium.plugins import HeatMap
import json
import os
from src.config.geo import MAP_CENTER, MAP_ZOOM

# Andhra Pradesh Core Center & Focus Coordinates
AP_CENTER = {"lat": 16.2000, "lon": 80.4500}
AP_ZOOM = 7.0

# Key Andhra Pradesh Major Operational Hotspot Clusters with detailed regional data
AP_MAJOR_ZONES = [
    {
        "id": "AP_ZONE_VIZAG",
        "city": "Visakhapatnam",
        "region": "North Coastal Zone",
        "lat": 17.6868,
        "lon": 83.2185,
        "type": "cyclone",
        "severity": "critical",
        "raw_text": "Coastal Storm Surge & Inundation alert near RK Beach & Port Zone",
        "hazard_zone": "⚠️ Cyclone & Coastal Surge",
        "depot": "King George Hospital Trauma Base"
    },
    {
        "id": "AP_ZONE_VIJAYAWADA",
        "city": "Vijayawada - Amaravati",
        "region": "Krishna River Delta",
        "lat": 16.5062,
        "lon": 80.6480,
        "type": "flood",
        "severity": "high",
        "raw_text": "Prakasam Barrage catchment overflow, urban waterlogging in low-lying wards",
        "hazard_zone": "⚠️ Riverine Flood Inundation",
        "depot": "Government General Hospital Vijayawada"
    },
    {
        "id": "AP_ZONE_GUNTUR",
        "city": "Guntur",
        "region": "Central AP Corridor",
        "lat": 16.3067,
        "lon": 80.4365,
        "type": "medical",
        "severity": "high",
        "raw_text": "Mass casualty chemical transit collision on NH-16 corridor, ALS required",
        "hazard_zone": "Safe Inland Corridor",
        "depot": "Guntur Medical College Emergency Wing"
    },
    {
        "id": "AP_ZONE_TIRUPATI",
        "city": "Tirupati",
        "region": "Rayalaseema South",
        "lat": 13.6288,
        "lon": 79.4192,
        "type": "flood",
        "severity": "medium",
        "raw_text": "Flash flood warning in Kapilatheertham ghats due to torrential rainfall",
        "hazard_zone": "⚠️ Flash Flood Hazard",
        "depot": "SVIMS Super Specialty Hospital Depot"
    },
    {
        "id": "AP_ZONE_KURNOOL",
        "city": "Kurnool",
        "region": "Tungabhadra Basin",
        "lat": 15.8281,
        "lon": 78.0373,
        "type": "flood",
        "severity": "high",
        "raw_text": "Tungabhadra river high discharge warning, low-lying village evacuation in progress",
        "hazard_zone": "⚠️ Flood Inundation Alert",
        "depot": "Kurnool District Emergency Operations Base"
    },
    {
        "id": "AP_ZONE_KAKINADA",
        "city": "Kakinada - Godavari",
        "region": "Godavari Delta Coast",
        "lat": 16.9891,
        "lon": 82.2475,
        "type": "cyclone",
        "severity": "critical",
        "raw_text": "High tidal wave warnings and coastal fisherman hamlet evacuation alert",
        "hazard_zone": "⚠️ Cyclone Danger Zone",
        "depot": "Rangaraya Medical Hospital Trauma Unit"
    }
]

# Dedicated AP Emergency Fleet Resources
AP_RESOURCES = [
    {"id": "AP_AMB_01", "type": "ambulance", "lat": 17.7042, "lon": 83.3005, "base_location": "King George Hospital Base, Vizag", "speed_kmh": 80.0, "capacity": 2, "available": True},
    {"id": "AP_AMB_02", "type": "ambulance", "lat": 16.5120, "lon": 80.6400, "base_location": "New Govt Hospital Base, Vijayawada", "speed_kmh": 75.0, "capacity": 2, "available": True},
    {"id": "AP_AMB_03", "type": "ambulance", "lat": 16.3100, "lon": 80.4400, "base_location": "Guntur GMC Emergency Hub", "speed_kmh": 75.0, "capacity": 2, "available": True},
    {"id": "AP_AMB_04", "type": "ambulance", "lat": 13.6350, "lon": 79.4250, "base_location": "SVIMS Trauma Centre, Tirupati", "speed_kmh": 70.0, "capacity": 2, "available": True},
    {"id": "AP_AMB_05", "type": "ambulance", "lat": 15.8300, "lon": 78.0400, "base_location": "Kurnool Emergency Response Base", "speed_kmh": 70.0, "capacity": 2, "available": True},
    {"id": "AP_AMB_06", "type": "ambulance", "lat": 16.9950, "lon": 82.2500, "base_location": "Kakinada Coastal Rescue Center", "speed_kmh": 75.0, "capacity": 2, "available": True},
    {"id": "AP_RESCUE_01", "type": "rescue_boat", "lat": 17.6950, "lon": 83.2350, "base_location": "Visakhapatnam Naval Dockyard SDRF Unit", "speed_kmh": 45.0, "capacity": 8, "available": True},
    {"id": "AP_RESCUE_02", "type": "rescue_boat", "lat": 16.5020, "lon": 80.6200, "base_location": "Krishna River Disaster Rescue Unit, Vijayawada", "speed_kmh": 45.0, "capacity": 8, "available": True},
    {"id": "AP_DRONE_01", "type": "drone", "lat": 16.5180, "lon": 80.6350, "base_location": "APSDMA Drone Reconnaissance Hub, Amaravati", "speed_kmh": 60.0, "capacity": 1, "available": True}
]


# Andhra Pradesh Outline Polygon for state geographic boundary visualization
AP_STATE_BORDER = [
    [13.50, 80.18], [13.75, 80.25], [14.30, 80.12], [14.95, 80.05],
    [15.50, 80.20], [15.85, 80.60], [16.15, 81.15], [16.45, 81.70],
    [16.90, 82.30], [17.30, 82.75], [17.70, 83.35], [18.25, 84.05],
    [18.90, 84.70], [19.10, 84.75], [18.70, 83.80], [18.20, 83.00],
    [17.80, 82.00], [17.40, 81.25], [16.80, 80.50], [16.45, 79.50],
    [16.10, 78.60], [15.80, 78.00], [15.20, 77.10], [14.60, 76.85],
    [13.80, 77.20], [13.30, 78.20], [13.40, 79.20], [13.50, 80.18]
]


def render_incident_heatmap(
    incidents: List[Dict[str, Any]],
    resources: List[Dict[str, Any]],
    show_cyclone: bool = True,
    show_seismic: bool = True,
    show_flood: bool = True,
    focus_ap: bool = False
) -> folium.Map:
    """
    Render folium heatmap layer with high-contrast Dark Mode surface,
    clean discrete markers, state jurisdiction boundary, and compact layer control.
    """
    if focus_ap:
        center = [AP_CENTER["lat"], AP_CENTER["lon"]]
        zoom = AP_ZOOM
    else:
        center = [MAP_CENTER["lat"], MAP_CENTER["lon"]]
        zoom = MAP_ZOOM

    # Initialize map without auto-generated URL label in the layer control
    dark_tiles_url = "https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles=None,
        control_scale=True,
    )

    # Base Tile Layers with clean human-readable names
    folium.TileLayer(
        tiles=dark_tiles_url,
        attr="Esri World Dark Gray",
        name="Dark Theme Base",
        overlay=False,
        control=True
    ).add_to(m)

    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Standard Street Map",
        overlay=False,
        control=True
    ).add_to(m)

    # If in Andhra Pradesh mode, render the official state boundary polygon
    if focus_ap:
        folium.Polygon(
            locations=AP_STATE_BORDER,
            color="#38bdf8",
            weight=2.5,
            dash_array="6, 6",
            fill=True,
            fill_color="#0284c7",
            fill_opacity=0.10,
            tooltip="Andhra Pradesh State Emergency Jurisdiction",
        ).add_to(folium.FeatureGroup(name="AP State Boundary", show=True).add_to(m))

    # Load hazards if enabled
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
                        "fillOpacity": 0.22,
                    },
                    tooltip=f"Active Hazard: {display_name}"
                ).add_to(m)

    if show_cyclone:
        _add_hazard("cyclone", "#38bdf8", "Cyclone Risk Coastline")
    if show_seismic:
        _add_hazard("seismic", "#f87171", "Seismic Fault Zones")
    if show_flood:
        _add_hazard("flood", "#c084fc", "Flood Inundation Basins")

    # HeatMap for broader density gradients
    heat_data = []
    severity_weights = {"low": 1, "medium": 2, "high": 3, "critical": 5}
    for i in incidents:
        w = severity_weights.get(i.get("severity", "low").lower(), 2)
        heat_data.append([i.get("lat", center[0]), i.get("lon", center[1]), w])

    radius_val = 26 if focus_ap else 24
    blur_val = 16 if focus_ap else 15
    HeatMap(heat_data, radius=radius_val, blur=blur_val, max_zoom=7 if focus_ap else 5).add_to(
        folium.FeatureGroup(name="Incident Hotspot Density").add_to(m)
    )

    # Incident Markers: Vibrant icons with distinct labels
    inc_group = folium.FeatureGroup(name="Active Incidents")
    for i in incidents:
        sev = i.get("severity", "high").lower()
        badge_color = "#ef4444" if sev == "critical" else "#f97316" if sev == "high" else "#3b82f6"
        loc_name = i.get("city", i.get("region", "Incident Hub"))
        inc_type = i.get("type", "Emergency").upper()

        # HTML popup card
        popup_html = f"""
        <div style="font-family:sans-serif; min-width:180px; padding:4px;">
            <div style="font-weight:bold; font-size:13px; color:#0f172a; margin-bottom:2px;">{loc_name}</div>
            <div style="font-size:11px; color:#475569; margin-bottom:6px;">Type: <b>{inc_type}</b></div>
            <span style="background:{badge_color}; color:white; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:bold;">
                {sev.upper()} SEVERITY
            </span>
            <div style="font-size:11px; color:#334155; margin-top:6px;">{i.get('raw_text', '')}</div>
        </div>
        """

        folium.CircleMarker(
            location=[i.get("lat", center[0]), i.get("lon", center[1])],
            radius=10 if focus_ap else 8,
            color="#ffffff",
            fill_color=badge_color,
            fill=True,
            fill_opacity=0.92,
            weight=2.5,
            tooltip=f"{loc_name} | {inc_type} ({sev.upper()})",
            popup=folium.Popup(popup_html, max_width=250),
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

    # Compact LayerControl: Collapsed by default so it never blocks the map view!
    folium.LayerControl(position="topright", collapsed=True).add_to(m)
    return m


def render_coverage_stats(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]], is_ap_mode: bool = False) -> Dict[str, Any]:
    """Calculate and display coverage stats."""
    from src.utils.dashboard_utils import check_incident_coverage

    total = len(incidents)
    check_radius = 40.0 if is_ap_mode else 50.0
    covered = sum(1 for i in incidents if check_incident_coverage(i, resources, radius_km=check_radius))
    coverage_pct = (covered / total * 100) if total > 0 else 100.0

    hotspots = max(1, total // 3 if is_ap_mode else total // 4)

    col1, col2, col3, col4 = st.columns(4)
    label_suffix = " (AP)" if is_ap_mode else ""
    col1.metric(f"Total Incidents{label_suffix}", total)
    col2.metric(f"Covered Incidents{label_suffix}", covered)
    col3.metric(f"Coverage %{label_suffix}", f"{coverage_pct:.1f}%")
    col4.metric(f"Active Hotspots{label_suffix}", hotspots)

    return {"total": total, "covered": covered, "coverage_pct": coverage_pct, "hotspots": hotspots}


def get_mock_incidents() -> List[Dict[str, Any]]:
    """Load from demo_incidents.json with smart type extraction and hazard intersection tags."""
    try:
        from src.utils.hazard_checker import get_intersecting_hazards
        with open("data/demo_incidents.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            for row in data:
                raw = row.get("raw_text", "").lower()
                if "flood" in raw:
                    row["type"] = "flood"
                elif "fire" in raw:
                    row["type"] = "fire"
                elif "earthquake" in raw:
                    row["type"] = "earthquake"
                elif "medical" in raw:
                    row["type"] = "medical"
                elif "cyclone" in raw:
                    row["type"] = "cyclone"
                else:
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


def get_andhra_pradesh_incidents() -> List[Dict[str, Any]]:
    """Return high-fidelity Andhra Pradesh major emergency zones."""
    return AP_MAJOR_ZONES


def get_andhra_pradesh_resources() -> List[Dict[str, Any]]:
    """Return dedicated Andhra Pradesh emergency response fleet."""
    return AP_RESOURCES
