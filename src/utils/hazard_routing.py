"""
HazardAwareRouter: Geospatial Hazard-Aware Route Evaluation & Detour Generation.
Uses Shapely for point-in-polygon and LineString intersection checks against
disaster hazard polygons (cyclones, flood basins, seismic zones).
"""
import os
import json
import math
from typing import List, Dict, Any, Optional, Tuple, Union

from shapely.geometry import shape, Point, LineString, Polygon

from src.routing.osrm_client import OSRMClient


class HazardAwareRouter:
    """
    HazardAwareRouter evaluates road route geometries against real-world
    disaster hazard zones and dynamically calculates safe bypass detours.
    """

    SEVERITY_WEIGHTS = {
        "cyclone": {"severity": "CRITICAL", "penalty_per_pct": 1.5},
        "flood": {"severity": "CRITICAL", "penalty_per_pct": 1.5},
        "seismic": {"severity": "HIGH", "penalty_per_pct": 0.8}
    }

    def __init__(
        self,
        hazard_dir: Optional[str] = None,
        osrm_client: Optional[OSRMClient] = None
    ):
        """
        Initialize the HazardAwareRouter.

        Args:
            hazard_dir: Path to directory containing GeoJSON hazard files.
                        Defaults to project root 'data/hazards'.
            osrm_client: Client for routing queries. If None, instantiates a default.
        """
        if hazard_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.hazard_dir = os.path.join(base_dir, "data", "hazards")
        else:
            self.hazard_dir = hazard_dir

        self.osrm_client = osrm_client if osrm_client is not None else OSRMClient()
        self.hazards: Dict[str, List[Dict[str, Any]]] = self._load_hazards()

    def _load_hazards(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load all GeoJSON hazard boundaries into Shapely polygon objects.
        """
        hazards_map = {}
        if not os.path.exists(self.hazard_dir):
            return hazards_map

        for fname in os.listdir(self.hazard_dir):
            if fname.endswith(".geojson"):
                hazard_type = fname.split(".")[0].lower()
                fpath = os.path.join(self.hazard_dir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        feature_list = []
                        for feature in data.get("features", []):
                            geom = shape(feature["geometry"])
                            props = feature.get("properties", {})
                            feature_list.append({
                                "geometry": geom,
                                "name": props.get("name", f"{hazard_type.capitalize()} Zone"),
                                "type": hazard_type
                            })
                        hazards_map[hazard_type] = feature_list
                except Exception as e:
                    print(f"[WARN] Failed to load hazard file {fname}: {e}")

        return hazards_map

    @staticmethod
    def normalize_coordinate(coord: Union[List[float], Tuple[float, float], Dict[str, float]]) -> Tuple[float, float]:
        """
        Normalize coordinate to (lon, lat) tuple for Shapely geometry operations.
        Correctly disambiguates [lon, lat] vs [lat, lon] based on Indian bounding box.
        """
        if isinstance(coord, dict):
            return float(coord["lon"]), float(coord["lat"])

        x, y = float(coord[0]), float(coord[1])
        # India geography heuristic: Latitude is roughly 6° to 38° N, Longitude is roughly 68° to 98° E
        if 6.0 <= x <= 38.5 and 68.0 <= y <= 98.5:
            # Format was [lat, lon] -> convert to (lon, lat)
            return y, x
        # Otherwise standard GeoJSON [lon, lat]
        return x, y

    def evaluate_route_safety(self, route_geometry: List[Any]) -> Dict[str, Any]:
        """
        Evaluate route geometry against all active disaster hazard layers.

        Args:
            route_geometry: List of coordinates (either [lon, lat] or [lat, lon] or dicts).

        Returns:
            Dict containing:
                - 'is_safe': bool (True if zero hazards intersected)
                - 'safety_score': float (0.0 to 100.0)
                - 'detected_hazards': list of intersected hazards with impact details
                - 'flagged_segments': list of coordinates inside danger zones
                - 'recommendation': PROCEED, CAUTION, or REROUTE_MANDATORY
        """
        if not route_geometry or len(route_geometry) < 2:
            return {
                "is_safe": True,
                "safety_score": 100.0,
                "detected_hazards": [],
                "flagged_segments": [],
                "total_points": len(route_geometry),
                "hazard_points_count": 0,
                "recommendation": "PROCEED"
            }

        # Normalize points to (lon, lat)
        normalized_points = [self.normalize_coordinate(c) for c in route_geometry]
        line = LineString(normalized_points)

        total_points = len(normalized_points)
        hazard_points = set()
        detected_hazards = []
        flagged_segments = []

        total_penalty = 0.0

        for h_type, hazard_entries in self.hazards.items():
            h_config = self.SEVERITY_WEIGHTS.get(h_type, {"severity": "MODERATE", "penalty_per_pct": 1.0})
            for h_entry in hazard_entries:
                poly: Polygon = h_entry["geometry"]
                h_name = h_entry["name"]

                # Check LineString intersection or Point containment
                line_intersects = poly.intersects(line)
                points_inside = [
                    (idx, pt) for idx, pt in enumerate(normalized_points)
                    if poly.contains(Point(pt[0], pt[1]))
                ]

                if line_intersects or points_inside:
                    penetration_ratio = len(points_inside) / float(total_points) if total_points > 0 else 0.5
                    # If line cuts polygon but no discrete point lands inside, record small penetration
                    if penetration_ratio == 0.0 and line_intersects:
                        penetration_ratio = 0.10

                    # Proportional penalty based on fraction of points exposed
                    severity_mult = 1.0 if h_config["severity"] == "CRITICAL" else 0.65
                    penalty = min(85.0, penetration_ratio * 85.0 * severity_mult)
                    total_penalty += penalty

                    detected_hazards.append({
                        "hazard_type": h_type,
                        "name": h_name,
                        "severity": h_config["severity"],
                        "penetration_pct": round(penetration_ratio * 100.0, 1),
                        "points_affected": len(points_inside)
                    })

                    for idx, pt in points_inside:
                        hazard_points.add(idx)
                        flagged_segments.append([pt[1], pt[0]])  # Return as [lat, lon]

        safety_score = max(0.0, round(100.0 - total_penalty, 1))
        is_safe = (len(detected_hazards) == 0 and safety_score >= 95.0)

        # Recommendation logic
        critical_hazards = any(h["severity"] == "CRITICAL" for h in detected_hazards)
        if not detected_hazards:
            recommendation = "PROCEED"
        elif critical_hazards or safety_score < 60.0:
            recommendation = "REROUTE_MANDATORY"
        else:
            recommendation = "CAUTION"

        return {
            "is_safe": is_safe,
            "safety_score": safety_score,
            "detected_hazards": detected_hazards,
            "flagged_segments": flagged_segments,
            "total_points": total_points,
            "hazard_points_count": len(hazard_points),
            "recommendation": recommendation
        }

    def _haversine_meters(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in meters."""
        R = 6371000.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        return R * 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))

    def _generate_synthetic_path(self, start: Tuple[float, float], end: Tuple[float, float], num_steps: int = 15) -> List[List[float]]:
        """Generate interpolated [lon, lat] coordinates between start and end."""
        path = []
        lon1, lat1 = start
        lon2, lat2 = end
        for i in range(num_steps + 1):
            fraction = i / float(num_steps)
            curr_lon = lon1 + fraction * (lon2 - lon1)
            curr_lat = lat1 + fraction * (lat2 - lat1)
            path.append([round(curr_lon, 5), round(curr_lat, 5)])
        return path

    def find_safe_detour(
        self,
        start_coords: Union[List[float], Dict[str, float]],
        end_coords: Union[List[float], Dict[str, float]],
        active_hazards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find a safe detour route avoiding active disaster hazard zones.

        Args:
            start_coords: Origin [lat, lon] or {'lat': ..., 'lon': ...}
            end_coords: Destination [lat, lon] or {'lat': ..., 'lon': ...}
            active_hazards: Optional filter for specific hazards to avoid.

        Returns:
            Dict containing:
                - 'detour_required': bool
                - 'detour_status': 'SUCCESS', 'NO_DETOUR_NEEDED', or 'PARTIAL_IMPROVEMENT'
                - 'original_route': dict with geometry and safety evaluation
                - 'detour_route': dict with geometry, safety evaluation, and waypoint details
                - 'safety_improvement': float (points improved)
        """
        start_lon, start_lat = self.normalize_coordinate(start_coords)
        end_lon, end_lat = self.normalize_coordinate(end_coords)

        # 1. Fetch Primary Route from OSRM or synthetic fallback
        primary_geom = None
        alt_geom = None

        if getattr(self.osrm_client, "available", False):
            try:
                osrm_res = self.osrm_client.get_route_geometry(start_lat, start_lon, end_lat, end_lon, alternatives=True)
                if osrm_res and "primary" in osrm_res:
                    primary_geom = osrm_res["primary"]["geometry"]
                if osrm_res and "alternative" in osrm_res:
                    alt_geom = osrm_res["alternative"]["geometry"]
            except Exception:
                primary_geom = None

        if not primary_geom:
            primary_geom = self._generate_synthetic_path((start_lon, start_lat), (end_lon, end_lat))

        # 2. Evaluate Primary Route Safety
        orig_safety = self.evaluate_route_safety(primary_geom)

        # If primary route is already completely safe, no detour needed
        if orig_safety["is_safe"]:
            return {
                "detour_required": False,
                "detour_status": "NO_DETOUR_NEEDED",
                "original_route": {
                    "geometry": primary_geom,
                    "safety": orig_safety
                },
                "detour_route": {
                    "geometry": primary_geom,
                    "safety": orig_safety,
                    "bypass_waypoint": None
                },
                "safety_improvement": 0.0
            }

        # 3. Primary route is in hazard zone -> Check if OSRM alternative is safe
        if alt_geom:
            alt_safety = self.evaluate_route_safety(alt_geom)
            if alt_safety["safety_score"] > orig_safety["safety_score"]:
                return {
                    "detour_required": True,
                    "detour_status": "SUCCESS",
                    "original_route": {
                        "geometry": primary_geom,
                        "safety": orig_safety
                    },
                    "detour_route": {
                        "geometry": alt_geom,
                        "safety": alt_safety,
                        "bypass_waypoint": "osrm_native_alternative"
                    },
                    "safety_improvement": round(alt_safety["safety_score"] - orig_safety["safety_score"], 1)
                }

        # 4. Generate Geometric Safe Bypass Waypoint
        # Compute bounding box of intersected hazards to ensure bypass waypoint is truly safe
        intersected_polys = []
        for h in orig_safety["detected_hazards"]:
            h_type = h["hazard_type"]
            for h_entry in self.hazards.get(h_type, []):
                intersected_polys.append(h_entry["geometry"])

        offset_lon = (start_lon + end_lon) / 2.0
        offset_lat = (start_lat + end_lat) / 2.0

        detected_types = {h["hazard_type"] for h in orig_safety["detected_hazards"]}
        
        if intersected_polys:
            # Aggregate bounds: minx, miny, maxx, maxy
            all_minx = min(p.bounds[0] for p in intersected_polys)
            all_miny = min(p.bounds[1] for p in intersected_polys)
            all_maxx = max(p.bounds[2] for p in intersected_polys)
            all_maxy = max(p.bounds[3] for p in intersected_polys)

            if "cyclone" in detected_types:
                # Coastal storm surge on East Coast -> Route inland well west of hazard polygon
                offset_lon = round(all_minx - 2.5, 5)
                offset_lat = (start_lat + end_lat) / 2.0
            elif "flood" in detected_types:
                # North river basin -> Route south of hazard polygon
                offset_lat = round(all_miny - 2.0, 5)
                offset_lon = (start_lon + end_lon) / 2.0
            elif "seismic" in detected_types:
                # Northern seismic fault -> Route south
                offset_lat = round(all_miny - 2.0, 5)
                offset_lon = (start_lon + end_lon) / 2.0
            else:
                offset_lon = round(all_minx - 2.0, 5)
        else:
            offset_lon = offset_lon - 2.5

        bypass_waypoint = [round(offset_lon, 5), round(offset_lat, 5)]

        # Construct 2-leg detour: start -> bypass_waypoint -> end
        leg1 = self._generate_synthetic_path((start_lon, start_lat), (offset_lon, offset_lat), num_steps=15)
        leg2 = self._generate_synthetic_path((offset_lon, offset_lat), (end_lon, end_lat), num_steps=15)
        detour_geom = leg1 + leg2[1:]  # Merge legs without duplicating midpoint

        detour_safety = self.evaluate_route_safety(detour_geom)
        improvement = round(max(0.0, detour_safety["safety_score"] - orig_safety["safety_score"]), 1)
        status = "SUCCESS" if detour_safety["safety_score"] >= 80.0 else "PARTIAL_IMPROVEMENT"

        return {
            "detour_required": True,
            "detour_status": status,
            "original_route": {
                "geometry": primary_geom,
                "safety": orig_safety
            },
            "detour_route": {
                "geometry": detour_geom,
                "safety": detour_safety,
                "bypass_waypoint": {"lat": bypass_waypoint[1], "lon": bypass_waypoint[0]}
            },
            "safety_improvement": improvement
        }
