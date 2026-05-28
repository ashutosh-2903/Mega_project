import requests
import random
import time

while True:

    data = {
        "vehicle_id": "CAR101",
        "latitude": 28.61 + random.uniform(-0.01, 0.01),
        "longitude": 77.20 + random.uniform(-0.01, 0.01),
        "speed": random.randint(20, 120),
        "timestamp": str(time.time())
    }

    requests.post(
        "http://127.0.0.1:8000/telemetry",
        json=data
    )

    print("Sent:", data)

    time.sleep(30)
    