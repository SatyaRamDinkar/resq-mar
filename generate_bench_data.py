import os
import json
import random

random.seed(42)

def generate_incidents():
    incidents = []
    types_dist = {
        'flood': [('low', 5), ('medium', 4), ('high', 4), ('critical', 2)],
        'fire': [('low', 3), ('medium', 3), ('high', 4), ('critical', 2)],
        'earthquake': [('low', 2), ('medium', 3), ('high', 3), ('critical', 2)],
        'medical': [('low', 2), ('medium', 2), ('high', 3), ('critical', 1)],
        'complex': [('critical', 5)]
    }
    
    idx = 1
    for itype, distribution in types_dist.items():
        for severity, count in distribution:
            for _ in range(count):
                req_res = []
                if itype == 'flood': req_res = ['rescue_boat', 'ambulance']
                elif itype == 'fire': req_res = ['fire_truck', 'ambulance']
                elif itype == 'medical': req_res = ['ambulance']
                elif itype == 'complex': req_res = ['fire_truck', 'ambulance', 'drone']
                else: req_res = ['drone', 'ambulance']

                incidents.append({
                    "id": f"BENCH_{idx:03d}",
                    "type": itype,
                    "severity": severity,
                    "description": f"Raw 911 report: Emergency involving {itype} with {severity} severity.",
                    "location": {
                        "lat": round(random.uniform(6.85, 6.98), 4),
                        "lon": round(random.uniform(79.80, 79.95), 4)
                    },
                    "timestamp": "2026-10-15T08:30:00",
                    "required_resources": req_res,
                    "expected_sop": f"SOP-{itype.upper()[:3]}-001"
                })
                idx += 1
    return incidents

def generate_resources():
    resources = []
    specs = [
        ('ambulance', 5, 80.0, 2),
        ('fire_truck', 4, 70.0, 4),
        ('rescue_boat', 3, 30.0, 6),
        ('drone', 3, 120.0, 1)
    ]
    
    idx = 1
    for rtype, count, speed, cap in specs:
        for _ in range(count):
            resources.append({
                "id": f"RES_{idx:03d}",
                "type": rtype,
                "lat": round(random.uniform(6.85, 6.98), 4),
                "lon": round(random.uniform(79.80, 79.95), 4),
                "base_location": f"Station {random.randint(1, 5)}",
                "speed_kmh": speed,
                "capacity": cap
            })
            idx += 1
    return resources

os.makedirs('data', exist_ok=True)
with open('data/benchmark_incidents.json', 'w') as f:
    json.dump(generate_incidents(), f, indent=2)

with open('data/benchmark_resources.json', 'w') as f:
    json.dump(generate_resources(), f, indent=2)

print("Generated benchmark data files.")
