"""Server-side MAPE-K state for short-lived operational map aggregates."""

from __future__ import annotations

from collections import defaultdict, deque
import logging
import threading
import time
from typing import Deque, Dict, Tuple

import h3

from config import DEDUP_WINDOW_SECONDS, H3_RESOLUTION
from domain.models import DefectMarker, TelemetryReading

logger = logging.getLogger("MAPEPlugin")

# (event timestamp in ms, traffic count, defect report count, unique defect count)
_CellEvent = Tuple[int, int, int, int]


class ServerMAPEPlugin:
    """Maintain a thread-safe, expiring H3 view of current fleet activity."""

    def __init__(self, h3_resolution: int = H3_RESOLUTION,
                 window_seconds: int = DEDUP_WINDOW_SECONDS):
        if h3_resolution < 0 or h3_resolution > 15:
            raise ValueError("h3_resolution must be between 0 and 15")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.h3_resolution = h3_resolution
        self.window_ms = window_seconds * 1000
        self._lock = threading.Lock()
        self._events: Dict[str, Deque[_CellEvent]] = defaultdict(deque)
        logger.info("[MAPE] H3 sliding-window knowledge store initialized "
                    "(resolution=%s, window=%ss)", h3_resolution, window_seconds)

    def on_telemetry(self, reading: TelemetryReading) -> None:
        """Record one fleet observation, weighted by its reported vehicle count."""
        self._record(reading.latitude, reading.longitude, reading.timestamp_ms,
                     traffic=max(0, reading.vehicle_count))

    def on_defect_new(self, marker: DefectMarker, reading: TelemetryReading) -> None:
        """Record a newly unique defect and its first report in the active window."""
        self._record(marker.latitude, marker.longitude, reading.timestamp_ms,
                     defect_reports=1, unique_defects=1)

    def on_defect_updated(self, marker: DefectMarker, reading: TelemetryReading) -> None:
        """Record corroboration without inflating the unique-defect count."""
        self._record(marker.latitude, marker.longitude, reading.timestamp_ms,
                     defect_reports=1)

    def _record(self, latitude: float, longitude: float, timestamp_ms: int,
                traffic: int = 0, defect_reports: int = 0,
                unique_defects: int = 0) -> None:
        try:
            cell = h3.latlng_to_cell(latitude, longitude, self.h3_resolution)
        except Exception as exc:
            logger.warning("[MAPE] Ignoring observation with invalid H3 position: %s", exc)
            return
        with self._lock:
            self._events[cell].append((timestamp_ms, traffic, defect_reports, unique_defects))
            self._expire_locked(timestamp_ms)

    def _expire_locked(self, now_ms: int) -> None:
        cutoff = now_ms - self.window_ms
        empty_cells = []
        for cell, events in self._events.items():
            while events and events[0][0] < cutoff:
                events.popleft()
            if not events:
                empty_cells.append(cell)
        for cell in empty_cells:
            del self._events[cell]

    def get_h3_density_map(self, now_ms: int | None = None) -> dict[str, int]:
        """Compatibility view of active traffic density, keyed by H3 cell."""
        return {cell: data["traffic_count"]
                for cell, data in self.get_h3_cells(now_ms).items()}

    def get_h3_cells(self, now_ms: int | None = None) -> dict[str, dict[str, int]]:
        """Return active totals after expiring observations outside the window."""
        now_ms = int(time.time() * 1000) if now_ms is None else now_ms
        with self._lock:
            self._expire_locked(now_ms)
            return {
                cell: {
                    "traffic_count": sum(event[1] for event in events),
                    "defect_reports": sum(event[2] for event in events),
                    "unique_defects": sum(event[3] for event in events),
                }
                for cell, events in self._events.items()
            }
