import pytest
from src.utils.hazard_checker import get_intersecting_hazards

def test_chennai_cyclone():
    # Chennai coordinates (Lat: 13.08, Lon: 80.27)
    # Should hit Cyclone layer
    hazards = get_intersecting_hazards(13.08, 80.27)
    assert "cyclone" in hazards
    assert "seismic" not in hazards

def test_delhi_seismic():
    # Delhi coordinates (Lat: 28.61, Lon: 77.20)
    # Should hit Seismic layer, miss Cyclone
    hazards = get_intersecting_hazards(28.61, 77.20)
    assert "seismic" in hazards
    assert "cyclone" not in hazards
