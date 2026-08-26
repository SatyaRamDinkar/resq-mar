"""
Tests for the HTML Academic Poster.
"""
import os
import pytest

def get_poster_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resq_mar_poster.html")

def test_poster_file_exists():
    assert os.path.exists(get_poster_path()), "Poster HTML file does not exist."

def test_poster_contains_title():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "RESQ-MAR: AI-Powered Multi-Agent" in html
    assert "An Open-Source, Zero-Cost Alternative" in html

def test_poster_contains_key_results():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "0.82" in html  # Agentic RAG coverage
    assert "-66.7%" in html  # AET improvement
    assert "100%" in html  # Truck-Drone coverage

def test_poster_contains_architecture():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "+---" in html
    assert "Retrieval" in html
    assert "AET Adaptive" in html
    assert "<pre>" in html

def test_poster_contains_all_sections():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "1. PROBLEM & MOTIVATION" in html
    assert "2. SYSTEM ARCHITECTURE" in html
    assert "3. KEY RESULTS" in html
    assert "4. WHY RESQ-MAR WINS" in html
    assert "5. FULL SYSTEM BENCHMARK" in html

def test_poster_css_inline():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read()
    assert "<style>" in html
    assert "display: grid;" in html
    assert "@page { size: A1 portrait;" in html

def test_poster_no_external_images():
    with open(get_poster_path(), "r", encoding="utf-8") as f:
        html = f.read().lower()
    # Check that there are no standard image tags downloading external assets
    assert "<img" not in html
