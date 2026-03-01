"""
Pathway Transformation Layer - Real-time Data Processing & Anomaly Detection
Performs streaming transformations on environmental data without decorators
"""

import pathway as pw
from typing import Optional
from datetime import datetime


class EnvironmentalAnomalyDetector:
    """Advanced anomaly detection for environmental data"""
    
    # Thresholds
    AQI_CRITICAL = 200
    AQI_WARNING = 100
    CO2_CRITICAL = 600
    CO2_WARNING = 500
    TEMP_CRITICAL_HIGH = 45
    TEMP_CRITICAL_LOW = 0
    
    @staticmethod
    def classify_aqi_severity(aqi: int) -> str:
        """Classify AQI into severity levels"""
        if aqi >= EnvironmentalAnomalyDetector.AQI_CRITICAL:
            return "critical"
        elif aqi >= EnvironmentalAnomalyDetector.AQI_WARNING:
            return "warning"
        else:
            return "normal"
    
    @staticmethod
    def classify_co2_severity(co2: int) -> str:
        """Classify CO2 into severity levels"""
        if co2 >= EnvironmentalAnomalyDetector.CO2_CRITICAL:
            return "critical"
        elif co2 >= EnvironmentalAnomalyDetector.CO2_WARNING:
            return "warning"
        else:
            return "normal"
    
    @staticmethod
    def compute_risk_score(aqi: int, co2: int, temperature: float) -> float:
        """
        Compute composite environmental risk score (0-100)
        Factors: AQI (40%), CO2 (40%), Temperature extremes (20%)
        """
        aqi_score = min(100, max(0, (aqi / 500) * 100))
        co2_score = min(100, max(0, ((co2 - 400) / 400) * 100))
        
        # Temperature penalty
        if temperature > 35:
            temp_score = min(100, (temperature - 35) * 5)
        elif temperature < 10:
            temp_score = min(100, (10 - temperature) * 3)
        else:
            temp_score = 0
        
        # Composite score (40% AQI, 40% CO2, 20% Temp)
        risk = (aqi_score * 0.4) + (co2_score * 0.4) + (temp_score * 0.2)
        return round(risk, 2)
    
    @staticmethod
    def get_anomaly_type(aqi: int, co2: int, temperature: float, humidity: int) -> str:
        """Determine anomaly type"""
        if aqi > EnvironmentalAnomalyDetector.AQI_CRITICAL:
            return "high_aqi"
        elif co2 > EnvironmentalAnomalyDetector.CO2_CRITICAL:
            return "high_co2"
        elif temperature > EnvironmentalAnomalyDetector.TEMP_CRITICAL_HIGH:
            return "extreme_heat"
        elif humidity > 80:
            return "high_humidity"
        else:
            return "normal"


class PathwayTransformationPipeline:
    """Builds complete transformation pipeline using Pathway"""
    
    @staticmethod
    def apply_severity_classification(table: pw.Table) -> pw.Table:
        """Apply multi-factor severity classification"""
        return table.select(
            city=pw.this.city,
            aqi=pw.this.aqi,
            co2=pw.this.co2,
            temperature=pw.this.temperature,
            humidity=pw.this.humidity,
            timestamp=pw.this.timestamp,
            aqi_severity=pw.apply(
                EnvironmentalAnomalyDetector.classify_aqi_severity,
                pw.this.aqi,
                dtype=str
            ),
            co2_severity=pw.apply(
                EnvironmentalAnomalyDetector.classify_co2_severity,
                pw.this.co2,
                dtype=str
            ),
            anomaly_type=pw.apply(
                EnvironmentalAnomalyDetector.get_anomaly_type,
                pw.this.aqi,
                pw.this.co2,
                pw.this.temperature,
                pw.this.humidity,
                dtype=str
            ),
            risk_score=pw.apply(
                EnvironmentalAnomalyDetector.compute_risk_score,
                pw.this.aqi,
                pw.this.co2,
                pw.this.temperature,
                dtype=float
            )
        )
    
    @staticmethod
    def apply_overall_severity(table: pw.Table) -> pw.Table:
        """Compute overall severity from individual factors"""
        def get_severity(aqi_sev: str, co2_sev: str) -> str:
            if aqi_sev == "critical" or co2_sev == "critical":
                return "critical"
            elif aqi_sev == "warning" or co2_sev == "warning":
                return "warning"
            else:
                return "normal"
        
        return table.select(
            **pw.this,
            severity=pw.apply(
                get_severity,
                pw.this.aqi_severity,
                pw.this.co2_severity,
                dtype=str
            )
        )
    
    @staticmethod
    def apply_health_metrics(table: pw.Table) -> pw.Table:
        """Compute health score and air quality classification"""
        def get_air_quality_class(aqi: int) -> str:
            if aqi > 300:
                return "hazardous"
            elif aqi > 200:
                return "very_unhealthy"
            elif aqi > 150:
                return "unhealthy"
            elif aqi > 100:
                return "unhealthy_for_groups"
            elif aqi > 50:
                return "moderate"
            else:
                return "good"
        
        def compute_health_score(risk: float) -> int:
            # 100 - risk_score, scaled to 0-100
            return max(0, min(100, int(100 - risk)))
        
        return table.select(
            **pw.this,
            health_score=pw.apply(
                compute_health_score,
                pw.this.risk_score,
                dtype=int
            ),
            air_quality_class=pw.apply(
                get_air_quality_class,
                pw.this.aqi,
                dtype=str
            )
        )
    
    @staticmethod
    def filter_alerts(table: pw.Table) -> pw.Table:
        """Filter to critical and warning alerts only"""
        return table.filter(
            (pw.this.severity == "critical") | (pw.this.severity == "warning")
        )
    
    @staticmethod
    def build_complete_pipeline(raw_table: pw.Table) -> dict:
        """Build complete transformation pipeline"""
        try:
            # Apply severity classification
            classified = PathwayTransformationPipeline.apply_severity_classification(raw_table)
            
            # Compute overall severity
            with_severity = PathwayTransformationPipeline.apply_overall_severity(classified)
            
            # Add health metrics
            with_health = PathwayTransformationPipeline.apply_health_metrics(with_severity)
            
            # Filter alerts
            alerts = PathwayTransformationPipeline.filter_alerts(with_health)
            
            return {
                "classified": classified,
                "with_severity": with_severity,
                "with_health": with_health,
                "alerts": alerts
            }
        except Exception as e:
            print(f"Error building pipeline: {e}")
            return {
                "classified": raw_table,
                "with_severity": raw_table,
                "with_health": raw_table,
                "alerts": raw_table
            }
