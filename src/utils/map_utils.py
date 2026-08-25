"""
Map utility functions for the Streamlit dashboard.
Dependencies: folium
"""
import folium
from typing import List, Tuple, Optional


# Color mapping for hazard types
HAZARD_COLORS = {
    "fire": "red",
    "flood": "blue",
    "earthquake": "orange",
    "medical": "green",
    "unknown": "gray",
}


def create_depot_marker(lat: float, lon: float, name: str = "Depot") -> folium.Marker:
    """
    Create a blue circle marker representing a vehicle depot.

    Args:
        lat: Latitude of the depot.
        lon: Longitude of the depot.
        name: Display name for the depot popup.

    Returns:
        folium.Marker: A blue marker with a circle icon.
    """
    return folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(f"<b>{name}</b><br>Type: Depot", max_width=200),
        tooltip=name,
        icon=folium.Icon(color="blue", icon="home", prefix="glyphicon"),
    )


def create_incident_marker(
    lat: float,
    lon: float,
    hazard_type: str,
    urgency: str,
    incident_id: str,
) -> folium.Marker:
    """
    Create a color-coded marker for an incident.

    Args:
        lat: Latitude of the incident.
        lon: Longitude of the incident.
        hazard_type: One of fire, flood, earthquake, medical, unknown.
        urgency: One of critical, high, medium, low.
        incident_id: A unique identifier for the incident.

    Returns:
        folium.Marker: A colored marker with a descriptive popup.
    """
    color = HAZARD_COLORS.get(hazard_type.lower(), "gray")
    icon_name = {
        "fire": "fire",
        "flood": "tint",
        "earthquake": "warning-sign",
        "medical": "plus-sign",
    }.get(hazard_type.lower(), "question-sign")

    popup_html = (
        f"<b>Incident: {incident_id}</b><br>"
        f"Hazard: {hazard_type}<br>"
        f"Urgency: {urgency}"
    )

    return folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{incident_id} ({hazard_type})",
        icon=folium.Icon(color=color, icon=icon_name, prefix="glyphicon"),
    )


def create_route_polyline(
    points: List[Tuple[float, float]],
    color: str = "blue",
) -> folium.PolyLine:
    """
    Create a polyline connecting a list of (lat, lon) points.

    Args:
        points: Ordered list of (latitude, longitude) tuples.
        color: Line color (CSS name or hex).

    Returns:
        folium.PolyLine: The route line to add to a map.
    """
    return folium.PolyLine(
        locations=points,
        color=color,
        weight=3,
        opacity=0.7,
    )


def get_map_center(incidents: Optional[List[dict]] = None) -> Tuple[float, float]:
    """
    Calculate the geographic center for the map view.

    If incidents are provided, returns the average lat/lon.
    Otherwise returns Bangalore, India as the default.

    Args:
        incidents: List of incident dicts, each having 'lat' and 'lon' keys.

    Returns:
        Tuple[float, float]: (latitude, longitude) for the map center.
    """
    if incidents:
        avg_lat = sum(inc.get("lat", 12.9716) for inc in incidents) / len(incidents)
        avg_lon = sum(inc.get("lon", 77.5946) for inc in incidents) / len(incidents)
        return (avg_lat, avg_lon)
    return (12.9716, 77.5946)  # Bangalore default
