"""
Performance Metrics Panel Component.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any

def render_performance_metrics(metrics: Dict[str, Any]) -> None:
    """Render 2x4 grid of performance metrics."""
    st.subheader('System Performance')
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Avg Response Time', f"{metrics.get('avg_response_time_ms', 0)} ms", '-15%')
    c2.metric('Total Incidents Handled', metrics.get('total_incidents_handled', 0))
    c3.metric('Incidents Today', metrics.get('incidents_today', 0), '+2')
    c4.metric('Solver Calls Saved', metrics.get('solver_calls_saved', 0), 'AET enabled')
    
    c5, c6, c7, c8 = st.columns(4)
    c5.metric('Coverage %', f"{metrics.get('coverage_percentage', 100):.1f}%")
    c6.metric('Route Quality (0-1)', f"{metrics.get('avg_route_quality', 1.0):.2f}")
    c7.metric('Human Decisions Req', metrics.get('human_decisions_required', 0))
    c8.metric('Human Decisions Made', metrics.get('human_decisions_made', 0))

def render_benchmark_chart(benchmark_data: Dict[str, Any]) -> None:
    """Render Agentic RAG vs Naive RAG chart."""
    st.subheader('RAG Coverage Benchmark')
    df = pd.DataFrame({
        'Naive RAG': benchmark_data.get('naive_rag_coverage', []),
        'Agentic RAG': benchmark_data.get('agentic_rag_coverage', [])
    }, index=benchmark_data.get('labels', []))
    st.bar_chart(df)

def render_routing_efficiency_chart(aet_data: Dict[str, Any], continuous_data: Dict[str, Any]) -> None:
    """Render AET vs Continuous routing chart."""
    st.subheader('Routing Efficiency (Solver Calls)')
    df = pd.DataFrame({
        'Solver Calls': [aet_data.get('solver_calls', 0), continuous_data.get('solver_calls', 0)]
    }, index=[aet_data.get('label', 'AET'), continuous_data.get('label', 'Continuous')])
    st.bar_chart(df)

def get_mock_metrics() -> Dict[str, Any]:
    return {
        'avg_response_time_ms': 1250,
        'total_incidents_handled': 142,
        'incidents_today': 12,
        'solver_calls_saved': 45,
        'coverage_percentage': 96.5,
        'avg_route_quality': 0.92,
        'human_decisions_required': 8,
        'human_decisions_made': 8
    }

def get_mock_benchmark_data() -> Dict[str, Any]:
    return {
        'naive_rag_coverage': [0.4, 0.5, 0.45, 0.55, 0.42],
        'agentic_rag_coverage': [0.85, 0.9, 0.88, 0.92, 0.86],
        'labels': ['S1', 'S2', 'S3', 'S4', 'S5']
    }
