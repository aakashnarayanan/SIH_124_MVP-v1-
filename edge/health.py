"""Portable, best-effort process health sampling for edge heartbeats."""
from __future__ import annotations

import ctypes
from pathlib import Path


def process_memory_mb() -> float:
    """Return current process RSS/working set in MiB without a new dependency."""
    try:
        if hasattr(ctypes, "windll"):
            class ProcessMemoryCounters(ctypes.Structure):
                _fields_ = [("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
                            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t)]
            counters = ProcessMemoryCounters()
            counters.cb = ctypes.sizeof(counters)
            ok = ctypes.windll.psapi.GetProcessMemoryInfo(
                ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
            )
            if ok:
                return counters.WorkingSetSize / (1024 * 1024)
        status = Path("/proc/self/status")
        if status.exists():
            for line in status.read_text(encoding="utf-8").splitlines():
                if line.startswith("VmRSS:"):
                    return float(line.split()[1]) / 1024
    except (OSError, ValueError, AttributeError):
        pass
    return 0.0


def cpu_temperature_c() -> float:
    """Return a real Linux thermal-zone value, or 0 when unavailable."""
    try:
        for zone in Path("/sys/class/thermal").glob("thermal_zone*/temp"):
            raw = float(zone.read_text(encoding="utf-8").strip())
            if raw > 0:
                return raw / 1000 if raw > 1000 else raw
    except (OSError, ValueError):
        pass
    return 0.0
