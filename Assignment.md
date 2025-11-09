



# PE Dashboard AI50 - Automated Private Equity Intelligence

**Project ORBIT** - Forbes AI 50 PE Dashboard Factory

Automated system for generating investment-grade PE dashboards for Forbes AI 50 companies using dual LLM pipelines with real-time GCS streaming.

---
## 📊 Current StatusThis starts:

- FastAPI: http://localhost:8000
- Codelab Link: https://codelabs-preview.appspot.com/?file_id=1q55eKm20EeYkN_g0Q4KdVb7A7g28D87yIkz8lyX2p8M#4
- demo video:- https://youtu.be/MvWR_xlf49E

## 🎯 Project Overview

This project automates the generation of investment-grade dashboards for the Forbes AI 50 companies, replacing manual analyst workflows with an AI-powered pipeline that:

- ✅ **Ingests** public data from company websites, career pages, and news sources (via Airflow)
- ✅ **Stores** all data in Google Cloud Storage (single source of truth)
- ✅ **Streams** data on-demand from GCS (no local caching)
- ✅ **Generates** comprehensive PE dashboards using two approaches:
  - **Structured Pipeline**: GCS Payload → Pydantic → ChatGPT → Dashboard
  - **RAG Pipeline**: GCS ChromaDB → Semantic Search → ChatGPT → Dashboard
- ✅ **Updates** data daily via Airflow DAGs (3 AM schedule)
- ✅ **Serves** dashboards via FastAPI + Streamlit UI

---

## 🏗️ Architecture

### Complete System Flow with GCS Streaming

```
┌─────────────────────────────────────────────────────────────────┐
│               AIRFLOW ORCHESTRATION (Daily Updates)             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  Scrape Jobs │ → │ Extract Data │ → │  Update GCS  │      │
│  │  (3 AM Daily)│    │   & Process  │    │   Bucket     │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│            GOOGLE CLOUD STORAGE (Source of Truth)               │
│  gs://us-central1-pe-airflow-env-2825d831-bucket/              │
│  ├── data/payloads/       (48 companies - Pydantic JSON)       │
│  ├── data/vector_db/      (ChromaDB - 215 chunks)              │
│  └── data/jobs/           (45 companies - Hiring data)         │
│                                                                  │
│  ✅ ALWAYS LATEST DATA - Updated daily by Airflow               │
│  ✅ NO LOCAL CACHING - Streamed on-demand                       │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              FASTAPI + STREAMLIT (Query Interface)              │
│  User Request → API Endpoint → Stream from GCS → Generate       │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                 DUAL PIPELINE GENERATION (Real-time)            │
│  ┌────────────────────────────┐  ┌──────────────────────────┐  │
│  │   STRUCTURED PIPELINE      │  │      RAG PIPELINE        │  │
│  │                            │  │                          │  │
│  │  1. Stream payload.json    │  │  1. Query GCS ChromaDB   │  │
│  │     from GCS               │  │     (semantic search)    │  │
│  │  2. Validate with Pydantic │  │  2. Retrieve top-k       │  │
│  │  3. Format as JSON context │  │     chunks               │  │
│  │  4. Call ChatGPT           │  │  3. Assemble context     │  │
│  │     (gpt-4o-mini)          │  │  4. Call ChatGPT         │  │
│  │  5. Generate dashboard     │  │     (gpt-4o-mini)        │  │
│  │                            │  │  5. Generate dashboard   │  │
│  │  ⚡ Uses latest GCS data   │  │  ⚡ Uses latest GCS data  │  │
│  └────────────────────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 ↓
┌─────────────────────────────────────────────────────────────────┐
│              DASHBOARD OUTPUT (Generated On-The-Fly)            │
│  ✅ 8 Required Sections:                                        │
│  1. Company Overview                                            │
│  2. Business Model and GTM                                      │
│  3. Funding & Investor Profile                                  │
│  4. Growth Momentum (with latest jobs data from GCS)            │
│  5. Visibility & Market Sentiment                               │
│  6. Risks and Challenges                                        │
│  7. Outlook                                                     │
│  8. Disclosure Gaps                                             │
│                                                                  │
│  📊 Always reflects LATEST data from GCS (updated daily)        │
│  🚫 NO pre-generated files - everything on-demand               │
└─────────────────────────────────────────────────────────────────┘
```

### Key Architecture Principles

1. **Single Source of Truth**: GCS bucket contains ALL data
2. **No Local Storage**: API streams data directly from GCS (no downloads)
3. **Always Fresh**: Airflow updates GCS daily at 3 AM
4. **On-Demand Generation**: Dashboards created in real-time per request
5. **Dual Validation**: Both Pydantic (structured) and ChromaDB (RAG) ensure quality

---

## 📊 Current Status

### Data Coverage (in GCS Bucket)
- **50 Companies**: All Forbes AI 50 companies indexed
- **48 Structured Payloads**: Validated Pydantic schemas in GCS (`data/payloads/`)
- **215 ChromaDB Chunks**: Vector database in GCS (`data/vector_db/`)
- **45 Jobs Files**: Hiring data in GCS (`data/jobs/`)
- **Daily Updates**: Airflow refreshes data every day at 3 AM

