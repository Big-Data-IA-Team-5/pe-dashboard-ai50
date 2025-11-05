# Project ORBIT - Current Status & To-Do Analysis

## Overview
This is Assignment 2 for DAMG7245 - building an automated PE intelligence dashboard for Forbes AI 50 companies. Your professor has **primed the codebase** with starter templates to standardize inputs/outputs, making it easier to get started.

---

## What You HAVE (Starter Code Provided by Professor)

### ✅ Project Structure
```
pe-dashboard-ai50/
├── Assignment.md              # Full assignment requirements
├── PE_Dashboard.md            # Dashboard generation system prompt
├── EVAL.md                    # Evaluation template (empty)
├── README.md                  # Basic run instructions
├── requirements.txt           # Basic dependencies (FastAPI, Streamlit, Pydantic)
├── CONTRIBUTION_ATTESTATION.txt  # Team member attestation template
├── data/
│   ├── forbes_ai50_seed.json  # PLACEHOLDER - needs real data
│   ├── sample_dashboard.md    # Example output format
│   └── starter_payload.json   # Complete example payload structure
├── dags/
│   ├── ai50_full_ingest_dag.py    # Minimal skeleton DAG
│   └── ai50_daily_refresh_dag.py  # Minimal skeleton DAG
├── docker/
│   ├── Dockerfile             # FastAPI + Streamlit container
│   └── docker-compose.yml     # Service orchestration
└── src/
    ├── models.py              # Complete Pydantic models (READY)
    ├── api.py                 # Minimal FastAPI endpoints (stubs)
    ├── streamlit_app.py       # Basic UI skeleton
    ├── rag_pipeline.py        # Stub function only
    ├── structured_pipeline.py # Load payload function only
    ├── evaluator.py           # Simple scoring function
    └── prompts/
        └── dashboard_system.md  # Complete prompt template
```

### ✅ Complete & Ready to Use
1. **Pydantic Models (`models.py`)**: Fully defined schemas for:
   - `Company`, `Event`, `Snapshot`, `Product`, `Leadership`, `Visibility`, `Payload`
   - All with proper typing, provenance tracking, schema versioning
   
2. **Dashboard Prompt (`PE_Dashboard.md` & `prompts/dashboard_system.md`)**: 
   - Complete system prompt for LLM
   - 8-section structure defined
   - Rules for provenance, "Not disclosed" handling
   
3. **Sample Data (`starter_payload.json`)**:
   - Complete example showing exact structure expected
   - Example AI company with funding event, leadership, visibility metrics
   
4. **Docker Setup**:
   - Dockerfile ready for FastAPI + Streamlit
   - docker-compose.yml configured

---

## What You NEED TO BUILD (11 Labs)

### 🔴 PHASE 1: Data Ingestion (Labs 0-3)

#### Lab 0: Project Bootstrap ✅ (Mostly Done)
**Status**: Repo structure exists, but needs:
- [ ] Populate `forbes_ai50_seed.json` with **real** Forbes AI 50 data from https://www.forbes.com/lists/ai50/
  - Currently has 1 placeholder company
  - Need all 50 companies with: name, website, LinkedIn, HQ, category

#### Lab 1: Scrape & Store 🔴 (NOT STARTED)
**Status**: No scraper exists
- [ ] Build Python scraper to fetch for each company:
  - Homepage HTML
  - /about page
  - /product or /platform page
  - /careers page
  - /blog or /news page
- [ ] Save raw HTML + clean text version
- [ ] Emit metadata (company_name, source_url, crawled_at)
- [ ] Store in `data/raw/<company_id>/` structure
- [ ] Consider using: BeautifulSoup, Scrapy, or Playwright

#### Lab 2: Full-Load Airflow DAG 🟡 (SKELETON ONLY)
**Status**: `ai50_full_ingest_dag.py` exists but just has placeholder tasks
- [ ] Implement `load_company_list()` - read from forbes_ai50_seed.json
- [ ] Implement `scrape_company_pages()` - call your scraper from Lab 1
- [ ] Add TaskGroup or dynamic task mapping for 50 companies
- [ ] Implement `store_raw_to_cloud()` - save to GCS/S3 or local
- [ ] Schedule: `@once`
- [ ] Test end-to-end execution

