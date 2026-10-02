import pytest
from unittest.mock import patch, MagicMock
from src.routing.osrm_client import OSRMClient

class TestLiveTrackingReRoute:
    def test_osrm_reroute_geometry(self):
        client = OSRMClient()
        client.available = True
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "routes": [
                {
                    "geometry": {"coordinates": [[77.0, 28.0], [77.1, 28.1]]},
                    "duration": 1000,
                    "distance": 5000
                },
                {
                    "geometry": {"coordinates": [[77.0, 28.0], [77.2, 28.2], [77.1, 28.1]]},
                    "duration": 1200,
                    "distance": 6000
                }
            ]
        }
        
        with patch('requests.get', return_value=mock_response):
            res = client.get_route_geometry(28.0, 77.0, 28.1, 77.1, alternatives=True)
            assert "primary" in res
            assert res["primary"]["duration_s"] == 1000
            assert "alternative" in res
            assert res["alternative"]["duration_s"] == 1200
            assert res["alternative"]["distance_m"] == 6000
            assert res["alternative"]["duration_s"] > res["primary"]["duration_s"]
            assert res["alternative"]["geometry"] != res["primary"]["geometry"]

    def test_fallback_geometry(self):
        client = OSRMClient()
        client.available = False
        res = client.get_route_geometry(28.0, 77.0, 28.1, 77.1, alternatives=True)
        assert "primary" in res
        assert "alternative" not in res
        assert len(res["primary"]["geometry"]) == 2
