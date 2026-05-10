@echo off
echo.
echo  ✦ Desktop AI Lifeform — Startup
echo  ──────────────────────────────
echo.

:: 1. Start Backend in a separate minimized window
echo  [1/2] Starting Backend Daemon...
start "Lifeform Backend" /min cmd /c "run_backend.bat"

:: 2. Wait a moment for the socket to be ready
timeout /t 2 /nobreak >nul

:: 3. Start Frontend
echo  [2/2] Starting Godot Frontend...
call run_frontend.bat

echo.
echo  ✦ System running.
echo    Minimize this window to keep the lifeform alive.
echo    Close this window to stop everything.
echo.
pause
