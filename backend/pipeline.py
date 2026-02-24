"""Streaming pipeline for environmental data processing"""

from simulated_stream import generate_environmental_data
from datetime import datetime
import time

# Global state for API access
pipeline_state = {
    "alerts": [],
    "stats": [],
    "latest_readings": {}
}

# Configuration
CO2_THRESHOLD = 600  # ppm
AQI_THRESHOLD = 100


def run_pipeline():
    """Main pipeline - processes environmental data in real-time"""
    print("🚀 Starting Environmental Data Pipeline...")
    
    try:
        for data in generate_environmental_data():
            process_data(data)
            time.sleep(0.1)
    except Exception as e:
        print(f"❌ Pipeline error: {e}")


def process_data(data):
    """Process environmental data and detect anomalies"""
    try:
        city = data.get("city")
        co2 = data.get("co2", 0)
        aqi = data.get("aqi", 0)
        temperature = data.get("temperature", 0)
        humidity = data.get("humidity", 0)
        timestamp = data.get("timestamp", datetime.now().isoformat())
        
        # Update latest readings
        pipeline_state["latest_readings"][city] = {
            "city": city,
            "temperature": temperature,
            "aqi": aqi,
            "co2": co2,
            "humidity": humidity,
            "timestamp": timestamp
        }
        
        # Check for anomalies
        if co2 > CO2_THRESHOLD or aqi > AQI_THRESHOLD:
            severity = "critical" if (co2 > CO2_THRESHOLD * 1.2 or aqi > AQI_THRESHOLD * 1.2) else "warning"
            alert = {
                "city": city,
                "co2": co2,
                "aqi": aqi,
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": timestamp,
                "severity": severity
            }
            pipeline_state["alerts"].append(alert)
            if len(pipeline_state["alerts"]) > 100:
                pipeline_state["alerts"].pop(0)
        
        # Update stats
        stats = {
            "city": city,
            "avg_co2": co2,
            "max_co2": co2,
            "avg_aqi": aqi,
            "avg_temp": temperature,
            "count": 1,
            "timestamp": timestamp
        }
        pipeline_state["stats"].append(stats)
        if len(pipeline_state["stats"]) > 100:
            pipeline_state["stats"].pop(0)
            
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    print("🌱 Starting GreenStream AI Pipeline...")
    run_pipeline()
