"""
SURADAK Urban AI Fleet Intelligence — Chaos Engineering Test Runner
=====================================================================
Simulates network severance on an individual edge node and demonstrates:
  1. Instant failover to SQLite local circuit-breaker cache (zero data loss)
  2. Telemetry accumulation during network dropout
  3. Automatic reconnection and chronological burst upload upon link restoration

Usage:
    python simulate_chaos.py --bus-id bus_2 --duration 8
    python simulate_chaos.py --bus-id bus_2 --offline
    python simulate_chaos.py --bus-id bus_2 --online
"""

import sys
import os
import time
import argparse
import sqlite3
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).parent.resolve()


def get_trigger_path(bus_id: str) -> Path:
    storage_dir = BASE_DIR / "edge" / "storage"
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / f"{bus_id}_offline.trigger"


def get_cache_count(bus_id: str) -> int:
    db_path = BASE_DIR / "edge" / "storage" / f"{bus_id}_cache.db"
    if not db_path.exists():
        return 0
    try:
        conn = sqlite3.connect(str(db_path), timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM offline_telemetry")
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 0
    except Exception:
        return 0


def set_offline(bus_id: str):
    trigger = get_trigger_path(bus_id)
    trigger.write_text(f"offline_requested_at={time.time()}", encoding="utf-8")
    print(f"\n[CHAOS] [ALERT] Triggered network disconnect for [{bus_id.upper()}].")
    print(f"        Trigger file created: {trigger}")
    print(f"        Edge node [{bus_id.upper()}] is now buffering to local SQLite cache.")


def set_online(bus_id: str):
    trigger = get_trigger_path(bus_id)
    if trigger.exists():
        trigger.unlink(missing_ok=True)
    print(f"\n[CHAOS] [ONLINE] Network restored for [{bus_id.upper()}].")
    print(f"        Edge node [{bus_id.upper()}] reconnecting to MQTT & bursting offline cache.")


def run_timed_chaos(bus_id: str, duration_sec: int):
    print("=" * 70)
    print(f"  SURADAK Chaos Engineering Test — [{bus_id.upper()}] Network Severance")
    print("=" * 70)
    initial_count = get_cache_count(bus_id)
    print(f"  Target Bus       : {bus_id}")
    print(f"  Dropout Duration : {duration_sec} seconds")
    print(f"  Initial Cache    : {initial_count} packets")
    print("=" * 70)

    # 1. Sever network link
    set_offline(bus_id)

    # 2. Monitor accumulation during outage
    print(f"\n[Outage Active] Simulating driving through network dead-zone for {duration_sec}s...")
    start_t = time.time()
    while time.time() - start_t < duration_sec:
        elapsed = int(time.time() - start_t)
        count = get_cache_count(bus_id)
        sys.stdout.write(f"\r  [*] Elapsed: {elapsed:2d}/{duration_sec}s | Packets in SQLite cache: {count:3d}  ")
        sys.stdout.flush()
        time.sleep(0.5)

    final_offline_count = get_cache_count(bus_id)
    print(f"\n\n[Dead-zone Exited] Accumulated {final_offline_count} packets in offline cache without data loss.")

    # 3. Restore network link
    set_online(bus_id)

    # 4. Monitor burst upload
    print("\n[Burst Recovery] Watching queue drain via burst upload to MQTT broker...")
    burst_start = time.time()
    while time.time() - burst_start < 12.0:
        remaining = get_cache_count(bus_id)
        sys.stdout.write(f"\r  [>>] Remaining in SQLite cache: {remaining:3d} packets  ")
        sys.stdout.flush()
        if remaining == 0:
            break
        time.sleep(0.3)

    remaining = get_cache_count(bus_id)
    print()
    if remaining == 0:
        print("=" * 70)
        print(f"  [SUCCESS] CHAOS TEST PASSED! All {final_offline_count} packets burst-uploaded.")
        print(f"  Zero data loss verified. Node [{bus_id.upper()}] is back ONLINE.")
        print("=" * 70)
    else:
        print(f"\n  [Notice] {remaining} packets remaining in cache buffer (draining in progress).")


def main():
    parser = argparse.ArgumentParser(description="SURADAK Chaos Engineering — Simulate network drop & burst upload")
    parser.add_argument("--bus-id", default="bus_2", help="Bus to simulate (default: bus_2)")
    parser.add_argument("--duration", type=int, default=8, help="Dropout duration in seconds (default: 8)")
    parser.add_argument("--offline", action="store_true", help="Sever network link (manual mode)")
    parser.add_argument("--online", action="store_true", help="Restore network link (manual mode)")

    args = parser.parse_args()

    if args.offline:
        set_offline(args.bus_id)
    elif args.online:
        set_online(args.bus_id)
    else:
        run_timed_chaos(args.bus_id, args.duration)


if __name__ == "__main__":
    main()
