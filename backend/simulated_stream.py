import random
import time
from datetime import datetime

def generate_environmental_data():
    """Generates realistic environmental data for 8 major Indian cities"""
    cities = [
        "Delhi", "Mumbai", "Bangalore", "Chennai", 
        "Kolkata", "Hyderabad", "Pune", "Ahmedabad"
    ]
    
    # City-specific baseline pollution levels for realism
    city_baselines = {
        "Delhi": {"aqi": 250, "co2": 600},
        "Mumbai": {"aqi": 180, "co2": 520},
        "Kolkata": {"aqi": 200, "co2": 550},
        "Ahmedabad": {"aqi": 170, "co2": 510},
        "Bangalore": {"aqi": 120, "co2": 450},
        "Hyderabad": {"aqi": 140, "co2": 470},
        "Chennai": {"aqi": 130, "co2": 460},
        "Pune": {"aqi": 110, "co2": 440}
    }

    while True:
        city = random.choice(cities)
        baseline = city_baselines[city]
        
        data = {
            "city": city,
            "temperature": round(random.uniform(20, 45), 2),
            "aqi": random.randint(max(50, baseline["aqi"] - 80), baseline["aqi"] + 100),
            "co2": random.randint(baseline["co2"] - 150, baseline["co2"] + 150),
            "humidity": random.randint(30, 90),
            "timestamp": datetime.now().isoformat()
        }

        yield data
        time.sleep(2)

