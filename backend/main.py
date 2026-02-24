"""Main entry point for GreenStream AI Backend"""

from api import app
import uvicorn

if __name__ == "__main__":
    print("🌱 GreenStream AI - Real-Time Environmental Monitoring")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
