import streamlit as st
import os
import tempfile
from typing import Dict, Any

def render_voice_uploader() -> str:
    """
    Render a file uploader for emergency audio files.
    
    Returns:
        str: Path to the saved temporary audio file, or None if no file.
    """
    st.markdown("### Upload Audio Recording")
    audio_file = st.file_uploader("Upload emergency call recording (WAV, MP3, M4A)", type=["wav", "mp3", "m4a"])
    
    if audio_file is not None:
        # Save to temp file
        file_ext = os.path.splitext(audio_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(audio_file.getvalue())
            temp_path = tmp_file.name
        
        st.audio(audio_file)
        if "temp_files" not in st.session_state: st.session_state.temp_files = []
        st.session_state.temp_files.append(temp_path)
        return temp_path
    
    return None

def render_microphone_input() -> str:
    """
    Render a microphone recording component.
    Uses st.audio_input if available (Streamlit 1.34+), otherwise provides instructions.
    
    Returns:
        str: Path to the saved temporary audio file, or None if no recording.
    """
    st.markdown("### Record Emergency Call (Live)")
    
    if hasattr(st, "audio_input"):
        # Modern Streamlit natively supports microphone input
        audio_data = st.audio_input("Record emergency details (Speak clearly)")
        
        if audio_data is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_data.getvalue())
                temp_path = tmp_file.name
            if "temp_files" not in st.session_state: st.session_state.temp_files = []
        st.session_state.temp_files.append(temp_path)
        return temp_path
    else:
        # Fallback for older Streamlit versions
        st.warning("st.audio_input is not available in your Streamlit version.")
        st.info("Please upgrade Streamlit (pip install --upgrade streamlit) or use the file uploader above.")
        
    return None

def render_transcription_result(result: Dict[str, Any]) -> None:
    """
    Display the transcription and the downstream IntakeAgent processing results.
    
    Args:
        result (Dict): The full incident dictionary returned by process_voice_emergency.
    """
    if "error" in result:
        st.error(f"Voice Processing Error: {result['error']}")
        return
        
    voice_meta = result.get("voice_metadata", {})
    transcription = voice_meta.get("transcription", "")
    language = voice_meta.get("detected_language", "unknown").upper()
    confidence = voice_meta.get("transcription_confidence", 0.0)
    
    st.markdown("### Transcription Results")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Detected Language", language)
    with col2:
        st.metric("Speech Confidence", f"{confidence:.2f}")
        
    st.info(f"**Transcribed Text:**\n\n\"{transcription}\"")
    
    st.markdown("### AI Extraction (IntakeAgent)")
    with st.spinner("Processing through IntakeAgent..."):
        # If the result dict contains metadata, we show it
        if "incident_type" in result or "metadata" in result:
            st.success("Metadata extracted successfully!")
            st.json(result)
        else:
            st.warning("Waiting for downstream processing...")
