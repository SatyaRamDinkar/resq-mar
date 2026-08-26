"""
Distance Matrix Builder replacing pure haversine calculations with OSRM network distances.
"""
from typing import List, Dict, Any
from src.routing.osrm_client import OSRMClient

def build_distance_matrix(locations: List[Dict[str, Any]], osrm_client: OSRMClient = None) -> Dict[str, Any]:
    """
    Build a square NxN distance matrix for a list of locations.
    Uses OSRM if available, otherwise falls back to Haversine.
    
    locations format: [{"id": "loc1", "lat": 6.9, "lon": 79.8}, ...]
    """
    client = osrm_client if osrm_client else OSRMClient()
    
    result = client.get_distance_matrix(origins=locations, destinations=locations)
    return {
        "matrix": result["distances"],
        "durations": result["durations"],
        "source": result["source"],
        "locations": [loc["id"] for loc in locations]
    }

def build_incident_resource_matrix(incidents: List[Dict[str, Any]], resources: List[Dict[str, Any]], osrm_client: OSRMClient = None) -> Dict[str, Any]:
    """
    Build an IxR distance matrix between incidents and resources.
    """
    client = osrm_client if osrm_client else OSRMClient()
    
    result = client.get_distance_matrix(origins=incidents, destinations=resources)
    return {
        "matrix": result["distances"],
        "durations": result["durations"],
        "source": result["source"]
    }

def format_matrix_for_ortools(matrix: List[List[float]]) -> List[List[int]]:
    """
    Convert a floating point distance matrix into an integer matrix for OR-Tools.
    Caps infinite or completely unreachable values to 999999.
    """
    int_matrix = []
    for row in matrix:
        int_row = []
        for val in row:
            if val is None or val > 999999:
                int_row.append(999999)
            else:
                int_row.append(int(round(val)))
        int_matrix.append(int_row)
    return int_matrix
