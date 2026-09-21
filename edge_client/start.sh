#!/bin/bash
# SURADAK Edge Client — Linux/Mac Launcher
# Usage: chmod +x start.sh && ./start.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo " ============================================================"
echo "  SURADAK Urban AI Fleet Intelligence -- Edge Client Node"
echo " ============================================================"
echo ""

# Check python3
if ! command -v python3 &> /dev/null; then
    echo " [ERROR] python3 not found. Install Python 3.10+ first."
    exit 1
fi

# Install deps if missing
python3 -c "import cv2, ultralytics, paho.mqtt" 2>/dev/null || {
    echo " [Setup] Installing dependencies..."
    pip3 install -r requirements.txt
}

echo " [Starting] Launching edge node... (Ctrl+C to stop)"
echo ""
python3 run.py "$@"
