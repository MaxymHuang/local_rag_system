@echo off
setlocal enabledelayedexpansion

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install requirements
    pause
    exit /b 1
)

echo Checking Ollama installation...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama is not installed.
    set /p install_ollama="Would you like to install Ollama? (Y/N): "
    if /i "!install_ollama!"=="Y" (
        start https://ollama.ai/download
        echo Please download and install Ollama from the opened webpage.
        echo After installation, run this script again.
        pause
        exit /b 0
    )
) else (
    echo Ollama is installed. Pulling required model...
    ollama pull hf.co/bartowski/Dolphin3.0-Llama3.2-3B-GGUF:Q4_K_M
    if %errorlevel% neq 0 (
        echo Failed to pull the model
        pause
        exit /b 1
    )
)

echo Checking other dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask...
    pip install flask
)

python -c "import flask_cors" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Flask-CORS...
    pip install flask-cors
)

echo Environment setup complete!
echo You can now run the application using: python app.py
pause 