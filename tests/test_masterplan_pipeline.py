"""
Full System Integration Test — Master Plan Architecture
======================================================
Tests:
  1. Protobuf serialization (EdgeTelemetryPacket)
  2. Edge SQLite circuit breaker (store & retrieve)
  3. Server KD-Tree 3-Meter deduplication (assert repeat within 2m merges, 10m creates new)
  4. H3 hexagonal cell mapping
  5. Edge MAPE-K Loop (Day vs Night mode adaptation)
  6. Server MAPE H3 sliding-window expiry and metric aggregation
  7. KD-Tree temporal window expiry (stale marker purge)
  8. Edge EvidenceClipBuffer local MP4 generation on MediaSyncRequest
"""

import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "server")))

from proto import telemetry_pb2
from edge.storage.cache import EdgeTelemetryCache
from edge.mape_k_edge import EdgeMAPELoop
from server.domain.deduplication import SpatialDeduplicationEngine
from server.core.ingestion_service import TelemetryIngestionService
from server.domain.models import TelemetryReading
import numpy as np


def test_protobuf_serialization():
    print("Testing Protobuf Serialization...")
    packet = telemetry_pb2.EdgeTelemetryPacket()
    packet.bus_id = "bus_delhi_101"
    packet.latitude = 28.6145
    packet.longitude = 77.2108
    packet.object_type = "pothole"
    packet.confidence = 0.92
    packet.timestamp_ms = int(time.time() * 1000)
    packet.vehicle_count = 5
    packet.lux_level = 14.5
    packet.vibration_g = 1.2
    packet.network_signal_db = -80.0

    raw_bytes = packet.SerializeToString()
    assert len(raw_bytes) > 0, "Packet should serialize to non-empty byte string"
    print(f"  [OK] Protobuf payload size: {len(raw_bytes)} bytes (ultra-compact)")

    # Decode
    decoded = telemetry_pb2.EdgeTelemetryPacket()
    decoded.ParseFromString(raw_bytes)
    assert decoded.bus_id == "bus_delhi_101"
    assert decoded.object_type == "pothole"
    assert abs(decoded.latitude - 28.6145) < 1e-4
    print("  [OK] Protobuf deserialization matched perfectly.")


def test_edge_sqlite_circuit_breaker():
    print("Testing Edge SQLite Circuit Breaker Cache...")
    test_db = "edge/storage/test_circuit_breaker.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    cache = EdgeTelemetryCache(db_path=test_db)
    assert cache.count() == 0

    # Enqueue 3 packets
    for i in range(3):
        cache.enqueue("fleet/bus_1/telemetry", f"test_data_{i}".encode("utf-8"), int(time.time() * 1000))

    assert cache.count() == 3
    batch = cache.peek_batch(limit=2)
    assert len(batch) == 2
    ids_to_remove = [item[0] for item in batch]
    cache.remove_batch(ids_to_remove)
    assert cache.count() == 1
    print("  [OK] SQLite offline queueing, FIFO batching, and purging works.")

    try:
        if os.path.exists(test_db):
            os.remove(test_db)
    except Exception:
        pass


def test_kdtree_deduplication():
    print("Testing Server 3-Meter KD-Tree Deduplication...")
    dedup = SpatialDeduplicationEngine(radius_meters=3.0)

    # Point 1: Connaught Place Center
    r1 = TelemetryReading(
        bus_id="bus_1",
        latitude=28.631500,
        longitude=77.216700,
        object_type="pothole",
        confidence=0.80,
        timestamp_ms=1000,
    )
    action1, m1 = dedup.process(r1)
    assert action1 == "new"
    assert m1.sighting_count == 1
    print(f"  [OK] First pothole registered: {m1.defect_id[:8]}..")

    # Point 2: 1.5 meters away (should MERGE into existing)
    # Approx 0.000013 degrees latitude is ~1.45 meters
    r2 = TelemetryReading(
        bus_id="bus_2",
        latitude=28.631513,
        longitude=77.216700,
        object_type="pothole",
        confidence=0.90,
        timestamp_ms=2000,
    )
    action2, m2 = dedup.process(r2)
    assert action2 == "updated"
    assert m2.defect_id == m1.defect_id
    assert m2.sighting_count == 2
    assert abs(m2.confidence - 0.85) < 0.01
    print("  [OK] Second reading 1.5m away successfully merged (sighting count: 2, conf: 0.85).")

    # Point 3: 50 meters away (should create NEW defect)
    r3 = TelemetryReading(
        bus_id="bus_3",
        latitude=28.632000,
        longitude=77.216700,
        object_type="pothole",
        confidence=0.75,
        timestamp_ms=3000,
    )
    action3, m3 = dedup.process(r3)
    assert action3 == "new"
    assert m3.defect_id != m1.defect_id
    assert dedup.get_marker_count() == 2
    print("  [OK] Third reading 55m away created new defect marker.")


