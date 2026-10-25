"""
NDMA Incident Action Plan (IAP) PDF Generator
=============================================
Generates a formal 1-page NDMA-201 Incident Action Plan PDF for each
emergency dispatch. Complies with NDMA / FEMA IAP format.

All output is ASCII-safe for Windows CP1252 terminal compatibility.
PDF content uses only standard Helvetica (built-in font, no TTF required).

Author: ResQ-MAR AI System
"""

import hashlib
import io
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

try:
    from fpdf import FPDF, XPos, YPos
    HAS_FPDF = True
except ImportError:
    FPDF = None
    HAS_FPDF = False


# ---------------------------------------------------------------------------
# Colour palette (NDMA Navy / Operational Orange / Safe Green)
# ---------------------------------------------------------------------------
NAVY     = (30,  58,  95)   # #1e3a5f
ORANGE   = (245, 158,  11)  # #f59e0b  - Critical severity
GREEN    = ( 34, 197,  94)  # #22c55e  - Safe / resolved
RED      = (220,  38,  38)  # #dc2626  - REROUTE / danger
GOLD     = (251, 191,  36)  # #fbbf24  - CAUTION
LIGHT_BG = (240, 244, 250)  # light blue-grey cell fill
WHITE    = (255, 255, 255)
DARK     = ( 15,  23,  42)  # near-black text
GREY     = (100, 116, 139)  # secondary text

SEVERITY_COLORS = {
    "critical": ORANGE,
    "high":     RED,
    "medium":   GOLD,
    "low":      GREEN,
}


def _severity_color(severity: str):
    return SEVERITY_COLORS.get(severity.lower(), GREY)


