"""Geographic configuration for ResQ-MAR (Full India)."""

COUNTRY = "India"

MAP_CENTER = {"lat": 21.0, "lon": 78.0}
MAP_ZOOM = 4.5

BOUNDING_BOX = {
    "min_lat": 6.5,
    "max_lat": 37.0,
    "min_lon": 68.0,
    "max_lon": 98.0
}

# Reference metro coordinates (lat, lon)
METRO_COORDINATES = {
    "NEW_DELHI": (28.6139, 77.2090),
    "MUMBAI": (19.0760, 72.8777),
    "CHENNAI": (13.0827, 80.2707),
    "KOLKATA": (22.5726, 88.3639),
    "BENGALURU": (12.9716, 77.5946),
    "HYDERABAD": (17.3850, 78.4867),
    "JAIPUR": (26.9124, 75.7873),
    "AHMEDABAD": (23.0225, 72.5714),
    "LUCKNOW": (26.8467, 80.9462),
    "PATNA": (25.5941, 85.1376)
}

DEFAULT_DEPOT = METRO_COORDINATES["NEW_DELHI"]