#### Lab 3: Daily/Update Airflow DAG 🟡 (SKELETON ONLY)
**Status**: `ai50_daily_refresh_dag.py` exists with single placeholder task
- [ ] Implement logic to detect changed pages (e.g., compare hashes, last-modified headers)
- [ ] Re-scrape only About, Careers, Blog pages (key signal pages)
- [ ] Create timestamped subfolders per run: `data/raw/<company_id>/2025-11-03/...`
- [ ] Log success/failure per company
- [ ] Schedule: `0 3 * * *` (3 AM daily)

---

### 🔴 PHASE 2: Knowledge Representation (Labs 4-6)

#### Lab 4: Vector DB & RAG Index 🔴 (STUB ONLY)
**Status**: `rag_pipeline.py` has dummy return
- [ ] Install vector DB: FAISS, ChromaDB, or Qdrant
- [ ] Chunk scraped text (500-1000 tokens)
- [ ] Generate embeddings (OpenAI, Sentence Transformers, or Cohere)
- [ ] Store chunks in vector DB with metadata (company_id, source_url)
- [ ] Implement `retrieve_context(company_name, query)` function
- [ ] Add FastAPI endpoint: `POST /rag/search`
- [ ] Test retrieval quality

#### Lab 5: Structured Extraction with Pydantic 🔴 (NOT STARTED)
**Status**: Models exist but no extraction logic
- [ ] Install `instructor` library
- [ ] For each scraped page, prompt LLM to extract:
  - Company info → `Company` model
  - Funding announcements → `Event` model (type="funding")
  - Job openings → `Snapshot` model
  - Product info → `Product` model
  - Leadership bios → `Leadership` model
  - News/sentiment → `Visibility` model
- [ ] Use instructor pattern to force structured output
- [ ] Save to `data/structured/<company_id>.json`
- [ ] Validate with Pydantic `.model_validate()`
- [ ] Test on 5 companies initially

#### Lab 6: Payload Assembly 🟡 (LOADER EXISTS)
**Status**: `structured_pipeline.py` can load, but no assembly logic
- [ ] Combine all extracted models into single `Payload` object
- [ ] Aggregate events, snapshots, products, leadership, visibility lists
- [ ] Add notes and provenance_policy
- [ ] Save to `data/payloads/<company_id>.json`
- [ ] Validate against `Payload` model
- [ ] Ensure it matches format of `starter_payload.json`

---

### 🔴 PHASE 3: Dashboard Generation (Labs 7-9)

#### Lab 7: RAG Pipeline Dashboard 🔴 (STUB ONLY)
**Status**: `POST /dashboard/rag` endpoint exists but returns hardcoded text
- [ ] Implement real retrieval using vector DB from Lab 4
- [ ] Build context string from top-k chunks
- [ ] Load dashboard system prompt from `PE_Dashboard.md`
- [ ] Call LLM (OpenAI GPT-4, Claude, etc.) with:
  - System prompt
  - Retrieved context
  - Company name
- [ ] Enforce 8-section output structure
- [ ] Return Markdown dashboard
- [ ] Handle "Not disclosed" for missing data

#### Lab 8: Structured Pipeline Dashboard 🟡 (STUB EXISTS)
**Status**: `POST /dashboard/structured` endpoint exists but returns minimal hardcoded text
- [ ] Load payload from `data/payloads/<company_id>.json`
- [ ] Serialize payload to JSON string for LLM context
- [ ] Load same dashboard system prompt
- [ ] Call LLM with structured payload as context
- [ ] Enforce same 8-section structure
- [ ] Return Markdown dashboard
- [ ] Should be more precise than RAG (less hallucination)

