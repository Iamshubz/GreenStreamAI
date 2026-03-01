"""
Pathway-FastAPI Integration Layer
Exposes Pathway streaming results through FastAPI endpoints
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
from collections import defaultdict
import threading

class PathwayDataStore:
    """
    In-memory store for Pathway pipeline results
    Bridges Pathway tables to FastAPI endpoints
    """
    
    def __init__(self):
        self.latest_readings: Dict[str, Dict[str, Any]] = {}
        self.alerts_buffer: List[Dict[str, Any]] = []
        self.processed_data: List[Dict[str, Any]] = []
        self.health_scores: Dict[str, float] = {}
        self.risk_scores: Dict[str, float] = {}
        self.anomaly_history: Dict[str, List[str]] = defaultdict(list)
        self.lock = threading.Lock()
    
    def update_reading(self, city: str, data: Dict[str, Any]):
        """Update latest reading for a city"""
        with self.lock:
            self.latest_readings[city] = {
                **data,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Store health and risk scores if available
            if "health_score" in data:
                self.health_scores[city] = data["health_score"]
            if "risk_score" in data:
                self.risk_scores[city] = data["risk_score"]
    
    def add_alert(self, alert: Dict[str, Any]):
        """Add an alert to the buffer (keep last 100)"""
        with self.lock:
            self.alerts_buffer.append(alert)
            if len(self.alerts_buffer) > 100:
                self.alerts_buffer.pop(0)
    
    def add_anomaly(self, city: str, anomaly_type: str):
        """Track anomaly history for a city"""
        with self.lock:
            self.anomaly_history[city].append(anomaly_type)
            if len(self.anomaly_history[city]) > 50:
                self.anomaly_history[city].pop(0)
    
    def get_all_readings(self) -> Dict[str, Dict[str, Any]]:
        """Get latest readings for all cities"""
        with self.lock:
            return dict(self.latest_readings)
    
    def get_city_reading(self, city: str) -> Optional[Dict[str, Any]]:
        """Get latest reading for a specific city"""
        with self.lock:
            return self.latest_readings.get(city)
    
    def get_critical_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent critical alerts"""
        with self.lock:
            return [a for a in self.alerts_buffer if a.get("severity") == "critical"][-limit:]
    
    def get_warnings(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent warnings"""
        with self.lock:
            return [a for a in self.alerts_buffer if a.get("severity") == "warning"][-limit:]
    
    def get_health_score(self, city: str) -> Optional[float]:
        """Get health score for a city"""
        with self.lock:
            return self.health_scores.get(city)
    
    def get_risk_score(self, city: str) -> Optional[float]:
        """Get risk score for a city"""
        with self.lock:
            return self.risk_scores.get(city)
    
    def get_city_anomaly_history(self, city: str) -> List[str]:
        """Get anomaly history for a city"""
        with self.lock:
            return list(self.anomaly_history.get(city, []))
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        with self.lock:
            cities = list(self.latest_readings.keys())
            critical_count = len([a for a in self.alerts_buffer if a.get("severity") == "critical"])
            warning_count = len([a for a in self.alerts_buffer if a.get("severity") == "warning"])
            avg_aqi = sum(r.get("aqi", 0) for r in self.latest_readings.values()) / len(cities) if cities else 0
            avg_health = sum(self.health_scores.values()) / len(self.health_scores) if self.health_scores else 0
            
            return {
                "total_cities": len(cities),
                "cities": cities,
                "critical_alerts": critical_count,
                "warnings": warning_count,
                "average_aqi": round(avg_aqi, 1),
                "average_health_score": round(avg_health, 1),
                "timestamp": datetime.now().isoformat(),
            }


class PathwayStreamProcessor:
    """
    Processes Pathway table data and updates the data store
    """
    
    def __init__(self, data_store: PathwayDataStore):
        self.data_store = data_store
    
    def process_pathway_results(self, 
                               raw_table_data: List[Dict[str, Any]],
                               processed_table_data: List[Dict[str, Any]],
                               alerts_table_data: List[Dict[str, Any]]):
        """
        Process Pathway table outputs and update data store
        
        Args:
            raw_table_data: Raw environmental readings
            processed_table_data: Processed readings with health metrics
            alerts_table_data: Filtered critical/warning alerts
        """
        
        # Update readings from processed data
        for record in processed_table_data:
            city = record.get("city")
            if city:
                self.data_store.update_reading(city, record)
        
        # Add alerts
        for alert in alerts_table_data:
            self.data_store.add_alert(alert)
            city = alert.get("city")
            anomaly_type = alert.get("anomaly_type", "unknown")
            if city:
                self.data_store.add_anomaly(city, anomaly_type)
    
    def continuous_update_from_generator(self, generator, interval_seconds: float = 1.0):
        """
        Continuously update data store from data generator
        Runs in background thread
        """
        import time
        
        while True:
            try:
                for city in ["Delhi", "Mumbai", "Chennai", "Bangalore"]:
                    reading = generator.generate_reading(city)
                    
                    # Compute risk and health scores
                    risk_score = self._compute_risk_score(
                        reading["aqi"],
                        reading["co2"],
                        reading["temperature"]
                    )
                    health_score = 100 - risk_score
                    
                    reading["risk_score"] = risk_score
                    reading["health_score"] = health_score
                    reading["severity"] = self._classify_severity(reading["aqi"], reading["co2"])
                    reading["anomaly_type"] = self._get_anomaly_type(reading)
                    
                    self.data_store.update_reading(city, reading)
                    
                    # Add alert if critical or warning
                    if reading["severity"] in ["critical", "warning"]:
                        self.data_store.add_alert(reading)
                        self.data_store.add_anomaly(city, reading["anomaly_type"])
                
                time.sleep(interval_seconds)
            except Exception as e:
                print(f"Error in continuous update: {e}")
                time.sleep(interval_seconds)
    
    @staticmethod
    def _compute_risk_score(aqi: int, co2: int, temperature: float) -> float:
        """Compute risk score"""
        aqi_score = min(100, max(0, (aqi / 500) * 100))
        co2_score = min(100, max(0, ((co2 - 400) / 400) * 100))
        temp_score = 0
        if temperature > 45:
            temp_score = 100
        return (aqi_score * 0.4) + (co2_score * 0.4) + (temp_score * 0.2)
    
    @staticmethod
    def _classify_severity(aqi: int, co2: int) -> str:
        """Classify severity"""
        if aqi > 200 or co2 > 600:
            return "critical"
        elif aqi > 100 or co2 > 500:
            return "warning"
        return "normal"
    
    @staticmethod
    def _get_anomaly_type(reading: Dict[str, Any]) -> str:
        """Get anomaly type"""
        anomalies = []
        if reading["aqi"] > 200:
            anomalies.append("high_aqi")
        if reading["co2"] > 600:
            anomalies.append("high_co2")
        if reading["temperature"] > 45:
            anomalies.append("extreme_heat")
        return ",".join(anomalies) if anomalies else "normal"


# Global data store instance
pathway_data_store = PathwayDataStore()
