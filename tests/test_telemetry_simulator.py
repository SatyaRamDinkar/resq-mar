"""
Unit Tests for Live Dynamic GPS Telemetry Simulator
===================================================
"""

import pytest
from src.utils.telemetry_simulator import (
    TelemetrySimulator,
    haversine_distance,
    calculate_bearing,
)

@pytest.fixture
def vizag_sample_route():
    # Route starting at King George Hospital, traveling through beach road, to collectorate
    return [
        (17.7042, 83.3005),
        (17.7100, 83.3100),
        (17.7180, 83.3180),
        (17.7250, 83.3220),
    ]


def test_haversine_distance_accuracy():
    # Distance between Vizag and nearby point
    p1 = (17.7042, 83.3005)
    p2 = (17.7100, 83.3100)
    dist = haversine_distance(p1, p2)
    assert 1.0 < dist < 2.0  # Approx 1.2-1.5 km


def test_calculate_bearing():
    # Due North: (0, 0) to (1, 0)
    north_bearing = calculate_bearing((0.0, 0.0), (1.0, 0.0))
    assert north_bearing == 0.0 or north_bearing == 360.0

    # Due East: (0, 0) to (0, 1)
    east_bearing = calculate_bearing((0.0, 0.0), (0.0, 1.0))
    assert 89.0 <= east_bearing <= 91.0


def test_simulator_initialization(vizag_sample_route):
    sim = TelemetrySimulator("AMB-TEST-01", vizag_sample_route, average_speed_kmh=50.0)
    assert sim.vehicle_id == "AMB-TEST-01"
    assert sim.total_distance_km > 2.0
    assert len(sim._segment_lengths) == 3


def test_invalid_route_raises_error():
    with pytest.raises(ValueError):
        TelemetrySimulator("AMB-FAIL", [(17.0, 83.0)])


def test_telemetry_progress_boundaries(vizag_sample_route):
    sim = TelemetrySimulator("AMB-01", vizag_sample_route)
    
    # Progress 0.0 (Start)
    pos_start = sim.get_position_at_progress(0.0)
    assert pos_start["status"] == "DISPATCH_ASSIGNED"
    assert pos_start["distance_covered_km"] == 0.0
    assert pos_start["current_coords"] == pytest.approx(vizag_sample_route[0], abs=1e-4)

    # Progress 1.0 (Arrival)
    pos_end = sim.get_position_at_progress(1.0)
    assert pos_end["status"] == "ARRIVED_AT_FACILITY"
    assert pos_end["remaining_distance_km"] == 0.0
    assert pos_end["eta_minutes"] == 0.0
    assert pos_end["current_coords"] == pytest.approx(vizag_sample_route[-1], abs=1e-4)


def test_telemetry_stream_generation(vizag_sample_route):
    sim = TelemetrySimulator("AMB-01", vizag_sample_route)
    stream = sim.generate_telemetry_stream(steps=5)
    assert len(stream) == 5
    assert stream[0]["progress_percent"] == 0.0
    assert stream[-1]["progress_percent"] == 100.0
    assert stream[2]["progress_percent"] == 50.0
