# ResQ-MAR Poster Printing Guide

Follow these instructions to successfully generate an A1-sized physical or digital poster from the provided HTML file.

## 1. How to Print to PDF
The poster uses CSS media queries (`@media print`) and absolute sizing to ensure it prints perfectly.

1. Open `docs/poster/resq_mar_poster.html` in **Google Chrome** or **Microsoft Edge**. (Chrome provides the most reliable CSS printing engine).
2. Press `Ctrl + P` (or `Cmd + P` on Mac) to open the print dialog.
3. Apply the following exact settings:
   - **Destination**: Save as PDF
   - **Paper size**: A1 (594 x 841 mm). *If A1 is not in the dropdown, look for "Custom" or "More settings" to define the size.*
   - **Orientation**: Portrait
   - **Margins**: None (or Custom -> 0 for all sides)
   - **Background graphics**: ENABLED (CHECKED) — *This is critical, otherwise the blue headers and red boxes will vanish!*
   - **Scale**: Custom -> 100%
4. Click **Save** and name it `ResQ_MAR_Poster_A1.pdf`.

## 2. Professional Printing Instructions
If you need a physical copy for the review panel on Nov 17-21:
- Take the generated PDF to a local university print shop or FedEx Office.
- **Request**: A1 Matte Poster Print. (Matte is better than glossy to avoid glare under presentation lights).
- **Alternative Size**: A0 (841 x 1189 mm). Because the layout uses relative flex-grids, the print shop can scale the A1 PDF up to A0 without losing structural fidelity, though A1 is the standard for academic stands.
- **Cost Estimate**: Typically $15 - $30 USD.

## 3. Poster Presentation Tips
- **Positioning**: Stand slightly to the left of the poster so you don't block the key results tables when pointing.
- **The 2-Minute Pitch**: Start with the "Problem" (Left column), walk through the "Architecture" (Center), and highlight the "Key Results" (Right). End with "Why ResQ-MAR Wins" (Bottom).
- **Interactive Handouts**: Print 10-20 small business-card-sized handouts with the GitHub QR code/link so professors can review the open-source code later.

## 4. Troubleshooting
- **Text looks too small in browser?**: This is normal. A1 is physically large. If you want to preview it on your screen comfortably, simply zoom the browser to 125% or 150%. 
- **Colors missing?**: You forgot to check "Background graphics" in the print dialog.
- **Formatting looks broken?**: Ensure you are not using Internet Explorer or older versions of Safari. Use a modern Chromium-based browser.
