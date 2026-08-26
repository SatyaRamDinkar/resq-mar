"""
FastAPI Router for OSRM Distance and Matrix Operations.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Any
from src.routing.osrm_client import OSRMClient
from src.routing.distance_matrix import build_distance_matrix

router = APIRouter(prefix="/routing", tags=["routing"])

# Initialize client globally for router
osrm_client = OSRMClient()

class MatrixRequest(BaseModel):
    origins: List[Dict[str, Any]]
    destinations: List[Dict[str, Any]]

@router.get("/distance")
async def get_distance(lat1: float, lon1: float, lat2: float, lon2: float):
    """
    Get the point-to-point driving distance and duration.
    Falls back to haversine if OSRM is down.
    """
    return osrm_client.get_distance(lat1, lon1, lat2, lon2)

@router.post("/matrix")
async def get_matrix(req: MatrixRequest):
    """
    Generate an NxM distance and duration matrix.
    Locations must contain 'lat' and 'lon'.
    """
    # Note: distance_matrix.py expects locations to have "id", "lat", "lon"
    # To keep this generic, we just use the raw get_distance_matrix which doesn't mandate "id"
    return osrm_client.get_distance_matrix(req.origins, req.destinations)

@router.get("/health")
async def check_osrm_health():
    """
    Check the health of the backend OSRM server.
    """
    # Force a re-check
    osrm_client.__init__(base_url=osrm_client.base_url, timeout=osrm_client.timeout)
    return osrm_client.health_check()
