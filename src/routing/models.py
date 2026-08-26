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
    is_roadblocked: bool = Field(default=False, description="True if unreachable by ground vehicles")
    drone_accessible: bool = Field(default=True, description="True if drone can reach it")


class Vehicle(BaseModel):
    """Represents an emergency response vehicle assigned to a depot."""
    id: str = Field(..., description="Unique identifier for this vehicle")
    capacity: int = Field(..., description="Maximum number of people this vehicle can transport")
    speed_kmh: float = Field(default=40.0, description="Average travel speed in km/h")
    start_location_id: str = Field(..., description="ID of the depot where this vehicle starts")
    vehicle_type: str = Field(default="truck", description="'truck' or 'drone'")
    is_aerial: bool = Field(default=False, description="True if aerial vehicle")
    launch_from: str = Field(default=None, description="ID of the truck this drone launches from, if applicable")


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

class DroneSubRoute(BaseModel):
    """Represents a sub-route performed by a drone launched from a truck."""
    drone_id: str
    launch_truck_id: str
    truck_location_id: str
    served_locations: List[str]
    flight_distance_km: float
    flight_time_min: int
    payload_delivered: int

class CollaborativeRoutingResult(BaseModel):
    """The output of the collaborative truck-drone routing solver."""
    truck_routes: List[Route]
    drone_subroutes: List[DroneSubRoute]
    unassigned: List[str]
    solver_status: str
    total_distance_km: float
    coverage_percentage: float
