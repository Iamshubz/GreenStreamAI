# Pathway Integration Setup Guide

## Quick Start

### 1. Install Dependencies

```bash
cd greenstream-fullstack

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install updated requirements (includes Pathway)
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Create .env file in backend directory
cd backend
echo "GEMINI_API_KEY=your-actual-api-key-here" > .env
```

> **Note:** Get your Gemini API key from [ai.google.dev](https://ai.google.dev)

### 3. Run the Server

```bash
python main.py
```

You should see:
```
🌱 GreenStream AI - Real-Time Environmental Monitoring
📊 Powered by Pathway Streaming Framework
🤖 Integrated with Google Gemini for AI Insights

🚀 Starting server...
📍 API available at http://localhost:8000
📚 Docs at http://localhost:8000/docs
```

### 4. Test the Integration

**In a new terminal:**

```bash
# Test pipeline status
curl http://localhost:8000/api/pipeline/status

# Get readings
curl http://localhost:8000/api/readings

# Get critical alerts
curl http://localhost:8000/api/alerts

# Get environmental reports with LLM explanations
curl http://localhost:8000/api/environmental-reports
```

Or access the interactive API docs at `http://localhost:8000/docs`

---

## File Structure

```
backend/
├── main.py                        # Entry point
├── api.py                         # FastAPI application (updated)
│
├── pathway_ingestion.py           # [NEW] Data streaming layer
├── pathway_transformations.py     # [NEW] Anomaly detection & aggregations
├── pathway_llm.py                 # [NEW] LLM integration for explanations
├── pathway_pipeline.py            # [NEW] Unified orchestration
├── test_pathway_integration.py    # [NEW] Integration tests
│
├── pipeline.py                    # [LEGACY] Keep for reference
├── simulated_stream.py            # [LEGACY] Keep for reference
│
├── .env                           # Environment variables (create this)
└── __pycache__/
```

---

## Architecture Overview

### Data Flow

```
┌─────────────────────────────────────────────┐
│     Simulated Data Generator                │
│  (Delhi, Mumbai, Chennai, Bangalore)        │
└────────────────┬────────────────────────────┘
                 │
                 ▼
         ┌──────────────────┐
         │ Ingestion Layer  │
         │  (Streaming in)  │
         └────────┬─────────┘
                  │
         ┌────────▼─────────┐
         │ Transformation   │
         │  • Anomaly Detect│  AQI > 200 → CRITICAL
         │  • Filter Alerts │  CO2 > 600 → HIGH
         │  • Rolling Avg   │  Per-city 10s window
         └────────┬─────────┘
                  │
         ┌────────▼─────────┐
         │ LLM Layer        │
         │  (Google Gemini) │  Generate explanations &
         │  Document Store  │  recommendations
         └────────┬─────────┘
                  │
         ┌────────▼──────────┐
         │ FastAPI Routes    │
         │  (REST API)       │
         └────────┬──────────┘
                  │
         ┌────────▼──────────────────┐
         │  Client Applications      │
         │  (Frontend, Mobile, etc)  │
         └───────────────────────────┘
```

### Separation of Concerns

| Layer | Module | Responsibility |
|-------|--------|---|
| **Ingestion** | `pathway_ingestion.py` | Stream data from multiple sources |
| **Transformation** | `pathway_transformations.py` | Detect anomalies, compute aggregates |
| **LLM/Insights** | `pathway_llm.py` | Generate contextual explanations |
| **Orchestration** | `pathway_pipeline.py` | Coordinate all layers, manage state |
| **API** | `api.py` | Expose results via REST endpoints |

---

## API Endpoints Summary

### Readings & Monitoring
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/readings` | GET | Latest readings for all cities |
| `/api/readings/{city}` | GET | Latest reading for specific city |

### Alerts & Anomalies
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/alerts` | GET | Recent critical alerts |
| `/api/alerts/{city}` | GET | Alerts for specific city |
| `/api/stats` | GET | Rolling averages for all cities |
| `/api/stats/{city}` | GET | Rolling statistics for city |

### LLM Integration (New!)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/environmental-reports` | GET | Reports with LLM explanations |
| `/api/environmental-reports/{city}` | GET | Reports for specific city |
| `/api/document-store/stats` | GET | Document store analytics |

### System Status
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check with pipeline status |
| `/api/pipeline/status` | GET | Detailed pipeline metrics |
| `/api/dashboard` | GET | Complete dashboard snapshot |

---

## Example Requests

### 1. Get Health Status
```bash
curl http://localhost:8000/api/health | jq
```

Response:
```json
{
  "status": "healthy",
  "pipeline_running": true,
  "alerts_count": 12,
  "reports_count": 8,
  "cities_monitored": ["Delhi", "Mumbai", "Bangalore", "Chennai"],
  "last_update": "2026-03-01T10:30:45.123456"
}
```

### 2. Get Current Readings
```bash
curl http://localhost:8000/api/readings | jq
```

Response:
```json
{
  "Delhi": {
    "city": "Delhi",
    "temperature": 32.5,
    "aqi": 245,
    "co2": 650,
    "humidity": 65,
    "timestamp": "2026-03-01T10:30:45.123456"
  },
  ...
}
```

### 3. Get Critical Alerts
```bash
curl http://localhost:8000/api/alerts?limit=10 | jq
```

Response:
```json
[
  {
    "city": "Delhi",
    "aqi": 245,
    "co2": 650,
    "temperature": 32.5,
    "humidity": 65,
    "timestamp": "2026-03-01T10:30:45.123456",
    "alert_type": "aqi_critical",
    "severity": "critical"
  },
  ...
]
```

### 4. Get Environmental Reports (With Explanations)
```bash
curl http://localhost:8000/api/environmental-reports?city=Delhi&limit=5 | jq
```

Response:
```json
[
  {
    "city": "Delhi",
    "aqi": 245,
    "co2": 650,
    "temperature": 32.5,
    "humidity": 65,
    "alert_type": "aqi_critical",
    "severity": "critical",
    "timestamp": "2026-03-01T10:30:45.123456",
    "explanation": "Delhi is experiencing critical air quality from vehicular emissions and industrial pollution. Residents should avoid outdoor activities.",
    "recommendation": "Stay indoors, use air purifiers, avoid strenuous physical activities."
  },
  ...
]
```

### 5. Get Document Store Statistics
```bash
curl http://localhost:8000/api/document-store/stats | jq
```

Response:
```json
{
  "total_reports": 42,
  "cached_reports": 40,
  "cities_covered": ["Delhi", "Mumbai", "Bangalore", "Chennai"],
  "cities_count": 4
}
```

### 6. Get Pipeline Status
```bash
curl http://localhost:8000/api/pipeline/status | jq
```

Response:
```json
{
  "status": "running",
  "last_update": "2026-03-01T10:30:45.123456",
  "metrics": {
    "total_alerts": 12,
    "total_reports": 8,
    "cities_monitored": 4,
    "rolling_averages_computed": 4
  },
  "cities": ["Delhi", "Mumbai", "Bangalore", "Chennai"],
  "data_layers": {
    "ingestion": "active",
    "transformation": "active",
    "llm_integration": "active"
  }
}
```

---

## Testing

### Run Integration Tests
```bash
cd backend
python test_pathway_integration.py
```

Expected output:
```
============================================================
TEST 1: Verifying module imports...
============================================================
✓ pathway_ingestion module loaded
✓ pathway_transformations module loaded
✓ pathway_llm module loaded
✓ pathway_pipeline module loaded

...

============================================================
SUMMARY
============================================================
✓ All tests passed!

Pathway integration is working correctly.
```

### Manual Testing Flow
1. Start server: `python main.py`
2. Wait 3-5 seconds for pipeline to start
3. Check health: `curl http://localhost:8000/api/health`
4. Check readings: `curl http://localhost:8000/api/readings`
5. Check alerts: `curl http://localhost:8000/api/alerts`
6. Check reports: `curl http://localhost:8000/api/environmental-reports`

---

## Configuration & Tuning

### Adjust Anomaly Thresholds
Edit `backend/pathway_transformations.py`:

```python
class PathwayTransformationLayer:
    AQI_CRITICAL_THRESHOLD = 200    # Change this
    CO2_HIGH_THRESHOLD = 600        # Change this
    AQI_WARNING_THRESHOLD = 150     # Change this
    CO2_WARNING_THRESHOLD = 500     # Change this
```

### Adjust Data Generation Rate
Edit `backend/pathway_ingestion.py`:

```python
def generate_environmental_data():
    ...
    time.sleep(0.5)  # Change interval (in seconds)
```

### Change Server Host/Port
```bash
# Via environment variables
export HOST=127.0.0.1
export PORT=8001
python main.py

# Or edit main.py directly
```

---

## Troubleshooting

### Issue: Module not found errors
```bash
# Ensure packages are installed
pip install -r requirements.txt

# Verify installation
python -c "import pathway; import fastapi; print('OK')"
```

### Issue: No alerts generated
```bash
# Check if data is being generated
curl http://localhost:8000/api/readings

# If no readings, pipeline may be still starting
# Wait 5-10 seconds and try again

# Check thresholds - they may be too strict
# Edit pathway_transformations.py and lower thresholds
```

### Issue: LLM not generating reports
```bash
# Check if GEMINI_API_KEY is set
cat backend/.env

# If not set or invalid:
echo "GEMINI_API_KEY=your-valid-key" > backend/.env

# Restart server
```

### Issue: Port already in use
```bash
# Use different port
export PORT=8001
python main.py

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Data ingestion rate | ~2 readings/sec per city |
| Anomaly detection latency | <10ms |
| Rolling average window | 10 seconds (per-city) |
| LLM processing time | 1-3 seconds |
| API response time | <100ms |
| State update interval | 100ms |
| Buffer sizes | 100 entries max (auto-purge) |

---

## Production Deployment

For production use, consider:

1. **Persistence:** Replace in-memory state with database
   - PostgreSQL + SQLAlchemy
   - MongoDB for document store

2. **Real Data Sources:**
   - AQI.in API integration
   - OpenWeatherMap API
   - Kafka topics
   - MQTT sensors

3. **Horizontal Scaling:**
   - Deploy on Kubernetes
   - Use Pathway Cloud
   - Add load balancer (Nginx)

4. **Monitoring & Logging:**
   - ELK stack (Elasticsearch, Logstash, Kibana)
   - Prometheus metrics
   - Sentry error tracking

5. **Security:**
   - API authentication (OAuth2)
   - Rate limiting
   - HTTPS/TLS

See `PATHWAY_INTEGRATION.md` for detailed documentation.

---

## Next Steps

1. ✅ **Verify Installation:** Run `test_pathway_integration.py`
2. ✅ **Start Server:** Run `python main.py`
3. ✅ **Test API:** Access `http://localhost:8000/docs`
4. ✅ **Connect Frontend:** Update frontend API calls to new endpoints
5. ✅ **Monitor Live:** Watch environmental reports update in real-time

---

## Support & Resources

- 📚 [Pathway Docs](https://pathway.com/docs)
- 📘 [FastAPI Docs](https://fastapi.tiangolo.com)
- 🤖 [Google Gemini API](https://ai.google.dev)
- 🌍 [AQI Standards](https://www.aqi.in)

**Version:** 1.0  
**Last Updated:** March 2026
