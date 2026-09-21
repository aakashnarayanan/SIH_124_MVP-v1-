# SURADAK Urban AI Fleet Intelligence — Demo Execution Guide

This guide walks you through running the full SURADAK demo on Windows with:
- **Pure-Python MQTT Broker** (amqtt on port 1883)
- **FastAPI Backend & WebSocket Service** (port 8000)
- **React / Vite Fleet Command Center** (port 5173)
- **3 Edge Detection Nodes** (Bus 1, Bus 2 with `test_dashcam.mp4`, Bus 3 with `test2.mp4`)
- **Multi-Bus Live Camera Feeds** (Switchable between Bus 1, Bus 2, Bus 3 `test2.mp4`)
- **Native H.264 Evidence Video Clips** (Native HTML5 playback in browser)
- **Circular GPS Loops** (Connaught Place, India Gate, Pragati Maidan)

---

## ⚡ Quick Start: 1-Click Launch (All 6 Windows)

Run the automated orchestrator from the project root:

```powershell
python exec.py
```

This launches all 6 components in separate console windows with a 1.5-second stagger:
1. `SURADAK MQTT Broker`
2. `SURADAK Server` (uvicorn with `--reload`)
3. `Edge Node 1` (`bus_1` — `test_dashcam.mp4`, Route 1 CP Ring)
4. `Edge Node 2` (`bus_2` — `test_dashcam.mp4`, Route 2 India Gate Loop)
5. `Edge Node 3` (`bus_3` — `test2.mp4`, Route 3 Pragati Loop)
6. `SURADAK Frontend Dashboard` (`npm run dev`)

Once started, open your browser at:
👉 **[http://localhost:5173](http://localhost:5173)**

---

## 🛠 Manual Step-by-Step Launch (Recommended for Debugging)

If you prefer opening terminals manually to inspect logs:

### Window 1 — Pure-Python MQTT Broker (amqtt)
```powershell
# From project root:
python mosquitto/broker.py
```
> Listens on `0.0.0.0:1883` with anonymous auth.

---

### Window 2 — FastAPI Central Server
```powershell
# From server/ directory:
cd server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
> REST API at `http://localhost:8000`, WebSocket at `ws://localhost:8000/ws/dashboard`.

---

### Window 3 — React Command Center Frontend
```powershell
# From frontend/ directory:
cd frontend
npm run dev
```
> Vite dev server running at `http://localhost:5173`.

---

### Window 4 — Edge Node 1 (`bus_1` — test_dashcam)
```powershell
# From project root:
python main.py --bus-id bus_1 --route edge/gps_tracks/route_1.csv --source edge/assets/test_dashcam.mp4 --fps 10 --verbose --demo-stream-frames
```

---

### Window 5 — Edge Node 2 (`bus_2` — test_dashcam)
```powershell
# From project root:
python main.py --bus-id bus_2 --route edge/gps_tracks/route_2.csv --source edge/assets/test_dashcam.mp4 --fps 10 --verbose --demo-stream-frames
```

---

### Window 6 — Edge Node 3 (`bus_3` — test2.mp4)
```powershell
# From project root:
python main.py --bus-id bus_3 --route edge/gps_tracks/route_3.csv --source edge/assets/test2.mp4 --fps 10 --verbose --demo-stream-frames
```

*(Optional: Add `--show-video` to any edge node command if you want a local OpenCV GUI window).*

---

## 🌐 How to Add a Friend's Laptop as an Edge Client

You can run an edge client on a friend's laptop connected to the same WiFi or mobile hotspot:

1. **Find your server laptop's local IPv4 address**:
   ```powershell
   ipconfig
   ```
   *(e.g., `192.168.1.45`)*
2. **Copy the `edge_client/` folder** (or clone the repository) onto your friend's laptop.
3. Open `edge_client/config.env` on your friend's laptop and set:
   ```ini
   SERVER_IP=192.168.1.45
   BUS_ID=bus_4
   ROUTE=route_4
   VIDEO=assets/friend_video.mp4
   ```
4. Place their dashcam video inside `edge_client/assets/friend_video.mp4`.
5. On your friend's laptop, run:
   ```bat
   # One-time dependency setup:
   SETUP.bat

   # Start the edge node:
   START.bat
   ```
6. Their bus will instantly appear on your Command Center map at `http://localhost:5173`!

---

## 🧭 Dashboard Verification Checklist

1. **Fleet Command Center (`/` or `/fleet`)**:
   - 3 yellow bus icons (`bus_1`, `bus_2`, `bus_3`) moving smoothly along their circular loops.
   - H3 hexagonal heatmap tiles appearing dynamically under detected defects (cyan → amber → red).
   - Real-time telemetry feed and deduplicated defect markers on the map.
   - Dark / Light mode toggle switch in the left navigation sidebar.

2. **AI Video Intelligence (`/video-intelligence`)**:
   - **Live Camera Feed Switcher**: Buttons for `All / Auto`, `Bus 1 (Route 1)`, `Bus 2 (Route 2)`, and `Bus 3 (test2.mp4)`. Clicking `Bus 3` displays the live stream from `test2.mp4`!
   - **Evidence Clips Grid**: Hover-to-play clips captured during pothole detections (encoded in browser-compatible H.264/AVC1, no black screens).
   - Real-time detection sparkline and active vehicle speeds.

3. **Urban Events (`/events`)**:
   - Event cards with `🎬 LIVE CLIP` badge (for detected clips) or `🖼 PREVIEW` badge (stock fallback).
   - Clicking a live event opens the interactive video player with inspection details.

---

## 🛑 How to Stop the Demo

To stop all components at once, run:
```powershell
Get-Process -Name python,node -ErrorAction SilentlyContinue | Stop-Process -Force
```
