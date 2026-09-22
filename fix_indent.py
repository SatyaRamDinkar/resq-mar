import os

path = "d:/Projects & Internships/resq-mar/frontend/streamlit_app_enhanced.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
in_block = False
for i, line in enumerate(lines):
    # This block was inserted without indentation:
    if line.startswith("# --- Live System Health Checks ---"):
        in_block = True
    
    if in_block:
        if line.startswith('""", unsafe_allow_html=True)'):
            new_lines.append('    """, unsafe_allow_html=True)\n')
            in_block = False
        elif line.strip() == "" or line == "\n":
            new_lines.append("\n")
        elif not line.startswith("    "):
            new_lines.append("    " + line)
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Indentation fixed.")
