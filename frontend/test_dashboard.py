"""
Smoke test for the Streamlit dashboard module.
Dependencies: pytest
"""
import os
import sys

# Ensure src and frontend can be imported from the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_import_map_utils():
    """Verify the map utility module imports without errors."""
    from src.utils.map_utils import (
        create_depot_marker,
        create_incident_marker,
        create_route_polyline,
        get_map_center,
    )
    assert callable(create_depot_marker)
    assert callable(create_incident_marker)
    assert callable(create_route_polyline)
    assert callable(get_map_center)


def test_map_center_default():
    """When no incidents are given, the center should be Bangalore."""
    from src.utils.map_utils import get_map_center

    lat, lon = get_map_center()
    assert abs(lat - 12.9716) < 0.001
    assert abs(lon - 77.5946) < 0.001


def test_map_center_with_incidents():
    """With incidents provided, the center should be the average."""
    from src.utils.map_utils import get_map_center

    incidents = [
        {"lat": 10.0, "lon": 80.0},
        {"lat": 12.0, "lon": 78.0},
    ]
    lat, lon = get_map_center(incidents)
    assert abs(lat - 11.0) < 0.001
    assert abs(lon - 79.0) < 0.001


def test_demo_incidents_json():
    """Verify the demo incidents file is valid JSON with 5 entries."""
    import json

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "demo_incidents.json",
    )
    with open(json_path, "r") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 5
    for inc in data:
        assert "id" in inc
        assert "raw_text" in inc
        assert "lat" in inc
        assert "lon" in inc
