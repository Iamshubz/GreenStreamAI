"""FastAPI entrypoint for GreenStreamAI (repo root)."""

import os
import sys
import uvicorn

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from api import app  # noqa: E402

if __name__ == "__main__":
    print("🌱 GreenStream AI - Real-Time Environmental Monitoring")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