def test_edge_mape_k_loop():
    print("Testing Edge MAPE-K Loop (Day vs Night Adaptability)...")
    loop = EdgeMAPELoop(lux_night_threshold=25.0)

    # Simulate bright daylight frame (mean pixel luminance = 160)
    day_frame = np.full((100, 100, 3), 160, dtype=np.uint8)
    m_day = loop.monitor(day_frame, last_frame_time=time.time())
    a_day = loop.analyze(m_day)
    p_day = loop.plan(a_day)
    e_day = loop.execute(p_day)
    assert not e_day["is_night_mode"]
    print("  [OK] Daylight correctly keeps Day Mode active.")

    # Simulate dark nighttime frame (mean pixel luminance = 10)
    night_frame = np.full((100, 100, 3), 10, dtype=np.uint8)
    m_night = loop.monitor(night_frame, last_frame_time=time.time())
    a_night = loop.analyze(m_night)
    p_night = loop.plan(a_night)
    # allow cooldown
    loop.last_switch_time = 0.0
    p_night = loop.plan(a_night)
    e_night = loop.execute(p_night)
    assert e_night["is_night_mode"]
    print("  [OK] Low light (lux < 25) dynamically triggered Night Mode adaptation.")


def test_ingress_sanitizer():
    print("Testing MQTT ingress sanitiser...")
    from server.domain.ingress import sanitize_reading

    ok = TelemetryReading(
        bus_id=" bus_1 ",
        latitude=28.63,
        longitude=77.21,
        object_type="pothole",
        confidence=0.8,
        timestamp_ms=1,
        vehicle_count=3,
    )
    cleaned = sanitize_reading(ok)
    assert cleaned is not None
    assert cleaned.bus_id == "bus_1"
    assert sanitize_reading(TelemetryReading(
        bus_id="bus_1", latitude=91, longitude=77, object_type="pothole",
        confidence=0.5, timestamp_ms=1,
    )) is None
    assert sanitize_reading(TelemetryReading(
        bus_id="bus_1", latitude=28, longitude=77, object_type="pothole",
        confidence=1.5, timestamp_ms=1,
    )) is None
    print("  [OK] Valid packets pass; out-of-range lat/confidence are dropped.")


def test_mape_h3_sliding_window():
    """Verify ServerMAPEPlugin sliding-window expiry and metric aggregation."""
    print("Testing Server MAPE H3 sliding-window expiry and aggregation...")
    import sys as _sys
    import os as _os
    _sys.path.insert(0, _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "server")))
    from server.plugins.mape_plugin import ServerMAPEPlugin
    from server.domain.models import DefectMarker as _DefectMarker

    # Use a 2-second window so we can test expiry without sleeping
    plugin = ServerMAPEPlugin(h3_resolution=9, window_seconds=2)
    t0_ms = 1_000_000

    r1 = TelemetryReading(
        bus_id="bus_1", latitude=28.6315, longitude=77.2167,
        object_type="pothole", confidence=0.85, timestamp_ms=t0_ms, vehicle_count=4,
    )
    m1 = _DefectMarker(
        defect_id="def_1", latitude=28.6315, longitude=77.2167,
        object_type="pothole", confidence=0.85, sighting_count=1,
        first_seen_ms=t0_ms, last_seen_ms=t0_ms,
    )

    plugin.on_telemetry(r1)
    plugin.on_defect_new(m1, r1)

    # Corroborating reading within active window
    r2 = TelemetryReading(
        bus_id="bus_2", latitude=28.6315, longitude=77.2167,
        object_type="pothole", confidence=0.90, timestamp_ms=t0_ms + 1000, vehicle_count=2,
    )
    plugin.on_telemetry(r2)
    plugin.on_defect_updated(m1, r2)

    # Verify aggregation at t0 + 1s (still within 2s window)
    cells = plugin.get_h3_cells(now_ms=t0_ms + 1000)
    assert len(cells) == 1, f"Expected 1 active cell, got {len(cells)}"
    cell_data = list(cells.values())[0]
    assert cell_data["traffic_count"] == 6, f"Expected traffic_count=6 (4+2), got {cell_data['traffic_count']}"
    assert cell_data["defect_reports"] == 2, f"Expected defect_reports=2, got {cell_data['defect_reports']}"
    assert cell_data["unique_defects"] == 1, f"Expected unique_defects=1, got {cell_data['unique_defects']}"
    print("  [OK] Aggregation: traffic_count=6, defect_reports=2, unique_defects=1.")

    # Advance well past the 2s window so both events (t0_ms and t0_ms+1000) are
    # strictly older than cutoff (now_ms - window_ms = t0+4000 - 2000 = t0+2000).
    # The expiry guard is `timestamp < cutoff` (strictly less than), so we need
    # the newest event (t0_ms+1000) to satisfy 1000 < 2000 — hence now_ms = t0+4000.
    expired_cells = plugin.get_h3_cells(now_ms=t0_ms + 4000)
    assert len(expired_cells) == 0, f"Expected 0 cells after window expiry, got {len(expired_cells)}"
    print("  [OK] Aggregation counts matched; expired cells purged past window.")


