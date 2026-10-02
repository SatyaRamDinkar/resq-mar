import os
import json
from shapely.geometry import shape, Point

def load_hazard_polygons():
    hazards = {}
    hazard_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "hazards")
    if not os.path.exists(hazard_dir):
        return hazards

    for fname in os.listdir(hazard_dir):
        if fname.endswith(".geojson"):
            hazard_name = fname.split('.')[0]
            path = os.path.join(hazard_dir, fname)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    polygons = []
                    for feature in data.get('features', []):
                        polygons.append(shape(feature['geometry']))
                    hazards[hazard_name] = polygons
            except Exception:
                pass
    return hazards

HAZARDS_CACHE = load_hazard_polygons()

def get_intersecting_hazards(lat: float, lon: float) -> list:
    """Check if a coordinate falls inside any known hazard polygons."""
    point = Point(lon, lat)  # shapely uses (x, y) = (lon, lat)
    intersecting = []
    
    for h_name, polygons in HAZARDS_CACHE.items():
        for poly in polygons:
            if poly.contains(point):
                intersecting.append(h_name)
                break
                
    return intersecting
