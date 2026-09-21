@echo off
title SURADAK Edge Client -- Setup
color 0B
echo.
echo  ============================================================
echo   SURADAK Edge Client -- One-Time Dependency Setup
echo  ============================================================
echo.
echo  Installing edge-node Python dependencies...
echo  (This only needs to run once per machine)
echo.

cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo  [ERROR] Installation failed. Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   [SUCCESS] Setup complete!
echo   Next step: Edit config.env with your SERVER_IP and BUS_ID
echo              then double-click START.bat
echo  ============================================================
echo.
pause
