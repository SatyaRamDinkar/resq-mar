"""
Script to generate the complete ResQ-MAR capstone report.
"""
import os
import sys

def read_chapter(path: str) -> str:
    """Read a markdown file and return its content."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return ""

def generate_toc(chapters: list) -> str:
    """Generate a simulated Table of Contents."""
    toc = "# Table of Contents\n\n"
    for i, title in enumerate(chapters, 1):
        if title == "References":
            toc += f"{title} ....................................................... {i}\n"
        else:
            toc += f"Chapter {i}: {title} ........................................ {i}\n"
    return toc

def generate_title_page() -> str:
    """Create a formatted title page."""
    return """=========================================
RESQ-MAR: AI-Powered Multi-Agent
Emergency Response System

A Capstone Project Report

Submitted in partial fulfillment
of the requirements for the degree of
Bachelor of Technology in Computer Science

By
Satya Ram Dinkar
[Roll Number]

Under the guidance of
[Guide Name]

[University Name]
[Department Name]
November 2026
=========================================
"""

def generate_full_report(output_path: str = "docs/report/ResQ-MAR_Full_Report.md") -> None:
    """Concatenate all chapters and generate the full report."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    chapter_files = [
        ("Introduction", "chapter1_introduction.md"),
        ("Literature Review", "chapter2_literature_review.md"),
        ("System Design and Architecture", "chapter3_system_design.md"),
        ("Implementation", "chapter4_implementation.md"),
        ("Evaluation and Results", "chapter5_evaluation.md"),
        ("Conclusion and Future Work", "chapter6_conclusion.md"),
        ("References", "references.md")
    ]
    
    title_page = generate_title_page()
    toc = generate_toc([title for title, _ in chapter_files])
    
    full_content = title_page + "\n\n---\n\n" + toc + "\n\n---\n\n"
    
    total_words = 0
    for title, filename in chapter_files:
        filepath = os.path.join(base_dir, filename)
        content = read_chapter(filepath)
        words = len(content.split())
        total_words += words
        print(f"Read {filename}: {words} words")
        full_content += content + "\n\n---\n\n"
        
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
        
    print(f"\nTotal Word Count: {total_words} words")
    print(f"[OK] Full report generated: {output_path}")

def generate_pdf_guide() -> str:
    """Return guide for converting to PDF."""
    return """
PDF Conversion Guide:
1. Using Pandoc: 
   pandoc docs/report/ResQ-MAR_Full_Report.md -o ResQ-MAR_Report.pdf --pdf-engine=xelatex -V geometry:margin=1in
2. Using VS Code:
   Install 'Markdown PDF' extension. Right click the generated markdown file -> 'Markdown PDF: Export (pdf)'
3. Recommended settings:
   - Font: Times New Roman 12pt
   - Line Spacing: 1.5
   - Page Size: A4
"""

if __name__ == "__main__":
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ResQ-MAR_Full_Report.md")
    generate_full_report(report_path)
    print(generate_pdf_guide())
