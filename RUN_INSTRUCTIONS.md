# Running PE Dashboard Factory

## Quick Start (Without Docker)

### 1. Start FastAPI Backend
```bash
cd /Users/pranavpatel/Desktop/Cursor/pe-dashboard-ai50
python3 -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Streamlit Frontend (in a new terminal)
```bash
cd /Users/pranavpatel/Desktop/Cursor/pe-dashboard-ai50
python3 -m streamlit run src/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
```

### 3. Access the Application
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## Running with Docker (Lab 10)

### Prerequisites
- Docker Desktop installed and running

### Build and Start Services
```bash
cd /Users/pranavpatel/Desktop/Cursor/pe-dashboard-ai50
docker compose -f docker/docker-compose.yml up --build
```

### Stop Services
```bash
docker compose -f docker/docker-compose.yml down
```

### Access the Application
- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## Current Status

✅ **FastAPI Running**: http://localhost:8000
- Health check: OPERATIONAL
- Companies loaded: 50
- Data completion: 96.0%

✅ **Streamlit Running**: http://localhost:8501
- Connected to FastAPI backend
- All features operational

---

## Features Available

### 🏠 Home & Overview
- System status dashboard
- Pipeline architecture overview
- Quick start guide

### 📊 Generate Dashboards
- Structured Pipeline (from Pydantic payloads)
- RAG Pipeline (from vector DB)
- Download dashboards as Markdown

### 🔬 Compare Pipelines
- Side-by-side comparison
- Rubric-based evaluation
- Winner determination

### 📈 System Statistics
- Companies list with data status
- Pipeline availability
- Completion metrics

---

## API Endpoints

### Core Endpoints
- `GET /` - API root with endpoint listing
- `GET /health` - Health check
- `GET /companies` - List all companies with metadata
- `GET /stats` - System statistics

### Dashboard Generation
- `POST /dashboard/structured?company_id={id}` - Generate structured dashboard
- `POST /dashboard/rag?company_id={id}` - Generate RAG dashboard
- `POST /compare?company_id={id}` - Compare both pipelines

### Metadata
- `GET /company/{company_id}/metadata` - Company data quality metrics
- `POST /rag/search` - Test RAG retrieval

---

## Troubleshooting

### FastAPI won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Streamlit won't start
- Check if port 8501 is already in use: `lsof -i :8501`
- Verify API connection at http://localhost:8000/health

### Frontend can't connect to API
- Ensure FastAPI is running first
- Check API_BASE_URL in src/streamlit_app.py (should be "http://localhost:8000")
- For Docker, it should be "http://api:8000"

---

## Development Notes

- FastAPI runs with `--reload` for auto-restart on code changes
- Streamlit auto-reloads when source files change
- Both services share the same `data/` folder
- API uses Pydantic models from `src/models.py`
- Dashboards follow 8-section PE format