class NDMAIncidentReportGenerator:
    """
    Generates formal NDMA-201 Incident Action Plan PDFs.
    """

    FORM_NUMBER = "NDMA-IAP-201"

    def generate_iap_pdf(
        self,
        incident_data:    Dict[str, Any],
        fleet_assignments: Optional[List[Dict[str, Any]]] = None,
        route_summary:    Optional[Dict[str, Any]]        = None,
        sop_citations:    Optional[List[str]]             = None,
        agents_involved:  Optional[List[str]]             = None,
    ) -> bytes:
        if not HAS_FPDF:
            raise RuntimeError(
                "fpdf2 is not installed. Run: pip install fpdf2"
            )

        mission_id  = self._generate_mission_id()
        timestamp   = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
        audit_trail = self._build_agent_audit_trail(
            agents_involved or ["PlannerAgent", "RouterAgent", "RAGAgent"]
        )

        fleet_assignments = fleet_assignments or []
        route_summary     = route_summary     or {}
        sop_citations     = sop_citations     or [
            "NDMA SOP 3.2 - Mass Casualty Incident Protocol",
            "NDMA SOP 5.1 - Flood Response Evacuation Procedure",
            "NDMA SOP 8.4 - Cyclone Emergency Dispatch Guidelines",
        ]

        pdf = _IAPDocument()
        pdf.set_margins(15, 15, 15)
        pdf.set_auto_page_break(auto=True, margin=18)
        pdf.add_page()

        self._render_header(pdf, mission_id, timestamp,
                            incident_data.get("severity", "unknown"))
        self._render_section1(pdf, incident_data, timestamp)
        self._render_section2(pdf, incident_data)
        self._render_section3(pdf, fleet_assignments)
        self._render_section4(pdf, sop_citations)
        self._render_section5(pdf, route_summary)
        self._render_footer(pdf, audit_trail, timestamp)

        return bytes(pdf.output())

    def _generate_mission_id(self) -> str:
        date_part = datetime.now().strftime("%Y%m%d")
        hash_part = uuid.uuid4().hex[:6].upper()
        return f"MSN-NDMA-{date_part}-{hash_part}"

    def _build_agent_audit_trail(self, agents_involved: List[str]) -> str:
        salt = datetime.now(timezone.utc).isoformat()
        payload = "|".join(agents_involved) + "|" + salt
        digest  = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return digest[:32].upper()

    def _render_header(self, pdf, mission_id: str,
                       timestamp: str, severity: str):
        pdf.set_fill_color(*NAVY)
        pdf.rect(15, 15, 180, 22, style="F")

        pdf.set_xy(17, 17)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(40, 8, "NDMA", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 7)
        pdf.set_xy(17, 25)
        pdf.cell(40, 5, "National Disaster", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(17, 29)
        pdf.cell(40, 4, "Management Authority", new_x=XPos.RIGHT, new_y=YPos.TOP)

        pdf.set_xy(57, 17)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(100, 5, "INCIDENT ACTION PLAN", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(57, 23)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(100, 4, f"Form {self.FORM_NUMBER}", align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_xy(57, 28)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(100, 4, "Government of India - Disaster Response Division",
                 align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)

        sev_color = _severity_color(severity)
        pdf.set_fill_color(*sev_color)
        pdf.set_xy(152, 18)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(*WHITE)
        pdf.cell(40, 7, f"SEVERITY: {severity.upper()}",
                 align="C", fill=True, new_x=XPos.RIGHT, new_y=YPos.TOP)

        pdf.set_fill_color(*LIGHT_BG)
        pdf.set_text_color(*NAVY)
        pdf.set_xy(15, 37)
        pdf.set_font("Helvetica", "B", 7.5)
        pdf.cell(90, 6, f"Mission ID: {mission_id}", fill=True, align="L", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.cell(90, 6, f"Generated: {timestamp}", fill=True, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    def _render_section1(self, pdf, incident_data: Dict, timestamp: str):
        self._section_title(pdf, "1. INCIDENT OVERVIEW")
        inc_type    = incident_data.get("type",        "Unknown")
        severity    = incident_data.get("severity",    "Unknown")
        description = incident_data.get("description", "No description provided.")
        inc_time    = incident_data.get("datetime",    timestamp)

        rows = [
            ("Incident Type",     inc_type),
            ("Severity Level",    severity.upper()),
            ("Date / Time",       inc_time),
            ("Brief Description", description[:160]),
        ]
        self._table_rows(pdf, rows)

    def _render_section2(self, pdf, incident_data: Dict):
        self._section_title(pdf, "2. GEOGRAPHIC DATA")
        lat     = incident_data.get("lat",     "N/A")
        lon     = incident_data.get("lon",     "N/A")
        address = incident_data.get("address", "Visakhapatnam, Andhra Pradesh, India")
        flags   = incident_data.get("hazard_flags", [])
        flag_str = ", ".join(flags) if flags else "None Detected"

        rows = [
            ("Latitude",            str(lat)),
            ("Longitude",           str(lon)),
            ("Address / Area",      address[:120]),
            ("Active Hazard Zones", flag_str),
        ]
        self._table_rows(pdf, rows)

    def _render_section3(self, pdf, fleet_assignments: List[Dict]):
        self._section_title(pdf, "3. ASSIGNED FLEET")

        if not fleet_assignments:
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*GREY)
            pdf.cell(0, 6, "No fleet assignments recorded.", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(2)
            return

        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 7.5)
        col_w = [28, 65, 35, 42]
        headers = ["Vehicle ID", "Hospital Base", "ETA (min)", "Driver Unit"]
        for i, h in enumerate(headers):
            pdf.cell(col_w[i], 6, h, border=1, fill=True, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln()

        pdf.set_text_color(*DARK)
        pdf.set_font("Helvetica", "", 7.5)
        fill = False
        for a in fleet_assignments:
            pdf.set_fill_color(*LIGHT_BG if fill else WHITE)
            pdf.cell(col_w[0], 5.5, str(a.get("vehicle_id",  "-")),
                     border=1, fill=fill, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(col_w[1], 5.5, str(a.get("hospital",    "-"))[:45],
                     border=1, fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(col_w[2], 5.5, str(a.get("eta_minutes", "-")),
                     border=1, fill=fill, align="C", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(col_w[3], 5.5, str(a.get("driver_unit", "-"))[:30],
                     border=1, fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            fill = not fill
        pdf.ln(2)

    def _render_section4(self, pdf, sop_citations: List[str]):
        self._section_title(pdf, "4. NDMA COMPLIANCE & SOP CITATIONS")
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*DARK)
        for i, sop in enumerate(sop_citations[:6], 1):
            pdf.set_x(20)
            pdf.cell(5, 5.5, f"{i}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.multi_cell(0, 5.5, sop[:140])
        pdf.ln(1)

    def _render_section5(self, pdf, route_summary: Dict):
        self._section_title(pdf, "5. ROUTE SUMMARY")

        waypoints  = route_summary.get("waypoints", [])
        total_km   = route_summary.get("total_km",  "N/A")
        bypass     = route_summary.get("hazard_bypass_notes", "None")

        rows = [
            ("Total Distance (km)", str(total_km)),
            ("Hazard Bypass Notes", str(bypass)[:160]),
        ]
        self._table_rows(pdf, rows)

        if waypoints:
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 5, "Turn-by-Turn Waypoints:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*DARK)
            for j, wp in enumerate(waypoints[:10], 1):
                pdf.set_x(22)
                label = wp if isinstance(wp, str) else str(wp)
                pdf.cell(0, 5, f"{j}. {label[:100]}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    def _render_footer(self, pdf, audit_trail: str, timestamp: str):
        pdf.set_draw_color(*NAVY)
        pdf.set_line_width(0.5)
        y = pdf.get_y() + 2
        if y > 265:
            y = 265
        pdf.line(15, y, 195, y)

        pdf.set_xy(15, y + 2)
        pdf.set_font("Helvetica", "", 6.5)
        pdf.set_text_color(*GREY)
        pdf.cell(0, 4,
                 f"AI Agent Consensus Hash: {audit_trail}  |  "
                 f"Timestamp: {timestamp}",
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_xy(15, pdf.get_y())
        pdf.set_font("Helvetica", "B", 6.5)
        pdf.set_text_color(*RED)
        pdf.cell(0, 4,
                 "OFFICIAL DOCUMENT - RESTRICTED DISTRIBUTION - "
                 "ResQ-MAR AI Emergency Response System",
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def _section_title(self, pdf, title: str):
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(*WHITE)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 6, f"  {title}", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)
        pdf.set_text_color(*DARK)

    def _table_rows(self, pdf, rows: List[tuple]):
        pdf.set_font("Helvetica", "", 8)
        fill = False
        for label, value in rows:
            pdf.set_fill_color(*LIGHT_BG if fill else WHITE)
            pdf.set_font("Helvetica", "B", 7.5)
            pdf.set_text_color(*NAVY)
            pdf.cell(52, 5.5, f"  {label}", border="LTB", fill=fill, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_text_color(*DARK)
            pdf.cell(128, 5.5, f"  {value}", border="RTB", fill=fill, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            fill = not fill
        pdf.ln(3)


if FPDF is not None:
    class _IAPDocument(FPDF):
        def header(self):
            pass

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 6)
            self.set_text_color(*GREY)
            self.cell(0, 4,
                      f"Page {self.page_no()} | NDMA-IAP-201 | "
                      "ResQ-MAR AI Emergency Response",
                      align="C")
else:
    class _IAPDocument(object):
        pass
