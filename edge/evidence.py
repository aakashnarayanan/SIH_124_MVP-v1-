"""Bounded, asynchronous evidence-clip creation for an edge node."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from pathlib import Path
import queue
import re
import threading
import time
from typing import Callable, Literal

import cv2
import numpy as np

FrameKind = Literal["annotated", "raw"]

@dataclass(frozen=True)
class BufferedFrame:
    captured_at: float
    raw: np.ndarray
    annotated: np.ndarray

class EvidenceClipBuffer:
    """Keeps recent raw/annotated frames and writes requested clips off-thread.

    Clips intentionally remain local; cloud upload is outside this component.
    """
    def __init__(self, output_dir: str | Path, fps: float, retention_seconds: float = 10.0,
                 max_pending_jobs: int = 4, on_complete: Callable[[Path], None] | None = None):
        self.output_dir = Path(output_dir)
        self.fps = max(1.0, float(fps))
        self.max_frames = max(1, int(self.fps * retention_seconds))
        self.on_complete = on_complete
        self._frames: deque[BufferedFrame] = deque(maxlen=self.max_frames)
        self._lock = threading.Lock()
        self._jobs: queue.Queue[tuple[str, FrameKind, list[BufferedFrame]] | None] = queue.Queue(maxsize=max_pending_jobs)
        self._stopped = False
        self._worker = threading.Thread(target=self._run, name="EvidenceClipWriter", daemon=True)
        self._worker.start()

    def add_frame(self, raw: np.ndarray, annotated: np.ndarray, captured_at: float | None = None) -> None:
        item = BufferedFrame(time.monotonic() if captured_at is None else captured_at, raw.copy(), annotated.copy())
        with self._lock:
            if not self._stopped:
                self._frames.append(item)

    def request_clip(self, defect_id: str, duration_seconds: int = 2, kind: FrameKind = "annotated") -> bool:
        """Snapshot recent evidence and queue a local MP4 write without blocking."""
        duration = max(1, min(int(duration_seconds or 2), 10))
        with self._lock:
            if self._stopped or not self._frames:
                return False
            latest = self._frames[-1].captured_at
            frames = [f for f in self._frames if f.captured_at >= latest - duration]
        try:
            self._jobs.put_nowait((defect_id, kind, frames))
            return True
        except queue.Full:
            return False

    @property
    def frame_count(self) -> int:
        with self._lock:
            return len(self._frames)

    def stop(self) -> None:
        with self._lock:
            self._stopped = True
        try:
            self._jobs.put_nowait(None)
        except queue.Full:
            self._jobs.put(None, timeout=1.0)
        self._worker.join(timeout=5.0)

    def _run(self) -> None:
        while True:
            job = self._jobs.get()
            if job is None:
                return
            defect_id, kind, frames = job
            try:
                output = self._write_clip(defect_id, kind, frames)
                if output and self.on_complete:
                    self.on_complete(output)
            finally:
                self._jobs.task_done()

    def _write_clip(self, defect_id: str, kind: FrameKind, frames: list[BufferedFrame]) -> Path | None:
        if not frames:
            return None
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", defect_id or "unknown")[:80]
        output = self.output_dir / f"{safe_id}_{int(time.time() * 1000)}_{kind}.mp4"
        image = frames[0].annotated if kind == "annotated" else frames[0].raw
        height, width = image.shape[:2]
        # Use H.264 (avc1) for native HTML5 browser playback, fallback to mp4v
        writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"avc1"), self.fps, (width, height))
        if not writer.isOpened():
            writer.release()
            writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), self.fps, (width, height))
        if not writer.isOpened():
            writer.release()
            return None
        try:
            for frame in frames:
                image = frame.annotated if kind == "annotated" else frame.raw
                if image.shape[:2] != (height, width):
                    image = cv2.resize(image, (width, height))
                writer.write(image)
        finally:
            writer.release()
        return output
