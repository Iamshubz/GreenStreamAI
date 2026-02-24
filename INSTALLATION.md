# 🚀 Installation & Quick Start

## 📋 Requirements

- Python 3.8+
- Node.js 16+
- Google Gemini API key

## 🔧 Setup

### 1. Clone and Navigate

```bash
cd greenstream-fullstack
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo "GEMINI_API_KEY=your-api-key-here" > backend/.env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Go back to root
cd ..
```

## 🏃 Running

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 📍 Access

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/health

## 🧪 Quick Test

```bash
# Health check
curl http://localhost:8000/api/health

# Get readings
curl http://localhost:8000/api/readings

# Get alerts
curl http://localhost:8000/api/alerts

# Get insights for Delhi
curl http://localhost:8000/api/insights/Delhi
```

## ⚡ What's Running

- **Simulated Data**: 4 cities, every 2 seconds
- **Anomaly Detection**: Automatic alert generation
- **AI Analysis**: Context-aware insights
- **Live Dashboard**: Real-time updates every 3 seconds

## 🆘 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Backend Not Responding

1. Check `.env` file has GEMINI_API_KEY
2. Verify backend is running in Terminal 1
3. Check http://localhost:8000/api/health

### Frontend Can't Fetch Data

1. Ensure backend is running
2. Check browser console for errors (F12)
3. Verify firewall allows port 8000

### No Data Appearing

- Takes 2-4 seconds for initial data
- Check backend logs for errors
- Try http://localhost:8000/api/readings in browser

## 📚 Documentation

- Swagger API Docs: http://localhost:8000/docs
- Architecture: See README.md
- Development: Edit files and reload (frontend auto-reloads, backend needs restart)
