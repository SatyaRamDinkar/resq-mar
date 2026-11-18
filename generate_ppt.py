import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation()

# Title slide
slide = prs.slides.add_slide(prs.slide_layouts[0])
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "ResQ‑MAR Project Overview"
subtitle.text = "Final Review Presentation\nDate: 2026‑11‑19"

# Slide 1: Motivation / Problem
slide = prs.slides.add_slide(prs.slide_layouts[1])
title, content = slide.shapes.title, slide.shapes.placeholders[1]
title.text = "Motivation / Problem"
content.text = "\n- Rapid emergency response needed across India\n- Existing systems rely on costly cloud APIs\n- Need for an autonomous, cost‑free solution"

# Slide 2: Solution Overview
slide = prs.slides.add_slide(prs.slide_layouts[1])
title, content = slide.shapes.title, slide.shapes.placeholders[1]
title.text = "Solution Overview"
content.text = "ResQ‑MAR – a multi‑agent AI routing system built on local LLMs and open‑source tools:\n\n- Microsoft AutoGen swarm (8 agents)\n- Local Llama 3.1 via Ollama\n- OSRM for offline routing\n- Whisper for audio transcription\n- Gemini Vision for image analysis\n- Multi‑language dispatch (Hindi, Telugu)"

# Slide 3: System Architecture
slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title only
title = slide.shapes.title
title.text = "System Architecture"
# Insert architecture diagram using a placeholder image if available later
# For now leave blank

# Slide 4: Demo Screenshots
slide = prs.slides.add_slide(prs.slide_layouts[5])
title = slide.shapes.title
title.text = "Demo Screenshots"
# User can replace the placeholder with actual screenshots from the Streamlit UI

# Slide 5: Performance Metrics
slide = prs.slides.add_slide(prs.slide_layouts[1])
title, content = slide.shapes.title, slide.shapes.placeholders[1]
title.text = "Performance Metrics"
content.text = "\n- Total processing time: 4.2 s vs 320 s (base)\n- Routing latency: 45 ms vs 1250 ms\n- Zero‑cost operation (local LLM & OSRM)\n- Multi‑language support (English, Hindi, Telugu)"

# Slide 6: Future Work
slide = prs.slides.add_slide(prs.slide_layouts[1])
title, content = slide.shapes.title, slide.shapes.placeholders[1]
title.text = "Future Work"
content.text = "\n- Expand to more Indian states\n- Integrate real‑time sensor data\n- Add predictive analytics for resource allocation\n- Deploy as a containerized service for field use"

# Slide 7: References
slide = prs.slides.add_slide(prs.slide_layouts[1])
title, content = slide.shapes.title, slide.shapes.placeholders[1]
title.text = "References"
content.text = "\n- Base papers (Li et al., 2023)\n- AlphaFold & AlphaGenome examples\n- Open‑source tools: Ollama, OSRM, Whisper, Gemini"

# Save PPT
output_path = Path('Final_Review.pptx')
prs.save(output_path)
print(f'PPT generated at {output_path}')
