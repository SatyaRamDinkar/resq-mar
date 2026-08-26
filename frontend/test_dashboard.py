"""
Tests for frontend dashboard components.
"""
import pytest
from unittest.mock import MagicMock
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from frontend.components.approval_panel import render_approval_panel
from src.utils.dashboard_utils import calculate_haversine_distance, check_incident_coverage

def test_calculate_haversine_distance():
    d = calculate_haversine_distance(6.9271, 79.8612, 6.9271, 79.8702)
    assert 0.9 < d < 1.1

def test_check_incident_coverage():
    inc = {'lat': 6.9271, 'lon': 79.8612}
    res = [{'lat': 6.9271, 'lon': 79.8650, 'available': True}]
    assert check_incident_coverage(inc, res, 5.0) is True
    
    res2 = [{'lat': 6.9271, 'lon': 79.8650, 'available': False}]
    assert check_incident_coverage(inc, res2, 5.0) is False

def test_approval_panel_no_pending(monkeypatch):
    mock_st = MagicMock()
    monkeypatch.setattr('frontend.components.approval_panel.st', mock_st)
    render_approval_panel({'pending_approvals': []})
    mock_st.success.assert_called_once()
