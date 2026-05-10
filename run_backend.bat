@echo off
:: run_backend.bat — Optimized for silent/stealth launch
:: USES PYTHONW TO AVOID CONSOLE WINDOW

:: Check Python
python --version >nul 2>&1
if errorlevel 1 exit /b 1

:: Install dependencies if needed (silent)
if not exist ".venv" (
    python -m venv .venv >nul 2>&1
    .venv\Scripts\pip install -r requirements.txt >nul 2>&1
)

:: Start daemon silently using pythonw
start /b "" .venv\Scripts\pythonw.exe -m backend.main
