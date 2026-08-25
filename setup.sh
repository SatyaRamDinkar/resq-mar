#!/bin/bash
# setup.sh - Environment setup script for ResQ-MAR
# To run: chmod +x setup.sh && ./setup.sh

echo "Setting up ResQ-MAR environment..."

# 1. Check if Python 3.10+ is installed
if command -v python3 &> /dev/null; then
    PY_CMD="python3"
elif command -v python &> /dev/null; then
    PY_CMD="python"
else
    echo "Python could not be found. Please install Python 3.10+."
    exit 1
fi

PYTHON_VERSION=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if ! awk -v ver="$PYTHON_VERSION" 'BEGIN { if (ver >= 3.10) exit 0; else exit 1 }'; then
    echo "Python 3.10+ is required. Found version $PYTHON_VERSION."
    exit 1
fi

echo "✓ Python $PYTHON_VERSION found."

# 2. Check if pip is available
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "pip could not be found. Please install pip."
    exit 1
fi
echo "✓ pip found."

# 3. Create a Python virtual environment at "resq-mar/venv/" if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment at 'venv/'..."
    $PY_CMD -m venv venv
else
    echo "✓ Virtual environment 'venv' already exists."
fi

# 4. Activate the virtual environment
echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Could not find activation script in venv."
    exit 1
fi

# 5. Upgrade pip, setuptools, wheel
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# 6. Install ALL required packages in one pip install command
echo "Installing required packages..."
pip install pyautogen==0.2.35 chromadb sentence-transformers streamlit folium streamlit-folium ortools fastapi uvicorn pydantic python-dotenv pytest psutil requests "scipy<1.13"

# 7. Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "✗ Ollama is not installed."
    echo "Please install Ollama from https://ollama.com/download"
else
    echo "✓ Ollama is installed."
    # 8. Pull the model "llama3.1"
    echo "Pulling llama3.1 model... (this may take a few minutes)"
    ollama pull llama3.1
fi

# 9. Print a success message with next steps
echo ""
echo "========================================="
echo "Setup Complete!"
echo "Next steps:"
echo "1. Activate the environment:"
echo "   Linux/Mac: source venv/bin/activate"
echo "   Windows (Git Bash): source venv/Scripts/activate"
echo "2. Start Ollama in a separate terminal: ollama serve"
echo "3. Run verification: python verify.py"
echo "4. Run hello world agent: python hello_world_agent.py"
echo "========================================="
