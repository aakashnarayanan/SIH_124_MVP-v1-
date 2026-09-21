# 🚍 SURADAK — Edge Transit AI Node

> **Real-Time On-Device Multi-Model Computer Vision, Autonomic MAPE-K Adaptation & Resilient Telemetry Streaming**  
> *Component of SURADAK Urban AI Fleet Intelligence*

---

## 📌 Overview

The **Edge Transit AI Node** (`edge/`) is designed to run directly on municipal transit buses equipped with forward-facing dashcams. Instead of uploading massive streams of raw video to the cloud, the edge node performs **on-device parallel neural inference**, detecting road surface defects and analyzing traffic density in real time.

Detections are packaged into ultra-compact **Google Protocol Buffers** and published over **MQTT**. If a bus enters a cellular dead zone, an on-device **SQLite circuit breaker** automatically buffers all telemetry and flushes it upon reconnection.

---

## 🧠 Core Features & Architecture

### 1. Parallel 3-Model YOLO Vision Engine (`inference.py`)
The node executes three specialized neural network pipelines concurrently:
- **Model A — Pothole Detection**: Identifies road cavities, asphalt voids, and surface depressions.
- **Model B — Traffic Survey & Breakdown**: Detects, tracks, and classifies surrounding vehicles (cars, buses, trucks, motorcycles, bicycles).
- **Model C — Road Hazard Segmentation**: Detects waterlogging, open manholes, and debris using polygon segmentation masks.

### 2. Autonomic MAPE-K Control Loop (`mape_k_edge.py`)
Implements an autonomic feedback loop that continuously optimizes edge computing performance:
- **Monitor**: Measures frame luminosity (LUX) and bus vibration ($G$).
- **Analyze**: Identifies low-light conditions ($\text{LUX} < 30$) or severe vibrations ($G > 2.5$) caused by rough terrain.
- **Plan & Execute**: 
  - Automatically activates **Night Vision Enhancement** (CLAHE contrast equalization) when driving in dark tunnels or at night.
  - Dynamically throttles processing or drops degraded blur frames to prevent thermal throttling and conserve GPU/CPU cycles.

### 3. Offline Circuit Breaker & Protocol Buffers (`storage/cache.py`)
- Serializes telemetry into binary **Google Protocol Buffers** (`proto/telemetry.proto`), cutting cellular payload size by ~80% compared to standard JSON.
- If MQTT broker connection drops, packets are automatically saved to a local SQLite database (`edge/storage/telemetry_cache.db`).
- Once cellular connectivity returns, cached packets are systematically flushed in FIFO order.

### 4. Monotonic GPS Tracking & Route Waypoints (`gps_tracks/`)
Coordinates advance monotonically along real-world urban bus routes:
- `route_1.csv`: Northeast Delhi transit trajectory (102 waypoints)
- `route_2.csv`: South Delhi transit trajectory (102 waypoints)
- `route_3.csv`: Northwest Delhi transit trajectory (102 waypoints)
*The GPS index advances smoothly across video loops (`processed_count // target_fps`), ensuring the bus travels steadily forward along the route without snapping back.*

---

## 🚀 Execution Guide

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run the Edge Node
From the project root:

```powershell
python main.py --source edge/assets/test_dashcam.mp4 --fps 15 --show-video --verbose
```

