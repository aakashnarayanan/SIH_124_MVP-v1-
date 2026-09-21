"""
SURADAK Edge Client — Main Launcher
====================================
Reads config.env, resolves all paths, and delegates to the full
edge runtime (run_edge_node) from the parent project's edge package.

Usage:
    python run.py                  # uses config.env
    python run.py --bus-id bus_3   # override bus ID on the fly
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# ── Path setup ────────────────────────────────────────────────────────────────
# edge_client/ is a subfolder of the project root.
# Add the project root to sys.path so `edge`, `proto`, `server` imports resolve.
CLIENT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = CLIENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(CLIENT_DIR))  # for local overrides if any

# ── Config loader ─────────────────────────────────────────────────────────────

def load_config(env_file: Path) -> dict:
    """Parse KEY=VALUE lines from config.env, ignoring comments and blanks."""
    cfg: dict[str, str] = {}
    if not env_file.exists():
        print(f"[Config] WARNING: {env_file} not found — using defaults.")
        return cfg
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            cfg[key.strip()] = value.strip()
    return cfg


def resolve_path(raw: str, base: Path) -> str:
    """Return absolute path; if relative, resolves from edge_client/ first,
    then from project root."""
    p = Path(raw)
    if p.is_absolute():
        return str(p)
    # Try relative to edge_client/
    candidate = base / p
    if candidate.exists():
        return str(candidate)
    # Try relative to project root
    candidate2 = PROJECT_ROOT / p
    if candidate2.exists():
        return str(candidate2)
    # Return the base-relative path anyway (caller will handle missing file)
    return str(candidate)


def main():
    # ── CLI overrides (allow quick one-liners without editing config.env) ──
    parser = argparse.ArgumentParser(
        description="SURADAK Edge Client — connect to a remote server node",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--config", default=str(CLIENT_DIR / "config.env"),
                        help="Path to the config.env file")
    parser.add_argument("--server-ip", default=None,
                        help="Override SERVER_IP from config.env")
    parser.add_argument("--bus-id", default=None,
                        help="Override BUS_ID from config.env")
    parser.add_argument("--route", default=None,
                        help="Override ROUTE from config.env (e.g. route_3)")
    parser.add_argument("--video", default=None,
                        help="Override VIDEO path from config.env")
    parser.add_argument("--fps", type=int, default=None,
                        help="Override FPS from config.env")
    parser.add_argument("--show-video", action="store_true", default=None,
                        help="Force-enable OpenCV display window")
    parser.add_argument("--no-stream", action="store_true", default=False,
                        help="Disable JPEG frame streaming (master-plan mode)")
    args = parser.parse_args()

    # ── Load config.env ────────────────────────────────────────────────────
    cfg = load_config(Path(args.config))

    server_ip   = args.server_ip  or cfg.get("SERVER_IP",   "127.0.0.1")
    bus_id      = args.bus_id     or cfg.get("BUS_ID",      "bus_2")
    route_name  = args.route      or cfg.get("ROUTE",       "route_2")
    video_raw   = args.video      or cfg.get("VIDEO",       "assets/dashcam.mp4")
    broker_port = int(cfg.get("BROKER_PORT", "1883"))
    fps         = args.fps or int(cfg.get("FPS", "10"))
    show_video  = args.show_video if args.show_video else cfg.get("SHOW_VIDEO", "false").lower() == "true"
    demo_stream = not args.no_stream and cfg.get("DEMO_STREAM_FRAMES", "true").lower() == "true"

    # Resolve route CSV
    route_csv_candidates = [
        CLIENT_DIR / "gps_tracks" / f"{route_name}.csv",
        PROJECT_ROOT / "edge" / "gps_tracks" / f"{route_name}.csv",
    ]
    route_csv = str(route_csv_candidates[0])
    for candidate in route_csv_candidates:
        if candidate.exists():
            route_csv = str(candidate)
            break

    # Resolve video
    video_path = resolve_path(video_raw, CLIENT_DIR)

    # Resolve video server URL
    video_server_url = f"http://{server_ip}:8000/api/video/frame"

    # ── Print banner ───────────────────────────────────────────────────────
    print("=" * 64)
    print("  SURADAK Edge Client Node")
    print("=" * 64)
    print(f"  Bus ID         : {bus_id}")
    print(f"  Server IP      : {server_ip}:{broker_port}")
    print(f"  Route CSV      : {route_csv}")
    print(f"  Video Source   : {video_path}")
    print(f"  Target FPS     : {fps}")
    print(f"  Stream Frames  : {'YES (demo mode)' if demo_stream else 'NO (Protobuf + on-demand clips only)'}")
    print(f"  Show Video GUI : {show_video}")
    print("=" * 64)

    # ── Validate ───────────────────────────────────────────────────────────
    if not Path(video_path).exists():
        print(f"\n[ERROR] Video file not found: {video_path}")
        print("  → Place your dashcam video in edge_client/assets/ and update VIDEO= in config.env")
        print("  → Or pass --video path/to/your/file.mp4 on the command line")
        sys.exit(1)

    if server_ip in ("192.168.1.100", "YOUR_SERVER_IP"):
        print("\n[WARNING] SERVER_IP is still set to the placeholder value!")
        print("  → Open config.env and set SERVER_IP= to your server laptop's IP address")
        answer = input("  Continue anyway with 127.0.0.1 (local test)? [y/N]: ").strip().lower()
        if answer != "y":
            sys.exit(0)
        server_ip = "127.0.0.1"

    # ── Delegate to edge runtime ───────────────────────────────────────────
    try:
        from edge.main import run_edge_node
    except ImportError as e:
        print(f"\n[ERROR] Cannot import edge runtime: {e}")
        print("  → Make sure you are running from the project root or edge_client/ directory")
        print("  → Run:  pip install -r requirements.txt")
        sys.exit(1)

    run_edge_node(
        source=video_path,
        show_video=show_video,
        verbose=True,
        bus_id=bus_id,
        route_csv=route_csv,
        target_fps=fps,
        broker_host=server_ip,
        broker_port=broker_port,
        video_server_url=video_server_url,
        demo_stream_frames=demo_stream,
    )


if __name__ == "__main__":
    main()
