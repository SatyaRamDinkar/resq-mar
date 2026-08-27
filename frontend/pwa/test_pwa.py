import os
import json
from pathlib import Path

PWA_DIR = Path("frontend/pwa")
INDEX_PATH = PWA_DIR / "index.html"
MANIFEST_PATH = PWA_DIR / "manifest.json"
SW_PATH = PWA_DIR / "sw.js"
APP_PATH = PWA_DIR / "app.js"

def test_index_html_exists():
    assert INDEX_PATH.exists(), "index.html does not exist"

def test_manifest_exists():
    assert MANIFEST_PATH.exists(), "manifest.json does not exist"
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert "name" in data
        assert "short_name" in data
        assert "start_url" in data
        assert "display" in data

def test_service_worker_exists():
    assert SW_PATH.exists(), "sw.js does not exist"

def test_app_js_exists():
    assert APP_PATH.exists(), "app.js does not exist"

def test_manifest_icons():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        icons = data.get("icons", [])
        sizes = [icon.get("sizes") for icon in icons]
        assert "192x192" in sizes
        assert "512x512" in sizes

def test_manifest_theme_color():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data.get("theme_color") == "#e94560"

def test_index_has_service_worker_registration():
    # Registration should be in app.js or index.html
    has_reg = False
    with open(APP_PATH, "r", encoding="utf-8") as f:
        if "navigator.serviceWorker.register" in f.read():
            has_reg = True
    assert has_reg, "Service worker registration not found in app.js"

def test_index_has_manifest_link():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        assert 'rel="manifest"' in f.read(), "Manifest link not found in index.html"

def test_offline_keywords_in_html():
    with open(INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read().lower()
        assert "offline" in content
        assert "cached" in content
        assert "emergency" in content

def test_ascii_only():
    files_to_check = [INDEX_PATH, MANIFEST_PATH, SW_PATH, APP_PATH]
    for file_path in files_to_check:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                non_ascii = [c for c in content if ord(c) >= 128]
                assert len(non_ascii) == 0, f"Non-ASCII characters found in {file_path}: {set(non_ascii)}"
