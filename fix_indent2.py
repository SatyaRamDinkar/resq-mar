import os

path = "d:/Projects & Internships/resq-mar/frontend/streamlit_app_enhanced.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("    try:") and lines[i-1].startswith("    def _check_service"):
        lines[i] = "        try:\n"
        lines[i+1] = "            _req.get(url, timeout=timeout)\n"
        lines[i+2] = "            return True\n"
        lines[i+3] = "        except Exception:\n"
        lines[i+4] = "            return False\n"
    if line.startswith("    return '<span") and lines[i-1].startswith("    def _badge"):
        lines[i] = "        return '<span class=\"status-badge badge-online\">ONLINE</span>' if ok else '<span class=\"status-badge badge-critical\">OFFLINE</span>'\n"
    if line.startswith("    color = ") and lines[i-1].startswith("    def _dot"):
        lines[i] = "        color = \"#22c55e\" if ok else \"#ef4444\"\n"
        lines[i+1] = "        return f'<span class=\"live-dot\" style=\"background:{color};\"></span>'\n"

with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
