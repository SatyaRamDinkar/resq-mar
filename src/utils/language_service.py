import os
import hashlib
from typing import Dict, Any

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class LanguageService:
    """
    Multi-language support module for ResQ-MAR.
    Translates incident reports, SOPs, and agent responses using the Gemini Free Tier.
    Includes in-memory caching to avoid redundant API calls.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the LanguageService.
        
        Args:
            api_key (str): Optional Gemini API key. Defaults to GEMINI_API_KEY env var.
        """
        self._cache = {}
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.enabled = False
        
        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
                # Using 1.5-flash for fast, free-tier optimized translations
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.enabled = True
                print("[OK] LanguageService initialized with Gemini API.")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini API: {e}")
                print("[WARN] Language support disabled. Falling back to English.")
        else:
            print("[WARN] No Gemini key provided or package missing.")
            print("[WARN] Multi-language support disabled. Falling back to English.")
            
    def _get_cache_key(self, prefix: str, text: str, lang: str) -> str:
        """Generate a unique cache key based on the text hash."""
        text_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
        return f"{prefix}_{lang}_{text_hash}"

    def detect_language(self, text: str) -> str:
        """
        Auto-detect the language of the incoming incident text.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            str: 2-letter ISO language code (e.g., 'en', 'hi', 'te', 'si', 'ta').
        """
        if not self.enabled or not text.strip():
            return "en"
            
        cache_key = self._get_cache_key("detect", text, "none")
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        prompt = (
            "Identify the language of the following text. "
            "Return ONLY the 2-letter ISO 639-1 language code (e.g., en, hi, te, si, ta). "
            "Text: " + text
        )
        
        try:
            response = self.model.generate_content(prompt)
            lang_code = response.text.strip().lower()
            # Clean up potential markdown formatting or extra text
            if len(lang_code) > 2:
                lang_code = lang_code[:2]
                
            self._cache[cache_key] = lang_code
            return lang_code
        except Exception as e:
            print(f"[ERROR] Language detection failed: {e}")
            return "en"

    def translate(self, text: str, target_lang: str) -> str:
        """
        Translate plain text to the target language.
        
        Args:
            text (str): The text to translate.
            target_lang (str): The target language code (e.g., 'hi', 'te').
            
        Returns:
            str: Translated text, or original text if translation fails.
        """
        if not self.enabled or target_lang == "en" or not text.strip():
            return text
            
        cache_key = self._get_cache_key("trans", text, target_lang)
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        prompt = (
            f"Translate the following emergency response text into language code '{target_lang}'. "
            "Keep the translation professional, clear, and actionable. "
            "Return ONLY the translated text.\n\n"
            f"Text:\n{text}"
        )
        
        try:
            response = self.model.generate_content(prompt)
            translated = response.text.strip()
            self._cache[cache_key] = translated
            return translated
        except Exception as e:
            print(f"[ERROR] Translation failed: {e}")
            return text

    def translate_sop(self, sop_markdown: str, target_lang: str) -> str:
        """
        Translate a full SOP document while preserving markdown formatting.
        
        Args:
            sop_markdown (str): The original SOP in Markdown.
            target_lang (str): Target language code.
            
        Returns:
            str: Translated Markdown text.
        """
        if not self.enabled or target_lang == "en" or not sop_markdown.strip():
            return sop_markdown
            
        cache_key = self._get_cache_key("sop", sop_markdown, target_lang)
        if cache_key in self._cache:
            return self._cache[cache_key]
            
        prompt = (
            f"Translate the following Standard Operating Procedure (SOP) into language code '{target_lang}'. "
            "You MUST preserve all Markdown formatting (headers, lists, bold, etc.). "
            "Do not translate technical ID strings or system keys if they are meant for software routing. "
            "Return ONLY the translated Markdown.\n\n"
            f"SOP Markdown:\n{sop_markdown}"
        )
        
        try:
            response = self.model.generate_content(prompt)
            translated = response.text.strip()
            self._cache[cache_key] = translated
            return translated
        except Exception as e:
            print(f"[ERROR] SOP Translation failed: {e}")
            return sop_markdown

    def get_localized_emergency_numbers(self, lang: str) -> Dict[str, str]:
        """
        Return emergency numbers with labels in the target language.
        Note: Using ASCII transliterations for labels to maintain ASCII-only system safety.
        
        Args:
            lang (str): 2-letter language code.
            
        Returns:
            Dict: Dictionary of localized emergency numbers and labels.
        """
        # Default Indian numbers (Andhra Pradesh focused)
        base_numbers = {
            "police": "100",
            "fire": "101",
            "ambulance": "108",
            "national_emergency": "112"
        }
        
        if lang == "si": # Sinhala (Sri Lanka context)
            return {
                "police": "119",
                "police_label": "Polisiya",
                "fire": "110",
                "fire_label": "Gini Niweem",
                "ambulance": "1990",
                "ambulance_label": "Gilan Ratha"
            }
        elif lang == "ta": # Tamil (Sri Lanka / India context)
            return {
                "police": "100",
                "police_label": "Kaval",
                "fire": "101",
                "fire_label": "Thee Anaippu",
                "ambulance": "108",
                "ambulance_label": "Avsara Oorthi"
            }
        elif lang == "hi": # Hindi (India context)
            return {
                **base_numbers,
                "police_label": "Police (Pulis)",
                "fire_label": "Fire (Aag)",
                "ambulance_label": "Ambulance",
                "national_label": "Rashtriya Aapatkal"
            }
        elif lang == "te": # Telugu (Andhra Pradesh context)
            return {
                **base_numbers,
                "police_label": "Police",
                "fire_label": "Fire",
                "ambulance_label": "Ambulance",
                "national_label": "Jathiya Apathkala"
            }
        else: # Default English
            return {
                **base_numbers,
                "police_label": "Police",
                "fire_label": "Fire",
                "ambulance_label": "Ambulance",
                "national_label": "National Emergency"
            }