### CLI Command Options

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--source` / `--video` | `str` | `edge/assets/test_dashcam.mp4` | Path to dashcam video file (e.g. `edge/assets/test2.mp4`) |
| `--fps` | `int` | `15` | Target inference frame rate |
| `--show-video` | `flag` | `False` | Opens real-time OpenCV desktop window with bounding boxes and HUD overlay |
| `--verbose` | `flag` | `True` | Streams structured telemetry output directly to the terminal |
| `--bus-id` | `str` | `bus_1` | Unique bus identifier (e.g. `bus_1`, `bus_2`) |
| `--route` | `str` | `edge/gps_tracks/route_1.csv` | GPS waypoint CSV file |
| `--broker-host` | `str` | `localhost` | MQTT broker hostname / IP address |
| `--broker-port` | `int` | `1883` | MQTT broker listening port |
| `--save-video` | `str` | `None` | Optional path to export annotated output video (`.mp4`) |

---

## 🖥️ Live Terminal Telemetry Format

When running with `--verbose`, the edge node streams clean, single-line telemetry records:

```text
[2026-09-06T10:15:30Z] Heading: NE | GPS: (28.614506, 77.210812) | Defects: 2 found: ['Pothole', 'Pothole'] | Traffic: 4 vehicles (3 cars, 1 bus) | Net: ONLINE (MQTT)
```

---

## 📁 Directory Structure

```
edge/
├── assets/                  # Test dashcam videos (test_dashcam.mp4, etc.)
├── config.py                # Edge thresholds (Lux, Vibration, Broker settings)
├── gps_tracks/              # Real-world waypoint CSV tracks
│   ├── route_1.csv          # Delhi Route 1 (102 waypoints)
│   ├── route_2.csv          # Delhi Route 2 (102 waypoints)
│   └── route_3.csv          # Delhi Route 3 (102 waypoints)
├── inference.py             # Parallel multi-YOLO inference & HUD overlay rendering
├── main.py                  # Edge transit node execution loop
├── mape_k_edge.py           # Autonomic MAPE-K adaptation loop (Lux & Vibration)
├── network/
│   └── mqtt_client.py       # Paho MQTT publisher with auto-reconnection
└── storage/
    └── cache.py             # SQLite offline circuit breaker storage
```

---

## 📅 Update Log

### Session 2 — 2026-09-21 · Circular Routes & Evidence Clips

#### GPS Routes — Now Circular Loops
The three route CSVs were updated to **closed circular rings** around Delhi landmarks so bus icons loop indefinitely on the dashboard map:

| Route | Location | Radius | Points |
|---|---|---|---|
| `route_1.csv` | Connaught Place ring | ~890m | 100 pts (2 laps) |
| `route_2.csv` | India Gate loop | ~1110m | 100 pts (2 laps) |
| `route_3.csv` | Pragati Maidan loop | ~850m | 100 pts (2 laps) |

#### Evidence Clip System (`evidence.py` — NEW file)
On-device `EvidenceClipBuffer`:
- Keeps a sliding 10-second ring buffer of annotated + raw frames.
- On `MediaSyncRequest` MQTT command, writes a local MP4 evidence clip off-thread (non-blocking).
- Clip saved to `edge/evidence_clips/{bus_id}/` on disk.
- Server exposes clips via REST `/api/clips` and `/api/clips/{bus_id}/{filename}`.

#### Health Monitor (`health.py` — NEW file)
Samples process RAM (`psutil`) and Linux CPU thermal zone temperature where available; returns 0 on Windows for temperature.

### Session 3 — 2026-09-21 · H.264 Video Codec Fix & Multi-Bus Streaming

#### Evidence Clips — Fixed Black Screen (mp4v → AVC1 H.264)
- `evidence.py` now uses `cv2.VideoWriter_fourcc(*"avc1")` (H.264) as primary codec with `mp4v` fallback.
- Requires Cisco OpenH264 DLL: automatically downloaded to Python runtime dir by `SETUP.bat` / manually from `http://ciscobinary.openh264.org/`.
- Old clips (MPEG-4 Part 2) were unplayable in browsers; new clips play natively in `<video>` tags.

#### New CLI Flag — `--demo-stream-frames`
The `run_edge_node()` function and `main()` both accept `--demo-stream-frames`. Without this flag, no JPEG frames are POSTed to the server (saves bandwidth; Protobuf telemetry always flows). **All 3 buses now pass this flag in `exec.py`.**

#### Multi-Bus MJPEG Streaming
Each bus's live JPEG frames are stored in a per-bus dictionary on the server (`bus_video_frames[bus_id]`). The dashboard's Video Intelligence page can switch between bus feeds in real time.
