"""
Unit tests for HazardAwareRouter (Geospatial Hazard Route Evaluation & Detours).
"""
import pytest
from src.utils.hazard_routing import HazardAwareRouter


@pytest.fixture
def hazard_router():
    """Fixture providing initialized HazardAwareRouter."""
    return HazardAwareRouter()


class TestHazardAwareRouter:
    """Test suite for HazardAwareRouter."""

    def test_route_intersecting_coastal_cyclone_zone(self, hazard_router):
        """
        A route along the Bay of Bengal coastline (Chennai to Visakhapatnam)
        must be flagged as intersecting the high-risk Cyclone hazard zone.
        """
        # Route points along Andhra / Tamil Nadu coast (inside cyclone polygon)
        coastal_route = [
            [80.2707, 13.0827],  # Chennai
            [80.0500, 14.4400],  # Nellore
            [80.4500, 15.8200],  # Ongole
            [80.6400, 16.5000],  # Vijayawada
            [83.3000, 17.7000]   # Visakhapatnam
        ]

        safety_eval = hazard_router.evaluate_route_safety(coastal_route)

        assert safety_eval["is_safe"] is False
        assert safety_eval["safety_score"] < 70.0
        assert safety_eval["recommendation"] == "REROUTE_MANDATORY"
        assert len(safety_eval["detected_hazards"]) > 0

        hazard_types = [h["hazard_type"] for h in safety_eval["detected_hazards"]]
        assert "cyclone" in hazard_types
        assert len(safety_eval["flagged_segments"]) > 0

    def test_safe_inland_route_zero_penalties(self, hazard_router):
        """
        A safe inland route away from the coast, northern seismic belt, and ganga flood basin
        (e.g., Pune to Solapur in western-central Maharashtra) should have 100% safety score.
        """
        inland_route = [
            [73.8567, 18.5204],  # Pune
            [74.5000, 18.2000],  # Daund
            [75.2000, 17.9000],  # Kurduvadi
            [75.9064, 17.6599]   # Solapur
        ]

        safety_eval = hazard_router.evaluate_route_safety(inland_route)

        assert safety_eval["is_safe"] is True
        assert safety_eval["safety_score"] == 100.0
        assert safety_eval["recommendation"] == "PROCEED"
        assert len(safety_eval["detected_hazards"]) == 0
        assert len(safety_eval["flagged_segments"]) == 0
        assert safety_eval["hazard_points_count"] == 0

    def test_dynamic_detour_generation_for_hazard_route(self, hazard_router):
        """
        When requesting a detour for a coastal cyclone danger route, the router must
        dynamically generate a bypass waypoint and improve the route safety score.
        """
        origin = [13.0827, 80.2707]      # Chennai [lat, lon]
        destination = [17.7000, 83.3000] # Visakhapatnam [lat, lon]

        detour_res = hazard_router.find_safe_detour(
            start_coords=origin,
            end_coords=destination
        )

        assert detour_res["detour_required"] is True
        assert detour_res["detour_status"] in ["SUCCESS", "PARTIAL_IMPROVEMENT"]
        assert detour_res["safety_improvement"] > 0
        assert detour_res["detour_route"]["bypass_waypoint"] is not None

        # Verify detour geometry was constructed
        assert len(detour_res["detour_route"]["geometry"]) > 2
        # Detour safety score must be higher than original dangerous route
        assert (
            detour_res["detour_route"]["safety"]["safety_score"] >
            detour_res["original_route"]["safety"]["safety_score"]
        )

    def test_no_detour_needed_for_safe_path(self, hazard_router):
        """A safe inland path should report detour_required = False."""
        pune = [18.5204, 73.8567]
        solapur = [17.6599, 75.9064]

        detour_res = hazard_router.find_safe_detour(
            start_coords=pune,
            end_coords=solapur
        )

        assert detour_res["detour_required"] is False
        assert detour_res["detour_status"] == "NO_DETOUR_NEEDED"
        assert detour_res["safety_improvement"] == 0.0

    def test_lat_lon_and_lon_lat_normalization(self, hazard_router):
        """Disambiguate [lat, lon] vs [lon, lat] for Indian coordinates."""
        # [lat, lon] input
        lon1, lat1 = hazard_router.normalize_coordinate([17.70, 83.30])
        assert round(lat1, 2) == 17.70
        assert round(lon1, 2) == 83.30

        # [lon, lat] input
        lon2, lat2 = hazard_router.normalize_coordinate([83.30, 17.70])
        assert round(lat2, 2) == 17.70
        assert round(lon2, 2) == 83.30

        # dict input
        lon3, lat3 = hazard_router.normalize_coordinate({"lat": 17.70, "lon": 83.30})
        assert round(lat3, 2) == 17.70
        assert round(lon3, 2) == 83.30
