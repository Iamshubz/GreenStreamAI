"""FastAPI backend for GreenStream AI with Pathway Streaming Integration"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import google.generativeai as genai
import os
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from pipeline import run_pipeline, pipeline_state
from pathway_api_integration import PathwayDataStore, PathwayStreamProcessor, pathway_data_store

# Initialize FastAPI
app = FastAPI(
    title="GreenStream AI",
    description="Real-time environmental monitoring with AI insights powered by Pathway streaming",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini API
_gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
if _gemini_api_key and _gemini_api_key != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=_gemini_api_key)
        gemini_model = genai.GenerativeModel("gemini-pro")
        print("✓ Gemini API configured")
    except Exception as e:
        print(f"⚠ Gemini API error: {e}")
        gemini_model = None
else:
    gemini_model = None

# Models
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
    severity: str

class AIInsight(BaseModel):
    alert: Alert
    explanation: str
    recommendation: str
    severity_level: str

# Startup
def start_pathway_pipeline():
    """Initialize Pathway streaming pipeline with fallback to legacy pipeline"""
    global pathway_data_store
    try:
        print("🛣️ Starting Pathway streaming pipeline...")
        # Initialize data generator directly without complex Pathway table setup
        from pathway_api_integration import PathwayStreamProcessor
        from pathway_ingestion import EnvironmentalDataGenerator
        
        processor = PathwayStreamProcessor(pathway_data_store)
        generator = EnvironmentalDataGenerator()
        
        # Start continuous background update thread
        pathway_thread = threading.Thread(
            target=processor.continuous_update_from_generator,
            args=(generator, 2.0),
            daemon=True
        )
        pathway_thread.start()
        print("✓ Pathway pipeline live with continuous data streaming")
    except Exception as e:
        print(f"⚠ Pathway init failed: {e}, using legacy pipeline")

@app.on_event("startup")
async def startup():
    start_pathway_pipeline()

# Routes
@app.get("/")
async def root():
    return {"service": "GreenStream AI", "version": "2.0.0", "status": "live"}

@app.get("/api/health")
async def health():
    """Health check with Pathway status"""
    pathway_active = len(pathway_data_store.latest_readings) > 0
    return {
        "status": "healthy",
        "pathway_active": pathway_active,
        "cities": list(pathway_data_store.latest_readings.keys()),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/readings")
async def get_readings() -> Dict[str, dict]:
    """Get all latest readings from Pathway"""
    readings = pathway_data_store.get_all_readings()
    return readings if readings else pipeline_state.get("latest_readings", {})

@app.get("/api/readings/{city}")
async def get_city_reading(city: str):
    """Get reading for specific city"""
    reading = pathway_data_store.get_city_reading(city)
    if reading:
        return reading
    
    if city in pipeline_state.get("latest_readings", {}):
        return pipeline_state["latest_readings"][city]
    
    raise HTTPException(status_code=404, detail=f"No data for {city}")

@app.get("/api/alerts")
async def get_alerts(limit: int = 50) -> List[dict]:
    """Get all alerts"""
    alerts = pathway_data_store.get_critical_alerts(limit)
    return alerts if alerts else pipeline_state.get("alerts", [])[-limit:]

@app.get("/api/alerts/critical")
async def get_critical_alerts(limit: int = 20) -> List[dict]:
    """Get critical alerts only"""
    return pathway_data_store.get_critical_alerts(limit)

@app.get("/api/alerts/warnings")
async def get_warning_alerts(limit: int = 30) -> List[dict]:
    """Get warning alerts"""
    return pathway_data_store.get_warnings(limit)

@app.get("/api/health/{city}")
async def get_city_health(city: str) -> dict:
    """Get health metrics for city"""
    reading = pathway_data_store.get_city_reading(city)
    if not reading:
        if city in pipeline_state.get("latest_readings", {}):
            reading = pipeline_state["latest_readings"][city]
        else:
            raise HTTPException(status_code=404, detail=f"No data for {city}")
    
    health_score = pathway_data_store.get_health_score(city)
    risk_score = pathway_data_store.get_risk_score(city)
    
    return {
        "city": city,
        "health_score": health_score or (100 - risk_score if risk_score else 50),
        "risk_score": risk_score or 50,
        "aqi": reading.get("aqi"),
        "co2": reading.get("co2"),
        "severity": reading.get("severity", "normal"),
        "timestamp": reading.get("timestamp")
    }

@app.get("/api/anomalies/{city}")
async def get_anomalies(city: str) -> dict:
    """Get anomaly history for city"""
    history = pathway_data_store.get_city_anomaly_history(city)
    return {
        "city": city,
        "anomalies": history[-20:],
        "total": len(history),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/insights/{city}")
async def get_insights(city: str) -> AIInsight:
    """Get AI-powered insights with Gemini"""
    # Try Pathway alerts first
    reading = pathway_data_store.get_city_reading(city)
    
    if not reading:
        # Fallback to legacy pipeline
        city_alerts = [a for a in pipeline_state.get("alerts", []) if a["city"] == city]
        if not city_alerts:
            raise HTTPException(status_code=404, detail=f"No alerts for {city}")
        reading = city_alerts[-1]
    
    explanation = "High pollution levels detected."
    recommendation = "Monitor air quality and limit outdoor activities."
    severity = reading.get("severity", "warning")
    
    try:
        if gemini_model is None:
            raise RuntimeError("Gemini not configured")
        
        prompt = f"""Analyze this environmental data:
