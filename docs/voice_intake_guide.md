# ResQ-MAR Voice Intake Guide

## 1. Why Voice Matters
Emergency 911 (or 112/100/108) calls are natively voice-based. 
- **Realism:** Panicked citizens in crisis situations cannot type detailed, formatted text prompts. They speak.
- **Accessibility:** Voice intake dramatically lowers the barrier to entry for reporting emergencies.
- **Multilingual Environments:** In diverse linguistic regions like India or Sri Lanka (supporting Telugu, Hindi, Sinhala, Tamil, English), speech recognition bypasses literacy and language barriers by auto-translating or transcribing directly to the AI.
- **Novelty:** ResQ-MAR is pioneering this space. Adding raw voice intake sets this project apart from standard text-based RAG architectures found in current literature.

## 2. Installation
The VoiceIntake module runs entirely offline using OpenAI's Whisper models.

### Prerequisites
1. **Python Packages**:
   `pip install openai-whisper sounddevice soundfile`
2. **System Dependencies (ffmpeg)**:
   Whisper requires `ffmpeg` to process audio files.
   - **Windows:** `choco install ffmpeg` (or download the executable and add to PATH)
   - **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
   - **MacOS:** `brew install ffmpeg`

### Model Download
Whisper will automatically download the specified model on first run.
- **tiny**: ~39MB (Very fast, less accurate)
- **base**: ~74MB (Recommended default, good balance of speed and accuracy)
- **small**: ~244MB (Slower, higher accuracy)

## 3. Usage
The Voice Intake pipeline can be accessed via the Streamlit dashboard or programmatically.

- **Upload Audio File:** Dispatchers or edge devices can upload pre-recorded `.wav`, `.mp3`, or `.m4a` files.
- **Live Recording:** Dispatchers can use the Streamlit interface (`st.audio_input`) to record live audio directly through the browser.
- **Pipeline Flow:** 
  1. The audio is captured.
  2. `VoiceIntake` transcribes the audio to text (offline).
  3. The transcribed text is automatically forwarded to the `IntakeAgent`.
  4. The `IntakeAgent` extracts the hazard type, location, and urgency as if it were a text prompt.
  5. The standard RAG routing pipeline continues seamlessly.

## 4. Language Support
Whisper is a massively multilingual model trained on 99 languages.
- **Automatic Detection:** By default, Whisper analyzes the first 30 seconds of audio and detects the language (e.g., English, Telugu, Hindi, Sinhala, Tamil).
- **Manual Override:** You can force a specific language dictionary via `transcribe(audio_path, language="hi")`.

## 5. Accuracy Notes
- **Clean Audio:** In standard call conditions, transcription accuracy sits at ~95%.
- **Noisy Audio:** In disaster environments with background noise (sirens, wind, screaming), accuracy can drop to ~80%.
- **Confidence Metrics:** The system calculates an internal confidence score (`1.0 - no_speech_prob`). Always verify low-confidence transcriptions manually.
