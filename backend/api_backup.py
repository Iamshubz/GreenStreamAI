"""FastAPI backend for GreenStream AI"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import google.generativeai as genai
import os
import threading
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from pipeline import run_pipeline, pipeline_state
from pathway_ingestion import create_environmental_data_table, create_pathway_pipeline
from pathway_api_integration import PathwayDataStore, PathwayStreamProcessor, pathway_data_store

# Initialize FastAPI app
app = FastAPI(
    title="GreenStream AI",
    description="Real-time environmental monitoring with AI insights powered by Pathway",
    version="2.0.0"
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
_gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
if _gemini_api_key and _gemini_api_key != "your_gemini_api_key_here":
    try:
        genai.configure(api_key=_gemini_api_key)
        gemini_model = genai.GenerativeModel("gemini-pro")
        print("✓ Gemini API configured successfully")
    except Exception as e:
        print(f"⚠ Gemini API configuration error: {e}")
        gemini_model = None
else:
    print("⚠ Gemini API key not configured (using fallback responses)")
    gemini_model = None

def start_pipeline():
    """Start pipeline in background thread"""
    pipeline_thread = threading.Thread(target=run_pipeline, daemon=True)
    pipeline_thread.start()


def start_pathway_pipeline():
    """Initialize and start Pathway streaming pipeline"""
    try:
        print("🛣️ Initializing Pathway streaming pipeline...")
        raw_data, generator = create_environmental_data_table()
        pipeline = create_pathway_pipeline()
        
        processor = PathwayStreamProcessor(pathway_data_store)
        
        # Start continuous updates from generator
        pathway_thread = threading.Thread(
            target=processor.continuous_update_from_generator,
            args=(generator, 2.0),  # Update every 2 seconds
            daemon=True
        )
        pathway_thread.start()
        print("✓ Pathway pipeline started successfully")
    except Exception as e:
        print(f"⚠ Pathway pipeline initialization error: {e}")
        print("  Falling back to legacy pipeline")
        start_pipeline()


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
    """Start the Pathway pipeline when the app starts"""
    start_pathway_pipeline()


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
    
    explanation = "High pollution levels detected. Air quality is poor."
    recommendation = "Monitor air quality alerts and limit outdoor activities."
    
    try:
        if gemini_model is None:
            raise RuntimeError("Gemini API key not configured")
        
        prompt = f"""Analyze this environmental data and provide:
1. A brief explanation (1-2 sentences)
2. A recommendation (1-2 sentences)

City: {city}
AQI: {latest_alert['aqi']} | CO2: {latest_alert['co2']} ppm
Temperature: {latest_alert['temperature']}°C | Humidity: {latest_alert['humidity']}%

Format your response as:
EXPLANATION: [your explanation]
RECOMMENDATION: [your recommendation]"""
        
        response = gemini_model.generate_content(prompt)
        response_text = response.text
        
        # Parse the response
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('EXPLANATION:'):
                explanation = line.replace('EXPLANATION:', '').strip()
            elif line.startswith('RECOMMENDATION:'):
                recommendation = line.replace('RECOMMENDATION:', '').strip()
        
        # Ensure we have content
        explanation = explanation or "Environmental monitoring detected high pollution levels."
        recommendation = recommendation or "Monitor the situation and follow local air quality guidelines."
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        # Fallback responses based on pollution levels
        if latest_alert['aqi'] > 300:
            explanation = f"CRITICAL: AQI of {latest_alert['aqi']} indicates hazardous air quality in {city}."
            recommendation = "Stay indoors, close windows, and use air purifiers. Avoid outdoor activities."
        elif latest_alert['aqi'] > 200:
            explanation = f"Poor air quality (AQI {latest_alert['aqi']}) detected in {city}. CO2 levels are elevated."
            recommendation = "Limit outdoor activities, wear N95 masks if venturing outside, and monitor air quality."
        else:
            explanation = f"Moderate pollution (AQI {latest_alert['aqi']}) detected in {city}."
            recommendation = "Be aware of air quality conditions and take precautions if sensitive to pollution."
    
    return AIInsight(
        alert=Alert(**latest_alert),
        explanation=explanation[:250],
        recommendation=recommendation[:250],
        severity_level=latest_alert.get("severity", "warning")
    )


@app.get("/api/dashboard")
async def get_dashboard():
    """Get complete dashboard data in one call"""
    # Try to use Pathway data first, fallback to legacy pipeline
    if pathway_data_store.latest_readings:
        return pathway_data_store.get_dashboard_summary()
    
    return {
        "readings": {city: data for city, data in pipeline_state["latest_readings"].items()},
        "recent_alerts": pipeline_state["alerts"][-10:],
        "recent_stats": pipeline_state["stats"][-10:],
        "timestamp": datetime.now().isoformat(),
        "cities": list(pipeline_state["latest_readings"].keys())
    }


@app.get("/api/readings")
async def get_readings() -> Dict[str, dict]:
    """Get latest readings from all cities via Pathway"""
    readings = pathway_data_store.get_all_readings()
    if readings:
        return readings
    
    # Fallback to legacy pipeline
    readings = {}
    for city, data in pipeline_state["latest_readings"].items():
        readings[city] = data
    return readings


@app.get("/api/readings/{city}")
async def get_city_reading(city: str) -> dict:
    """Get latest reading for a specific city"""
    reading = pathway_data_store.get_city_reading(city)
    if reading:
        return reading
    
    # Fallback to legacy pipeline
    if city not in pipeline_state["latest_readings"]:
        raise HTTPException(status_code=404, detail=f"No data for city: {city}")
    
    return pipeline_state["latest_readings"][city]


@app.get("/api/alerts")
async def get_alerts(limit: int = 50) -> List[dict]:
    """Get recent alerts from Pathway"""
    alerts = pathway_data_store.get_critical_alerts(limit)
    if alerts:
        return alerts
    
    # Fallback to legacy pipeline
    return pipeline_state["alerts"][-limit:]


@app.get("/api/alerts/critical")
async def get_critical_alerts(limit: int = 20) -> List[dict]:
    """Get critical alerts only"""
    return pathway_data_store.get_critical_alerts(limit)


@app.get("/api/alerts/warnings")
async def get_warning_alerts(limit: int = 30) -> List[dict]:
    """Get warning level alerts"""
    return pathway_data_store.get_warnings(limit)


@app.get("/api/health/{city}")
async def get_city_health(city: str) -> dict:
    """Get health metrics for a specific city"""
    reading = pathway_data_store.get_city_reading(city)
    if not reading:
        raise HTTPException(status_code=404, detail=f"No data for city: {city}")
    
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
async def get_city_anomalies(city: str) -> dict:
    """Get anomaly history for a city"""
    history = pathway_data_store.get_city_anomaly_history(city)
    return {
        "city": city,
        "anomalies": history[-20:],  # Last 20 anomalies
        "total_anomalies": len(history),
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GreenStream AI Backend...")
    print("📍 API available at http://localhost:8000")
    print("📚 Docs at http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
