import streamlit as st
from typing import List, Dict, Any
import folium
from folium.plugins import HeatMap
try:
    from streamlit_folium import st_folium
    HAS_ST_FOLIUM = True
except ImportError:
    HAS_ST_FOLIUM = False
import streamlit.components.v1 as components
import json
import os
from src.config.geo import MAP_CENTER, MAP_ZOOM

def render_incident_heatmap(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> folium.Map:
    """Render folium heatmap layer."""
    center = [MAP_CENTER["lat"], MAP_CENTER["lon"]]
        
    m = folium.Map(location=center, zoom_start=MAP_ZOOM)
    
    heat_data = []
    severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    for i in incidents:
        w = severity_weights.get(i.get('severity', 'low').lower(), 1)
        heat_data.append([i.get('lat', center[0]), i.get('lon', center[1]), w])
        
    # HeatMap for broader hotspots at India scale
    HeatMap(heat_data, radius=25, blur=15, max_zoom=1).add_to(folium.FeatureGroup(name='Incident Heatmap').add_to(m))
    
    colors = {'flood': 'blue', 'fire': 'red', 'earthquake': 'orange', 'medical': 'green', 'unknown': 'gray'}
    inc_group = folium.FeatureGroup(name='Incident Markers')
    for i in incidents:
        c = colors.get(i.get('type', 'flood').lower(), 'gray')
        # Using slightly larger circles for India scale readability
        folium.CircleMarker(
            location=[i.get('lat', center[0]), i.get('lon', center[1])],
            radius=6,
            color=c,
            fill=True,
            fill_opacity=0.8,
            weight=1,
            tooltip=f"{i.get('type', 'Unknown').upper()} - {i.get('severity', 'Unknown')}"
        ).add_to(inc_group)
    inc_group.add_to(m)
    
    res_group = folium.FeatureGroup(name='Resources')
    for r in resources:
        if 'lat' not in r or 'lon' not in r: continue
        c = 'green' if r.get('available', False) else 'red'
        # Regular markers may cluster too heavily at zoom 4.5, but for demo sizes it's ok. 
        # Making icons slightly more distinct.
        folium.Marker(
            location=[r['lat'], r['lon']],
            icon=folium.Icon(color=c, icon='info-sign'),
            tooltip=f"{r.get('type', 'Resource')} - {'Available' if r.get('available') else 'Busy'}"
        ).add_to(res_group)
    res_group.add_to(m)
    
    folium.LayerControl().add_to(m)
    return m

def render_coverage_stats(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate and display coverage stats."""
    from src.utils.dashboard_utils import check_incident_coverage
    
    total = len(incidents)
    # Increased coverage check radius for India scale demo (5km -> 50km for macro view)
    covered = sum(1 for i in incidents if check_incident_coverage(i, resources, radius_km=50.0))
    coverage_pct = (covered / total * 100) if total > 0 else 100.0
    
    hotspots = total // 5
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Incidents', total)
    col2.metric('Covered Incidents', covered)
    col3.metric('Coverage %', f'{coverage_pct:.1f}%')
    col4.metric('Macro Hotspots', hotspots)
    
    return {'total': total, 'covered': covered, 'coverage_pct': coverage_pct, 'hotspots': hotspots}

def get_mock_incidents() -> List[Dict[str, Any]]:
    # Load from the updated demo_incidents.json
    try:
        with open('data/demo_incidents.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # transform schema slightly to match heatmap expectation if needed
            for row in data:
                row['type'] = row.get('type', 'unknown')
                row['severity'] = row.get('severity', 'high')
            return data
    except Exception:
        return []

def get_mock_resources() -> List[Dict[str, Any]]:
    try:
        with open('data/benchmark_resources.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Pick a subset of 10 to not overcrowd the India map
            return data[:10]
    except Exception:
        return []
