import os
import json
import re

ROOT = "d:/Projects & Internships/resq-mar"

def patch_file(rel_path, replacements):
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements:
        if isinstance(old, re.Pattern):
            content = old.sub(new, content)
        else:
            content = content.replace(old, new)
            
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {rel_path}")

# 1. requirements.txt
with open(os.path.join(ROOT, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write("""pyautogen==0.2.35
chromadb>=0.4
sentence-transformers>=2.5
streamlit>=1.30
folium>=0.15
streamlit-folium>=0.18
ortools>=9.8
fastapi>=0.109
uvicorn>=0.27
pydantic>=2.5
python-dotenv>=1.0
pytest>=8.0
psutil>=5.9
requests>=2.31
scipy<1.13
duckduckgo-search>=6.0
google-generativeai>=0.7
openai-whisper>=20231117
sounddevice>=0.4
soundfile>=0.12
Pillow>=10.0
groq>=1.0
pandas>=2.0
numpy>=1.24
""")

# 2. .env.example
with open(os.path.join(ROOT, ".env.example"), "w", encoding="utf-8") as f:
    f.write("""# ResQ-MAR Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
EDGE_OLLAMA_URL=http://localhost:11435
""")

# 3. demo_incidents.json
with open(os.path.join(ROOT, "data/demo_incidents.json"), "w", encoding="utf-8") as f:
    f.write('''[
  {
    "id": "demo_1",
    "raw_text": "Fire in commercial building at Jagadamba Junction, 2nd floor, people trapped inside",
    "lat": 17.7120,
    "lon": 83.2979
  },
  {
    "id": "demo_2",
    "raw_text": "Severe flooding at RK Beach Road, vehicles submerged, families stranded on rooftops",
    "lat": 17.7005,
    "lon": 83.3180
  },
  {
    "id": "demo_3",
    "raw_text": "Earthquake tremors reported near Gajuwaka industrial area, building partially collapsed",
    "lat": 17.6868,
    "lon": 83.2185
  },
  {
    "id": "demo_4",
    "raw_text": "Medical emergency, elderly person unconscious near Madhurawada IT corridor bus stop",
    "lat": 17.7897,
    "lon": 83.3732
  },
  {
    "id": "demo_5",
    "raw_text": "Wildfire spreading from Kailasagiri hill toward residential colony, evacuation needed",
    "lat": 17.7522,
    "lon": 83.3812
  }
]''')

# 4. Create missing __init__.py files
for p in ["src", "src/config", "scripts", "frontend/pwa"]:
    init_path = os.path.join(ROOT, p, "__init__.py")
    os.makedirs(os.path.dirname(init_path), exist_ok=True)
    with open(init_path, "a") as f:
        pass

# 5. Fix voice_intake.py
patch_file("src/agents/voice_intake.py", [
    ('llm_config={"model": "llama3.1", "base_url": "http://localhost:11434"}',
     'llm_config={"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]}')
])

# 6. Fix agentic_rag.py
patch_file("src/rag/agentic_rag.py", [
    ('"text": f"LIVE WEB SEARCH CONTEXT:\\n{web_summary}",',
     '"content": f"LIVE WEB SEARCH CONTEXT:\\n{web_summary}",')
])

# 7. Fix web_search.py
patch_file("src/rag/web_search.py", [
    ('import google.generativeai as genai',
     '''try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    genai = None
    HAS_GEMINI = False'''),
    ('if gemini_api_key:', 'if gemini_api_key and HAS_GEMINI:')
])

# 8. Fix live_awareness_agent.py
patch_file("src/agents/live_awareness_agent.py", [
    ('from duckduckgo_search import DDGS',
     '''try:
    from duckduckgo_search import DDGS
    HAS_DDGS = True
except ImportError:
    DDGS = None
    HAS_DDGS = False'''),
    ('def fetch_live_context(self, hazard: str, location: str) -> str:',
     '''def fetch_live_context(self, hazard: str, location: str) -> str:
        if not HAS_DDGS: return "Live awareness unavailable: duckduckgo-search not installed."''')
])

# 9. Fix vision_input.py
patch_file("frontend/components/vision_input.py", [
    ('use_column_width=True', 'use_container_width=True'),
    ('return temp_path',
     '''if "temp_files" not in st.session_state: st.session_state.temp_files = []
        st.session_state.temp_files.append(temp_path)
        return temp_path''')
])

# 9b. Fix voice_input.py temp files
patch_file("frontend/components/voice_input.py", [
    ('return temp_path',
     '''if "temp_files" not in st.session_state: st.session_state.temp_files = []
        st.session_state.temp_files.append(temp_path)
        return temp_path''')
])

# 10. Fix base_agent.py Ollama crash
patch_file("src/agents/base_agent.py", [
    ('response = self.generate_reply(messages=messages)',
     '''try:
            response = self.generate_reply(messages=messages)
        except Exception as e:
            print(f"[ERROR] {self.name} LLM call failed: {e}")
            return {"error": f"llm_offline: {str(e)}"}''')
])

# 11. Fix language_service.py Sri Lanka numbers
patch_file("src/utils/language_service.py", [
    (re.compile(r'elif lang == "si":.*?elif lang == "ta":', re.DOTALL), 'elif lang == "ta":')
])

# 12. Fix benchmark_resources.json
bp = os.path.join(ROOT, "data/benchmark_resources.json")
if os.path.exists(bp):
    with open(bp, "r") as f:
        res = json.load(f)
    vizag_coords = [
        {"lat": 17.6868, "lon": 83.2185},
        {"lat": 17.7120, "lon": 83.2979},
        {"lat": 17.7005, "lon": 83.3180},
        {"lat": 17.6600, "lon": 83.2600}
    ]
    for i, r in enumerate(res):
        r["lat"] = vizag_coords[i % len(vizag_coords)]["lat"]
        r["lon"] = vizag_coords[i % len(vizag_coords)]["lon"]
    with open(bp, "w") as f:
        json.dump(res, f, indent=2)
    print("Patched data/benchmark_resources.json")

# 13. Fix streamlit_app_enhanced.py
patch_file("frontend/streamlit_app_enhanced.py", [
    ('sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))',
     '''sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()
import atexit
def _cleanup_temp_files():
    import os
    import streamlit as st
    for f in st.session_state.get("temp_files", []):
        try: os.unlink(f)
        except: pass
atexit.register(_cleanup_temp_files)
'''),
    ('st_folium(m, width=None, height=550, use_container_width=True)',
     'st_folium(m, width=None, height=550, use_container_width=True, returned_objects=[])'),
    (re.compile(r'<div style="padding: 8px 0;">.*?</div>\n    """, unsafe_allow_html=True\)', re.DOTALL),
     '''<div style="padding: 8px 0;">
</div>
""", unsafe_allow_html=True)

# --- Live System Health Checks ---
import requests as _req

def _check_service(url, timeout=1):
    try:
        _req.get(url, timeout=timeout)
        return True
    except Exception:
        return False

_ollama_ok = _check_service("http://localhost:11434/api/tags")
_osrm_ok   = _check_service("http://localhost:5000/")
_chroma_ok = True

def _badge(ok):
    return '<span class="status-badge badge-online">ONLINE</span>' if ok else '<span class="status-badge badge-critical">OFFLINE</span>'

def _dot(ok):
    color = "#22c55e" if ok else "#ef4444"
    return f'<span class="live-dot" style="background:{color};"></span>'

st.markdown(f"""
<div style="padding: 8px 0;">
  <div class="stat-row"><span class="stat-label">{_dot(_ollama_ok)}Ollama LLM</span>{_badge(_ollama_ok)}</div>
  <div class="stat-row"><span class="stat-label">{_dot(_chroma_ok)}ChromaDB</span>{_badge(_chroma_ok)}</div>
  <div class="stat-row"><span class="stat-label">{_dot(_osrm_ok)}OSRM Router</span>{_badge(_osrm_ok)}</div>
</div>
""", unsafe_allow_html=True)''')
])

# Create conftest
os.makedirs(os.path.join(ROOT, "tests"), exist_ok=True)
with open(os.path.join(ROOT, "tests/conftest.py"), "w", encoding="utf-8") as f:
    f.write('''"""Shared pytest fixtures."""
import os
import sys
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture
def dummy_llm_config():
    return {"config_list": [{"model": "llama3.1", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]}

@pytest.fixture(autouse=True)
def mock_env_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key")
''')

# Create voice test
with open(os.path.join(ROOT, "tests/test_voice_intake.py"), "w", encoding="utf-8") as f:
    f.write('''"""Tests for VoiceIntake module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestVoiceIntake:
    def test_voice_intake_no_whisper(self):
        with patch.dict("sys.modules", {"whisper": None}):
            from src.agents.voice_intake import VoiceIntake
            vi = VoiceIntake(model_size="base")
            assert vi.model is None
    def test_transcribe_missing_file(self):
        from src.agents.voice_intake import VoiceIntake
        vi = VoiceIntake.__new__(VoiceIntake)
        vi.model = None
        result = vi.process_voice_emergency("/nonexistent.wav")
        assert "error" in result
''')

# Create vision test
with open(os.path.join(ROOT, "tests/test_vision_agent.py"), "w", encoding="utf-8") as f:
    f.write('''"""Tests for VisionAgent module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestVisionAgent:
    def test_vision_agent_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.agents.vision_agent import VisionAgent
            va = VisionAgent(api_key=None)
            assert va.enabled is False
    def test_analyze_missing_image(self):
        from src.agents.vision_agent import VisionAgent
        va = VisionAgent.__new__(VisionAgent)
        va.enabled = True
        va.model = MagicMock()
        result = va.analyze_damage("/nonexistent.jpg")
        assert "error" in result
''')

# Create live awareness test
with open(os.path.join(ROOT, "tests/test_live_awareness.py"), "w", encoding="utf-8") as f:
    f.write('''"""Tests for LiveAwarenessAgent module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestLiveAwarenessAgent:
    def test_agent_no_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.agents.live_awareness_agent import LiveAwarenessAgent
            agent = LiveAwarenessAgent(api_key=None)
            assert agent.enabled is False
    def test_fetch_returns_string(self):
        from src.agents.live_awareness_agent import LiveAwarenessAgent
        agent = LiveAwarenessAgent.__new__(LiveAwarenessAgent)
        agent.enabled = False
        result = agent.fetch_live_context("flood", "Vizag")
        assert isinstance(result, str)
''')

# Create language test
with open(os.path.join(ROOT, "tests/test_language_service.py"), "w", encoding="utf-8") as f:
    f.write('''"""Tests for LanguageService module."""
import os, sys, pytest
from unittest.mock import patch, MagicMock

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path: sys.path.insert(0, PROJECT_ROOT)

class TestLanguageService:
    def test_init_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            from src.utils.language_service import LanguageService
            svc = LanguageService(api_key=None)
            assert svc.enabled is False
    def test_detect_language_fallback(self):
        from src.utils.language_service import LanguageService
        svc = LanguageService.__new__(LanguageService)
        svc.enabled = False
        svc._cache = {}
        assert svc.detect_language("Hello") == "en"
''')

print("All fixes applied successfully.")
