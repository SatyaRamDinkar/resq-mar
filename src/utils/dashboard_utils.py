"""
Utility functions for the ResQ-MAR Enhanced Dashboard.
"""
import math
import json
from datetime import datetime
from typing import Dict, Any, List

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in kilometers between two lat/lon points."""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def check_incident_coverage(incident: Dict[str, Any], resources: List[Dict[str, Any]], radius_km: float = 5.0) -> bool:
    """Return True if any available resource is within radius_km of the incident."""
    lat1, lon1 = incident.get('lat', 0.0), incident.get('lon', 0.0)
    for res in resources:
        if res.get('available', False):
            lat2, lon2 = res.get('lat', 0.0), res.get('lon', 0.0)
            dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
            if dist <= radius_km:
                return True
    return False

def format_timestamp(dt) -> str:
    """Return YYYY-MM-DD HH:MM:SS format string from datetime or ISO string."""
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            return dt
    if isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return str(dt)

def generate_plan_id() -> str:
    """Return unique plan ID: PLAN-{timestamp}-{random_4_digits}."""
    import random
    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    rnd = random.randint(1000, 9999)
    return f'PLAN-{ts}-{rnd}'

def serialize_state(state: Dict[str, Any]) -> str:
    """Convert dict to JSON string, handle datetime serialization."""
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f'Type {type(obj)} not serializable')
    return json.dumps(state, default=default_serializer)

def deserialize_state(json_str: str) -> Dict[str, Any]:
    """Convert JSON string back to dict."""
    return json.loads(json_str)
