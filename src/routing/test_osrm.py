"""
Tests for the OSRM Client and Distance Matrix builders.
"""
import pytest
from unittest.mock import patch, Mock
import requests
from src.routing.osrm_client import OSRMClient
from src.routing.distance_matrix import build_distance_matrix, format_matrix_for_ortools

@patch("requests.get")
def test_osrm_client_init_available(mock_get):
    """Test successful initialization when OSRM is running."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    client = OSRMClient()
    assert client.available is True
    assert client.health_check()["available"] is True

@patch("requests.get")
def test_osrm_client_init_unavailable(mock_get):
    """Test graceful fallback when initialization fails."""
    mock_get.side_effect = requests.exceptions.ConnectionError("Refused")
    
    client = OSRMClient()
    assert client.available is False

@patch("requests.get")
def test_get_distance_osrm(mock_get):
    """Test route parsing when OSRM is up."""
    mock_init = Mock()
    mock_init.status_code = 200
    
    mock_route = Mock()
    mock_route.status_code = 200
    mock_route.json.return_value = {"routes": [{"distance": 1500.5, "duration": 120.0}]}
    
    mock_get.side_effect = [mock_init, mock_route]
    
    client = OSRMClient()
    res = client.get_distance(6.9, 79.8, 6.91, 79.81)
    
    assert res["source"] == "osrm"
    assert res["distance_m"] == 1500.5
    assert res["duration_s"] == 120.0

@patch("requests.get")
def test_get_distance_fallback(mock_get):
    """Test that haversine is used when OSRM fails during query."""
    mock_init = Mock()
    mock_init.status_code = 200
    
    mock_get.side_effect = [mock_init, requests.exceptions.Timeout("Timeout"), requests.exceptions.Timeout("Timeout")]
    
    client = OSRMClient()
    res = client.get_distance(6.9, 79.8, 6.91, 79.81)
    
    assert res["source"] == "haversine_error"
    assert res["distance_m"] > 0
    assert res["duration_s"] > 0

@patch("requests.get")
def test_build_distance_matrix_fallback(mock_get):
    """Test NxN matrix construction using fallback."""
    mock_get.side_effect = requests.exceptions.ConnectionError()
    
    client = OSRMClient()
    locs = [{"id": "a", "lat": 6.9, "lon": 79.8}, {"id": "b", "lat": 6.91, "lon": 79.81}]
    
    matrix = build_distance_matrix(locs, client)
    
    assert matrix["source"] == "haversine"
    assert len(matrix["matrix"]) == 2
    assert len(matrix["matrix"][0]) == 2
    assert matrix["matrix"][0][0] == 0.0  # Distance to self is 0

def test_format_matrix_for_ortools():
    """Verify infinity capping and float->int conversion."""
    float_matrix = [
        [0.0, 15.6, 9999999.0],
        [15.6, 0.0, None]
    ]
    int_matrix = format_matrix_for_ortools(float_matrix)
    
    assert int_matrix == [
        [0, 16, 999999],
        [16, 0, 999999]
    ]