def test_kdtree_window_expiry():
    """Verify SpatialDeduplicationEngine purges markers older than the window."""
    print("Testing KD-Tree temporal window expiry...")
    from server.domain.deduplication import SpatialDeduplicationEngine as _SDE

    dedup = _SDE(radius_meters=3.0, window_seconds=2)
    t0_ms = 1_000_000

    r1 = TelemetryReading(
        bus_id="bus_1", latitude=28.631500, longitude=77.216700,
        object_type="pothole", confidence=0.80, timestamp_ms=t0_ms,
    )
    action1, m1 = dedup.process(r1)
    assert action1 == "new", f"Expected 'new', got '{action1}'"
    assert dedup.get_marker_count() == 1
    print(f"  [OK] Initial marker registered: {m1.defect_id[:8]}..")

    # Same location but arrives after window cutoff (t0 + 3s > 2s window)
    r2 = TelemetryReading(
        bus_id="bus_2", latitude=28.631500, longitude=77.216700,
        object_type="pothole", confidence=0.85, timestamp_ms=t0_ms + 3000,
    )
    action2, m2 = dedup.process(r2)
    assert action2 == "new", f"Stale marker must not merge — expected 'new', got '{action2}'"
    assert m2.defect_id != m1.defect_id, "Re-instantiated marker must have a fresh defect_id"
    assert dedup.get_marker_count() == 1, (
        f"Purged stale marker must be removed — expected count=1, got {dedup.get_marker_count()}"
    )
    print("  [OK] Stale markers purged and re-instantiated outside window.")


def test_evidence_clip_buffer():
    """Verify EvidenceClipBuffer captures frames and exports a local MP4 on request_clip()."""
    print("Testing Edge EvidenceClipBuffer local MP4 generation...")
    import tempfile
    import shutil
    from pathlib import Path
    from edge.evidence import EvidenceClipBuffer

    temp_dir = Path(tempfile.mkdtemp(prefix="suradak_test_evidence_"))
    try:
        saved_clips: list = []
        buf = EvidenceClipBuffer(
            output_dir=temp_dir,
            fps=10.0,
            retention_seconds=3.0,
            on_complete=lambda p: saved_clips.append(p),
        )

        dummy_frame = np.zeros((120, 160, 3), dtype=np.uint8)
        # Push 15 frames (~1.5 s of simulated footage at 10 fps)
        for i in range(15):
            buf.add_frame(raw=dummy_frame, annotated=dummy_frame, captured_at=float(i) * 0.1)

        assert buf.frame_count == 15, f"Expected 15 buffered frames, got {buf.frame_count}"

        ok = buf.request_clip(defect_id="test_pothole_42", duration_seconds=1)
        assert ok is True, "request_clip() must return True when buffer is non-empty"

        buf.stop()  # Blocks until the writer thread flushes all pending jobs

        assert len(saved_clips) == 1, f"Expected 1 saved clip, got {len(saved_clips)}"
        assert saved_clips[0].exists(), f"Clip file not found: {saved_clips[0]}"
        assert saved_clips[0].stat().st_size > 0, "Clip file must be non-empty"
        print(f"  [OK] Evidence MP4 successfully captured and flushed: {saved_clips[0].name}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING MASTER PLAN PIPELINE TESTS")
    print("=" * 60)
    test_protobuf_serialization()
    test_edge_sqlite_circuit_breaker()
    test_kdtree_deduplication()
    test_edge_mape_k_loop()
    test_ingress_sanitizer()
    test_mape_h3_sliding_window()
    test_kdtree_window_expiry()
    test_evidence_clip_buffer()
    print("=" * 60)
    print("[SUCCESS] ALL MASTER PLAN TESTS PASSED! (8/8)")
    print("=" * 60)
