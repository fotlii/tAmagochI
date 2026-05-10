@echo off
setlocal enabledelayedexpansion

echo.
echo  ✦ Desktop AI Lifeform — Godot Frontend
echo  ─────────────────────────────────────
echo.

:: 1. Search for Godot
set "GP="

:: Try 'godot' command
where godot >nul 2>&1
if !errorlevel! equ 0 (
    for /f "delims=" %%i in ('where godot') do set "GP=%%i"
)

:: Try common paths
if "!GP!"=="" (
    for %%G in (
        "C:\Program Files\Godot\Godot_v4.5-stable_win64.exe"
        "C:\Program Files\Godot\Godot_v4.3-stable_win64.exe"
        "C:\Program Files\Godot\Godot.exe"
        "%USERPROFILE%\Downloads\Godot_v4.5-stable_win64.exe"
        "%USERPROFILE%\Downloads\Godot_v4.3-stable_win64.exe"
        "C:\Godot\Godot.exe"
        "Godot.exe"
    ) do (
        if exist "%%~G" set "GP=%%~G"
    )
)

if "!GP!"=="" (
    echo  [ERROR] No he podido encontrar el ejecutable de Godot automaticamente.
    echo.
    echo  Por favor, haz una de estas dos cosas:
    echo  1. Copia tu Godot.exe a esta misma carpeta.
    echo  2. Arrastra tu Godot.exe sobre este archivo .bat
    echo.
    pause
    exit /b 1
)

echo  Iniciando con: "!GP!"
echo  Ruta proyecto: "%~dp0frontend"
echo.

:: EXTREMELY IMPORTANT: Quote the path to handle spaces
"!GP!" --path "%~dp0frontend"

if !errorlevel! neq 0 (
    echo.
    echo  [ERROR] Godot se ha cerrado con el codigo de error !errorlevel!.
    echo  Revisa si hay algun mensaje de error arriba.
    pause
)
