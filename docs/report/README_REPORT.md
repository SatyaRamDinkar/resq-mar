# ResQ-MAR Capstone Report Guide

This directory contains the finalized, academic-grade markdown chapters for the ResQ-MAR Capstone Project Report.

## How to Generate the Full Report
To stitch all chapters together into a single, cohesive document, run the generator script from the project root:
```bash
python docs/report/report_generator.py
```
This will create `ResQ-MAR_Full_Report.md`.

## How to Convert to PDF
You can convert the compiled markdown file to a professional PDF using any of the following methods:

**Method 1: VS Code (Recommended)**
1. Install the `Markdown PDF` extension.
2. Open `ResQ-MAR_Full_Report.md`.
3. Right-click anywhere in the file and select `Markdown PDF: Export (pdf)`.

**Method 2: Pandoc via CLI**
```bash
pandoc docs/report/ResQ-MAR_Full_Report.md -o ResQ-MAR_Report.pdf --pdf-engine=xelatex -V geometry:margin=1in
```

## Formatting Guidelines for Print
- **Font**: Times New Roman, 12pt
- **Line Spacing**: 1.5
- **Margins**: 1 inch all around (left margin 1.5 inch if spiral binding)
- **Paper**: A4 size, printed double-sided.

## Submission Checklist
Before submitting on Nov 20, ensure:
- [ ] Title page is printed and physically signed by your project guide.
- [ ] Roll number and University details are filled out on the title page.
- [ ] All 6 chapters + References are included.
- [ ] The generated PDF is burned to a CD/USB along with the `resq-mar` source code repository.
