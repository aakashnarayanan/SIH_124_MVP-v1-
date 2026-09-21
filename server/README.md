# ⚡ SURADAK — Core Ingestion & Deduplication Server

> **High-Throughput Protobuf Ingestion, Concurrent 3-Meter Spatial Deduplication & Real-Time WebSocket Broadcaster**  
> *Component of SURADAK Urban AI Fleet Intelligence*

---

## 📌 Overview

The **Core Server** (`server/`) serves as the central brain of the SURADAK platform. Designed following **Hexagonal Architecture (Ports & Adapters)**, it ingests binary Protobuf telemetry streams published by edge nodes over MQTT, executes a concurrent **SciPy KD-Tree deduplication engine** to eliminate repeated defect sightings, calculates municipal density heatmaps using **Uber H3**, and broadcasts live telemetry to dashboard clients via **WebSockets**.

---

## 🏛️ Architecture & Key Systems

```
                              ┌──────────────────────────────────────────────┐
                              │            CORE INGESTION ENGINE             │
                              │                                              │
  [ Edge Node MQTT Telemetry ]│  1. Binary Protobuf Deserialization          │
  (fleet/+/telemetry)         │     (telemetry.proto -> TelemetryReading)    │
              │               │                                              │
              ▼               │  2. Concurrent 3-Meter Spatial Dedup         │
  ┌────────────────────────┐  │     (SciPy cKDTree Cartesian O(log N))       │
  │   MQTT Inbound Port    │──┼─►                                            │
  │ (Paho MQTT Adapter)    │  │  3. Uber H3 Spatial Density Aggregation      │
  └────────────────────────┘  │     (Resolution 9 Hexagonal Polygons)        │
                              │                                              │
                              └──────────────────────┬───────────────────────┘
                                                     │
                                                     ▼
                             ┌───────────────────────────────────────────────┐
                             │               OUTBOUND PORTS                  │
                             │                                               │
                             │  • WebSocket Broadcaster (/ws/dashboard)      │
                             │    - vehicle_moved, defect_new, defect_updated│
                             │  • REST API Endpoints                         │
                             │    - /vehicles, /defects, /health             │
                             └───────────────────────────────────────────────┘
```

### 1. Concurrent 3-Meter Spatial Deduplication (`domain/deduplication.py`)
- **The Challenge**: When a bus drives over a pothole at 10 FPS, or when multiple buses traverse the same avenue throughout the day, the same defect is detected dozens of times. Naive systems create duplicate tickets.
- **The Solution**:
  - The deduplication engine projects geographic coordinates (latitude, longitude) into an equidistant Cartesian plane.
  - Using **`scipy.spatial.cKDTree`**, incoming defect coordinates are queried in $O(\log N)$ time with a **3-meter radius**.
  - If a match is found: coordinates are refined using a running centroid, confidence is recalculated with weighted probability, and `sighting_count` increments.
  - If no match exists: a new verified `defect_id` is assigned and indexed into the KD-Tree.

### 2. Uber H3 Hexagonal Density Matrix (`core/ingestion_service.py`)
- Hazards and traffic density are mapped to **Uber H3 hexagonal indices** at **Resolution 9** (~174m edge length).
- The server computes hex density boundaries via `h3.cell_to_boundary` for instant rendering on client maps without heavy client-side spatial calculations.

### 3. Hexagonal Adapters
- **Inbound MQTT Adapter (`adapters/mqtt_adapter.py`)**: Subscribes to `fleet/+/telemetry` and `fleet/+/heartbeat`, automatically unpacking binary protobuf packets.
- **Outbound WebSocket Adapter (`adapters/websocket_adapter.py`)**: Manages concurrent WebSocket connections and broadcasts instant updates to the web dashboard.

---

## 🚀 Execution Guide

### 1. Install Dependencies
```powershell
cd server
pip install -r requirements.txt
```

### 2. Run Server
```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
> *Server starts at: **`http://localhost:8000`** (Swagger docs available at **`http://localhost:8000/docs`**).*

---

## 🌐 API & Event Reference

### REST Endpoints

| Endpoint | Method | Response | Purpose |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | `{"status": "online", "service": "..."}` | Root health & service status |
| `/health` or `/api/health` | `GET` | JSON | Active buses, defect counts, H3 clusters & uptime |
| `/vehicles` or `/api/vehicles` | `GET` | `{"count": N, "vehicles": [...]}` | Current coordinates of all active buses |
| `/defects` or `/api/defects` | `GET` | `{"count": N, "defects": [...]}` | Deduplicated road defect records |
| `/ws/dashboard` | `WS` | WebSocket Pipeline | Real-time event stream to frontend |

