# PE Dashboard AI50 - AI Agent Instructions

## Project Overview
**Project ORBIT**: Automated PE intelligence dashboard generator for Forbes AI 50 companies. Two parallel LLM pipelines (RAG vs Structured) generate investor diligence dashboards, orchestrated by Airflow, served via FastAPI + Streamlit.

## Architecture - The Big Picture

### Three-Layer Pipeline Architecture
```
Data Ingestion (Airflow) → Knowledge Representation (Vector DB + Pydantic) → Dashboard Generation (LLM)
```

**Critical Flow**:
1. **Scraping** (`dags/`) → Raw HTML/text in `data/raw/<company_id>/`
2. **Extraction** → Structured JSON payloads in `data/payloads/<company_id>.json` + Vector DB chunks in `data/chroma_db/`
3. **Generation** → Two parallel pipelines produce Markdown dashboards

### Dual Pipeline Design (Core Thesis)
This project compares **two approaches** to LLM-powered dashboard generation:

- **Structured Pipeline** (`src/structured_pipeline.py`): Pydantic payload → JSON context → LLM → Dashboard
  - More precise, less hallucination
  - Requires complete extraction upfront
  - Uses `src/models.py` schemas strictly
  
- **RAG Pipeline** (`src/rag_pipeline.py`): Vector search → Retrieved chunks → LLM → Dashboard  
  - More flexible, works with partial data
  - Requires vector DB (`src/vector_db.py` with ChromaDB)
  - May hallucinate if context is sparse

**Key Insight**: Both use the SAME system prompt (`PE_Dashboard.md`) but different context assembly strategies.

## Critical Data Models (src/models.py)

All data MUST conform to Pydantic models. **Never modify these schemas** - they're the contract:

- `Payload`: Root object containing all company data
  - `company_record: Company` - Basic info, funding totals
  - `events: List[Event]` - Timestamped events (funding, product launches, layoffs, etc.)
  - `snapshots: List[Snapshot]` - Point-in-time metrics (headcount, job openings)
  - `products: List[Product]` - Product catalog with pricing
  - `leadership: List[Leadership]` - Executive team with provenance
  - `visibility: List[Visibility]` - Sentiment, mentions, GitHub stars

**Provenance Tracking**: Every model has `provenance: List[Provenance]` with `source_url`, `crawled_at`, `snippet`. Never invent data without a source.

## Developer Workflows

### Running Locally
```bash
# Install dependencies first
pip install -r requirements.txt

# Set up environment variables (.env file required)
# OPENAI_API_KEY=sk-...

# Start API (terminal 1)
uvicorn src.api:app --reload --port 8000

# Start Streamlit (terminal 2)  
streamlit run src.streamlit_app.py --server.port 8501

# Access
# API: http://localhost:8000/docs
# UI: http://localhost:8501
```

### Quick Health Check
```bash
# Check API is running
curl http://localhost:8000/health

# Check companies loaded
curl http://localhost:8000/companies | python3 -m json.tool | head -30

# Test structured pipeline (works immediately)
curl -X POST "http://localhost:8000/dashboard/structured?company_id=anthropic"

# Test RAG pipeline (uses local vector DB by default)
curl -X POST "http://localhost:8000/dashboard/rag?company_id=anthropic"

# Test RAG pipeline with GCS sync (set env var first)
export VECTOR_DB_USE_GCS=true
curl -X POST "http://localhost:8000/dashboard/rag?company_id=anthropic"
```

### Docker (Production-like)
```bash
cd docker
docker compose up --build
```

### Building Vector Database
**Current Status**: ✅ Vector database is already built and operational!
- **215 chunks indexed** across all 50 companies
- **Location**: `data/vector_db/` (local) or `gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/` (GCS)
- **Collection name**: `company_docs`
- **Size**: ~14.6 MB

**Usage (Local)**:
```python
from src.vector_db import VectorDatabase
vdb = VectorDatabase()  # Auto-loads from data/vector_db/
results = vdb.search("openai", "funding rounds", k=5)
```

**Usage (GCS - Sync from Cloud)**:
```python
from src.vector_db import VectorDatabase
vdb = VectorDatabase(use_gcs=True)  # Downloads from GCS first
results = vdb.search("openai", "funding rounds", k=5)
```

**Environment Variable** (for automatic GCS sync in RAG pipeline):
```bash
export VECTOR_DB_USE_GCS=true  # Enable GCS sync
# OR in .env file:
VECTOR_DB_USE_GCS=true
```

