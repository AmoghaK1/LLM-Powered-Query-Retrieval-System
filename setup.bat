@echo off
echo Setting up LLM Query Retrieval System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "sandbox" (
    echo Creating virtual environment...
    python -m venv sandbox
)

REM Activate virtual environment
echo Activating virtual environment...
call sandbox\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ⚠️  WARNING: .env file not found!
    echo Please create a .env file with your Gemini API key:
    echo.
    echo 1. Copy .env.example to .env
    echo 2. Get your API key from: https://makersuite.google.com/app/apikey
    echo 3. Replace 'your_actual_api_key_here' with your real API key
    echo.
)

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Make sure your .env file has your Gemini API key
echo 2. Add PDF documents to the 'documents' folder
echo 3. Run: start_server.bat
echo.
pause
