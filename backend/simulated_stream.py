import random
import time
from datetime import datetime

def generate_environmental_data():
    """Generates realistic environmental data every 2 seconds"""
    cities = ["Delhi", "Mumbai", "Bangalore", "Chennai"]

    while True:
        data = {
            "city": random.choice(cities),
            "temperature": round(random.uniform(20, 45), 2),
            "aqi": random.randint(50, 400),
            "co2": random.randint(350, 700),
            "humidity": random.randint(30, 90),
            "timestamp": datetime.now().isoformat()
        }

        yield data
        time.sleep(2)
