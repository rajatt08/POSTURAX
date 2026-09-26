from fastapi import FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

app = FastAPI(
    title="PosturaX Telemetry Backend",
    description="Real-time MPU6050 posture telemetry ingestion backend for ESP32",
    version="1.0.0"
)

# Enable CORS for frontend dashboards or mobile web apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Secret Key authentication matching Arduino C++ code
EXPECTED_API_KEY = "posturax_secret_key_2026"

# In-memory store for live state and sensor history
latest_telemetry = {
    "pitch": 0.0,
    "deviation": 0.0,
    "status": "AWAITING_HARDWARE",
    "timestamp": None,
    "connected": False
}

telemetry_history: List[dict] = []
MAX_HISTORY_LENGTH = 100

# Strict payload validation matching ESP32 JSON schema
class PostureTelemetryPayload(BaseModel):
    pitch: float = Field(..., description="Filtered pitch angle in degrees")
    deviation: float = Field(..., description="Deviation from calibrated reference posture")
    status: str = Field(..., description="Calculated posture state string")

@app.post("/api/telemetry", status_code=status.HTTP_200_OK)
async def receive_telemetry(
    payload: PostureTelemetryPayload,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    Primary API endpoint called by ESP32 to push live posture metrics over Wi-Fi.
    """
    # 1. API Key Authentication
    if x_api_key != EXPECTED_API_KEY:
        print(f"[SECURITY ALERT] Rejected unauthorized request with API Key: '{x_api_key}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing x-api-key header"
        )

    # 2. Extract Data & Create Timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reading = {
        "pitch": payload.pitch,
        "deviation": payload.deviation,
        "status": payload.status,
        "timestamp": current_time,
        "connected": True
    }

    # 3. Update Current Live State
    latest_telemetry.update(reading)

    # 4. Append to History Buffer
    telemetry_history.append(reading)
    if len(telemetry_history) > MAX_HISTORY_LENGTH:
        telemetry_history.pop(0)

    # 5. Live Hardware Stream Console Logging
    print(
        f"[{current_time}] ESP32 TELEMETRY -> "
        f"Pitch: {payload.pitch:6.2f}° | "
        f"Deviation: {payload.deviation:6.2f}° | "
        f"Status: {payload.status}"
    )

    return {
        "status": "success",
        "message": "Telemetry received",
        "data": reading
    }

@app.get("/api/live")
async def get_live_status():
    """Endpoint for frontend or dashboard to poll the latest active sensor reading."""
    return latest_telemetry

@app.get("/api/history")
async def get_history(limit: int = 20):
    """Returns the last N sensor readings for graphing or analytics."""
    return telemetry_history[-limit:]

@app.get("/")
async def root():
    return {
        "application": "PosturaX Backend",
        "status": "Online",
        "mode": "Live Hardware Telemetry",
        "device_connected": latest_telemetry["connected"],
        "last_seen": latest_telemetry["timestamp"]
    }
