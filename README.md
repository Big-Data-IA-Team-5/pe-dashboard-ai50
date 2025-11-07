# PE Dashboard AI50 - Automated Private Equity Intelligence# Project ORBIT — PE Dashboard for Forbes AI 50



**Project ORBIT** - Forbes AI 50 PE Dashboard FactoryThis is the starter package for **Assignment 2 — DAMG7245**.



Automated system for generating private equity diligence dashboards for all Forbes AI 50 companies using dual LLM pipelines (Structured vs RAG).## Run locally (dev)



---```bash

python -m venv .venv

## 🎯 Project Overviewsource .venv/bin/activate

pip install -r requirements.txt

This project automates the generation of investment-grade dashboards for the Forbes AI 50 companies, replacing manual analyst workflows with an AI-powered pipeline that:uvicorn src.api:app --reload

# in another terminal

- ✅ **Ingests** public data from company websites, career pages, and news sourcesstreamlit run src/streamlit_app.py

- ✅ **Extracts** structured information using Pydantic + LLM validation```

- ✅ **Generates** comprehensive PE dashboards using two approaches:

  - **Structured Pipeline**: Pydantic payload → LLM → Dashboard## Docker (app layer only)

  - **RAG Pipeline**: ChromaDB Vector DB → LLM → Dashboard

- ✅ **Evaluates** both pipelines with a 10-point rubric```bash

- ✅ **Serves** dashboards via FastAPI + Streamlit UIcd docker

docker compose up --build

---```



## 📊 Current StatusThis starts:

- FastAPI: http://localhost:8000

### Data Coverage- Streamlit: http://localhost:8501

- **50 Companies**: All Forbes AI 50 companies indexed

- **48 Structured Payloads**: Validated Pydantic schemas with complete data# Add instructions on running on the cloud based on your setup and links to Codelabs, architecture diagrams etc.
- **50 RAG Dashboards**: Generated from ChromaDB vector database
- **215 ChromaDB Chunks**: Comprehensive vector database coverage
- **45 Jobs Files**: Hiring data integrated into dashboards

### Generated Outputs
- **98 Dashboards Total**: 48 Structured + 50 RAG
- **EVAL.md**: Comprehensive comparison of both pipelines across 48 companies
- **Concise Format**: Bloomberg Terminal-style dashboards (500-1500 words)
- **Jobs Integration**: Hiring data in Growth Momentum section

