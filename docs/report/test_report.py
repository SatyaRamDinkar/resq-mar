"""
Tests for the report generator.
"""
import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from report_generator import generate_title_page, generate_toc, read_chapter, generate_full_report

def test_title_page_generation():
    title = generate_title_page()
    assert "RESQ-MAR: AI-Powered Multi-Agent" in title
    assert "Satya Ram Dinkar" in title

def test_toc_generation():
    chapters = ["Intro", "Lit", "System", "Impl", "Eval", "Conc", "References"]
    toc = generate_toc(chapters)
    assert "Chapter 1: Intro" in toc
    assert "References" in toc

def test_chapter_reading(tmp_path):
    test_file = tmp_path / "test.md"
    test_file.write_text("Hello World", encoding='utf-8')
    content = read_chapter(str(test_file))
    assert content == "Hello World"

def test_full_report_generation(tmp_path):
    # Just test that the function creates a file and doesn't crash
    # when chapters don't exist (it should handle it gracefully)
    out_file = tmp_path / "Report.md"
    generate_full_report(str(out_file))
    assert out_file.exists()
    assert "RESQ-MAR" in out_file.read_text(encoding='utf-8')
