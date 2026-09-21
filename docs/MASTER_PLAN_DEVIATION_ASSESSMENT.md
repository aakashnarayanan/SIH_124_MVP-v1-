# SURADAK — Master Plan Deviation Assessment

> **Last updated:** 2026-09-21 · Session 3

## Executive Summary

SURADAK is a strong hackathon-grade prototype delivering a working edge-to-dashboard AI fleet intelligence system. After three focused engineering sessions, the SIH MVP fidelity is now **~94%**. The remaining 6% consists of infrastructure items (PostGIS persistence, cloud upload, auth/TLS) that were explicitly de-scoped for the live demo.

| Target | Coverage | Rationale |
|---|---:|---|
| **3-day SIH MVP** | **~94%** | Full end-to-end pipeline running: MQTT, edge YOLO, server MAPE, H3 hexmap, KD-Tree dedup, multi-bus circular routes, live MJPEG video per bus, H.264 evidence clips, dark/light mode, Urban Events badges, portable edge client. |
| Full master plan (industrial-grade) | ~45% | Persistence, production plugin microkernel, real hardware telemetry, cloud evidence storage, TLS/auth, and production Docker fleet orchestration are not implemented. |

---

## ✅ Implemented & Working (as of 2026-09-21)

| Feature | Implementation |
|---|---|
| Edge video simulation with CSV GPS route loops | 3 circular routes: Connaught Place, India Gate, Pragati Maidan |
| Protobuf telemetry over MQTT QoS 1 | `EdgeTelemetryPacket` → broker → server ingestion |
| MQTT persistent session (clean_session=False) | Offline SQLite cache with burst upload on reconnect |
| Pure-Python MQTT broker (amqtt) | No Docker/Mosquitto binary needed on Windows |
| MQTT ingress sanitiser | lat/lon range, confidence [0,1], positive timestamp; malformed payloads dropped |
| KD-Tree 3m spatial de-duplication | Weighted confidence merge; temporal window expiry (300s) |
| H3 hexagonal heatmap (server-side) | Resolution 8, 5-minute sliding window MAPE aggregation |
| H3 heatmap frontend rendering | 5-tier color scale (cyan→red), wired to `/h3-grid` endpoint |
| FastAPI REST + WebSocket broadcast | `/vehicles`, `/defects`, `/h3-grid`, `/stats`, `/api/clips`, `/api/video/stream/{bus_id}` |
| Multi-bus live MJPEG streams | Per-bus streams `/api/video/stream/{bus_id}`; camera switcher in frontend |
| Evidence clip generation (H.264 AVC1) | OpenH264 via OpenCV; ring buffer, off-thread MP4 writer, hover-to-play in UI |
| Urban Events with live clip badges | `🎬 LIVE CLIP` when clip_url is set; `🖼 PREVIEW` for stock fallback |
| Dark / Light mode toggle | CSS variable system, persists in localStorage |
| Portable edge_client folder | Friend edits `config.env` → `SERVER_IP=`, runs `START.bat` |
| Pipeline test suite (8/8 pass) | Protobuf, SQLite cache, KD-Tree dedup, MAPE-K, ingress sanitiser, H3 window, temporal expiry, evidence clip |

---

## ❌ Known Deviations from Full Master Plan

| Master Plan Promise | Current Implementation | Notes |
|---|---|---|
| No continuous video uplink; request-only 2-second clips | JPEG frames uploaded per `--demo-stream-frames` flag; gated for demo mode | Acceptable for SIH demo; wrong for field deployment |
| H.265 evidence clips + cloud (S3/MinIO) upload | H.264 local MP4 clips; no cloud upload | Clips stay on edge node filesystem |
| PostGIS/TimescaleDB spatial warehouse | In-memory only; history lost on server restart | Durable storage is post-SIH roadmap |
| Actual hardware diagnostics (IMU, thermal, GPS) | Lux derived from brightness; vibration is default value; GPS simulated via CSV | Demo-appropriate; real hardware requires device integration |
| INT8 quantised custom YOLO models | Generic YOLOv8n models; custom hazard training not done | Traffic counting credible; specialised hazard detection unvalidated |
| Strict ports/adapters microkernel + event bus | Folder structure represents architecture; no formal plugin registry or lifecycle isolation | Architecture-shaped code; full microkernel is a later milestone |
| Eclipse Mosquitto / Docker | Pure-Python amqtt broker runs locally | Practical Windows shortcut; not production-equivalent |
| `cKDTree` O(log N) at scale | `scipy.spatial.KDTree` rebuilt per insert; fine at demo scale | High-throughput claim unverified |
| Centroid re-indexing after merge | Updated centroids not re-inserted into KD-Tree | Demo-scale limitation; correct for small fleets |
| Automated multi-bus chaos demonstration | Manual `exec.py` launch of 3 buses | No automated failure drill or Docker compose orchestration |
| Full analytics page (historical data) | Analytics UI uses demo-derived content | Real analytics needs backend aggregation endpoints |

---

## Overall Conclusion

SURADAK successfully validates the live edge-to-command-centre loop for SIH demonstration. The core architectural direction is sound:

> *SURADAK validates the live edge-to-command-centre loop. Production hardening — persistent spatial storage, adaptive evidence clips, real hardware telemetry, secure fleet deployment, and scalable orchestration — is the next phase.*

The team made correct time-driven tradeoffs for SIH. The project is demo-ready and presentable.
