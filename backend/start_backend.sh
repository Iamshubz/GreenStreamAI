#!/bin/bash

# GreenStream Backend Startup Script

echo "🚀 Starting GreenStream Backend..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment
source "../.venv/bin/activate"

# Start the server
python main.py runserver
