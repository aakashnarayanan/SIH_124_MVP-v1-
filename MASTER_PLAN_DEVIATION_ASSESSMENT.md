# SURADAK Master Plan Deviation Assessment

## Executive assessment

SURADAK is a strong hackathon prototype with a working edge-to-dashboard path. It is substantially closer to the three-day SIH MVP than to the master plan's industrial-grade target.

| Target | Estimated coverage | Rationale |
|---|---:|---|
| 3-day SIH MVP | ~75% | The core demo pipeline, spatial merging, dashboard, edge simulation, and MQTT transport are present. Multi-bus proof and chaos testing are not fully verified. |
| Full master plan | ~40% | The architectural direction is represented, but persistence, a true plugin/microkernel runtime, adaptive media retrieval, data-quality controls, and production telemetry are incomplete. |

These percentages are an engineering assessment, not a test-derived metric.

## Functionality that is genuinely implemented

- Video-file edge simulation with CSV-based GPS route progression.
- Protobuf telemetry published through MQTT QoS 1.
- MQTT persistent-session configuration (`clean_session=False`).
- SQLite offline queueing with reconnection burst upload.
- FastAPI REST endpoints, WebSocket broadcasts, vehicle state, and defect state.
- Thread-safe 3-metre spatial de-duplication with a KD-tree and weighted confidence merging.
- Server-side H3 indexing.
- Edge night-mode, FPS, and vibration MAPE-K decision logic.
- Dashboard pages for command centre, fleet, video, events, analytics, and settings.
- Server-side `MediaSyncRequest` command publication.

The integration test covers Protobuf encoding/decoding, edge cache behavior, 3-metre merging, and night-mode switching.

## Deviation matrix

| Master-plan promise | Current implementation | Consequence |
|---|---|---|
| No continuous video uplink; request a 2-second clip only for severe or unique defects | The edge continuously sends the newest annotated JPEG to `/api/video/frame`; the server holds only one latest frame. | Conflicts with the bandwidth-saving principle in the plan. Useful for a live demo, unsuitable for field deployment. |
| Edge command triggers clip extraction, compression, and cloud storage | The server can publish `MediaSyncRequest`, but the active edge runner has no command handler, ring buffer, clip extraction, H.265 encoding, or S3/MinIO upload. | Knowledge-Media is command plumbing, not an end-to-end evidence workflow. |
| Actual hardware diagnostics | Lux is derived from frame brightness, but vibration remains at its default value; heartbeat CPU temperature, RAM, and signal figures are fixed simulated values. | MAPE-K behavior is demonstrable but not based on real device telemetry. |
| Quantized deployable edge inference | Three models run concurrently in a thread pool, but no INT8 export/runtime optimization or hardware profiling is implemented. | Appropriate for a laptop demo; bus-hardware performance is unproven. |
| Hazard segmentation for waterlogging and debris | `yolov8n-seg.pt` is generic unless replaced with a custom hazard model. Expected puddle/water/crack labels are not standard generic-model classes. | Traffic counting is credible; specialised hazard detection is unvalidated. |
| Five-minute sliding-window confidence and traffic aggregation | `DEDUP_WINDOW_SECONDS = 300` is configured but unused. Counts accumulate for the process lifetime. | No temporal smoothing, expiry, or outlier filtering. |
| Backend-provided H3 heatmap | The server uses H3 resolution 8, while configuration/docs and the frontend use resolution 9. The frontend calculates its own cells from defects rather than consuming `/h3-grid`. | Visible dashboard data can disagree with backend metrics. |
| High-throughput `cKDTree`, O(log N) core | The code uses `scipy.spatial.KDTree` and rebuilds the tree for every new marker. Updated centroids are not re-indexed. | Correct at demo scale, but below the stated high-throughput capability. |
| Strict ports/adapters, microkernel host, plugin lifecycle, and event bus | Folder structure suggests the architecture, but there are no formal port interfaces, event bus, plugin registry, lifecycle isolation, or connected server MAPE plugin. | Architecture-shaped code rather than a complete microkernel implementation. |
| PostGIS/TimescaleDB municipal warehouse | Fleet, defect, H3, and analytics data are in-memory only. | Restart loses history; historical planning and durable audit trails are unavailable. |
| Ingress validation and sanitisation | MQTT payloads are decoded directly into domain records without coordinate/range validation, idempotency controls, authentication, or TLS. | Fine for localhost; not safe or reliable for deployment. |
| Eclipse Mosquitto/Docker fleet environment | A custom pure-Python `amqtt` broker runs locally. | A practical Windows demo shortcut, but not an equivalent hardened broker deployment. |
| Five-bus simulation and chaos demonstration | Emulator scripts support distinct IDs and routes, but there is no orchestration, compose setup, or automated multi-bus/failure drill. | The scenario can be demonstrated manually but is not repeatably proven. |
| Live operational dashboard | The frontend seeds five buses and eight defects when APIs are unavailable. Settings, backup, uptime/storage, and much analytics content are UI/demo-derived. | Strong presentation fallback, but it can mask an unavailable backend. |

## Code-level evidence

- `server/core/ingestion_service.py` creates H3 cells at resolution 8; `frontend/src/components/MapView.tsx` independently uses resolution 9.
- `server/plugins/mape_plugin.py` labels itself a stub and is not wired into the ingestion flow.
- `edge/main.py` continuously uploads latest annotated JPEGs instead of retaining and conditionally uploading an evidence clip.
- `frontend/src/hooks/useRestApi.ts` deliberately switches to presentation data if the API cannot be reached.
- `server/domain/deduplication.py` is thread-safe and valid for demonstration scale, but does not deliver the documented high-throughput behavior.

## Overall conclusion

The team made reasonable time-driven tradeoffs for SIH. Infrastructure, persistence, hardware telemetry, and media storage were reduced in favour of a polished, locally runnable end-to-end demonstration.

The accurate presentation position is:

> SURADAK validates the live edge-to-command-centre loop. Production hardening—persistent spatial storage, adaptive evidence clips, real hardware telemetry, secure fleet deployment, and scalable orchestration—is the next phase.