**Prerequisites for GCS sync**:
- Google Cloud SDK installed (`gcloud` or `gsutil`)
- Authenticated: `gcloud auth login`
- Requires network access to GCS bucket

**Metadata Structure**:
```python
{
    'company_id': 'openai',
    'page_type': 'homepage',  # or 'about', 'careers', 'blog'
    'source_url': 'https://...'
}
```

**If you need to rebuild** (requires `data/raw/<company_id>/*.txt` files):
```bash
python3 scripts/build_vector_db.py
```

### Batch Dashboard Generation
```bash
python scripts/batch_dashboard_generator.py  # Generates for all 50 companies
python scripts/batch_evaluator.py           # Evaluates both pipelines
```

### Testing Pipelines Individually
```bash
# Test structured pipeline
python src/structured_pipeline.py

# Test RAG pipeline  
python src/rag_pipeline.py

# Test LLM client
python src/llm_client.py
```

## Project-Specific Conventions

### File Naming Patterns
- Company IDs: **kebab-case** (`openai`, `world-labs`, `hugging-face`)
- Payloads: `data/payloads/<company_id>.json`
- Raw data: `data/raw/<company_id>/<page_type>.txt`
- Generated dashboards: `data/dashboards/{structured|rag}/<company_id>.md`

### The "Not disclosed" Rule
**Critical**: If data is missing, write `"Not disclosed."` - NEVER invent metrics, valuations, revenue, ARR, customer names. This is enforced in:
- System prompt (`PE_Dashboard.md`)
- Pydantic models (Optional fields)
- Evaluator scoring (`src/evaluator.py` - provenance criterion)

### LLM Temperature Strategy
- Dashboard generation: `temperature=0.2` (deterministic, factual)
- Evaluation: `temperature=0.0` (consistent scoring)

### Required Dashboard Sections (8 Total)
Every dashboard MUST have these sections in order:
1. `## Company Overview`
2. `## Business Model and GTM`
3. `## Funding & Investor Profile`
4. `## Growth Momentum`
5. `## Visibility & Market Sentiment`
6. `## Risks and Challenges`
7. `## Outlook`
8. `## Disclosure Gaps` ← Lists ALL missing critical information

Validated by `llm_client.validate_structure()`.

## API Integration Patterns

### FastAPI Endpoint Naming
- `POST /dashboard/structured?company_id={id}` - Structured pipeline
- `POST /dashboard/rag?company_id={id}` - RAG pipeline  
- `POST /compare?company_id={id}` - Side-by-side comparison
- `GET /companies` - List all with payload availability
- `GET /company/{id}/metadata` - Data quality metrics

### Error Handling Convention
All pipeline functions return dicts with optional `"error"` key:
```python
if "error" in result:
    raise HTTPException(status_code=404, detail=result["error"])
```

## Common Issues & Solutions

### "No context found" (RAG Pipeline)
**Most Common Cause**: ChromaDB not installed in your Python environment.

**Status Check**:
```bash
pip list | grep chromadb
# Should show: chromadb>=0.4.22
```

**If ChromaDB is missing**:
```bash
pip install chromadb>=0.4.22
```

**Current Vector DB Status**:
- ✅ Database exists at `data/vector_db/` with 215 chunks
- ✅ All 50 companies indexed
- ⚠️ Requires ChromaDB installed to access

**Fallback Behavior**: If ChromaDB is not available, RAG pipeline automatically uses mock data (see `_mock_retrieve()` in `rag_pipeline.py`).

### "Payload not found" (Structured Pipeline)
**Cause**: Extraction not run for company.
**Fix**: Check `data/payloads/<company_id>.json` exists. May need to run extraction logic.

### Mock Data Fallback
RAG pipeline has mock data fallback for when ChromaDB is unavailable:
- **Trigger**: `ImportError` when importing `chromadb` or exceptions during vector search
- **Behavior**: `_mock_retrieve()` in `rag_pipeline.py` generates company-specific fake chunks
- **Detection**: Check `"using_mock_data": true` in API responses
- **Quality**: Generic dashboards with placeholder data (funding amounts, team info, etc.)

Structured pipeline also has fallback:
- Falls back to `data/starter_payload.json` (UUID: `00000000-0000-0000-0000-000000000000`) if specific payload missing

