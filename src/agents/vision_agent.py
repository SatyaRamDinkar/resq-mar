import os
import json
from typing import Dict, Any

try:
    import PIL.Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class VisionAgent:
    """
    Vision-Based Damage Assessment Agent.
    Analyzes citizen-uploaded disaster photos to determine severity, 
    detect hazards, and route priority in the multi-agent pipeline.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.enabled = False
        
        if not HAS_PIL:
            print("[ERROR] Pillow (PIL) is required for VisionAgent. pip install Pillow")
            return
            
        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-1.5-flash")
                self.enabled = True
                print("[OK] VisionAgent initialized with Gemini 1.5 Flash Vision capabilities.")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini Vision API: {e}")
        else:
            print("[WARN] VisionAgent disabled. Missing GEMINI_API_KEY or google-generativeai.")

    def analyze_damage(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a disaster image and return structured severity metadata.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            Dict: Contains severity, hazards_detected, and reasoning.
        """
        if not self.enabled:
            return {"error": "Vision AI is disabled. Please provide GEMINI_API_KEY."}
            
        if not os.path.exists(image_path):
            return {"error": f"Image not found at path: {image_path}"}
            
        print(f"[*] VisionAgent analyzing image: {image_path}")
        try:
            img = PIL.Image.open(image_path)
            
            prompt = (
                "You are an expert emergency response visual analyst. "
                "Analyze the disaster image provided and assess the damage severity. "
                "Output ONLY a valid JSON object with no markdown formatting or backticks. "
                "Use the following exact format:\n"
                '{"severity": "low|medium|high|critical", '
                '"hazards_detected": ["list", "of", "visible", "hazards"], '
                '"structural_damage": true|false, '
                '"analysis_reasoning": "Brief explanation of why this severity was assigned"}'
            )
            
            response = self.model.generate_content([prompt, img])
            text = response.text.strip()
            
            # Clean up potential markdown formatting from LLM
            if text.startswith("```json"):
                text = text.replace("```json", "", 1)
            if text.startswith("```"):
                text = text.replace("```", "", 1)
            if text.endswith("```"):
                text = text[:-3]
                
            result = json.loads(text.strip())
            
            # Ensure required keys exist
            if "severity" not in result:
                result["severity"] = "unknown"
            if "hazards_detected" not in result:
                result["hazards_detected"] = []
                
            return result
            
        except json.JSONDecodeError as e:
            print(f"[ERROR] VisionAgent failed to parse JSON: {e}\nRaw output: {text}")
            return {"error": "Failed to parse visual analysis structure."}
        except Exception as e:
            print(f"[ERROR] VisionAgent analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
