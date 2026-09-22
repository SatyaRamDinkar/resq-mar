import streamlit as st
import os
import tempfile
from typing import Dict, Any

def render_vision_uploader() -> str:
    """
    Render a file uploader for citizen disaster photos.
    
    Returns:
        str: Path to the saved temporary image file, or None if no file.
    """
    st.markdown("### Upload Disaster Photo")
    image_file = st.file_uploader("Upload visual evidence for damage assessment (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if image_file is not None:
        # Save to temp file
        file_ext = os.path.splitext(image_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(image_file.getvalue())
            temp_path = tmp_file.name
        
        st.image(image_file, caption="Uploaded Evidence", use_container_width=True)
        if "temp_files" not in st.session_state: st.session_state.temp_files = []
        st.session_state.temp_files.append(temp_path)
        return temp_path
    
    return None

def render_vision_result(result: Dict[str, Any]) -> None:
    """
    Display the VisionAgent damage assessment results.
    
    Args:
        result (Dict): The dictionary returned by VisionAgent.analyze_damage.
    """
    if "error" in result:
        st.error(f"Vision Processing Error: {result['error']}")
        return
        
    severity = result.get("severity", "unknown").upper()
    hazards = result.get("hazards_detected", [])
    reasoning = result.get("analysis_reasoning", "No reasoning provided.")
    structural = result.get("structural_damage", False)
    
    st.markdown("### Visual Damage Assessment")
    
    # Severity Badge Coloring
    if severity == "CRITICAL":
        st.error(f"**SEVERITY: {severity}**")
    elif severity == "HIGH":
        st.warning(f"**SEVERITY: {severity}**")
    elif severity == "MEDIUM":
        st.info(f"**SEVERITY: {severity}**")
    else:
        st.success(f"**SEVERITY: {severity}**")
        
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Hazards Detected:**")
        if hazards:
            for h in hazards:
                st.write(f"- {h.title()}")
        else:
            st.write("None clear")
            
    with col2:
        st.write("**Structural Damage:**")
        if structural:
            st.error("YES - Collapse Risk")
        else:
            st.success("NO - Stable")
            
    st.info(f"**AI Analyst Reasoning:**\n{reasoning}")
