# ResQ-MAR Demo Recording Guide

## 1. Required Software
- **OBS Studio**: Free software for screen recording.
- **Terminal**: Windows Terminal, PowerShell, or VS Code integrated terminal (preferred, with a clean dark theme).
- **Browser**: Chrome or Edge for displaying the Streamlit Dashboard.

## 2. Recording Setup
- **Resolution**: Set OBS canvas and output resolution to `1920x1080`.
- **Zoom**: Increase terminal font size (Ctrl + '+') to ~130% so text is easily readable on mobile/smaller screens.
- **Workspace**: Hide personal files. Close irrelevant VS Code tabs. Keep only the `resq-mar` folder visible.
- **Audio**: Use a good quality external microphone. Record in a quiet room to minimize background noise.

## 3. Execution Order
1. **Start Ollama**: Open a separate terminal window, run `ollama serve` (or start the Windows app). Keep it hidden.
2. **Start the Dashboard**: In a hidden terminal, run `streamlit run frontend/streamlit_app_enhanced.py`. Keep the browser tab open but minimized.
3. **Record Main Script**: 
   - Start OBS recording.
   - Run `python scripts/run_full_demo.py` in the main visible terminal.
   - Speak clearly, pacing your words with the console output (the script has built-in `time.sleep` delays specifically for this).
4. **Transition**: As the script prints the final summary table, pause briefly, then Alt-Tab to the Streamlit browser window to show the visual heatmap and agent monitor.
5. **Stop Recording**: Complete the closing statement and stop OBS.

## 4. Editing Tips
- **Pacing**: Use Premiere Pro or DaVinci Resolve to cut out any awkward pauses or throat clearing.
- **Callouts**: Add slight zooms or red boxes/arrows during editing to highlight the specific metrics mentioned in the narration (e.g., highlighting "Truck-Drone coverage: 100%").
- **Time Limit**: The capstone strict limit is usually 5 minutes. The script is timed for ~4:30. Do not speak too fast; let the pauses breathe.
- **Audio Polish**: Apply a slight compressor or vocal enhancer to the audio track.

## 5. Export Settings
- **Format**: MP4 (H.264 codec)
- **Resolution**: 1920x1080 (1080p)
- **Framerate**: 30fps
- **Bitrate**: 10-15 Mbps
- **Filename**: `ResQ-MAR_Demo_v1.mp4`
