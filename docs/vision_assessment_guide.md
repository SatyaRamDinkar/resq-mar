# ResQ-MAR Vision-Based Damage Assessment

## 1. Context and Novelty
Traditional emergency routing systems (including Li et al.'s base study) explore Computer Vision for damage assessment, but typically treat it as a **standalone, isolated task**. 

ResQ-MAR pioneers true **Multi-Modal Integration**. Rather than just classifying an image, the `VisionAgent` acts as a first-class citizen in the Agentic pipeline. It intercepts citizen-uploaded photos, extracts structural integrity metadata and hazard classifications, and routes these insights directly into the `IntakeAgent` to dynamically elevate the overall incident severity.

## 2. Architecture
The `VisionAgent` utilizes the **Gemini 1.5 Flash Multi-Modal Vision API**.
- **Speed & Cost:** Utilizes the free tier (1,500 requests/day) to perform rapid image inference.
- **Structured Output:** The agent is rigidly prompted to return structured JSON data, bridging the gap between raw pixels and actionable routing logic.

## 3. Data Extracted
When a user uploads a disaster photo (JPG/PNG), the model extracts:
- **Severity Level:** (Low, Medium, High, Critical)
- **Hazards Detected:** Array of specific visible threats (e.g., "electrical fire", "flooded road", "collapsed roof").
- **Structural Damage:** Boolean flag indicating if critical infrastructure has been compromised.
- **Analysis Reasoning:** A human-readable explanation of why the severity was assigned, enhancing the XAI (Explainable AI) dashboard.

## 4. Pipeline Integration
1. **Upload:** A citizen or edge-device uploads an image to the Live Command Center.
2. **Inference:** `VisionAgent` passes the image to Gemini Vision.
3. **Synthesis:** The resulting JSON is displayed to the dispatcher. If integrated into an active RAG flow, the JSON parameters bypass natural language ambiguity, forcing the `AssessorAgent` to elevate the protocol (e.g., triggering a Mass Casualty Event SOP if structural collapse is visually confirmed).

## 5. Prerequisites
- `pip install Pillow` (for image processing and API transport)
- `google-generativeai` package (already installed via previous multi-language configuration)
- `GEMINI_API_KEY` environment variable configured.