### WebSocket Event Schemas

Clients connecting to `ws://localhost:8000/ws/dashboard` receive JSON-formatted event frames:

```json
// 1. Vehicle Movement Update
{
  "event": "vehicle_moved",
  "data": {
    "bus_id": "bus_1",
    "latitude": 28.614506,
    "longitude": 77.210812,
    "timestamp_ms": 1725443400000,
    "lux": 105,
    "vibration_g": 0.32
  }
}

// 2. New Defect Discovered
{
  "event": "defect_new",
  "data": {
    "defect_id": "def_a1b2c3d4",
    "latitude": 28.614506,
    "longitude": 77.210812,
    "object_type": "pothole",
    "confidence": 0.88,
    "sighting_count": 1,
    "first_seen_ms": 1725443400000,
    "last_seen_ms": 1725443400000,
    "bus_id": "bus_1"
  }
}

// 3. Existing Defect Sighted & Merged
{
  "event": "defect_updated",
  "data": {
    "defect_id": "def_a1b2c3d4",
    "confidence": 0.94,
    "sighting_count": 4,
    "last_seen_ms": 1725443410000
  }
}
```

---

## 📁 Directory Structure

```
server/
├── adapters/
│   ├── mqtt_adapter.py           # Inbound MQTT client with Protobuf deserialization
│   └── websocket_adapter.py      # Thread-safe WebSocket broadcaster
├── clips_router.py               # [NEW] Evidence clips REST API router
├── config.py                     # Host, port, and spatial deduplication constants
├── core/
│   └── ingestion_service.py      # Business logic coordinator & H3 density grid
├── domain/
│   ├── deduplication.py          # 3-Meter SciPy cKDTree spatial deduplication engine
│   ├── ingress.py                # [NEW] MQTT ingress sanitiser / validation layer
│   └── models.py                 # TelemetryReading, DefectMarker, VehiclePosition dataclasses
├── plugins/
│   ├── km_plugin.py              # Knowledge-Media snapshot orchestration
│   └── mape_plugin.py            # Autonomic feedback server metrics
├── main.py                       # FastAPI application & REST endpoint routes
└── requirements.txt              # Server dependencies (FastAPI, Uvicorn, SciPy, H3, etc.)
```

---

## 📅 Update Log

### Session 1 — 2026-09-20 · MQTT Ingress Sanitiser & H3 Sliding Window

- **`domain/ingress.py`** (NEW): Validates all inbound MQTT telemetry. Drops packets with latitude outside [-90, 90], longitude outside [-180, 180], confidence outside [0.0, 1.0], or non-positive timestamp. Truncates `bus_id` and `object_type` to 64 chars.
- **`plugins/mape_plugin.py`**: Now a live 5-minute H3 sliding-window MAPE aggregator. Thread-safe deque per H3 cell. `get_h3_cells(now_ms)` filters events to the active window. Aggregates `traffic_count`, `defect_reports`, `unique_defects`.
- **`domain/deduplication.py`**: Added `DEDUP_WINDOW_SECONDS = 300` — markers older than the window are purged and their positions can be re-registered.

### Session 2 — 2026-09-21 · Evidence Clips REST API

- **`clips_router.py`** (NEW): FastAPI `APIRouter` mounted at `/api/clips`:
  - `GET /api/clips` — lists all MP4 clips from `edge/evidence_clips/` sorted newest-first
  - `GET /api/clips/{bus_id}/{filename}` — streams MP4 via `FileResponse`
- **`main.py`**: Clips router mounted at startup; CORS enabled for localhost frontend.

### Session 3 — 2026-09-21 · Multi-Bus MJPEG Video Streaming

- **`main.py`**: Added `bus_video_frames: dict[str, bytes]` global keyed by `X-Bus-Id` HTTP header.
  - `POST /api/video/frame` now stores frame in per-bus dict (and still updates `latest_video_frame` for backward compatibility).
  - `GET /api/video/stream/{bus_id}` — per-bus MJPEG stream.
  - `GET /api/video/stream` — unchanged; returns most-recent frame.
  - `GET /api/video/buses` — returns list of bus IDs currently posting frames.
