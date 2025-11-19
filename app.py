from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
from dotenv import load_dotenv
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

app = FastAPI()
load_dotenv()

MONGO_URI = os.getenv("MONGO_DB_URI")
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client.SmartParking
spots_collection = db.spots

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

class ParkingStatus(BaseModel):
    spot_id: int
    is_free: bool
    lat: float
    lng: float

@app.post("/parking_status")
async def update_parking_status(status: ParkingStatus):
    timestamp = datetime.utcnow()
    result = spots_collection.update_one(
        {"spot_id": status.spot_id},
        {
            "$set": {
                "lat": status.lat,
                "lng": status.lng,
                "is_free": status.is_free,
                "last_updated": timestamp
            },
            "$push": {
                "history": {
                    "is_free": status.is_free,
                    "timestamp": timestamp
                }
            }
        },
        upsert=True
    )
    return {"success": True, "modified_count": result.modified_count}

@app.get("/parking_spots")
async def get_all_spots():
    spots = list(spots_collection.find({}, {"_id": 0}))
    return spots