from firebase_config import db

data = {
    "vehicle": "huiiii",
    "speed": 60,
    "latitude": 28.61,
    "longitude": 77.20
}

db.collection("telemetry").add(data)

print("Data sent to Firebase")