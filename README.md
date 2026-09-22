# 🛰️ SURADAK — Smart Urban Road AI & Fleet Intelligence

> **Edge-AI Powered Municipal Road Infrastructure Monitoring, Spatial Deduplication & Public Transit Intelligence**  
> *Developed for Smart India Hackathon (SIH)*

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](#)
[![React 18](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?logo=typescript&logoColor=white)](#)
[![YOLOv8](https://img.shields.io/badge/Ultralytics-YOLOv8-FF6F00?logo=ultralytics&logoColor=white)](#)
[![Protobuf](https://img.shields.io/badge/Protocol%20Buffers-v4-4285F4?logo=google&logoColor=white)](#)
[![MQTT](https://img.shields.io/badge/MQTT-v3.1.1%2F5.0-660066?logo=eclipse-mosquitto&logoColor=white)](#)
[![Uber H3](https://img.shields.io/badge/Uber%20H3-Spatial%20Grid-000000?logo=uber&logoColor=white)](#)

---

## 📌 Executive Summary

Modern municipal corporations struggle with road infrastructure maintenance. Traditional road inspection approaches rely either on **expensive survey vans** (equipped with LiDAR, costing millions and deployed once a year) or **passive citizen complaints** (where potholes are reported only after causing accidents or severe traffic bottlenecks).

**SURADAK** turns everyday public transit buses into **autonomous, mobile road-diagnostic units**. By mounting intelligent edge AI nodes onto existing municipal bus fleets, SURADAK continuously and passively audits urban roadways during daily commercial transit operations.

Every detected road defect is:
1. Identified on the edge in real time using **3 concurrent YOLO vision models**.
2. Serialized into ultra-compact **Google Protocol Buffers** and published over **MQTT**.
3. Deduplicated across multi-bus passes using a **concurrent 3-meter KD-Tree spatial engine**.
4. Spatially aggregated into **Uber H3 hexagonal indices** for municipal heatmaps.
5. Streamed via **WebSockets** into an executive midnight-neon command center dashboard.

---

## 🏗️ System Architecture

SURADAK is architected as an industrial-grade **Hexagonal (Ports & Adapters) 3-Tier Pipeline**:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TIER 1: EDGE TRANSIT NODE                              │
│                                                                                        │
│   [ Dashcam Video Stream ]                                                             │
│              │                                                                         │
│              ▼                                                                         │
│   ┌───────────────────────┐         ┌────────────────────────┐                         │
│   │   MAPE-K Loop Engine  │ ◄─────► │ Parallel Multi-YOLO    │                         │
│   │ (Lux / Vibration Adap)│         │ • Traffic Density      │                         │
│   └───────────────────────┘         │ • Pothole Detection    │                         │
│              │                      │ • Hazard Segmentation  │                         │
│              ▼                      └────────────────────────┘                         │
│   ┌───────────────────────┐                                                            │
│   │ Protobuf Serialization│ ──────┐                                                    │
│   └───────────────────────┘       │                                                    │
│              │                    ▼                                                    │
│              │          ┌───────────────────────┐                                      │
│              └────────► │ SQLite Storage Buffer │ (Offline Circuit Breaker)            │
│                         └───────────────────────┘                                      │
└─────────────────────────────────────┬──────────────────────────────────────────────────┘
                                      │  MQTT QoS 1 / Protobuf Binary
                                      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              TIER 2: CORE INGESTION SERVER                             │
│                                                                                        │
│   ┌────────────────────────┐         ┌──────────────────────────────────────────────┐  │
│   │  MQTT Inbound Adapter  │ ──────► │ Concurrent 3-Meter Spatial Deduplication     │  │
│   │ (fleet/+/telemetry)    │         │ (SciPy cKDTree clustering, O(log N) lookup)  │  │
│   └────────────────────────┘         └──────────────────────┬───────────────────────┘  │
│                                                             │                          │
│                                                             ▼                          │
│   ┌────────────────────────┐         ┌──────────────────────────────────────────────┐  │
│   │   REST API Service     │         │ Uber H3 Hexagonal Density Matrix             │  │
│   │  (FastAPI + OpenAPI)   │         │ (Resolution 9, ~174m edge-length hexagons)   │  │
│   └────────────────────────┘         └──────────────────────┬───────────────────────┘  │
│                                                             │                          │
│                                                             ▼                          │
│                                      ┌──────────────────────────────────────────────┐  │
│                                      │ WebSocket Broadcast Adapter (/ws/dashboard)  │  │
│                                      └──────────────────────┬───────────────────────┘  │
└─────────────────────────────────────────────────────────────┼──────────────────────────┘
                                                              │  JSON WebSockets / REST
                                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            TIER 3: SURADAK OPERATIONS DASHBOARD                        │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ • Command Center: Live midnight-neon Leaflet map with pulsing bus badges       │   │
│   │ • Fleet Tracking: Monitored bus list, route milestones & docked telemetry HUD  │   │
│   │ • AI Video Intelligence: Real-time detection HUD, density gauge & timeline     │   │
│   │ • Urban Events: Collapsible defect feed, confidence metrics & photo previews   │   │
│   │ • Analytics Dashboard: Defect breakdown donuts, historical hourly density      │   │
│   │ • System Settings: Threshold controls, unit toggles & system diagnostics       │   │
│   └────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ⭐ What Sets SURADAK Apart? (Key Differentiators)

| Feature | Traditional Municipal Inspection | Citizen Grievance Apps (e.g. Swachhata) | **SURADAK Platform** |
| :--- | :--- | :--- | :--- |
| **Fleet / Equipment Cost** | Millions of ₹ for dedicated LiDAR survey vans | Zero (relies on citizens) | **Zero Additional Fleet Cost** (leverages existing city transit buses) |
| **Data Freshness** | Yearly or biannual static reports | Highly sporadic and reactive | **Continuous, self-updating dynamic digital twin** of city roads |
| **Edge Intelligence** | Raw video recorded for offline post-processing | Manual photo upload by user | **On-device real-time 3-model parallel inference** (YOLOv8) |
| **Network Footprint** | Gigabytes of raw video files | High-res JPEG uploads over cellular | **Ultra-compact binary Protobuf** (~80% smaller than JSON) |
| **Offline Resilience** | N/A | Fails without mobile data | **Self-healing SQLite buffer** with automatic network re-transmission |
| **Deduplication** | Manual analyst review | High rate of duplicate citizen complaints | **Mathematical 3-meter KD-Tree clustering** ($O(\log N)$) |
| **Spatial Indexing** | Isolated GPS coordinates | Isolated point pins | **Uber H3 Discrete Global Grid** (resolution 9 heatmaps) |
| **Self-Adaptation** | None | None | **MAPE-K autonomic control loop** (lux and vibration adaptation) |

---

## 🧩 Deep-Dive Implementation Details

### 1. Edge Transit Node (`edge/`)
- **Parallel Multi-Model Inference (`edge/inference.py`)**: Runs three specialized YOLO neural networks concurrently:
  - **Model A (Pothole)**: Specialized bounding-box detector identifying surface voids and asphalt depressions.
  - **Model B (Traffic & Vehicles)**: Multi-class tracker classifying cars, buses, trucks, motorcycles, and bicycles.
  - **Model C (Hazard Segmentation)**: Polygon segmentation identifying waterlogging and debris hazards.
- **Autonomic MAPE-K Adaptation Loop (`edge/mape_k_edge.py`)**:
  - **Monitor**: Reads frame luminosity (LUX) and simulates 3-axis accelerometer vibration ($G$).
  - **Analyze**: Detects low-light conditions ($\text{LUX} < 30$) or motion-blur vibrations ($G > 2.5$).
  - **Plan & Execute**: Automatically switches inference pipelines to night enhancement (contrast equalized CLAHE) or drops degraded frames to conserve compute.
- **Resilient Offline Circuit Breaker (`edge/storage/cache.py`)**:
  - Telemetry is buffered in a local thread-safe SQLite cache if cellular connection drops.
  - When connection is restored, cached packets are systematically flushed in FIFO order without data loss.
- **Monotonic GPS Progression**: GPS coordinates progress continuously across video loops (`processed_count // target_fps`), eliminating location jumping.

### 2. Core Server & Spatial Deduplication (`server/`)
- **Concurrent 3-Meter KD-Tree Engine (`server/domain/deduplication.py`)**:
  - High-frequency detections create dozens of sightings for a single pothole.
  - SURADAK maps GPS coordinates into Cartesian space and queries a spatial KD-tree in $O(\log N)$ time with a 3-meter threshold radius.
  - Identical defects are merged: coordinates are averaged, confidence is dynamically recalculated using weighted probability, and the `sighting_count` increments.
- **Uber H3 Spatial Heatmap Matrix (`server/core/ingestion_service.py`)**:
  - Transforms raw point coordinates into Uber H3 hexagonal cells (Resolution 9, ~174m edge length).
  - Supplies the frontend with pre-computed polygon boundaries for municipal zone health scores.

### 3. SURADAK Command Center Dashboard (`frontend/`)
- **Midnight-Neon Design System**: Styled with deep space navy (`#080d1a`), electric cyan (`#06b6d4`), amber (`#f59e0b`), and emerald (`#10b981`).
- **Interactive Leaflet Canvas (`frontend/src/components/MapView.tsx`)**:
  - Dark Esri base-tiles with glowing route traces.
  - Neon Pill bus markers displaying real-time vehicle speed and GPS.
  - Animated radar pulse rings indicating road defect severity.
- **Docked HUD & Responsive Panels**:
  - Fleet Tracking features a cleanly docked bottom HUD showing live speed, distance, route milestones, and a glowing station progression line.
  - Urban Events features a collapsible event feed with one-click close (`[X]`).
  - AI Video Intelligence features a centered circular traffic density gauge with non-overlapping metrics.

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+** (Tested on Python 3.11 & 3.12)
- **Node.js 18+** & npm

---

### Step 1: Install Dependencies

```powershell
# 1. Install root dependencies
pip install -r requirements.txt

# 2. Install server dependencies
cd server
pip install -r requirements.txt
cd ..

# 3. Install frontend dependencies
cd frontend
npm install
cd ..
```

---

### Step 2: Run the System (4 Terminal Setup)

#### Recommended broker option: Eclipse Mosquitto in Docker

For a repeatable broker environment, start Eclipse Mosquitto from the repository root:

```powershell
docker compose -f docker-compose.mqtt.yml up -d
```

The legacy `python mosquitto/broker.py` option below remains useful when Docker is unavailable. Both options listen on port `1883`; run only one of them at a time.

Open **4 PowerShell terminal windows** from the project root directory (`SIH_PROJECT/`):

#### **Terminal 1: MQTT Telemetry Broker**
```powershell
python mosquitto/broker.py
```
> *Starts the lightweight, zero-install Python MQTT broker on `0.0.0.0:1883`.*

#### **Terminal 2: Core FastAPI Server**
```powershell
cd server ; python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
> *Starts the ingestion engine, KD-Tree deduplication, and WebSocket broadcaster on `http://localhost:8000`.*

#### **Terminal 3: Edge AI Video Inference Node**
```powershell
python main.py --source edge/assets/test_dashcam.mp4 --fps 10 --show-video --verbose
```
> *Runs the 3 parallel YOLO models over the dashcam video. Opens an OpenCV GUI window showing bounding boxes and streams telemetry to the broker.*

#### **Terminal 4: SURADAK Web Dashboard**
```powershell
cd frontend ; npm run dev
```
> *Starts the Vite development server. Open **[http://localhost:5173](http://localhost:5173)** in your browser.*

---

## 📡 Protocol Contracts

### MQTT Topics

| Topic | Publisher | Subscriber | Payload | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `fleet/{bus_id}/telemetry` | Edge Node | Core Server | Protobuf (`EdgeTelemetryPacket`) | High-frequency telemetry with defect coordinates & traffic stats |
| `fleet/{bus_id}/heartbeat` | Edge Node | Core Server | JSON | Periodic keep-alive containing edge FPS and system status |
| `fleet/{bus_id}/command` | Core Server | Edge Node | JSON | Remote commands (e.g., adapt frame rate, trigger snapshot) |

### REST API Endpoints

| Endpoint | Method | Response | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | JSON | Service status and version information |
| `/health` or `/api/health` | `GET` | JSON | Broker connection state, active buses, and defect counts |
| `/vehicles` or `/api/vehicles` | `GET` | JSON | List of all active tracked transit vehicles |
| `/defects` or `/api/defects` | `GET` | JSON | List of deduplicated road defects with coordinates & sightings |
| `/ws/dashboard` | `WebSocket` | Stream | Bi-directional real-time event pipeline (`vehicle_moved`, `defect_new`, etc.) |

---

## 🗺️ Future Vision & Roadmap

```
  Phase 1 (Completed)          Phase 2 (Near-Term)         Phase 3 (Medium-Term)         Phase 4 (Long-Term)
┌───────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐   ┌────────────────────────┐
│ • Parallel Multi-YOLO │   │ • Automated PWD Work   │   │ • Predictive Pavement  │   │ • Citizen Navigation   │
│ • 3m KD-Tree Dedup    │──►│   Order Generation     │──►│   Deterioration ML     │──►│   Warning Integration  │
│ • Real-Time Dashboard │   │ • Contractor SLA &     │   │ • Weather & Monsoon    │   │ • Smart City Traffic   │
│ • MQTT / Protobuf     │   │   Repair Tracking      │   │   Erosion Modeling     │   │   Signal Prioritization│
└───────────────────────┘   └────────────────────────┘   └────────────────────────┘   └────────────────────────┘
```

1. **Automated PWD Work Order Dispatching (Phase 2)**:
   - Direct integration with Public Works Department (PWD) enterprise systems.
   - Automatically clusters severe defects into repair work-orders and routes maintenance crews with verified GPS coordinates.
2. **Predictive Pavement Deterioration AI (Phase 3)**:
   - Machine learning models that analyze minor surface cracks over time, estimating asphalt fatigue and predicting pothole formation *before* it occurs.
3. **Citizen Navigation Safety Layer (Phase 4)**:
   - High-confidence hazard data exposed via open municipal APIs to navigation providers (Google Maps, Mappls, Apple Maps) to warn motorists of upcoming road defects in real time.

---

## 📂 Repository Structure

```
SIH_PROJECT/
├── edge/                           # Tier 1: Edge Transit Node
│   ├── assets/                     # Sample dashcam videos (test_dashcam.mp4, test2.mp4)
│   ├── config.py                   # Edge thresholds (Lux, Vibration, MQTT)
│   ├── gps_tracks/                 # Real-world waypoint traces (route_1.csv)
│   ├── inference.py                # 3-Model parallel YOLO inference & HUD rendering
│   ├── main.py                     # Edge runtime runner
│   ├── mape_k_edge.py              # Autonomic MAPE-K adaptation loop
│   ├── network/                    # MQTT Paho client wrapper
│   └── storage/                    # SQLite offline circuit breaker cache
│
├── server/                         # Tier 2: Core Ingestion & Deduplication Server
│   ├── adapters/                   # Hexagonal adapters (MQTT Inbound, WebSocket Broadcast)
│   ├── config.py                   # Server settings (MQTT Host/Port, Dedup Radius)
│   ├── core/                       # Ingestion service & H3 spatial density matrix
│   ├── domain/                     # 3-Meter KD-Tree deduplication & data models
│   ├── main.py                     # FastAPI application & REST endpoints
│   └── plugins/                    # Server-side MAPE loop & media orchestration
│
├── frontend/                       # Tier 3: SURADAK Command Dashboard
│   ├── src/
│   │   ├── components/             # Reusable UI cards, Sidebar, MapView (Leaflet), H3Layer
│   │   ├── data/                   # Route 17 waypoints & station stops
│   │   ├── hooks/                  # WebSocket and REST data synchronization hooks
│   │   ├── pages/                  # 6 Core Screens:
│   │   │                           #  1. CommandCenter (Overview map + live metrics)
│   │   │                           #  2. FleetTracking (Bus status, timeline, docked HUD)
│   │   │                           #  3. VideoIntelligence (Detection feed, traffic gauge)
│   │   │                           #  4. UrbanEvents (Collapsible defect feed + previews)
│   │   │                           #  5. Analytics (Severity breakdown donuts + trends)
│   │   │                           #  6. Settings (System configuration & unit toggles)
│   │   ├── App.tsx                 # Root router & global state orchestrator
│   │   ├── index.css               # Complete Midnight-Neon design system (dark + light mode)
│   │   ├── theme.tsx               # [NEW] ThemeProvider + useTheme hook
│   │   └── types.ts                # Master TypeScript schemas
│   ├── package.json
│   └── vite.config.ts              # Vite configuration with backend proxy
│
├── proto/                          # Shared Protocol Buffer Contracts
│   ├── telemetry.proto             # Protobuf binary schema
│   └── telemetry_pb2.py            # Compiled Python bindings
│
├── mosquitto/                      # Lightweight MQTT Broker
│   ├── broker.py                   # Zero-install pure-Python broker for instant local testing
│   └── config/                     # Mosquitto server configuration
│
├── docs/                           # [NEW] Engineering documentation
│   ├── DEVIATION_REMEDIATION_LOG.md   # Full session-by-session engineering log
│   ├── MASTER_PLAN_DEVIATION_ASSESSMENT.md  # Fidelity assessment vs master plan
│   └── HOW_TO_RUN_DEMO.md         # Complete demo startup & verification guide
│
├── edge_client/                    # [NEW] Portable edge node for friend's laptop
│   ├── run.py                      # Main launcher (reads config.env)
│   ├── config.env                  # Set SERVER_IP= to server laptop's IP
│   ├── SETUP.bat / START.bat       # Windows one-click setup & start
│   ├── start.sh                    # Linux/macOS start
│   ├── assets/                     # Place dashcam video here
│   └── gps_tracks/                 # Routes 1-5 CSV files
│
├── exec.py                         # [NEW] 1-click launcher for all 6 demo components
├── HOW_TO_RUN_DEMO.md              # Quick access demo guide (also in docs/)
├── simulate_chaos.py               # [NEW] Multi-bus chaos simulation script
├── main.py                         # Root CLI launcher for edge execution
├── requirements.txt                # Global Python dependencies
└── README.md                       # Master project documentation
---

## 📦 Excluded Files & Setup Guide for Friends / GitHub Clones

When cloning this repository to a new computer or sharing it with team members, some files are intentionally excluded via `.gitignore` to keep git operations fast, avoid pushing heavy binary files (e.g. videos and DLLs), and prevent tracking temporary runtime databases.

### 📋 Full Table of Excluded Files

| Excluded Item | Where to Put It | Why It's Excluded | How to Get or Generate It |
|---|---|---|---|
| **`openh264-2.5.0-win64.dll`** | Project root `SIH_PROJECT/` or `edge_client/` or Python directory | Windows compiled binary (~986 KB). OpenCV needs it to encode native **H.264 (`avc1`)** evidence clips. Without it, OpenCV falls back to `mp4v`, resulting in **black video screens** in browsers. | **Auto-downloaded** when running `edge_client/SETUP.bat`. Alternatively, run this 1-line Python command:<br>`python -c "import bz2, urllib.request; open('openh264-2.5.0-win64.dll','wb').write(bz2.decompress(urllib.request.urlopen('http://ciscobinary.openh264.org/openh264-2.5.0-win64.dll.bz2').read()))"` |
| **`edge_client/assets/*.mp4`** *(e.g. `dashcam.mp4`)* | `edge_client/assets/dashcam.mp4` | Large video files (10–15 MB each) are excluded from `edge_client/assets/` to prevent repository bloat. | **Auto-copied** from `edge/assets/test_dashcam.mp4` by `edge_client/SETUP.bat` on first run. Or supply any MP4 road video. *(Note: Sample videos `edge/assets/test_dashcam.mp4` and `edge/assets/test2.mp4` are already tracked in git).* |
| **`edge/evidence_clips/**/*.mp4`** | `edge/evidence_clips/bus_1/`, `bus_2/`, `bus_3/` | Dynamically created at runtime when potholes/hazards are detected during edge inference. | Automatically generated by `edge/evidence.py`. Empty folder structure is maintained in git via `.gitkeep`. |
| **`edge/storage/*.db`** | `edge/storage/bus_*_cache.db` | Local SQLite offline caches for telemetry buffering during network drops. | Automatically generated by edge nodes on startup. |
| **`.venv/` and `node_modules/`** | Root and `frontend/` | Standard Python virtual environments and Node.js package trees. | Python: `pip install -r requirements.txt`<br>Frontend: `cd frontend && npm install` |

---

### 👥 How Your Friends Can Run as an Edge Client

To have a friend run their own bus node on their laptop:

1. **Have your friend clone this repo** (or send them the project zip):
   ```bash
   git clone https://github.com/Raj-Kanna-05/SIH_124_MVP-v1-.git
   ```
2. **Connect both laptops to the same WiFi or Mobile Hotspot**.
3. **On your server laptop**, find your local IP address:
   ```cmd
   ipconfig
   ```
   *(Look for IPv4 Address under your active network adapter, e.g. `192.168.1.45`)*
4. **On your friend's laptop**, open `edge_client/config.env` and set:
   ```ini
   SERVER_IP=192.168.1.45       # Your server laptop's IP
   BUS_ID=bus_4                 # Unique ID for friend's bus
   ROUTE=route_4                # Pick route_1 through route_5
   VIDEO=assets/dashcam.mp4     # Auto-created by SETUP.bat
   ```
5. **On your friend's laptop**, double-click:
   - **`edge_client/SETUP.bat`** *(run once: installs dependencies, downloads OpenH264 codec, initializes video)*
   - **`edge_client/START.bat`** *(starts live inference and telemetry streaming)*
6. Watch their bus appear live on your Command Center map at `http://localhost:5173`!

---

## 📅 Changelog

### Sessions 2 & 3 — 2026-09-21 · SIH MVP Polishing

#### New: Multi-Bus Demo Orchestration
- `exec.py`: One command launches all 6 components (MQTT broker, FastAPI server, 3 edge nodes, Vite frontend) each in a separate console window.
- `python exec.py` → then open `http://localhost:5173`

#### New: Circular GPS Routes (Buses now loop indefinitely)
| Bus | Route | Location |
|---|---|---|
| bus_1 | route_1.csv | Connaught Place ring, Delhi (~890m radius) |
| bus_2 | route_2.csv | India Gate loop, Delhi (~1110m radius) |
| bus_3 | route_3.csv | Pragati Maidan loop, Delhi (~850m radius) |

#### Fixed: Evidence Clips — Black Screen (H.264 AVC1)
- Root cause: OpenCV `mp4v` (MPEG-4 Part 2) is not supported natively by HTML5 `<video>`.
- Fix: Cisco OpenH264 DLL downloaded; `edge/evidence.py` now writes `avc1` H.264 clips.
- Evidence clips now play directly in the browser without any plugins.

#### New: Multi-Bus Live Camera Switcher
- Dashboard Video Intelligence page: click **Bus 1 / Bus 2 / Bus 3 (test2.mp4)** buttons to switch the live MJPEG feed between buses in real time.
- Server tracks a per-bus frame buffer (`bus_video_frames[bus_id]`) and exposes `/api/video/stream/{bus_id}`.

#### New: Dark / Light Mode
- Click the moon/sun icon in the sidebar to switch. Preference is saved in `localStorage`.

#### New: Portable Edge Client (`edge_client/`)
- Zip and send `edge_client/` to a friend. They edit `config.env`:
  ```
  SERVER_IP=<your laptop IP>
  BUS_ID=bus_4
  ```
  Double-click `SETUP.bat` then `START.bat`. Their bus immediately appears on your dashboard.

#### Tests: 8/8 Passing
```
python tests/test_masterplan_pipeline.py
→ [SUCCESS] ALL MASTER PLAN TESTS PASSED! (8/8)
```

---

*Developed for **Smart India Hackathon (SIH)**.*
