"""
Heatmap View Component using Folium.
"""
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

def render_incident_heatmap(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> folium.Map:
    """Render folium heatmap layer."""
    if not incidents:
        center = [6.9271, 79.8612]
    else:
        lats = [i['lat'] for i in incidents]
        lons = [i['lon'] for i in incidents]
        center = [sum(lats)/len(lats), sum(lons)/len(lons)]
        
    m = folium.Map(location=center, zoom_start=12)
    
    heat_data = []
    severity_weights = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    for i in incidents:
        w = severity_weights.get(i.get('severity', 'low').lower(), 1)
        heat_data.append([i['lat'], i['lon'], w])
        
    HeatMap(heat_data).add_to(folium.FeatureGroup(name='Incident Heatmap').add_to(m))
    
    colors = {'flood': 'blue', 'fire': 'red', 'earthquake': 'orange', 'medical': 'green'}
    inc_group = folium.FeatureGroup(name='Incident Markers')
    for i in incidents:
        c = colors.get(i.get('type', 'flood').lower(), 'gray')
        folium.CircleMarker(
            location=[i['lat'], i['lon']],
            radius=5,
            color=c,
            fill=True,
            tooltip=f"{i.get('type', 'Unknown').upper()} - {i.get('severity', 'Unknown')}"
        ).add_to(inc_group)
    inc_group.add_to(m)
    
    res_group = folium.FeatureGroup(name='Resources')
    for r in resources:
        c = 'green' if r.get('available', False) else 'red'
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
    covered = sum(1 for i in incidents if check_incident_coverage(i, resources, radius_km=5.0))
    coverage_pct = (covered / total * 100) if total > 0 else 100.0
    
    hotspots = total // 5
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Total Incidents', total)
    col2.metric('Covered Incidents', covered)
    col3.metric('Coverage %', f'{coverage_pct:.1f}%')
    col4.metric('Hotspots Detected', hotspots)
    
    return {'total': total, 'covered': covered, 'coverage_pct': coverage_pct, 'hotspots': hotspots}

def get_mock_incidents() -> List[Dict[str, Any]]:
    return [
        {'lat': 6.9271, 'lon': 79.8612, 'type': 'flood', 'severity': 'high', 'status': 'active'},
        {'lat': 6.9300, 'lon': 79.8500, 'type': 'fire', 'severity': 'critical', 'status': 'active'},
        {'lat': 6.9100, 'lon': 79.8700, 'type': 'medical', 'severity': 'medium', 'status': 'active'},
        {'lat': 6.9400, 'lon': 79.8800, 'type': 'earthquake', 'severity': 'high', 'status': 'active'},
        {'lat': 6.9250, 'lon': 79.8650, 'type': 'flood', 'severity': 'low', 'status': 'active'},
    ]

def get_mock_resources() -> List[Dict[str, Any]]:
    return [
        {'lat': 6.9200, 'lon': 79.8600, 'type': 'Ambulance', 'available': True},
        {'lat': 6.9350, 'lon': 79.8550, 'type': 'Fire Truck', 'available': False},
        {'lat': 6.9150, 'lon': 79.8750, 'type': 'Drone', 'available': True},
    ]
