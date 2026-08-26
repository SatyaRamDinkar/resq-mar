"""
Tests for the Reveal.js Presentation.
"""
import os
import pytest

def get_presentation_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "final_review.html")

def test_html_file_exists():
    assert os.path.exists(get_presentation_path()), "Presentation HTML file does not exist."

def test_reveal_js_loaded():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "reveal.js/4.5.0" in html, "Reveal.js CDN not found."

def test_all_slides_present():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    # Simple count of <section> tags assuming flat structure 
    # (or just verify specific slide titles exist)
    assert "RESQ-MAR: AI-Powered Multi-Agent" in html
    assert "When Disaster Strikes" in html
    assert "Four Questions Driving Our Design" in html
    assert "What Exists vs. What is Missing" in html
    assert "Thank You" in html

def test_speaker_notes_present():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    notes_count = html.count('<aside class="notes">')
    assert notes_count == 18, f"Expected 18 speaker notes, found {notes_count}."

def test_ascii_only():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "”" not in html, "Smart quotes detected."
    assert "’" not in html, "Smart quotes detected."

def test_pdf_export_script():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "print-pdf" in html, "PDF export detection script missing."

def test_custom_css():
    with open(get_presentation_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "<style>" in html
    assert ".reveal" in html
