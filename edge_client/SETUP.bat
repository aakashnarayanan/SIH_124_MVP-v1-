@echo off
title SURADAK Edge Client -- Setup
color 0B
echo.
echo  ============================================================
echo   SURADAK Edge Client -- One-Time Dependency Setup
echo  ============================================================
echo.
echo  [1/3] Installing edge-node Python dependencies...
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
echo  [2/3] Checking Cisco OpenH264 codec (for web-playable evidence clips)...
python -c "import bz2, urllib.request; from pathlib import Path; p1 = Path('openh264-2.5.0-win64.dll'); p2 = Path('..') / 'openh264-2.5.0-win64.dll'; have_dll = p1.exists() or p2.exists(); (print('       [OK] OpenH264 DLL found.')) if have_dll else (print('       Downloading openh264-2.5.0-win64.dll from Cisco...'), p1.write_bytes(bz2.decompress(urllib.request.urlopen('http://ciscobinary.openh264.org/openh264-2.5.0-win64.dll.bz2', timeout=15).read())), print('       [OK] Downloaded and ready.'))"

echo.
echo  [3/3] Checking dashcam video asset...
if not exist "assets\dashcam.mp4" (
    if exist "..\edge\assets\test_dashcam.mp4" (
        echo        Copying default sample video from edge\assets\test_dashcam.mp4...
        copy "..\edge\assets\test_dashcam.mp4" "assets\dashcam.mp4" >nul
        echo        [OK] assets\dashcam.mp4 initialized.
    ) else (
        echo        [INFO] No default video found. Place your dashcam video in:
        echo               assets\dashcam.mp4
    )
) else (
    echo        [OK] assets\dashcam.mp4 is present.
)

echo.
echo  ============================================================
echo   [SUCCESS] Setup complete!
echo   Next steps:
echo     1. Edit config.env with your SERVER_IP and BUS_ID
echo     2. Double-click START.bat
echo  ============================================================
echo.
pause

