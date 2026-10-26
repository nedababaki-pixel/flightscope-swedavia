@echo off
REM FlightScope - one-click start for Windows.
REM Creates a virtual environment the first time, installs packages, then starts the app.
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv || (echo Python was not found. Install Python 3.10+ from python.org and tick "Add to PATH". & pause & exit /b 1)
)

call ".venv\Scripts\activate.bat"
python -m pip install --quiet --disable-pip-version-check -r requirements.txt || (echo Package installation failed. & pause & exit /b 1)

echo.
echo Open http://127.0.0.1:5055 in your browser.
python app.py
pause
