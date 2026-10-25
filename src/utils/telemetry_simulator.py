"""
Live Dynamic GPS Telemetry Simulator
====================================
Simulates real-time ambulance movement along hazard-aware route geometries.
Provides high-frequency GPS coordinate interpolation, dynamic bearing calculations,
speed modeling, and proximity-based event triggers.

Author: ResQ-MAR AI System
"""

import math
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timezone


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great circle distance in kilometers between two points (lat, lon).
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371.0  # Earth radius in km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2.0) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_bearing(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate compass bearing in degrees (0 - 360) from coord1 to coord2.
    """
    lat1 = math.radians(coord1[0])
    lat2 = math.radians(coord2[0])
    diff_lon = math.radians(coord2[1] - coord1[1])

    x = math.sin(diff_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_lon))
    initial_bearing = math.atan2(x, y)
    compass_bearing = (math.degrees(initial_bearing) + 360.0) % 360.0
    return round(compass_bearing, 1)


class TelemetrySimulator:
    """
    Simulates high-precision GPS telemetry streaming for active emergency fleet.
    """

    def __init__(
        self,
        vehicle_id: str,
        route_coordinates: List[Tuple[float, float]],
        target_hospital: str = "Regional Trauma Center",
        average_speed_kmh: float = 48.0,
    ):
        """
        Parameters
        ----------
        vehicle_id : str
            Identifier of the ambulance unit (e.g. 'AMB-01').
        route_coordinates : list of (lat, lon)
            Ordered route polyline waypoints.
        target_hospital : str
            Designated destination facility.
        average_speed_kmh : float
            Baseline transit speed in km/h.
        """
        if not route_coordinates or len(route_coordinates) < 2:
            raise ValueError("route_coordinates must contain at least 2 points.")

        self.vehicle_id = vehicle_id
        self.route_coordinates = route_coordinates
        self.target_hospital = target_hospital
        self.average_speed_kmh = max(10.0, average_speed_kmh)

        # Precompute segment distances and cumulative lengths
        self._segment_lengths: List[float] = []
        self._cumulative_lengths: List[float] = [0.0]
        for i in range(len(self.route_coordinates) - 1):
            dist = haversine_distance(self.route_coordinates[i], self.route_coordinates[i + 1])
            self._segment_lengths.append(dist)
            self._cumulative_lengths.append(self._cumulative_lengths[-1] + dist)

        self.total_distance_km = self._cumulative_lengths[-1]

    def get_position_at_progress(self, progress: float) -> Dict[str, Any]:
        """
        Interpolate vehicle position, current segment, bearing, and remaining ETA
        given completion progress (0.0 to 1.0).

        Parameters
        ----------
        progress : float
            Normalized mission progress from 0.0 (start) to 1.0 (destination).

        Returns
        -------
        dict with keys:
            vehicle_id, current_coords, bearing, speed_kmh,
            distance_covered_km, remaining_distance_km, eta_minutes,
            status, timestamp
        """
        clamped_progress = max(0.0, min(1.0, float(progress)))
        target_dist = clamped_progress * self.total_distance_km

        # Find which segment contains the vehicle
        seg_idx = 0
        for i in range(len(self._segment_lengths)):
            if self._cumulative_lengths[i + 1] >= target_dist:
                seg_idx = i
                break
        else:
            seg_idx = max(0, len(self._segment_lengths) - 1)

        seg_start_dist = self._cumulative_lengths[seg_idx]
        seg_len = self._segment_lengths[seg_idx]
        
        # Segment fraction
        if seg_len > 0:
            seg_fraction = (target_dist - seg_start_dist) / seg_len
            seg_fraction = max(0.0, min(1.0, seg_fraction))
        else:
            seg_fraction = 1.0

        p1 = self.route_coordinates[seg_idx]
        p2 = self.route_coordinates[seg_idx + 1]

        # Linear interpolation of lat/lon
        curr_lat = p1[0] + seg_fraction * (p2[0] - p1[0])
        curr_lon = p1[1] + seg_fraction * (p2[1] - p1[1])
        curr_coords = (round(curr_lat, 6), round(curr_lon, 6))

        # Compass bearing
        bearing = calculate_bearing(p1, p2)

        # Remaining distance & ETA
        remaining_km = max(0.0, self.total_distance_km - target_dist)
        eta_minutes = round((remaining_km / self.average_speed_kmh) * 60.0, 1)

        # Operational status mapping
        if clamped_progress >= 0.99:
            status = "ARRIVED_AT_FACILITY"
        elif clamped_progress >= 0.50:
            status = "PATIENT_ONBOARD_TRANSIT"
        elif clamped_progress > 0.0:
            status = "EN_ROUTE_TO_PATIENT"
        else:
            status = "DISPATCH_ASSIGNED"

        return {
            "vehicle_id": self.vehicle_id,
            "current_coords": curr_coords,
            "bearing": bearing,
            "speed_kmh": round(self.average_speed_kmh, 1),
            "distance_covered_km": round(target_dist, 2),
            "remaining_distance_km": round(remaining_km, 2),
            "eta_minutes": eta_minutes,
            "status": status,
            "destination": self.target_hospital,
            "progress_percent": round(clamped_progress * 100.0, 1),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def generate_telemetry_stream(self, steps: int = 10) -> List[Dict[str, Any]]:
        """
        Generate a complete discrete time-series stream of telemetry frames.
        """
        if steps < 2:
            steps = 2
        stream = []
        for step in range(steps):
            prog = step / (steps - 1)
            stream.append(self.get_position_at_progress(prog))
        return stream
