"""
OSRM Client module for real road network distance querying.
Includes automatic fallback to Haversine straight-line distance if OSRM is unavailable.
"""
import math
import time
import requests
from typing import Dict, List, Any

class OSRMClient:
    """Client for communicating with a local Open Source Routing Machine (OSRM) server."""
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 5):
        """Initialize the OSRM client and test connectivity."""
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.available = False
        
        # Test connectivity
        try:
            # Query a test route in Colombo, Sri Lanka
            test_url = f"{self.base_url}/route/v1/driving/79.8612,6.9271;79.8650,6.9300?overview=false"
            response = requests.get(test_url, timeout=self.timeout)
            if response.status_code == 200:
                self.available = True
                print(f"[OK] OSRM connected at {self.base_url}")
            else:
                print(f"[WARN] OSRM returned status {response.status_code}. Falling back to haversine.")
        except requests.exceptions.RequestException:
            print("[WARN] OSRM unavailable. Falling back to haversine.")

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great-circle distance between two points in meters."""
        R = 6371000  # Radius of earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _estimate_duration(self, distance_m: float) -> float:
        """Estimate duration in seconds assuming 40 km/h average speed."""
        speed_mps = 40.0 * (1000.0 / 3600.0)
        return distance_m / speed_mps

    def get_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
        """
        Get driving distance and duration between two points.
        Returns fallback haversine distance if OSRM is unavailable.
        """
        if self.available:
            url = f"{self.base_url}/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
            retries = 2
            for attempt in range(retries):
                try:
                    res = requests.get(url, timeout=self.timeout)
                    if res.status_code == 200:
                        data = res.json()
                        if data.get("routes"):
                            route = data["routes"][0]
                            return {
                                "distance_m": float(route.get("distance", 0.0)),
                                "duration_s": float(route.get("duration", 0.0)),
                                "source": "osrm"
                            }
                except requests.exceptions.RequestException:
                    time.sleep(0.1)
        
        # Fallback
        dist = self._haversine(lat1, lon1, lat2, lon2)
        dur = self._estimate_duration(dist)
        return {
            "distance_m": dist,
            "duration_s": dur,
            "source": "haversine_error" if self.available else "haversine"
        }

    def get_distance_matrix(self, origins: List[Dict[str, Any]], destinations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get an NxM distance and duration matrix.
        origins/destinations format: [{"lat": float, "lon": float, "id": str}]
        """
        if self.available and origins and destinations:
            # Combine coordinates for the query
            all_coords = origins + destinations
            coords_str = ";".join([f"{c['lon']},{c['lat']}" for c in all_coords])
            
            src_indices = ",".join(str(i) for i in range(len(origins)))
            dst_indices = ",".join(str(len(origins) + i) for i in range(len(destinations)))
            
            url = f"{self.base_url}/table/v1/driving/{coords_str}?sources={src_indices}&destinations={dst_indices}"
            
            retries = 2
            for attempt in range(retries):
                try:
                    res = requests.get(url, timeout=self.timeout)
                    if res.status_code == 200:
                        data = res.json()
                        return {
                            "distances": data.get("distances", []),
                            "durations": data.get("durations", []),
                            "source": "osrm"
                        }
                except requests.exceptions.RequestException:
                    time.sleep(0.1)

        # Fallback NxM matrix
        dist_matrix = []
        dur_matrix = []
        for orig in origins:
            dist_row = []
            dur_row = []
            for dest in destinations:
                d = self._haversine(orig["lat"], orig["lon"], dest["lat"], dest["lon"])
                dist_row.append(d)
                dur_row.append(self._estimate_duration(d))
            dist_matrix.append(dist_row)
            dur_matrix.append(dur_row)
            
        return {
            "distances": dist_matrix,
            "durations": dur_matrix,
            "source": "haversine"
        }

    def get_nearest_road(self, lat: float, lon: float) -> Dict[str, Any]:
        """Snap a coordinate to the nearest road network point."""
        if self.available:
            url = f"{self.base_url}/nearest/v1/driving/{lon},{lat}"
            try:
                res = requests.get(url, timeout=self.timeout)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("waypoints"):
                        wp = data["waypoints"][0]
                        return {
                            "lat": float(wp["location"][1]),
                            "lon": float(wp["location"][0]),
                            "name": wp.get("name", "")
                        }
            except requests.exceptions.RequestException:
                pass
        
        # Fallback
        return {"lat": lat, "lon": lon, "name": "unknown (fallback)"}

    def health_check(self) -> Dict[str, Any]:
        """Return the health status of the OSRM client."""
        return {
            "available": self.available,
            "base_url": self.base_url,
            "version": "1.0.0" if self.available else "N/A"
        }
