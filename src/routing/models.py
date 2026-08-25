"""
Pydantic models for the VRP routing module.
Dependencies: pydantic
"""
from pydantic import BaseModel, Field
from typing import List


class Location(BaseModel):
    """Represents a geographic point — either a depot, incident site, or hospital."""
    id: str = Field(..., description="Unique identifier for this location")
    lat: float = Field(..., description="Latitude in decimal degrees")
    lon: float = Field(..., description="Longitude in decimal degrees")
    demand: int = Field(default=0, description="Number of people needing assistance (0 for depots)")
    priority: int = Field(default=1, description="Urgency level: 1=low, 2=medium, 3=high, 4=critical")


class Vehicle(BaseModel):
    """Represents an emergency response vehicle assigned to a depot."""
    id: str = Field(..., description="Unique identifier for this vehicle")
    capacity: int = Field(..., description="Maximum number of people this vehicle can transport")
    speed_kmh: float = Field(default=40.0, description="Average travel speed in km/h")
    start_location_id: str = Field(..., description="ID of the depot where this vehicle starts")


class Route(BaseModel):
    """Represents the optimized route for a single vehicle."""
    vehicle_id: str = Field(..., description="ID of the vehicle assigned to this route")
    location_ids: List[str] = Field(default_factory=list, description="Ordered list of location IDs to visit")
    total_distance_km: float = Field(..., description="Total route distance in kilometers")
    estimated_time_min: int = Field(..., description="Estimated total travel time in minutes")
    total_demand: int = Field(..., description="Total number of people served on this route")


class RoutingResult(BaseModel):
    """The complete output of the VRP solver."""
    routes: List[Route] = Field(default_factory=list, description="Optimized routes for each vehicle")
    unassigned: List[str] = Field(default_factory=list, description="Location IDs that could not be assigned to any vehicle")
    solver_status: str = Field(..., description="OR-Tools solver outcome: OPTIMAL, FEASIBLE, or FAILED")
