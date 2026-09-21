"""
Server Core: Telemetry Ingestion Service
========================================
Coordinates the full ingestion pipeline:
  1. Updates vehicle position in memory
  2. Updates Uber H3 hexagonal spatial density index
  3. Executes KD-Tree 3-Meter Spatial Deduplication
  4. Triggers K-M plugin for video sync if confidence is high
  5. Broadcasts real-time events to frontend via WebSockets
"""

import asyncio
import logging
import time
from dataclasses import asdict
from typing import Optional, Dict, List, Any
import h3

from domain.models import TelemetryReading, DefectMarker, VehiclePosition
from domain.deduplication import SpatialDeduplicationEngine

logger = logging.getLogger("IngestionService")


class TelemetryIngestionService:
    def __init__(
        self,
        dedup_engine: SpatialDeduplicationEngine,
        ws_broadcast=None,
        km_plugin=None,
        mape_plugin=None,
    ):
        self._dedup = dedup_engine
        self._ws_broadcast = ws_broadcast
        self._km_plugin = km_plugin
        self._mape_plugin = mape_plugin

        self._vehicle_positions: Dict[str, VehiclePosition] = {}
        self._vehicle_health: Dict[str, dict] = {}

        logger.info("[IngestionService] Initialized")

    def set_ws_broadcast(self, broadcast_fn):
        self._ws_broadcast = broadcast_fn

    def set_km_plugin(self, km_plugin):
        self._km_plugin = km_plugin

    def set_mape_plugin(self, mape_plugin):
        self._mape_plugin = mape_plugin

    def handle_heartbeat(self, hb: dict):
        bus_id = hb.get("bus_id", "unknown")
        self._vehicle_health[bus_id] = hb

    def handle_telemetry_sync(self, reading: TelemetryReading, loop: Optional[asyncio.AbstractEventLoop] = None):
        """Thread-safe synchronous wrapper called by MQTT thread."""
        if loop and loop.is_running():
            asyncio.run_coroutine_threadsafe(self.handle_telemetry(reading), loop)
        else:
            # Run without async broadcast if loop not provided
            self._process_reading_sync(reading)

    def _process_reading_sync(self, reading: TelemetryReading):
        # 1. Update vehicle position
        self._update_vehicle_position(reading)

        # 2. Update the server-side MAPE-K five-minute H3 knowledge store.
        if self._mape_plugin:
            self._mape_plugin.on_telemetry(reading)

        # 3. Spatial Deduplication (if it's a defect)
        if reading.object_type != "traffic_survey":
            action, marker = self._dedup.process(reading)
            if marker and self._mape_plugin:
                if action == "new":
                    self._mape_plugin.on_defect_new(marker, reading)
                else:
                    self._mape_plugin.on_defect_updated(marker, reading)
            return action, marker
        return None, None

    async def handle_telemetry(self, reading: TelemetryReading):
        action, marker = self._process_reading_sync(reading)

        # Broadcast vehicle movement
        if self._ws_broadcast:
            veh_data = asdict(self._vehicle_positions[reading.bus_id])
            veh_data["lux"] = reading.lux_level
            veh_data["vibration_g"] = reading.vibration_g
            await self._ws_broadcast("vehicle_moved", veh_data)

            # Broadcast defect event
            if marker:
                event_name = "defect_new" if action == "new" else "defect_updated"
                await self._ws_broadcast(event_name, asdict(marker))

        # Trigger K-M Media Orchestration Plugin (Day 3 / Master Plan)
        if marker and self._km_plugin and marker.confidence >= 0.75 and action == "new":
            self._km_plugin.request_media_sync(
                bus_id=reading.bus_id,
                defect_id=marker.defect_id,
                timestamp_ms=reading.timestamp_ms,
            )

    def _update_vehicle_position(self, reading: TelemetryReading):
        self._vehicle_positions[reading.bus_id] = VehiclePosition(
            bus_id=reading.bus_id,
            latitude=reading.latitude,
            longitude=reading.longitude,
            timestamp_ms=reading.timestamp_ms,
        )

    def get_all_vehicles(self) -> List[VehiclePosition]:
        return list(self._vehicle_positions.values())

    def get_all_defects(self) -> List[DefectMarker]:
        return self._dedup.get_all_markers()

    def get_h3_grid(self) -> List[Dict[str, Any]]:
        """Return the authoritative active-window H3 grid for Leaflet rendering."""
        cells = []
        h3_cells = self._mape_plugin.get_h3_cells() if self._mape_plugin else {}
        for h3_id, metrics in h3_cells.items():
            try:
                boundary = h3.cell_to_boundary(h3_id)  # [(lat, lng), ...]
                cells.append({
                    "h3_index": h3_id,
                    "count": metrics["traffic_count"],
                    "traffic_count": metrics["traffic_count"],
                    "defect_reports": metrics["defect_reports"],
                    "unique_defects": metrics["unique_defects"],
                    "coordinates": boundary,
                })
            except Exception:
                continue
        return cells

    def get_stats(self) -> dict:
        h3_clusters = len(self._mape_plugin.get_h3_cells()) if self._mape_plugin else 0
        return {
            "active_vehicles": len(self._vehicle_positions),
            "total_defects": self._dedup.get_marker_count(),
            "h3_clusters": h3_clusters,
            "uptime_s": int(time.time()),
        }
