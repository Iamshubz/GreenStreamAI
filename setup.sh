#!/bin/bash

# GreenStream AI - Full-Stack Setup Script

echo "🌱 GreenStream AI - Full-Stack Setup"
echo "===================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check Node.js
echo -e "${BLUE}Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js $NODE_VERSION found${NC}"
echo ""

# Backend Setup
echo -e "${BLUE}=== Setting up Backend ===${NC}"
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating .env file..."
if [ ! -f backend/.env ]; then
    cp .env.example backend/.env
    echo -e "${YELLOW}⚠️  Created .env file. Please add your OPENAI_API_KEY${NC}"
else
    echo "✅ .env file already exists"
fi
echo -e "${GREEN}✅ Backend setup complete${NC}"
echo ""

# Frontend Setup
echo -e "${BLUE}=== Setting up Frontend ===${NC}"
cd frontend
echo "Installing npm dependencies..."
npm install
echo -e "${GREEN}✅ Frontend setup complete${NC}"
cd ..
echo ""

# Summary
echo "===================================="
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo "===================================="
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Edit backend/.env with your OpenAI API key:"
echo "   OPENAI_API_KEY=sk-your-key-here"
echo ""
echo "2. Terminal 1 - Start Backend:"
echo "   cd backend && python main.py"
echo ""
echo "3. Terminal 2 - Start Frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open Dashboard:"
echo "   http://localhost:5173"
echo ""
echo "5. API Documentation:"
echo "   http://localhost:8000/docs"
echo ""
