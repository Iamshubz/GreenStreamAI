"""FastAPI backend for GreenStream AI"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import google.generativeai as genai
import os
import threading

from pipeline import run_pipeline, pipeline_state

# Initialize FastAPI app
app = FastAPI(
    title="GreenStream AI",
    description="Real-time environmental monitoring with AI insights",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Gemini client (optional)
_gemini_api_key = os.getenv("GEMINI_API_KEY")
if _gemini_api_key:
    genai.configure(api_key=_gemini_api_key)
    gemini_model = genai.GenerativeModel("gemini-pro")
else:
    gemini_model = None

def start_pipeline():
    """Start pipeline in background thread"""
    pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
    pipeline_thread.start()


# Pydantic models
class Reading(BaseModel):
    city: str
    temperature: float
    aqi: int
    co2: int
    humidity: int
    timestamp: str


class Alert(BaseModel):
    city: str
    co2: int
    aqi: int
    temperature: float
    humidity: float
    timestamp: str
    severity: str  # "warning" or "critical"


class Stats(BaseModel):
    city: str
    avg_co2: float
    max_co2: int
    avg_aqi: float
    avg_temp: float
    count: int
    timestamp: str


class AIInsight(BaseModel):
    alert: Alert
    explanation: str
    recommendation: str
    severity_level: str


# Routes

@app.on_event("startup")
async def startup_event():
    """Start the pipeline when the app starts"""
    start_pipeline()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "ok", "service": "GreenStream AI Backend"}


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "alerts_count": len(pipeline_state["alerts"]),
        "stats_count": len(pipeline_state["stats"])
    }


@app.get("/api/readings")
async def get_readings() -> Dict[str, Reading]:
    """Get latest readings from all cities"""
    readings = {}
    for city, data in pipeline_state["latest_readings"].items():
        readings[city] = Reading(**data)
    return readings


@app.get("/api/readings/{city}")
async def get_city_reading(city: str) -> Reading:
    """Get latest reading for a specific city"""
    if city not in pipeline_state["latest_readings"]:
        raise HTTPException(status_code=404, detail=f"No data for city: {city}")
    
    data = pipeline_state["latest_readings"][city]
    return Reading(**data)


@app.get("/api/alerts")
async def get_alerts(limit: int = 50) -> List[Alert]:
    """Get recent alerts"""
    alerts = pipeline_state["alerts"][-limit:]
    return [Alert(**alert) for alert in alerts]


@app.get("/api/alerts/{city}")
async def get_city_alerts(city: str, limit: int = 20) -> List[Alert]:
    """Get alerts for a specific city"""
    city_alerts = [a for a in pipeline_state["alerts"] if a["city"] == city]
    return [Alert(**alert) for alert in city_alerts[-limit:]]


@app.get("/api/stats")
async def get_stats(limit: int = 50) -> List[Stats]:
    """Get rolling window statistics"""
    stats = pipeline_state["stats"][-limit:]
    return [Stats(**stat) for stat in stats]


@app.get("/api/stats/{city}")
async def get_city_stats(city: str, limit: int = 20) -> List[Stats]:
    """Get statistics for a specific city"""
    city_stats = [s for s in pipeline_state["stats"] if s["city"] == city]
    return [Stats(**stat) for stat in city_stats[-limit:]]


@app.get("/api/insights/{city}")
async def get_insights(city: str) -> AIInsight:
    """Get AI-powered insights for a city"""
    city_alerts = [a for a in pipeline_state["alerts"] if a["city"] == city]
    
    if not city_alerts:
        raise HTTPException(status_code=404, detail=f"No recent alerts for {city}")
    
    latest_alert = city_alerts[-1]
    
    try:
        if gemini_model is None:
            raise RuntimeError("Gemini API key not configured")
        prompt = f"""Environmental Alert Analysis for {city}:
CO2: {latest_alert['co2']} ppm | AQI: {latest_alert['aqi']}
Temperature: {latest_alert['temperature']}°C | Humidity: {latest_alert['humidity']}%

As an environmental scientist, briefly explain what causes this alert and recommend actions."""
        
        response = gemini_model.generate_content(prompt)
        insight_text = response.text
        parts = insight_text.split("\n")
        explanation = " ".join(p for p in parts if "2." not in p and p.strip())[:200]
        recommendation = " ".join(p for p in parts if "2." in p or "recommended" in p.lower())[:200]
    except Exception:
        explanation = f"High pollution levels detected in {city}."
        recommendation = f"Monitor situation and follow local air quality guidance."
    
    return AIInsight(
        alert=Alert(**latest_alert),
        explanation=explanation or "Environmental monitoring detected anomaly.",
        recommendation=recommendation or "Monitor situation.",
        severity_level=latest_alert.get("severity", "warning")
    )


@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data in one call"""
    return {
        "readings": {city: data for city, data in pipeline_state["latest_readings"].items()},
        "recent_alerts": pipeline_state["alerts"][-10:],
        "recent_stats": pipeline_state["stats"][-10:],
        "timestamp": datetime.now().isoformat(),
        "cities": list(pipeline_state["latest_readings"].keys())
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GreenStream AI Backend...")
    print("📍 API available at http://localhost:8000")
    print("📚 Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
