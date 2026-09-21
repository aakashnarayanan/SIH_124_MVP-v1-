import os
import time

commands = [
    ("SURADAK MQTT Broker", "python mosquitto/broker.py"),
    ("SURADAK Server", "cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"),
    ("Edge Node 1 (bus_1 - test_dashcam)", "python main.py --bus-id bus_1 --route edge/gps_tracks/route_1.csv --source edge/assets/test_dashcam.mp4 --fps 10 --show-video --verbose --demo-stream-frames"),
    ("Edge Node 2 (bus_2 - test_dashcam)", "python main.py --bus-id bus_2 --route edge/gps_tracks/route_2.csv --source edge/assets/test_dashcam.mp4 --fps 10 --show-video --verbose --demo-stream-frames"),
    ("Edge Node 3 (bus_3 - test2)", "python main.py --bus-id bus_3 --route edge/gps_tracks/route_3.csv --source edge/assets/test2.mp4 --fps 10 --show-video --verbose --demo-stream-frames"),
    ("SURADAK Frontend Dashboard", "cd frontend && npm run dev"),
]

for title, command in commands:
    print(f"Launching {title}...")
    os.system(f'start "{title}" cmd /k "{command}"')
    time.sleep(1.5)

print("\n[SUCCESS] All 6 SURADAK demo components launched in separate console windows.")
print("Open http://localhost:5173 in your browser to view the Command Center Dashboard.")