"""
Real-time AQI Data Integration Guide
=====================================

This module provides integration options for fetching real AQI data from various APIs.

OPTION 1: OpenWeatherMap Air Pollution API (Recommended - Free tier available)
------------------------------------------------------------------------------
- Free tier: 1,000 calls/day
- Coverage: Global (including Indian cities)
- Data: AQI, CO, NO, NO2, O3, SO2, PM2.5, PM10, NH3
- Sign up: https://openweathermap.org/api/air-pollution

Example Implementation:
"""

import requests
from typing import Dict, Optional
import os


class OpenWeatherMapAQI:
    """Fetch real AQI data from OpenWeatherMap API"""
    
    BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
    
    # Coordinates for Indian cities
    CITY_COORDS = {
        "Mumbai": {"lat": 19.0760, "lon": 72.8777},
        "Delhi": {"lat": 28.6139, "lon": 77.2090},
        "Bangalore": {"lat": 12.9716, "lon": 77.5946},
        "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
        "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
        "Chennai": {"lat": 13.0827, "lon": 80.2707},
        "Kolkata": {"lat": 22.5726, "lon": 88.3639},
        "Pune": {"lat": 18.5204, "lon": 73.8567},
        "Lucknow": {"lat": 26.8467, "lon": 80.9462},
        "Jaipur": {"lat": 26.9124, "lon": 75.7873}
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", "")
        
    def get_city_aqi(self, city: str) -> Optional[Dict]:
        """
        Fetch real-time AQI data for a city.
        
        Returns dict with:
        - aqi: Air Quality Index (1-5 scale)
        - co: Carbon monoxide (μg/m³)
        - no2: Nitrogen dioxide (μg/m³)
        - pm2_5: PM2.5 (μg/m³)
        - pm10: PM10 (μg/m³)
        """
        if not self.api_key:
            return None
            
        coords = self.CITY_COORDS.get(city)
        if not coords:
            return None
            
        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "lat": coords["lat"],
                    "lon": coords["lon"],
                    "appid": self.api_key
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if data and "list" in data and len(data["list"]) > 0:
                pollution = data["list"][0]
                components = pollution["components"]
                
                # Convert OpenWeather AQI (1-5) to US AQI (0-500)
                aqi_scale = {1: 50, 2: 100, 3: 150, 4: 200, 5: 300}
                aqi = aqi_scale.get(pollution["main"]["aqi"], 100)
                
                return {
                    "city": city,
                    "aqi": aqi,
                    "co2": int(components.get("co", 0) / 10),  # Convert to ppm
                    "pm2_5": components.get("pm2_5", 0),
                    "pm10": components.get("pm10", 0),
                    "no2": components.get("no2", 0),
                    "so2": components.get("so2", 0),
                }
        except Exception as e:
            print(f"Error fetching AQI for {city}: {e}")
            return None


"""
OPTION 2: IQAir API (Most accurate, limited free tier)
-------------------------------------------------------
- Free tier: 10,000 calls/month
- Most accurate data
- Sign up: https://www.iqair.com/air-pollution-data-api

Example:
"""

class IQAirAPI:
    """Fetch real AQI data from IQAir API"""
    
    BASE_URL = "https://api.airvisual.com/v2/city"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("IQAIR_API_KEY", "")
        
    def get_city_aqi(self, city: str) -> Optional[Dict]:
        """Fetch real-time AQI for Indian city"""
        if not self.api_key:
            return None
            
        try:
            response = requests.get(
                self.BASE_URL,
                params={
                    "city": city,
                    "state": "Maharashtra" if city == "Mumbai" else "Delhi",  # Adjust per city
                    "country": "India",
                    "key": self.api_key
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "success":
                pollution = data["data"]["current"]["pollution"]
                weather = data["data"]["current"]["weather"]
                
                return {
                    "city": city,
                    "aqi": pollution["aqius"],
                    "temperature": weather["tp"],
                    "humidity": weather["hu"],
                }
        except Exception as e:
            print(f"Error fetching IQAir data for {city}: {e}")
            return None


"""
OPTION 3: Indian Government CPCB API (Official source, no key required)
------------------------------------------------------------------------
- Free, no API key needed
- Official Central Pollution Control Board data
- Website: https://app.cpcbccr.com/ccr/#/caaqm-dashboard-all/caaqm-landing

Note: CPCB doesn't have a public REST API, but you can scrape their dashboard
or use their open data portal: https://cpcb.nic.in/
"""


"""
INTEGRATION STEPS:
==================

1. Choose an API provider (OpenWeatherMap recommended for starting)

2. Get API Key:
   - OpenWeatherMap: https://home.openweathermap.org/users/sign_up
   - IQAir: https://www.iqair.com/dashboard/api

3. Add to backend/.env:
   OPENWEATHER_API_KEY=your_key_here
   # OR
   IQAIR_API_KEY=your_key_here

4. Update backend/simulated_stream.py to use real data:
   - Replace generate_environmental_data() with API calls
   - Add caching to avoid hitting rate limits
   - Fallback to simulated data if API fails

5. Update requirements.txt:
   requests>=2.31.0

Example Integration in simulated_stream.py:
--------------------------------------------
"""

def generate_real_environmental_data():
    """Generate real environmental data using API"""
    from .real_aqi_integration import OpenWeatherMapAQI
    
    api = OpenWeatherMapAQI()
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad"]
    
    for city in cities:
        # Try to fetch real data
        real_data = api.get_city_aqi(city)
        
        if real_data:
            yield real_data
        else:
            # Fallback to simulated data
            yield {
                "city": city,
                "temperature": 25.0,
                "aqi": 150,
                "co2": 450,
                "humidity": 60,
                "timestamp": datetime.now().isoformat()
            }
