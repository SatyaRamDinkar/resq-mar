import os
import time
import tempfile
from typing import Dict, List, Any

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    MIC_AVAILABLE = True
except ImportError:
    MIC_AVAILABLE = False

# Assuming IntakeAgent is in src.agents.intake_agent
try:
    from src.agents.intake_agent import IntakeAgent
except ImportError:
    IntakeAgent = None

class VoiceIntake:
    """
    VoiceIntake module for ResQ-MAR.
    Handles audio transcription using OpenAI's Whisper model (local execution),
    and pipes the transcribed text into the existing IntakeAgent for metadata extraction.
    """
    def __init__(self, model_size: str = "base"):
        """
        Initialize the VoiceIntake module and load the Whisper model.
        
        Args:
            model_size (str): Model size (tiny, base, small, medium, large). Default is 'base' (74MB).
        """
        self.model_size = model_size
        self.model = None
        
        if not WHISPER_AVAILABLE:
            print("[ERROR] openai-whisper is not installed.")
            print("Please run: pip install openai-whisper")
            return
            
        print(f"[*] Loading Whisper model '{model_size}'...")
        try:
            self.model = whisper.load_model(model_size)
            print(f"[OK] Whisper voice intake ready (model: {model_size})")
        except Exception as e:
            print(f"[ERROR] Failed to load Whisper model: {e}")
            print("Ensure ffmpeg is installed on your system.")

    def transcribe(self, audio_path: str, language: str = None) -> Dict[str, Any]:
        """
        Use Whisper to transcribe an audio file.
        
        Args:
            audio_path (str): Path to the audio file.
            language (str, optional): Force a specific language. If None, auto-detects.
            
        Returns:
            Dict: Contains transcription, language, confidence, and segments.
        """
        if not self.model:
            return {"error": "Whisper model not loaded. Is it installed?"}
            
        if not os.path.exists(audio_path):
            return {"error": f"Audio file not found: {audio_path}"}
            
        print(f"[*] Transcribing {audio_path}...")
        try:
            decode_options = {}
            if language:
                decode_options["language"] = language
                
            result = self.model.transcribe(audio_path, **decode_options)
            
            # Extract basic confidence metric if available in segments, else default
            segments = result.get("segments", [])
            avg_confidence = 0.0
            if segments:
                conf_sum = sum(seg.get("no_speech_prob", 0.0) for seg in segments)
                # confidence is roughly 1.0 - no_speech_prob
                avg_confidence = 1.0 - (conf_sum / len(segments))
                
            return {
                "transcription": result.get("text", "").strip(),
                "language": result.get("language", "unknown"),
                "confidence": avg_confidence,
                "segments": segments
            }
        except Exception as e:
            return {"error": f"Transcription failed: {str(e)}"}

    def transcribe_from_microphone(self, duration: int = 10) -> Dict[str, Any]:
        """
        Record from system microphone for a specified duration and transcribe.
        
        Args:
            duration (int): Duration to record in seconds.
            
        Returns:
            Dict: Transcription result.
        """
        if not MIC_AVAILABLE:
            return {"error": "sounddevice or soundfile not installed. Please pip install sounddevice soundfile"}
            
        fs = 16000  # Whisper expects 16kHz
        print(f"[*] Recording for {duration} seconds. Speak now...")
        try:
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
            sd.wait()  # Wait until recording is finished
            print("[*] Recording complete.")
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_path = tmp_file.name
                
            sf.write(temp_path, recording, fs)
            
            result = self.transcribe(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
            return result
        except Exception as e:
            return {"error": f"Microphone recording failed: {str(e)}"}

    def process_voice_emergency(self, audio_path: str, intake_agent: Any = None) -> Dict[str, Any]:
        """
        Transcribe audio and pass the transcription to the IntakeAgent for metadata extraction.
        
        Args:
            audio_path (str): Path to the emergency audio recording.
            intake_agent (IntakeAgent): An instance of IntakeAgent. If None, instantiates one.
            
        Returns:
            Dict: Full incident dictionary including voice metadata.
        """
        transcription_result = self.transcribe(audio_path)
        
        if "error" in transcription_result:
            return {"status": "error", "message": transcription_result["error"]}
            
        text = transcription_result.get("transcription", "")
        
        if intake_agent is None:
            if IntakeAgent:
                intake_agent = IntakeAgent(llm_config={"model": "llama3.1", "base_url": "http://localhost:11434"})
            else:
                return {"error": "IntakeAgent not found."}
                
        # Process the transcribed text using standard text pipeline
        incident_data = intake_agent.process_report(text)
        
        # Inject voice metadata
        incident_data["voice_metadata"] = {
            "original_audio_path": audio_path,
            "transcription": text,
            "detected_language": transcription_result.get("language", "unknown"),
            "transcription_confidence": transcription_result.get("confidence", 0.0)
        }
        
        return incident_data

    def batch_transcribe(self, audio_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple audio files sequentially.
        
        Args:
            audio_paths (List[str]): List of file paths to audio files.
            
        Returns:
            List[Dict]: List of transcription results.
        """
        results = []
        total = len(audio_paths)
        print(f"[*] Starting batch transcription of {total} files...")
        
        for idx, path in enumerate(audio_paths, 1):
            res = self.transcribe(path)
            results.append(res)
            print(f"[+] Transcribed {idx}/{total} files")
            
        return results
