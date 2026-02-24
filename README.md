# 🌱 GreenStream AI - Environmental Monitoring System

Real-time environmental monitoring dashboard with AI-powered insights, built with FastAPI, React, and Google Gemini.

## 📂 Project Structure

```
greenstream-fullstack/
├── backend/
│   ├── main.py                 # Server entry point
│   ├── api.py                  # FastAPI routes
│   ├── pipeline.py             # Data processing
│   └── simulated_stream.py     # Data generator
├── frontend/
│   ├── src/
│   │   ├── App.jsx             # Main dashboard
│   │   ├── index.jsx           # Entry point
│   │   └── index.css           # Styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Quick Start

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
export GEMINI_API_KEY=your-api-key

# Start backend
cd backend
python main.py
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at `http://localhost:5173`

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Server status |
| `/api/readings` | GET | Latest city readings |
| `/api/readings/{city}` | GET | Specific city data |
| `/api/alerts` | GET | Recent anomaly alerts |
| `/api/alerts/{city}` | GET | City-specific alerts |
| `/api/insights/{city}` | GET | AI analysis for city |
| `/api/dashboard` | GET | Complete dashboard data |
| `/api/stats` | GET | Rolling statistics |

## 🎨 Features

- **Real-time Monitoring**: Continuous environmental data tracking
- **Anomaly Detection**: Automatic alert generation for unusual readings
- **AI Insights**: Google Gemini-powered analysis and recommendations
- **Live Dashboard**: React-based UI with Tailwind CSS
- **RESTful API**: Complete API documentation at `/docs`

## 🔧 Environment Variables

Create `.env` file in backend directory:

```env
GEMINI_API_KEY=your-gemini-api-key
```

## 🧪 Test API Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Get all readings
curl http://localhost:8000/api/readings

# Get recent alerts
curl http://localhost:8000/api/alerts

# Get AI insights
curl http://localhost:8000/api/insights/Delhi
```

## 📈 Data Flow

1. **Data Generation**: Simulated environmental sensors (every 2 sec)
2. **Processing**: Real-time anomaly detection and statistics
3. **API Serving**: REST endpoints for frontend
4. **Visualization**: React dashboard with live updates
5. **Intelligence**: AI-generated insights on demand

## 🌍 Monitored Cities

- Delhi
- Mumbai
- Bangalore
- Chennai

## 📦 Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: React, Vite, Tailwind CSS
- **AI**: Google Gemini API
- **Icons**: Lucide React

## 📝 License

Part of Green Bharat initiative