#### Lab 9: Evaluation & Comparison 🔴 (TEMPLATE ONLY)
**Status**: `EVAL.md` has empty table, `evaluator.py` has simple sum function
- [ ] Generate dashboards for **at least 5 companies** using both methods
- [ ] Score each on rubric (0-10 points):
  - Factual correctness (0-3)
  - Schema adherence (0-2)
  - Provenance use (0-2)
  - Hallucination control (0-2)
  - Readability (0-1)
- [ ] Fill out comparison table in `EVAL.md`
- [ ] Write 1-page reflection on which method works better and why
- [ ] Add to repo

---

### 🔴 PHASE 4: Deployment (Labs 10-11)

#### Lab 10: Dockerize 🟡 (DOCKERFILE READY)
**Status**: Docker files exist but untested
- [ ] Test local Docker build: `docker build -t pe-dashboard .`
- [ ] Test local run: `docker-compose up`
- [ ] Verify FastAPI accessible at `http://localhost:8000`
- [ ] Verify Streamlit accessible at `http://localhost:8501`
- [ ] Deploy to GCP (Cloud Run, GKE) or AWS (ECS, App Runner)
- [ ] Update README with cloud deployment URLs

#### Lab 11: DAG ↔ App Integration 🔴 (NOT STARTED)
**Status**: No integration exists
- [ ] Modify daily DAG to:
  - After scraping, trigger structured extraction
  - Generate payload files
  - Write to `data/payloads/` (or cloud bucket)
- [ ] Update Streamlit to read from latest payload location
- [ ] (Optional) Add Airflow trigger from API
- [ ] (Optional) Add email/Slack notification on DAG failure
- [ ] Test end-to-end: DAG runs → new data → Streamlit shows update

---

## Critical Missing Pieces

### 🔴 HIGH PRIORITY (Must Do First)
1. **Real Forbes AI 50 Data**: Populate `forbes_ai50_seed.json` with all 50 companies
2. **Web Scraper**: Build actual scraping logic (Lab 1)
3. **LLM Integration**: No LLM calls implemented yet
   - Need OpenAI API key or Anthropic/Cohere/etc.
   - Need to add to `requirements.txt`: `openai`, `anthropic`, or `instructor`
4. **Vector Database**: Choose and implement (FAISS, Chroma, Qdrant)
5. **Instructor Library**: For structured extraction (Lab 5)

### 🟡 MEDIUM PRIORITY
1. **Airflow Implementation**: DAGs need real scraping/extraction tasks
2. **Evaluation Logic**: Build comparison framework
3. **Cloud Deployment**: Deploy Docker containers to GCP/AWS

### 🟢 LOW PRIORITY (Already Mostly Done)
1. **Pydantic Models**: ✅ Complete
2. **Dashboard Prompt**: ✅ Complete
3. **Docker Setup**: ✅ Ready to use
4. **Basic API Structure**: ✅ Endpoints exist

---

## Dependencies to Add

Current `requirements.txt` is minimal. You'll need to add:

```txt
# LLM & Structured Output
openai>=1.0.0              # For GPT-4/GPT-3.5
# OR anthropic>=0.7.0      # For Claude
instructor>=0.4.0          # For structured extraction

# Vector DB (choose one)
chromadb>=0.4.0           # Recommended for simplicity
# OR faiss-cpu>=1.7.0
# OR qdrant-client>=1.6.0

# Embeddings
sentence-transformers>=2.2.0  # For local embeddings
# OR use OpenAI embeddings

# Scraping
beautifulsoup4>=4.12.0
requests>=2.32.3
lxml>=4.9.0
# OR playwright>=1.40.0    # For JS-heavy sites

# Airflow (if running locally)
apache-airflow>=2.7.0

# Text processing
tiktoken>=0.5.0           # Token counting for OpenAI
langchain>=0.1.0          # Optional: for RAG helpers
```

---

## Recommended Implementation Order

### Week 1: Data Foundation
1. ✅ Lab 0: Populate Forbes AI 50 seed data (1-2 hours)
2. 🔴 Lab 1: Build web scraper (4-6 hours)
3. 🔴 Lab 2: Implement full ingestion DAG (3-4 hours)
4. 🔴 Lab 3: Implement daily refresh DAG (2-3 hours)