### OpenAI API Key
Required in `.env`:
```bash
OPENAI_API_KEY=sk-...

# Optional: Enable GCS sync for vector database
VECTOR_DB_USE_GCS=true
```
Used by `src/llm_client.py` (singleton pattern via `get_llm_client()`).

## Airflow DAGs (Orchestration)

### DAG Locations
- `dags/ai50_full_ingest_dag.py` - Initial scraping (schedule: `@once`)
- `dags/ai50_daily_refresh_dag.py` - Daily updates (schedule: `0 3 * * *`)

**Note**: DAGs are currently minimal skeletons. Production versions should:
1. Use TaskGroups or dynamic task mapping for 50 companies
2. Trigger extraction after scraping
3. Rebuild vector DB after new data
4. Send notifications on failure

## Evaluation Rubric (Lab 9)

Dashboards scored 0-10 across 5 criteria:
- **Factual correctness** (0-3): Requires manual verification
- **Schema adherence** (0-2): All 8 sections present
- **Provenance** (0-2): Uses "Not disclosed" for missing data
- **Hallucination control** (0-2): No speculative language ("likely", "estimated to be")
- **Readability** (0-1): Proper length (500-3000 words), formatting

Implemented in `src/evaluator.py` - `auto_evaluate_dashboard()` and `compare_dashboards()`.

## Key Files Reference

### Core Logic
- `src/models.py` - Pydantic schemas (NEVER modify without team consensus)
- `src/llm_client.py` - OpenAI wrapper with retry logic, loads `PE_Dashboard.md`
- `src/structured_pipeline.py` - Payload → Dashboard pipeline
- `src/rag_pipeline.py` - Vector search → Dashboard pipeline
- `src/vector_db.py` - ChromaDB wrapper for RAG
- `src/evaluator.py` - Rubric-based scoring

### API & UI
- `src/api.py` - FastAPI endpoints (8 routes)
- `src/streamlit_app.py` - Multi-page UI with tabs

### Data
- `data/forbes_ai50_seed.json` - 50 companies with basic metadata
- `data/payloads/*.json` - Validated Pydantic payloads (48 companies)
- `data/vector_db/` - Persistent vector database (215 chunks, 14.6 MB)
  - Collection: `company_docs`
  - Synced to GCS: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/`
- `PE_Dashboard.md` - System prompt (8-section template)

## When Adding New Features

### Adding New Event Types
1. Update `Event.event_type` Literal in `src/models.py`
2. Update extraction logic to recognize new type
3. Update `PE_Dashboard.md` if new section needed

### Adding New API Endpoints
1. Add route in `src/api.py`
2. Add corresponding UI in `src/streamlit_app.py`
3. Test with FastAPI docs at `/docs`

### Extending Evaluation Criteria
1. Update scoring logic in `src/evaluator.py`
2. Update `EVAL.md` template
3. Regenerate evaluations with `scripts/batch_evaluator.py`

## Assignment Context (DAMG7245)

This is **Assignment 2 - Project ORBIT** (Part 1 of Case Study 2). Key deliverables:
- Working Airflow DAGs (full + daily ingestion)
- Both dashboard pipelines operational
- Comparison evaluation for 5+ companies (`EVAL.md`)
- Docker deployment to GCP/AWS
- Demo video ≤10 minutes

**Professor's Note**: "I primed the codebase to standardize inputs/outputs" - meaning the Pydantic models and dashboard format are FIXED. Focus on pipeline implementation, not schema design.

### Current Implementation Status (as of Nov 2025)
✅ **Complete & Working**:
- Pydantic data models (`src/models.py`)
- Structured pipeline with 48 company payloads
- FastAPI with 8 endpoints
- Streamlit UI with 4 tabs
- LLM client with OpenAI integration (gpt-4o-mini)
- Dashboard evaluation rubric
- Docker configuration
- **Vector database with 215 chunks** (all 50 companies indexed)
- RAG pipeline (requires ChromaDB installation)

⚠️ **Environment-Dependent**:
- RAG pipeline requires `pip install chromadb>=0.4.22`
- Falls back to mock data if ChromaDB unavailable
- Check API metadata: `"using_mock_data"` field

✅ **Data Complete**:
- 48/50 companies have structured payloads in `data/payloads/`
- 50/50 companies indexed in vector DB (`data/vector_db/`)
- Vector DB synced to GCS: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/`

**Implication**: Both pipelines can be tested/demoed immediately. RAG pipeline will use real vector data if ChromaDB is installed, otherwise gracefully falls back to mock data.
