import os
import pytest

MANUAL_PATH = "docs/manual/USER_MANUAL.md"
QUICK_START_PATH = "docs/manual/QUICK_START.md"

def test_user_manual_exists():
    assert os.path.exists(MANUAL_PATH), f"{MANUAL_PATH} does not exist"

def test_quick_start_exists():
    assert os.path.exists(QUICK_START_PATH), f"{QUICK_START_PATH} does not exist"

def test_manual_has_all_chapters():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    expected_chapters = [
        "CHAPTER 1: SYSTEM OVERVIEW",
        "CHAPTER 2: INSTALLATION AND SETUP",
        "CHAPTER 3: STARTING THE SYSTEM",
        "CHAPTER 4: DISPATCHER GUIDE",
        "CHAPTER 5: EMERGENCY OPERATIONS",
        "CHAPTER 6: ADMINISTRATOR GUIDE",
        "CHAPTER 7: TROUBLESHOOTING",
        "CHAPTER 8: DEVELOPER GUIDE"
    ]
    
    for chapter in expected_chapters:
        assert chapter in content, f"Missing chapter: {chapter}"

def test_manual_has_toc():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Table of Contents" in content, "Table of Contents not found"

def test_manual_has_glossary():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "APPENDIX B: GLOSSARY" in content, "Glossary appendix not found"

def test_manual_ascii_only():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    non_ascii_chars = [c for c in content if ord(c) >= 128]
    assert len(non_ascii_chars) == 0, f"Found non-ASCII characters: {set(non_ascii_chars)}"

def test_manual_minimum_length():
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    word_count = len(content.split())
    assert word_count >= 3000, f"Manual is too short. Expected >= 3000 words, got {word_count}"
