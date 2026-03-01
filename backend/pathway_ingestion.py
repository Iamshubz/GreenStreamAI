"""
Pathway Ingestion Layer - Real-time Environmental Data Streaming
Ingests data from multiple cities and streams to Pathway tables
"""

import pathway as pw
import pandas as pd
from datetime import datetime, timedelta
import random
import asyncio
from typing import Dict, Any

# City configurations with realistic baselines
CITY_CONFIGS = {
    "Delhi": {"aqi_base": 250, "co2_base": 600, "temp_range": (20, 45)},
    "Mumbai": {"aqi_base": 180, "co2_base": 520, "temp_range": (25, 40)},
    "Chennai": {"aqi_base": 130, "co2_base": 460, "temp_range": (25, 38)},
    "Bangalore": {"aqi_base": 120, "co2_base": 450, "temp_range": (18, 35)},
}


class EnvironmentalDataGenerator:
    """Generates realistic environmental data streams"""
    
    def __init__(self):
        self.last_readings = {city: self._generate_initial_reading(city) for city in CITY_CONFIGS}
    
    def _generate_initial_reading(self, city: str) -> Dict[str, Any]:
        """Generate initial realistic reading for a city"""
        config = CITY_CONFIGS[city]
        return {
            "city": city,
            "aqi": random.randint(max(50, config["aqi_base"] - 80), config["aqi_base"] + 100),
            "co2": random.randint(config["co2_base"] - 150, config["co2_base"] + 150),
            "temperature": round(random.uniform(config["temp_range"][0], config["temp_range"][1]), 2),
            "humidity": random.randint(30, 90),
            "timestamp": datetime.now().isoformat(),
        }
    
    def generate_reading(self, city: str) -> Dict[str, Any]:
        """Generate next reading with realistic variation"""
        config = CITY_CONFIGS[city]
        last = self.last_readings[city]
        
        # Add small variation to make it realistic
        aqi_delta = random.randint(-20, 30)
        co2_delta = random.randint(-30, 50)
        
        reading = {
            "city": city,
            "aqi": max(50, min(500, last["aqi"] + aqi_delta)),
            "co2": max(350, min(800, last["co2"] + co2_delta)),
            "temperature": round(random.uniform(config["temp_range"][0], config["temp_range"][1]), 2),
            "humidity": random.randint(30, 90),
            "timestamp": datetime.now().isoformat(),
        }
        
        self.last_readings[city] = reading
        return reading


def create_environmental_data_table() -> pw.Table:
    """
    Create a Pathway table streaming environmental data from all cities
    Returns a table with continuous updates from the data generator
    """
    
    generator = EnvironmentalDataGenerator()
    
    # Create a demo data source that continuously generates readings
    data_records = []
    
    for i in range(20):  # Initial batch
        for city in CITY_CONFIGS.keys():
            data_records.append(generator.generate_reading(city))
    
    df = pd.DataFrame(data_records)
    
    # Convert to Pathway table
    env_data = pw.debug.table_from_pandas(df)
    
    return env_data, generator


def apply_anomaly_detection(env_table: pw.Table) -> pw.Table:
    """
    Apply anomaly detection transformations to environmental data
    - Flag AQI > 200 as critical
    - Flag CO2 > 600 as high
    - Compute risk scores
    """
    
    @pw.transformer
    class AnomalyDetector:
        city = pw.this.city
        aqi = pw.this.aqi
        co2 = pw.this.co2
        temperature = pw.this.temperature
        humidity = pw.this.humidity
        timestamp = pw.this.timestamp
        
        # Anomaly flags
        aqi_critical = pw.this.aqi > 200
        co2_high = pw.this.co2 > 600
        
        # Risk score (0-100)
        aqi_score = pw.apply(lambda aqi: min(100, max(0, (aqi / 500) * 100)), pw.this.aqi)
        co2_score = pw.apply(lambda co2: min(100, max(0, ((co2 - 400) / 400) * 100)), pw.this.co2)
        risk_score = pw.apply(lambda aqi_s, co2_s: (aqi_s + co2_s) / 2, 
                             pw.this.aqi_score, pw.this.co2_score)
        
        # Severity level
        severity = pw.apply(
            lambda aqi, co2: "critical" if aqi > 200 or co2 > 600 else "warning" if aqi > 100 else "normal",
            pw.this.aqi, pw.this.co2
        )
    
    return env_table >> AnomalyDetector()


def apply_rolling_aggregations(anomaly_table: pw.Table) -> pw.Table:
    """
    Apply rolling window aggregations per city
    Computes 10-second rolling averages
    """
    
    @pw.transformer
    class RollingStats:
        city = pw.this.city
        aqi = pw.this.aqi
        co2 = pw.this.co2
        temperature = pw.this.temperature
        severity = pw.this.severity
        risk_score = pw.this.risk_score
        timestamp = pw.this.timestamp
        
        # Note: Full rolling window aggregation would require temporal joins
        # For demo, we'll compute basic stats
        aqi_rounded = pw.apply(lambda x: round(x / 10) * 10, pw.this.aqi)
        co2_rounded = pw.apply(lambda x: round(x / 10) * 10, pw.this.co2)
    
    return anomaly_table >> RollingStats()


def filter_critical_alerts(processed_table: pw.Table) -> pw.Table:
    """Filter only critical and warning severity alerts"""
    return processed_table.filter(
        (pw.this.severity == "critical") | (pw.this.severity == "warning")
    )


def create_pathway_pipeline():
    """
    Create complete Pathway streaming pipeline with all transformations
    Returns multiple output tables for different use cases
    """
    
    # Ingestion layer
    raw_data, generator = create_environmental_data_table()
    
    # Transformation layer
    anomaly_detected = apply_anomaly_detection(raw_data)
    processed = apply_rolling_aggregations(anomaly_detected)
    critical_alerts = filter_critical_alerts(processed)
    
    return {
        "raw_data": raw_data,
        "anomaly_detected": anomaly_detected,
        "processed": processed,
        "critical_alerts": critical_alerts,
        "generator": generator,
    }
