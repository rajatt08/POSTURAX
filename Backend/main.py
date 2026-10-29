import os
from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import pandas as pd
import joblib
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI(
    title="PosturaX Unified Telemetry & Stress Backend",
    description="Real-time MPU6050 posture telemetry & ML-powered stress wellness engine",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (HTML, CSS, JS) ke liye folder mount kiya
# (Ensure karein ki aapke project mein 'static' folder ho)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    # Yeh aapki static folder ke andar rakhi index.html file ko browser par load kar dega
    index_file = os.path.join(BASE_DIR, "static", "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return {"message": "PosturaX Backend is running successfully! Place your index.html inside the static folder."}

EXPECTED_API_KEY = "posturax_secret_key_2026"

latest_telemetry = {
    "pitch": 0.0,
    "deviation": 0.0,
    "status": "AWAITING_HARDWARE",
    "heart_rate": 75.0,
    "timestamp": None,
    "connected": False
}

telemetry_history: List[dict] = []
MAX_HISTORY_LENGTH = 100

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, 'stress_model.pkl')
csv_path = os.path.join(BASE_DIR, '../single_user_stress_dataset.csv')

model = joblib.load(model_path) if os.path.exists(model_path) else None
df = pd.read_csv(csv_path) if os.path.exists(csv_path) else None


class PostureTelemetryPayload(BaseModel):
    pitch: float = Field(..., description="Filtered pitch angle")
    deviation: float = Field(..., description="Deviation from reference")
    status: str = Field(..., description="Posture state")
    heart_rate: Optional[float] = Field(75.0, description="BPM")


class CustomStressInput(BaseModel):
    sleep_hrs: float = Field(..., description="Hours of sleep")
    water_ml_today: float = Field(..., description="Water in ml")
    mood: int = Field(..., description="Mood scale 1-4")


@app.post("/api/telemetry", status_code=status.HTTP_200_OK)
async def receive_telemetry(payload: PostureTelemetryPayload, x_api_key: Optional[str] = Header(None, alias="x-api-key")):
    if x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reading = {
        "pitch": payload.pitch,
        "deviation": payload.deviation,
        "status": payload.status,
        "heart_rate": payload.heart_rate,
        "timestamp": current_time,
        "connected": True
    }

    latest_telemetry.update(reading)
    telemetry_history.append(reading)
    if len(telemetry_history) > MAX_HISTORY_LENGTH:
        telemetry_history.pop(0)

    return {"status": "success", "data": reading}


@app.get("/api/live")
async def get_live_status():
    return latest_telemetry


@app.post("/api/calculate-stress")
def calculate_custom_stress(payload: CustomStressInput):
    if model is None or df is None:
        return {"error": "Model or dataset missing!"}
    
    current_hr = latest_telemetry.get("heart_rate", 75.0)
    current_hour = datetime.now().hour

    input_data = pd.DataFrame([[
        current_hr, 35.0, 45.0, 15.0,
        payload.sleep_hrs, payload.water_ml_today, payload.mood, current_hour
    ]], columns=['hr_bpm', 'rmssd_ms', 'sdnn_ms', 'pnn50_pct', 'sleep_hrs', 'water_ml_today', 'mood', 'hour_of_day'])
    
    predicted_score = float(model.predict(input_data)[0])
    
    if predicted_score < 40:
        level = "Low"
        exercises = [
            {"id": "walk_10", "name": "Light Walking (10 mins)", "type": "walking", "duration": "10 mins", "desc": "Casual outdoor stroll to maintain physical agility.", "action_type": "timer"},
            {"id": "stretch_desk", "name": "Desk Neck & Shoulder Stretch", "type": "stretching", "duration": "5 mins", "desc": "Release tension in upper traps.", "action_type": "youtube", "url": "https://www.youtube.com/results?search_query=desk+neck+and+shoulder+stretching+exercises"},
            {"id": "hobby_music", "name": "Relaxing Music / Hobby", "type": "extracurricular", "duration": "15 mins", "desc": "Listen to calming instrumental music.", "action_type": "info"}
        ]
    elif predicted_score < 65:
        level = "Medium"
        exercises = [
            {"id": "box_breathe", "name": "Box Breathing Exercise", "type": "breathing", "duration": "5 mins", "desc": "Guided Breathe-in, Hold, Breathe-out routine.", "action_type": "breathing_guide"},
            {"id": "walk_brisk", "name": "Brisk Walking (15 mins)", "type": "walking", "duration": "15 mins", "desc": "Cardio refresh to clear mental clutter.", "action_type": "timer"},
            {"id": "yoga_spine", "name": "Spine Posture Yoga", "type": "stretching", "duration": "10 mins", "desc": "Fix slouching and open up chest cavity.", "action_type": "youtube", "url": "https://www.youtube.com/results?search_query=spine+posture+yoga+stretching"}
        ]
    else:
        level = "High"
        exercises = [
            {"id": "deep_breathe", "name": "Deep Relaxation Breathing", "type": "breathing", "duration": "10 mins", "desc": "Deep slow inhales and exhales to drop heart rate.", "action_type": "breathing_guide"},
            {"id": "nature_walk", "name": "Calming Nature Walk", "type": "walking", "duration": "15 mins", "desc": "Unplug in a quiet environment.", "action_type": "timer"},
            {"id": "full_stretch", "name": "Full Body Stress Relief Stretch", "type": "stretching", "duration": "12 mins", "desc": "Deep muscular relaxation routine.", "action_type": "youtube", "url": "https://www.youtube.com/results?search_query=full+body+stress+relief+stretching"}
        ]
        
    factors = []
    if payload.sleep_hrs < 6.0:
        factors.append(f"Low sleep duration ({payload.sleep_hrs} hrs) is spiking stress.")
    if payload.water_ml_today < 1000:
        factors.append(f"Low water intake ({payload.water_ml_today} ml). Hydrate more.")
    if current_hr > 90:
        factors.append(f"Elevated heart rate ({current_hr} BPM) detected.")
    if not factors:
        factors.append("Your lifestyle and system metrics are well-balanced!")

    return {
        "application": "PosturaX Backend",
        "status": "Online",
        "mode": "Live Hardware Telemetry",
        "device_connected": latest_telemetry["connected"],
        "last_seen": latest_telemetry["timestamp"]
    }
    
    return{
        "stress_score": round(predicted_score, 1),
        "stress_level": level,
        "factors_affecting": factors,
        "recommended_exercises": exercises,
        "recommendations": {
            "posture_tip": "Keep your spine upright and shoulders relaxed to maintain optimal focus."
        }
    }

# Crucial for cloud deployment (Render/Railway port binding)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)




