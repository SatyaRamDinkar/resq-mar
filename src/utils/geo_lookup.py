import math

# Simple metro mapping to States and Regional Languages
METROS = [
    {"city": "Chennai", "state": "Tamil Nadu", "lang": "ta", "lat": 13.0827, "lon": 80.2707},
    {"city": "Mumbai", "state": "Maharashtra", "lang": "mr", "lat": 19.0760, "lon": 72.8777},
    {"city": "Kolkata", "state": "West Bengal", "lang": "bn", "lat": 22.5726, "lon": 88.3639},
    {"city": "Bangalore", "state": "Karnataka", "lang": "kn", "lat": 12.9716, "lon": 77.5946},
    {"city": "Delhi", "state": "Delhi", "lang": "hi", "lat": 28.6139, "lon": 77.2090},
    {"city": "Hyderabad", "state": "Telangana", "lang": "te", "lat": 17.3850, "lon": 78.4867},
    {"city": "Ahmedabad", "state": "Gujarat", "lang": "gu", "lat": 23.0225, "lon": 72.5714},
    {"city": "Pune", "state": "Maharashtra", "lang": "mr", "lat": 18.5204, "lon": 73.8567},
    {"city": "Jaipur", "state": "Rajasthan", "lang": "hi", "lat": 26.9124, "lon": 75.7873},
    {"city": "Lucknow", "state": "Uttar Pradesh", "lang": "hi", "lat": 26.8467, "lon": 80.9462},
]

def get_state_language(lat: float, lon: float):
    """
    Returns the (state_name, language_code, language_name) for the closest metro.
    """
    best = None
    min_dist = float('inf')
    
    for m in METROS:
        dist = math.hypot(m["lat"] - lat, m["lon"] - lon)
        if dist < min_dist:
            min_dist = dist
            best = m
            
    if best:
        lang_names = {
            "ta": "Tamil",
            "te": "Telugu",
            "hi": "Hindi",
            "bn": "Bengali",
            "mr": "Marathi",
            "kn": "Kannada",
            "gu": "Gujarati"
        }
        return best["state"], best["lang"], lang_names.get(best["lang"], "Hindi")
    return "Delhi", "hi", "Hindi"
