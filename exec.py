import os

commands = [
    "python mosquitto/broker.py",
    "cd server && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload",
    "python main.py --source edge/assets/test_dashcam.mp4 --fps 10 --show-video --verbose",
    "cd frontend && npm run dev"
]

for command in commands:
    os.system(f'start cmd /k "{command}"')

#