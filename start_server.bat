@echo off
echo Starting Retrieval System API Server...
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Install requirements if they don't exist
python -c "import fastapi" 2>nul || (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting API server on http://localhost:8000
echo API Documentation available at: http://localhost:8000/docs
echo.

python api_server.py

pause
