# SURADAK Edge Client — Setup Guide

This folder is the **edge node client** for the SURADAK Urban AI Fleet Intelligence system.
Run this on any laptop to add a bus to the live demo.

---

## Prerequisites

- Python 3.10 or newer ([python.org](https://python.org))
- A dashcam / driving video file (MP4)
- Connected to the **same WiFi or hotspot** as the server laptop

---

## Step 1 — One-Time Setup (run once per machine)

```
Double-click: SETUP.bat
```

This installs all Python dependencies. Takes 3–5 minutes on first run.

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

## Step 3 — Add Your Video

Place your dashcam video inside the `assets/` folder:

```
assets/dashcam.mp4
```

> If you name it differently, update `VIDEO=` in `config.env`.

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