### Evaluation Results
- **RAG Pipeline**: 41 wins (85.4%) - Average score: 8.0/10
- **Structured Pipeline**: 7 wins (14.6%) - Average score: 8.1/10
- **Quality**: Both pipelines produce high-quality, investor-ready dashboards

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA INGESTION                           │
│  Forbes AI 50 → Scraping → Raw Data → Extraction → Payloads │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  KNOWLEDGE REPRESENTATION                    │
│  • data/payloads/*.json (Pydantic-validated)                 │
│  • data/vector_db/ (ChromaDB with 215 chunks)                │
│  • data/jobs/*.json (Hiring data for 45 companies)           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  DUAL PIPELINE GENERATION                    │
│  ┌──────────────────────┐  ┌──────────────────────┐         │
│  │  Structured Pipeline │  │    RAG Pipeline      │         │
│  │  Payload → LLM       │  │  ChromaDB → LLM      │         │
│  └──────────────────────┘  └──────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    DASHBOARD OUTPUT                          │
│  8 Required Sections:                                        │
│  1. Company Overview                                         │
│  2. Business Model and GTM                                   │
│  3. Funding & Investor Profile                               │
│  4. Growth Momentum (with jobs data)                         │
│  5. Visibility & Market Sentiment                            │
│  6. Risks and Challenges                                     │
│  7. Outlook                                                  │
│  8. Disclosure Gaps                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker Desktop (for containerized deployment)
- OpenAI API Key

### Installation

```bash
# Clone repository
git clone https://github.com/Big-Data-IA-Team-5/pe-dashboard-ai50.git
cd pe-dashboard-ai50

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
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
docker compose up -d
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

**Structured Pipeline**:
```bash
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic"
```

**RAG Pipeline**:
```bash
curl -X POST "http://localhost:8000/dashboard/rag?company_id=anthropic&top_k=50"
```

**Compare Both**:
```bash
curl -X POST "http://localhost:8000/compare?company_id=anthropic"
```

### Generate Dashboard (Streamlit UI)

1. Open http://localhost:8501
2. Select a company from dropdown
3. Click "Generate (Structured)" or "Generate (RAG)"
4. View dashboard with metadata and validation results
5. Download as Markdown file

### Batch Generation

Generate dashboards for all companies:

```bash
# Generate both pipelines
python scripts/batch_generate_all.py

# Generate evaluation report
python scripts/generate_eval_from_dashboards.py
```

---

## 📁 Project Structure

```
pe-dashboard-ai50/
├── src/
│   ├── api.py                    # FastAPI backend (8 endpoints)
│   ├── streamlit_app.py          # Streamlit UI (4 tabs)
│   ├── structured_pipeline.py    # Pydantic → LLM pipeline
│   ├── rag_pipeline.py           # ChromaDB → LLM pipeline
│   ├── llm_client.py             # OpenAI wrapper (gpt-4o-mini)
│   ├── vector_db.py              # ChromaDB interface
│   ├── jobs_loader.py            # Jobs data loader
│   ├── evaluator.py              # Dashboard comparison rubric
│   └── models.py                 # Pydantic schemas (DO NOT MODIFY)
│
├── data/
│   ├── forbes_ai50_seed.json     # All 50 companies metadata
│   ├── payloads/                 # 48 structured Pydantic payloads
│   ├── vector_db/                # ChromaDB (215 chunks, 14.6 MB)
│   ├── jobs/                     # 45 companies with hiring data
│   └── dashboards/
│       ├── structured/           # 48 generated dashboards
│       └── rag/                  # 50 generated dashboards
│
├── scripts/
│   ├── batch_generate_all.py    # Generate all dashboards
│   └── generate_eval_from_dashboards.py  # Create EVAL.md
│
├── dags/                         # Airflow DAGs (orchestration)
│   ├── ai50_full_ingest_dag.py   # Full ingestion pipeline
│   └── ai50_daily_refresh_dag.py # Daily updates
│
├── docker/
│   ├── Dockerfile                # Multi-service container
│   └── docker-compose.yml        # API + Streamlit services
│
├── PE_Dashboard_Concise.md       # System prompt (Bloomberg style)
├── EVAL.md                       # Pipeline comparison report
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=sk-...                    # OpenAI API key

# Optional
API_BASE_URL=http://localhost:8000       # API endpoint for Streamlit
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
- **Open job positions** (engineering, sales, other)
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

## 🎯 Evaluation Rubric

Dashboards are scored on a 10-point scale:

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Factual Correctness** | 0-3 | All facts verified against sources |
| **Schema Adherence** | 0-2 | All 8 sections present |
| **Provenance** | 0-2 | Proper use of "Not disclosed" |
| **Hallucination Control** | 0-2 | No speculative language |
| **Readability** | 0-1 | 500-3000 words, proper formatting |
| **TOTAL** | 0-10 | Overall quality score |

**Results**: RAG Pipeline wins 85.4% of comparisons (avg 8.0/10 vs 8.1/10)

---

## 🔬 API Endpoints

### Core Dashboard Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/companies` | GET | List all companies with payload status |
| `/dashboard/structured` | POST | Generate structured dashboard |
| `/dashboard/rag` | POST | Generate RAG dashboard |
| `/compare` | POST | Side-by-side comparison |
| `/company/{id}/metadata` | GET | Data quality metrics |

### Example Request

```bash
curl -X POST "http://localhost:8000/dashboard/structured?company_id=openai" \
  | python3 -m json.tool
```

---

## 🛠️ Development

### Test API

```bash
# Health check
curl http://localhost:8000/health

# List companies
curl http://localhost:8000/companies | python3 -m json.tool

# Generate test dashboard
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic"
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

### Issue: "Docker containers not starting"
```bash
# Check Docker is running
docker ps

# View logs
docker compose logs -f

# Rebuild from scratch
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
- ✅ Working FastAPI with 8 endpoints
- ✅ Working Streamlit UI with 4 tabs
- ✅ Two dashboard pipelines (Structured + RAG)
- ✅ Evaluation report (EVAL.md) for 48 companies
- ✅ Docker deployment (docker-compose.yml)
- ✅ Vector database (215 chunks)
- ✅ 98 generated dashboards

### Critical Rules
1. **Never invent data**: Use "Not disclosed" for missing information
2. **Fixed schema**: 8 sections required in exact order
3. **Provenance**: Every claim must be traceable to sources
4. **No hallucination**: No speculative language ("likely", "estimated")

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Forbes AI 50**: Source data
- **OpenAI**: GPT-4o-mini model
- **ChromaDB**: Vector database

---

**Last Updated**: November 7, 2025  
**Version**: 2.0.0  
**Status**: Production Ready ✅