### System Capabilities
- **Real-time Generation**: Dashboards created on-the-fly from GCS
- **Always Fresh**: No stale data - streams latest from cloud
- **Dual Pipeline**: Structured (Pydantic) + RAG (ChromaDB)
- **Format**: Bloomberg Terminal-style (500-1500 words)
- **Quality**: Both pipelines score 8.0-8.1/10 average

### Technical Stack
- **LLM**: OpenAI GPT-4o-mini (fast, cost-effective)
- **Vector DB**: ChromaDB with GCS persistence
- **Validation**: Pydantic 2.x for type safety
- **Storage**: Google Cloud Storage (no local caching)
- **Orchestration**: Apache Airflow (daily updates)
- **API**: FastAPI + Uvicorn
- **UI**: Streamlit multi-page app

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop (for containerized deployment)
- OpenAI API Key
- Google Cloud credentials (for GCS access)

### Installation

```bash
# Clone repository
git clone https://github.com/Big-Data-IA-Team-5/pe-dashboard-ai50.git
cd pe-dashboard-ai50

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add:
#   OPENAI_API_KEY=sk-...
#   GCS_BUCKET_NAME=us-central1-pe-airflow-env-2825d831-bucket
#   GOOGLE_APPLICATION_CREDENTIALS=./gcp-service-account-key.json
```

### Local Development

#### Option 1: Run Locally (Recommended for Development)

```bash
# Terminal 1: Start FastAPI backend
uvicorn src.api:app --reload --port 8000

# Terminal 2: Start Streamlit frontend
streamlit run src.streamlit_app.py --server.port 8501
```

Access:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Streamlit UI**: http://localhost:8501

#### Option 2: Run with Docker (Recommended for Production)

```bash
cd docker
docker compose up --build -d
```

Access:
- **API**: http://localhost:8000
- **Streamlit UI**: http://localhost:8501

Check status:
```bash
docker compose ps
docker compose logs -f api        # View API logs
docker compose logs -f streamlit  # View Streamlit logs
```

---

## 📖 Usage Guide

### Generate Dashboard (API)

**Structured Pipeline** (streams from GCS):
```bash
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic&use_gcs=true"
```

**RAG Pipeline** (queries GCS ChromaDB):
```bash
curl -X POST "http://localhost:8000/dashboard/rag?company_id=anthropic&use_gcs=true&top_k=10"
```

**Compare Both** (side-by-side):
```bash
curl -X POST "http://localhost:8000/compare?company_id=anthropic"
```

### Generate Dashboard (Streamlit UI)

1. Open http://localhost:8501
2. Select a company from dropdown (50 companies available)
3. Click "Generate (Structured)" or "Generate (RAG)"
4. View dashboard with metadata and validation results
5. Download as Markdown file

### Key API Parameters

- `company_id`: Company identifier (e.g., `anthropic`, `openai`)
- `use_gcs`: Stream from GCS (default: `true`) or use local fallback
- `top_k`: Number of chunks for RAG (default: 10)

---

## 📁 Project Structure

```
pe-dashboard-ai50/
├── src/
│   ├── api.py                    # FastAPI backend (8 endpoints)
│   ├── streamlit_app.py          # Streamlit UI (4 tabs)
│   ├── structured_pipeline.py    # GCS Payload → Pydantic → LLM
│   ├── rag_pipeline.py           # GCS ChromaDB → Retrieval → LLM
│   ├── llm_client.py             # OpenAI wrapper (gpt-4o-mini)
│   ├── chromadb_gcs.py           # ChromaDB with GCS persistence
│   ├── gcs_client.py             # GCS streaming client (singleton)
│   ├── jobs_loader.py            # Jobs data loader
│   ├── evaluator.py              # Dashboard comparison rubric
│   └── models.py                 # Pydantic schemas (DO NOT MODIFY)
│
├── data/                         # LOCAL COPY (for reference only)
│   ├── forbes_ai50_seed.json     # All 50 companies metadata
│   ├── payloads/                 # 48 structured payloads
│   ├── vector_db/                # ChromaDB (215 chunks)
│   └── jobs/                     # 45 companies with hiring data
│
├── dags/                         # Airflow DAGs (orchestration)
│   ├── ai50_full_ingest_dag.py   # Full ingestion pipeline
│   └── ai50_daily_refresh_dag.py # Daily updates (3 AM schedule)
│
├── docker/
│   ├── Dockerfile                # Multi-service container
│   └── docker-compose.yml        # API + Streamlit services
│
├── PE_Dashboard_Concise.md       # System prompt (Bloomberg style)
├── gcp-service-account-key.json  # GCS credentials (DO NOT COMMIT)
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-...                                          # OpenAI API key
GCS_BUCKET_NAME=us-central1-pe-airflow-env-2825d831-bucket   # GCS bucket
GOOGLE_APPLICATION_CREDENTIALS=./gcp-service-account-key.json # GCS auth

# Optional
API_BASE_URL=http://localhost:8000                            # API endpoint
```

---

## 📊 Dashboard Format

All dashboards follow an 8-section structure with strict validation:

### 1. Company Overview
- Company name, location, founding year
- Leadership team (CEO, CTO, executives)
- Industry category

### 2. Business Model and GTM
- Target customers and market segments
- Product lineup with descriptions
- Pricing models (if disclosed)

### 3. Funding & Investor Profile
- Funding history with dates and amounts
- Lead investors and syndicate members
- Last valuation and total capital raised

### 4. Growth Momentum
- Current headcount and growth rate
- **Open job positions** (engineering, sales, other) - **STREAMED FROM GCS DAILY**
- Recent product launches

### 5. Visibility & Market Sentiment
- News mentions (last 30 days)
- Average sentiment score
- GitHub stars and Glassdoor ratings

### 6. Risks and Challenges
- Competitive pressure
- Regulatory risks
- Market uncertainties

### 7. Outlook
- Growth trajectory assessment
- Market fit evaluation

### 8. Disclosure Gaps
- **Critical**: Lists ALL missing information
- Examples: "Valuation not disclosed", "Customer counts not disclosed"

---

## 🔬 API Endpoints

### Core Dashboard Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check + pipeline status |
| `/companies` | GET | List all 50 companies with payload availability |
| `/dashboard/structured` | POST | Generate structured dashboard (GCS streaming) |
| `/dashboard/rag` | POST | Generate RAG dashboard (GCS ChromaDB) |
| `/compare` | POST | Side-by-side comparison of both pipelines |
| `/company/{id}/metadata` | GET | Data quality metrics |

### Example Request/Response

```bash
# Request
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic&use_gcs=true"

# Response
{
  "company_id": "anthropic",
  "method": "structured_gcs",
  "markdown": "# Private Equity Dashboard for Anthropic\n\n## Company Overview...",
  "validation": {
    "valid": true,
    "section_count": 8,
    "present_sections": ["## Company Overview", ...]
  },
  "metadata": {
    "company_name": "Anthropic",
    "pipeline": "structured_gcs",
    "model": "gpt-4o-mini",
    "data_source": "gcs",
    "response_time_seconds": 11.88,
    "num_events": 1,
    "num_products": 4
  }
}
```

---

## 🛠️ Development

### Test API

```bash
# Health check
curl http://localhost:8000/health

# List companies
curl http://localhost:8000/companies | python3 -m json.tool | head -30

# Generate test dashboard (GCS streaming)
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic&use_gcs=true" \
  | python3 -m json.tool

# Test RAG pipeline (GCS ChromaDB)
curl -X POST "http://localhost:8000/dashboard/rag?company_id=anthropic&use_gcs=true&top_k=10"
```

---

## 🚧 Troubleshooting

### Issue: "ChromaDB not found"
```bash
pip install chromadb>=0.4.22
```

### Issue: "OpenAI API key invalid"
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Verify API key at: https://platform.openai.com/api-keys
```

### Issue: "GCS authentication failed"
```bash
# Verify service account key exists
ls -la gcp-service-account-key.json

# Test GCS access
gsutil ls gs://us-central1-pe-airflow-env-2825d831-bucket/data/
```

### Issue: "Docker containers not starting"
```bash
# Check Docker is running
docker ps

# View logs
docker compose logs -f

# Rebuild from scratch (no cache)
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 📝 Assignment Context

**Course**: DAMG7245 - Big Data Systems and Intelligence Analytics  
**Assignment**: Assignment 2 - Project ORBIT (Part 1)  
**Team**: Big-Data-IA-Team-5  

### Key Deliverables
- ✅ Working FastAPI with 8 endpoints (GCS streaming)
- ✅ Working Streamlit UI with 4 tabs
- ✅ Two dashboard pipelines (Structured + RAG)
- ✅ Real-time GCS data streaming (no local caching)
- ✅ Daily Airflow updates (3 AM schedule)
- ✅ Docker deployment (docker-compose.yml)
- ✅ Vector database (215 chunks in GCS)
- ✅ On-demand dashboard generation

### Critical Rules
1. **Never invent data**: Use "Not disclosed" for missing information
2. **Fixed schema**: 8 sections required in exact order
3. **Provenance**: Every claim must be traceable to sources
4. **No hallucination**: No speculative language ("likely", "estimated")
5. **Always fresh**: All data streamed from GCS (updated daily)

### How It Works

#### Structured Pipeline
```
GCS Payload (JSON) → Pydantic Validation → ChatGPT → Dashboard
```
- **Purpose**: Use Pydantic for data validation, ChatGPT for text generation
- **Input**: Structured JSON from GCS
- **Output**: Human-readable markdown dashboard

#### RAG Pipeline
```
GCS ChromaDB → Semantic Search → ChatGPT → Dashboard
```
- **Purpose**: Use ChromaDB for retrieval, ChatGPT for synthesis
- **Input**: Vector database queries from GCS
- **Output**: Context-enriched markdown dashboard

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Forbes AI 50**: Source data
- **OpenAI**: GPT-4o-mini model
- **ChromaDB**: Vector database
- **Google Cloud**: Storage and infrastructure

---

**Last Updated**: November 8, 2025  
**Version**: 3.0.0  
**Status**: Production Ready with GCS Streaming ✅
