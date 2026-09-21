@echo off
title SURADAK Edge Client Node
color 0A
echo.
echo  ============================================================
echo   SURADAK Urban AI Fleet Intelligence -- Edge Client Node
echo  ============================================================
echo.

REM ── Check Python ─────────────────────────────────────────────
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [ERROR] Python not found! Install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM ── Move to the edge_client directory ────────────────────────
cd /d "%~dp0"

REM ── Check if requirements are installed ──────────────────────
python -c "import cv2, ultralytics, paho.mqtt" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo  [Setup] Dependencies not installed. Running SETUP.bat first...
    echo.
    call "%~dp0SETUP.bat"
    if %ERRORLEVEL% neq 0 (
        echo  [ERROR] Setup failed. Please run SETUP.bat manually and check errors.
        pause
        exit /b 1
    )
)

REM ── Launch edge client ────────────────────────────────────────
echo  [Starting] Launching edge node... (Ctrl+C to stop)
echo.
python run.py %*

echo.
echo  [Stopped] Edge node exited.
pause
