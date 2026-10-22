"""
Unit tests for FleetOptimizer agent (Google OR-Tools Multi-Depot CVRP).
"""
import pytest
from unittest.mock import MagicMock, patch

from src.agents.fleet_optimizer import FleetOptimizer


@pytest.fixture
def sample_depots():
    """3 Hospital Depots in Visakhapatnam region."""
    return [
        {"id": "HOSP_KGH", "name": "King George Hospital", "lat": 17.7088, "lon": 83.3071},
        {"id": "HOSP_CARE", "name": "CARE Hospital Ramnagar", "lat": 17.7214, "lon": 83.3148},
        {"id": "HOSP_APOLLO", "name": "Apollo Hospital Health City", "lat": 17.7554, "lon": 83.3427}
    ]


@pytest.fixture
def sample_incidents():
    """5 Simultaneous emergency incidents across the city."""
    return [
        {"id": "INC_FIRE_1", "lat": 17.7120, "lon": 83.2979, "demand": 1, "priority": 1},
        {"id": "INC_FLOOD_2", "lat": 17.7005, "lon": 83.3180, "demand": 1, "priority": 1},
        {"id": "INC_QUAKE_3", "lat": 17.6868, "lon": 83.2185, "demand": 2, "priority": 2},
        {"id": "INC_MED_4", "lat": 17.7897, "lon": 83.3732, "demand": 1, "priority": 3},
        {"id": "INC_COLLAPSE_5", "lat": 17.7522, "lon": 83.3812, "demand": 1, "priority": 1}
    ]


class TestFleetOptimizer:
    """Test suite for FleetOptimizer CVRP solver."""

    def test_fleet_optimization_3_hospitals_5_incidents(self, sample_depots, sample_incidents):
        """
        Verify that 5 simultaneous incidents across 3 hospitals are properly
        allocated and solved to optimal/feasible status.
        """
        # 3 vehicles with capacity 2 each = total capacity 6 (demand = 1+1+2+1+1 = 6)
        capacities = [2, 2, 2]
        optimizer = FleetOptimizer()

        result = optimizer.optimize_fleet(
            incidents=sample_incidents,
            hospital_depots=sample_depots,
            vehicle_capacities=capacities
        )

        assert result["status"] in ["OPTIMAL", "FEASIBLE"]
        assert result["total_distance_km"] > 0
        assert result["total_duration_min"] > 0
        assert len(result["vehicle_routes"]) == 3
        assert len(result["unassigned_incidents"]) == 0
        assert len(result["incident_assignments"]) == 5

        # Verify each incident is assigned to an active vehicle
        for inc in sample_incidents:
            assert inc["id"] in result["incident_assignments"]
            assigned_veh = result["incident_assignments"][inc["id"]]["vehicle_id"]
            assert assigned_veh is not None

    def test_offline_haversine_fallback(self, sample_depots, sample_incidents):
        """
        Test that when OSRM is offline or unreachable, FleetOptimizer gracefully
        falls back to offline Haversine distance calculations without failing.
        """
        mock_osrm = MagicMock()
        mock_osrm.available = False
        mock_osrm.get_distance_matrix.side_effect = Exception("OSRM Offline Connection Refused")

        optimizer = FleetOptimizer(osrm_client=mock_osrm)
        result = optimizer.optimize_fleet(
            incidents=sample_incidents,
            hospital_depots=sample_depots,
            vehicle_capacities=[3, 3, 3]
        )

        assert result["status"] in ["OPTIMAL", "FEASIBLE"]
        assert result["routing_source"] == "haversine_offline"
        assert result["total_distance_km"] > 0
        assert len(result["incident_assignments"]) == 5

    def test_capacity_constraint_enforcement(self, sample_depots, sample_incidents):
        """
        Verify that vehicle capacity limits are strictly respected.
        If total demand exceeds fleet capacity, overflowing incidents are marked unassigned.
        """
        # Total demand = 6 (1+1+2+1+1).
        # We supply only 2 vehicles with capacity 1 each = total capacity 2.
        severely_limited_capacities = [1, 1]

        optimizer = FleetOptimizer()
        result = optimizer.optimize_fleet(
            incidents=sample_incidents,
            hospital_depots=sample_depots[:2],
            vehicle_capacities=severely_limited_capacities
        )

        # Capacity constraints must never be violated
        for route in result["vehicle_routes"]:
            assert route["patients_served"] <= route["capacity"]

        # Incidents exceeding capacity must be flagged as unassigned
        assert len(result["unassigned_incidents"]) > 0
        assert result["status"] in ["FEASIBLE", "OPTIMAL"]
        assert result["fleet_utilization_percent"] <= 100.0

    def test_empty_incidents_returns_clean_response(self, sample_depots):
        """Optimizer should handle zero-incident scenarios gracefully."""
        optimizer = FleetOptimizer()
        result = optimizer.optimize_fleet(
            incidents=[],
            hospital_depots=sample_depots
        )

        assert result["status"] == "OPTIMAL"
        assert result["total_distance_km"] == 0.0
        assert len(result["vehicle_routes"]) == 0
        assert len(result["unassigned_incidents"]) == 0

    def test_dict_vehicle_capacities_specification(self, sample_depots, sample_incidents):
        """Test specifying fleet using explicit vehicle dicts with custom hospital affiliations."""
        custom_fleet = [
            {"id": "KGH_Rapid_1", "hospital_id": "HOSP_KGH", "capacity": 3},
            {"id": "Apollo_ICU_1", "hospital_id": "HOSP_APOLLO", "capacity": 4}
        ]

        optimizer = FleetOptimizer()
        result = optimizer.optimize_fleet(
            incidents=sample_incidents,
            hospital_depots=sample_depots,
            vehicle_capacities=custom_fleet
        )

        assert len(result["vehicle_routes"]) == 2
        route_ids = [r["vehicle_id"] for r in result["vehicle_routes"]]
        assert "KGH_Rapid_1" in route_ids
        assert "Apollo_ICU_1" in route_ids
