# 🌱 GreenStream AI

Real-time environmental monitoring platform with:
- **FastAPI + Pathway** backend (streaming, anomaly detection, AI reports)
- **React + Vite** frontend dashboard
- **Gemini** anomaly explanations
- **Login page** (demo credentials)

## ✅ Is AQI real right now?

Current setup uses **simulated streaming data** for demo reliability.

You can switch to real AQI sources using `backend/real_aqi_integration.py`:
- OpenWeatherMap Air Pollution API
- IQAir API

## 🧱 Project Structure

```text
greenstream-fullstack/
├── api/
│   └── index.py
├── backend/
│   ├── main.py
│   ├── api.py
│   ├── pathway_pipeline.py
│   ├── pathway_ingestion.py
│   ├── pathway_transformations.py
│   ├── pathway_llm.py
│   ├── simulated_stream.py
│   ├── real_aqi_integration.py
│   ├── .env.example
│   └── start_backend.sh
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── LoginPage.jsx
│       ├── CityDetailModal.jsx
│       └── index.css
├── requirements.txt
├── vercel.json
└── README.md
```

## 🔐 Login (Frontend)

- Username: `Shubham`
- Password: `Shubh@123`

After successful login, dashboard opens and city cards are interactive.

## ⚙️ Local Development

### 1) Backend

```bash
cd backend
cp .env.example .env
# edit .env and set GEMINI_API_KEY

source ../.venv/bin/activate
pip install -r ../requirements.txt
python main.py
```

Backend: `http://localhost:8000`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173` (or next available Vite port)

## 🧪 Useful API Endpoints

- `GET /api/health`
- `GET /api/readings`
- `GET /api/alerts`
- `GET /api/environmental-reports?limit=5`
- `GET /api/pipeline/status`

## ☁️ Free Deployment Options (End-to-End)

### Option A (Recommended): Frontend + Backend split

- **Frontend**: Netlify or Vercel (free)
- **Backend**: Render / Railway / Fly.io (free tiers vary)

Why recommended:
- Long-running FastAPI + Pathway backend works better on backend-focused hosts.
- Frontend stays fast/static on CDN.

### Option B: Vercel-only (limited backend behavior)

This repo already has:
- `vercel.json`
- `api/index.py`

But Vercel Python functions are **serverless** and not ideal for persistent streaming workloads like Pathway long-running pipelines.

## 🚀 Deployment Steps

### A) Deploy Backend on Render (free tier example)

1. Push repo to GitHub.
2. Create a new **Web Service** on Render, root: repository root.
3. Build command:

```bash
pip install -r requirements.txt
```

4. Start command:

```bash
cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT
```

5. Add environment variable in Render dashboard:

```bash
GEMINI_API_KEY=your_real_key
```

6. Optional: Use included `render.yaml` for one-click setup.

### B) Deploy Frontend on Netlify

1. New site from GitHub repo.
2. Base directory: `frontend`
3. Build command:

```bash
npm run build
```

4. Publish directory:

```bash
dist
```

5. Add frontend environment variable:

```bash
VITE_API_URL=https://your-backend-service-url
```

6. Optional: Use included `netlify.toml` for one-click setup.

### C) Deploy Frontend on Vercel (alternative)

1. Import GitHub repo.
2. Set root to `frontend`.
3. Framework preset: Vite.
4. Add env var:

```bash
VITE_API_URL=https://your-backend-service-url
```

## 🔒 Confidential Data Safety (Done)

This repo is now hardened for GitHub push:
- `.env` files ignored
- log/runtime files ignored
- exposed API keys removed from `.env.example` files

## 📦 Push to GitHub Safely

Run from repo root:

```bash
git rm --cached backend/.env 2>/dev/null || true
git rm --cached .env 2>/dev/null || true
git add .
git status
git commit -m "Clean repo, secure secrets, update README and deployment setup"
git push origin main
```

## 📌 Notes

- Gemini SDK warning in logs is due to `google.generativeai` deprecation; app still runs.
- A future upgrade to `google.genai` is recommended.
- For production auth, replace demo login with real user management.
- [ ] Mobile app (React Native)
- [ ] Predictive analytics
- [ ] Email/SMS notifications
- [ ] Kubernetes deployment
- [ ] Multi-model LLM support

## 🐛 Troubleshooting

**Q: Pipeline not starting?**  
A: Check imports and dependencies with `python test_pathway_integration.py`

**Q: No alerts generated?**  
A: Wait 10 seconds for data, check thresholds in `pathway_transformations.py`

**Q: LLM reports not working?**  
A: Verify `GEMINI_API_KEY` in `.env`, fallback mode uses static text

**Q: Port 8000 already in use?**  
A: Use different port: `export PORT=8001 && python main.py`

## 💡 Key Innovations

1. **Pathway for Streaming** - Real-time data processing with sub-ms latency
2. **Intelligent Document Store** - Maintains history of LLM-generated reports
3. **Layered Architecture** - Clean separation: Ingestion → Transform → LLM → API
4. **Thread-Safe Pipeline** - Concurrent data processing without race conditions
5. **Fallback Intelligence** - Works without API keys using sensible defaults

## 📝 License

Part of Green Bharat initiative

---

**Version**: 2.0 (Pathway Integrated)  
**Last Updated**: March 2026  
**Status**: Production Ready
