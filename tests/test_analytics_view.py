"""
Unit tests for Analytics & Benchmarks View (Publication-grade Plotly Figures).
"""
import pytest
import plotly.graph_objects as go
from frontend.components.analytics_view import (
    build_latency_bar_chart,
    build_routing_scaling_chart,
    build_hallucination_reduction_donut,
    build_resilience_radar_chart
)


class TestAnalyticsView:
    """Test suite for interactive Plotly figures in analytics_view."""

    def test_latency_bar_chart_structure(self):
        """Verify the End-to-End Latency comparison bar chart."""
        fig = build_latency_bar_chart()
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Bar)
        # Verify 3 systems are plotted: ResQ-MAR, Cloud LLMs, Human Dispatch
        assert len(fig.data[0].x) == 3
        # ResQ-MAR latency is 4.10s
        assert fig.data[0].y[0] == 4.10
        # Human dispatch is 320s
        assert fig.data[0].y[2] == 320.00

    def test_routing_scaling_chart_structure(self):
        """Verify the routing concurrency scaling line chart."""
        fig = build_routing_scaling_chart()
        assert isinstance(fig, go.Figure)
        # 3 traces: Local OSRM, ORS, Google Maps
        assert len(fig.data) == 3
        osrm_trace = fig.data[0]
        assert "Local OSRM" in osrm_trace.name
        # OSRM latency stays fast (< 60ms) across 50 requests
        assert osrm_trace.y[-1] < 100

    def test_hallucination_reduction_donut(self):
        """Verify the NDMA RAG grounding donut chart."""
        fig = build_hallucination_reduction_donut()
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert isinstance(fig.data[0], go.Pie)
        # Compliant slice is 95.9%
        assert fig.data[0].values[0] == 95.9
        # Hallucinated slice is 4.1%
        assert fig.data[0].values[1] == 4.1

    def test_resilience_radar_chart_structure(self):
        """Verify the 5-dimension radar spider chart."""
        fig = build_resilience_radar_chart()
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 3
        resq_trace = fig.data[0]
        assert "ResQ-MAR" in resq_trace.name
        # Offline resilience score is 100%
        assert resq_trace.r[0] == 100
