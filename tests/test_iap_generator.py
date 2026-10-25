"""
Unit Tests for NDMA Incident Action Plan (IAP) PDF Generator
============================================================
"""

import pytest
from src.utils.iap_generator import NDMAIncidentReportGenerator, HAS_FPDF

@pytest.fixture
def sample_incident():
    return {
        "type": "Flash Flood & Cyclone",
        "severity": "critical",
        "description": "Severe inundation in low-lying coastal sector with trapped citizens.",
        "lat": 17.6868,
        "lon": 83.2185,
        "address": "Beach Road, Visakhapatnam, Andhra Pradesh",
        "hazard_flags": ["Cyclone Danger Zone", "Flood Inundation Level-2"],
        "datetime": "2026-10-25 21:00:00 UTC",
    }

@pytest.fixture
def sample_fleet():
    return [
        {
            "vehicle_id": "AMB-01",
            "hospital": "King George Hospital",
            "eta_minutes": 8.5,
            "driver_unit": "NDRF Unit Alpha",
        },
        {
            "vehicle_id": "AMB-02",
            "hospital": "Apollo Hospital Vizag",
            "eta_minutes": 14.2,
            "driver_unit": "SDRF Coastal Unit",
        },
    ]

@pytest.fixture
def sample_route():
    return {
        "total_km": 12.4,
        "hazard_bypass_notes": "Bypassed flooded NH-16 underpass via Coastal Outer Ring Road.",
        "waypoints": [
            "King George Hospital Base",
            "Turn left on Maharanipeta Main Rd",
            "Detour via Collectorate Flyover",
            "Arrival at Beach Road Sector 4",
        ],
    }

@pytest.fixture
def sample_sops():
    return [
        "NDMA SOP 3.2 - Mass Casualty Incident Protocol",
        "NDMA SOP 5.1 - Urban Flood Evacuation Standard",
    ]


def test_iap_pdf_generation_basic(sample_incident, sample_fleet, sample_route, sample_sops):
    if not HAS_FPDF:
        pytest.skip("fpdf2 not installed")

    gen = NDMAIncidentReportGenerator()
    pdf_bytes = gen.generate_iap_pdf(
        incident_data=sample_incident,
        fleet_assignments=sample_fleet,
        route_summary=sample_route,
        sop_citations=sample_sops,
        agents_involved=["PlannerAgent", "HazardAwareRouter", "RAGGroundingAgent"],
    )

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")


def test_iap_pdf_minimal_inputs():
    if not HAS_FPDF:
        pytest.skip("fpdf2 not installed")

    gen = NDMAIncidentReportGenerator()
    minimal_incident = {
        "type": "General Emergency",
        "severity": "medium",
    }
    pdf_bytes = gen.generate_iap_pdf(incident_data=minimal_incident)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_mission_id_format():
    gen = NDMAIncidentReportGenerator()
    mission_id = gen._generate_mission_id()
    assert mission_id.startswith("MSN-NDMA-")
    parts = mission_id.split("-")
    assert len(parts) == 4
    assert len(parts[2]) == 8  # YYYYMMDD
    assert len(parts[3]) == 6  # 6-char hex


def test_audit_trail_hashing():
    gen = NDMAIncidentReportGenerator()
    agents = ["IntakeAgent", "RouterAgent"]
    hash1 = gen._build_agent_audit_trail(agents)
    assert len(hash1) == 32
    assert hash1.isupper()
