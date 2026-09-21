"""
Evidence Clips REST Endpoint
============================
Serves locally-saved evidence clips captured by edge nodes via MediaSyncRequest.
Clips are stored in: edge/evidence_clips/<bus_id>/<defect_id>_<ts>_annotated.mp4

Routes:
  GET /api/clips              — list all clips (newest first)
  GET /api/clips/<path>       — stream / download a specific .mp4 file
"""

import os
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

router = APIRouter(prefix="/api/clips", tags=["Evidence Clips"])

# Root where edge nodes save local clips
_BASE_DIR = Path(__file__).parent.parent  # project root
CLIPS_ROOT = _BASE_DIR / "edge" / "evidence_clips"


def _scan_clips() -> List[Dict[str, Any]]:
    """Walk evidence_clips dir and return clip metadata sorted newest-first."""
    clips: List[Dict[str, Any]] = []
    if not CLIPS_ROOT.exists():
        return clips
    for bus_dir in sorted(CLIPS_ROOT.iterdir()):
        if not bus_dir.is_dir():
            continue
        bus_id = bus_dir.name
        for clip in sorted(bus_dir.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True):
            stat = clip.stat()
            # Parse defect_id from filename: <defect_id>_<ts>_annotated.mp4
            parts = clip.stem.split("_")
            defect_id = parts[0] if len(parts) >= 1 else "unknown"
            timestamp_ms = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0
            clips.append({
                "bus_id": bus_id,
                "filename": clip.name,
                "defect_id": defect_id,
                "timestamp_ms": timestamp_ms,
                "size_bytes": stat.st_size,
                "url": f"/api/clips/{bus_id}/{clip.name}",
            })
    clips.sort(key=lambda c: c["timestamp_ms"], reverse=True)
    return clips


@router.get("")
async def list_clips():
    """Return metadata for all locally-saved evidence clips."""
    clips = _scan_clips()
    return {"count": len(clips), "clips": clips}


@router.get("/{bus_id}/{filename}")
async def get_clip(bus_id: str, filename: str):
    """Stream a specific evidence clip .mp4 file."""
    # Safety: disallow path traversal
    if ".." in bus_id or ".." in filename:
        return JSONResponse({"error": "forbidden"}, status_code=403)
    clip_path = CLIPS_ROOT / bus_id / filename
    if not clip_path.exists() or not clip_path.is_file():
        return JSONResponse({"error": "clip not found"}, status_code=404)
    return FileResponse(
        path=str(clip_path),
        media_type="video/mp4",
        filename=filename,
    )