### Week 2: Knowledge Extraction
5. 🔴 Lab 5: Structured extraction with instructor (6-8 hours) 
   - Do this BEFORE Lab 4 - easier to test
6. 🔴 Lab 6: Payload assembly (2-3 hours)
7. 🔴 Lab 4: Vector DB & RAG (4-6 hours)

### Week 3: Dashboard Generation
8. 🔴 Lab 8: Structured pipeline dashboard (4-5 hours)
   - Do this BEFORE Lab 7 - easier to debug
9. 🔴 Lab 7: RAG pipeline dashboard (4-5 hours)
10. 🔴 Lab 9: Evaluation (3-4 hours)

### Week 4: Deployment
11. 🔴 Lab 10: Docker deployment (2-3 hours)
12. 🔴 Lab 11: DAG integration (3-4 hours)
13. 📹 Demo video (1-2 hours)
14. 📝 Documentation & attestation (1-2 hours)

**Total Estimated Time**: 40-55 hours

---

## Final Deliverables Checklist

- [ ] GitHub repo: `pe-dashboard-ai50`
- [ ] Working FastAPI with endpoints:
  - [ ] `GET /companies`
  - [ ] `POST /dashboard/rag`
  - [ ] `POST /dashboard/structured`
- [ ] Working Streamlit UI (company dropdown → generate dashboard)
- [ ] Two Airflow DAGs:
  - [ ] `ai50_full_ingest_dag.py` (full load)
  - [ ] `ai50_daily_refresh_dag.py` (daily refresh)
- [ ] Docker working locally + deployed to cloud
- [ ] `EVAL.md` completed with 5+ company comparisons
- [ ] Demo video ≤10 mins (link in README)
- [ ] `CONTRIBUTION_ATTESTATION.txt` filled out

---

## Quick Start Steps (What to Do NOW)

1. **Install dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Get API keys**:
   - OpenAI API key (for GPT-4 or GPT-3.5-turbo)
   - Store in `.env` file (add to `.gitignore`)

3. **Populate Forbes AI 50 seed**:
   - Scrape https://www.forbes.com/lists/ai50/
   - Fill `data/forbes_ai50_seed.json` with real companies

4. **Build scraper** (Lab 1):
   - Start with 2-3 companies to test
   - Use BeautifulSoup or Playwright

5. **Test example payload**:
   - Run: `uvicorn src.api:app --reload`
   - Test: `http://localhost:8000/dashboard/structured`
   - See it return the example dashboard

6. **Read through `PE_Dashboard.md`**:
   - This is your LLM system prompt
   - Understand the 8 sections required

---

## Notes from Professor

> "I primed the codebase and examples to make it easier for you to get started and to standardize the outputs and inputs."

**Translation**: 
- ✅ Data models are DONE - use them exactly as-is
- ✅ Dashboard output format is DEFINED - follow the 8 sections
- ✅ Example payload shows EXACT structure expected
- 🔴 You still need to BUILD the scraping, extraction, and generation logic

> "We will extend this assignment into Case study 5. So this is a short assignment!"

**Translation**:
- Focus on getting the **pipeline working** end-to-end
- Don't over-engineer - starter code is intentionally minimal
- Quality > quantity (5 well-evaluated companies better than rushed 50)
- This is Part 1 - you'll build on this foundation later

---

## Key Success Factors

1. ✅ **Follow the schema exactly** - models are provided for a reason
2. ✅ **Use "Not disclosed"** - never invent data
3. ✅ **Test incrementally** - get 1 company working before doing all 50
4. ✅ **Provenance tracking** - every claim needs a source_url
5. ✅ **Compare RAG vs Structured** - this is the core learning outcome

---

## Questions to Ask Professor/TA

1. Which LLM should we use? (OpenAI GPT-4, Claude, open-source?)
2. Should we deploy to GCP or AWS? (Or just local Docker OK for now?)
3. What's the grading weight on evaluation quality vs. completeness?
4. Can we use fewer than 50 companies for initial submission?

Good luck! 🚀
