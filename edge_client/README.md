# SURADAK Edge Client — Setup Guide

This folder is the **edge node client** for the SURADAK Urban AI Fleet Intelligence system.
Run this on any laptop to add a bus to the live demo.

---

## Prerequisites

- Python 3.10 or newer ([python.org](https://python.org))
- A dashcam / driving video file (MP4)
- Connected to the **same WiFi or hotspot** as the server laptop

---

## 📦 Files Excluded from GitHub & Where to Place Them

To keep the repository fast to clone, large binary media and compiled libraries are excluded via `.gitignore`. Here is what you need and where it goes:

| File | Where to Put It | Why It's Needed | How to Get It |
|---|---|---|---|
| **`dashcam.mp4`** *(or any driving MP4)* | `edge_client/assets/dashcam.mp4` | Driving video feed processed by the 3 YOLO AI models | **Auto-copied** by `SETUP.bat` from `edge/assets/test_dashcam.mp4` if cloned with repo. Or drop in any 720p/1080p MP4 dashcam video. |
| **`openh264-2.5.0-win64.dll`** | `edge_client/openh264-2.5.0-win64.dll` (or project root) | Cisco H.264 codec library. Without this, OpenCV encodes clips in `mp4v` which causes **black screens** in web browsers. | **Auto-downloaded** by `SETUP.bat` directly from Cisco. Or run: `python -c "import bz2, urllib.request; open('openh264-2.5.0-win64.dll','wb').write(bz2.decompress(urllib.request.urlopen('http://ciscobinary.openh264.org/openh264-2.5.0-win64.dll.bz2').read()))"` |
| **YOLO Weights** (`*.pt`) | `edge/models/*.pt` | AI inference models (`pothole.pt`, `traffic.pt`, `yolov8n-seg.pt`) | **Already committed** to GitHub in `edge/models/`. |
| **Evidence Clips** (`*.mp4`) | `edge/evidence_clips/bus_*/` | Local on-demand incident recordings | Generated automatically at runtime when road defects are detected. |
| **SQLite Cache** (`*.db`) | `edge/storage/bus_*_cache.db` | Local offline telemetry buffer | Generated automatically at runtime. |

---

## Step 1 — One-Time Setup (run once per machine)

```
Double-click: SETUP.bat
```

This automatically:
1. Installs all edge Python dependencies (`ultralytics`, `opencv-python`, `paho-mqtt`, `protobuf`, etc.)
2. Downloads the Cisco `openh264-2.5.0-win64.dll` codec so evidence clips play natively in the browser without black screens
3. Copies `edge/assets/test_dashcam.mp4` to `edge_client/assets/dashcam.mp4` if no video exists yet

Takes ~1–3 minutes on first run.

---

## Step 2 — Configure Your Bus

Open `config.env` in Notepad and edit **only these two lines**:

```
SERVER_IP=192.168.1.100   ← Change to the server laptop's IP address
BUS_ID=bus_2              ← Change to your assigned bus ID (bus_2, bus_3, etc.)
```

> **How to find the server's IP:**
> On the server laptop, open Command Prompt and run: `ipconfig`
> Look for "IPv4 Address" under your WiFi or hotspot adapter.

Also pick your GPS route (each bus should use a different route):

```
ROUTE=route_2    ← route_1 through route_5 available
```

---

## Step 3 — Add Your Video (Optional if using default)

If you have your own driving footage, place your dashcam video inside the `assets/` folder:

```
assets/dashcam.mp4
```

> If you name it differently (e.g. `assets/my_drive.mp4`), update `VIDEO=` in `config.env`.
> If left as default, `SETUP.bat` automatically sets up the sample dashcam video.

---

## Step 4 — Run

```
Double-click: START.bat
```

You should see:

```
================================================================
  SURADAK Edge Client Node
================================================================
  Bus ID         : bus_2
  Server IP      : 192.168.1.100:1883
  Route CSV      : gps_tracks/route_2.csv
  Video Source   : assets/dashcam.mp4
  Target FPS     : 10
  Stream Frames  : YES (demo mode)
  Show Video GUI : False
================================================================
[Starting] Launching edge node...
```

The bus icon will appear on the server's dashboard map within seconds.

---

## Bus Assignment Table

| Person | BUS_ID | ROUTE | Config line |
|--------|--------|-------|-------------|
| You    | bus_2  | route_2 | already set |
| Friend 2 | bus_3 | route_3 | edit config.env |
| Friend 3 | bus_4 | route_4 | edit config.env |
| Friend 4 | bus_5 | route_5 | edit config.env |
| Your laptop (2nd instance) | bus_1 | route_1 | separate window |

---

## Running Multiple Buses on One Laptop

Open multiple Command Prompt windows and run:

```bat
python run.py --bus-id bus_2 --route route_2
python run.py --bus-id bus_3 --route route_3
```

Each window becomes a separate bus.

---

## Command-Line Overrides

You can override any `config.env` setting on the command line:

```
python run.py --server-ip 192.168.1.50 --bus-id bus_4 --route route_4 --fps 15
python run.py --show-video        # Enable OpenCV video window
python run.py --no-stream         # Disable JPEG streaming (pure Protobuf mode)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `[ERROR] Video file not found` | Put dashcam.mp4 in assets/ and check VIDEO= in config.env |
| Bus not appearing on dashboard | Check SERVER_IP is correct. Try `ping <SERVER_IP>` in cmd |
| MQTT connection refused | Make sure Mosquitto is running on the server laptop (port 1883) |
| `ModuleNotFoundError` | Run SETUP.bat again |
| Port 1883 blocked by firewall | On server laptop: allow port 1883 in Windows Defender Firewall |

---

## What This Runs

- **3 YOLO models** (Traffic count, Pothole detection, Road segmentation)
- **Local MAPE-K self-healing** (night mode, vibration, thermal adaptation)
- **Protobuf telemetry** over MQTT to the central server
- **SQLite offline cache** — if WiFi drops, data is queued and burst-uploaded on reconnect
- **On-demand evidence clips** — server can request a local MP4 clip of any detected defect