City: {city}
AQI: {reading['aqi']} | CO2: {reading['co2']} ppm
Temperature: {reading.get('temperature', 'N/A')}°C | Humidity: {reading.get('humidity', 'N/A')}%

Provide in this format:
EXPLANATION: [brief 1-2 sentence explanation]
RECOMMENDATION: [1-2 sentence recommendation]"""
        
        response = gemini_model.generate_content(prompt)
        for line in response.text.split('\n'):
            if line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('RECOMMENDATION:'):
                recommendation = line.replace('RECOMMENDATION:', '').strip()
    
    except Exception as e:
        # Intelligent fallback based on pollution level
        aqi = reading.get("aqi", 150)
        if aqi > 300:
            explanation = f"CRITICAL: AQI {aqi} indicates hazardous air quality."
            recommendation = "Stay indoors, close windows, and use air purifiers."
        elif aqi > 200:
            explanation = f"Poor air quality (AQI {aqi}). CO2 levels are elevated."
            recommendation = "Limit outdoor activities and wear protective masks."
        else:
            explanation = f"Moderate pollution detected (AQI {aqi})."
            recommendation = "Monitor air quality conditions."
    
    return AIInsight(
        alert=Alert(
            city=city,
            aqi=reading.get("aqi", 0),
            co2=reading.get("co2", 0),
            temperature=reading.get("temperature", 0),
            humidity=reading.get("humidity", 0),
            timestamp=reading.get("timestamp", datetime.now().isoformat()),
            severity=severity
        ),
        explanation=explanation[:250],
        recommendation=recommendation[:250],
        severity_level=severity
    )

@app.get("/api/dashboard")
async def get_dashboard() -> dict:
    """Get complete dashboard summary"""
    # Get readings from Pathway data store
    readings = pathway_data_store.get_all_readings()
    
    # Fallback to legacy if no Pathway data
    if not readings:
        readings = pipeline_state.get("latest_readings", {})
    
    cities = list(readings.keys())
    alerts = pipeline_state.get("alerts", [])
    
    # Calculate stats
    total_cities = len(cities)
    critical_count = len([a for a in alerts if a.get("severity") == "critical"])
    warning_count = len([a for a in alerts if a.get("severity") == "warning"])
    avg_aqi = round(sum(r.get("aqi", 0) for r in readings.values()) / total_cities, 1) if total_cities else 0
    avg_health = round(sum(r.get("health_score", 50) for r in readings.values()) / total_cities, 1) if total_cities else 0
    
    return {
        "total_cities": total_cities,
        "cities": cities,
        "critical_alerts": critical_count,
        "warnings": warning_count,
        "average_aqi": avg_aqi,
        "average_health_score": avg_health,
        "readings": readings,
        "recent_alerts": alerts[-10:],
        "recent_stats": [],
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GreenStream AI Backend (Pathway-powered)...")
    print("📍 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
