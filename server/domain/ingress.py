"""Inbound telemetry sanitiser. Invalid packets are dropped, never ingested."""
from __future__ import annotations

import logging
from typing import Optional

from domain.models import TelemetryReading

logger = logging.getLogger("IngressSanitizer")

_MAX_OBJECT_TYPE = 64
_MAX_BUS_ID = 64


def sanitize_reading(reading: TelemetryReading) -> Optional[TelemetryReading]:
    reasons: list[str] = []
    bus_id = (reading.bus_id or "").strip()
    if not bus_id or len(bus_id) > _MAX_BUS_ID:
        reasons.append("invalid bus_id")

    lat = reading.latitude
    lon = reading.longitude
    if not isinstance(lat, (int, float)) or lat != lat or lat < -90.0 or lat > 90.0:
        reasons.append("latitude out of range")
    if not isinstance(lon, (int, float)) or lon != lon or lon < -180.0 or lon > 180.0:
        reasons.append("longitude out of range")

    confidence = reading.confidence
    if not isinstance(confidence, (int, float)) or confidence != confidence or confidence < 0.0 or confidence > 1.0:
        reasons.append("confidence out of range")

    if reading.timestamp_ms < 0:
        reasons.append("negative timestamp")

    if reading.vehicle_count < 0:
        reasons.append("negative vehicle_count")

    if reasons:
        logger.warning("[Ingress] Dropped telemetry from %s: %s", bus_id or "unknown", ", ".join(reasons))
        return None

    object_type = (reading.object_type or "unknown").strip()[:_MAX_OBJECT_TYPE] or "unknown"
    return TelemetryReading(
        bus_id=bus_id,
        latitude=float(lat),
        longitude=float(lon),
        object_type=object_type,
        confidence=float(confidence),
        timestamp_ms=int(reading.timestamp_ms),
        vehicle_count=int(reading.vehicle_count),
        lux_level=float(reading.lux_level),
        vibration_g=float(reading.vibration_g),
        network_signal_db=float(reading.network_signal_db),
    )
