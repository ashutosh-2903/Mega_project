from fastapi import FastAPI
from firebase_config import db

app = FastAPI()

@app.post("/telemetry")
def save_data(data: dict):

    db.collection("telemetry").add(data)

    return {"status": "saved to cloud"}