# Team Work Division - Project ORBIT
**3-Person Team: Frontend, Backend, Pipeline+Embedding**

---

## 👥 Team Member 1: Frontend & UI Engineer
**Focus**: Streamlit UI, User Experience, Visualization

### Responsibilities (33%)

#### Core Tasks
- **Lab 10 (partial)**: Streamlit UI enhancement & Docker testing
- **Lab 9 (partial)**: Evaluation dashboard & visualization
- **Demo Video**: Production & editing

#### Detailed Breakdown

##### Week 1-2: Streamlit UI Development (15-18 hours)
1. **Enhanced Company Selection** (3 hours)
   - Improve `src/streamlit_app.py`
   - Add search/filter functionality
   - Show company metadata (HQ, category, founded year)
   - Add company logos/icons

2. **Dashboard Display** (4 hours)
   - Side-by-side RAG vs Structured comparison
   - Collapsible sections for 8 dashboard sections
   - Syntax highlighting for markdown
   - Export to PDF functionality

3. **Evaluation Dashboard** (4 hours)
   - Interactive evaluation interface
   - Score each dashboard on 5 criteria
   - Comparison charts (bar/radar charts)
   - Historical comparisons

4. **Data Visualization** (4 hours)
   - Company stats dashboard (funding, headcount, growth)
   - Timeline view of events
   - Visibility metrics charts
   - Integration with backend data

##### Week 3: Testing & Polish (8-10 hours)
1. **Docker Integration** (3 hours)
   - Test Streamlit in Docker
   - Fix any port/networking issues
   - Ensure volume mounts work for data updates

2. **UI/UX Refinement** (3 hours)
   - Responsive design
   - Error handling & loading states
   - User feedback messages
   - Help/documentation tooltips

3. **Demo Video** (4 hours)
   - Script writing
   - Screen recording
   - Editing & narration
   - Upload & README link

#### Dependencies
**Needs from Backend Engineer**:
- API endpoints ready: `/companies`, `/dashboard/rag`, `/dashboard/structured`
- Sample response data for testing

**Needs from Pipeline Engineer**:
- At least 5 companies with complete payloads in `data/payloads/`

#### Deliverables
- [ ] Enhanced Streamlit UI with company browser
- [ ] Side-by-side dashboard comparison view
- [ ] Interactive evaluation interface
- [ ] Data visualization dashboard
- [ ] Docker-ready Streamlit service
- [ ] Demo video (≤10 mins) with link in README
- [ ] Updated README with screenshots

#### Skills Needed
- Python Streamlit
- Data visualization (Plotly, Altair)
- Docker basics
- Video editing (iMovie, DaVinci Resolve, or similar)

---

## 🔧 Team Member 2: Backend & API Engineer
**Focus**: FastAPI, LLM Integration, Dashboard Generation

### Responsibilities (33%)

#### Core Tasks
- **Lab 7**: RAG Pipeline Dashboard
- **Lab 8**: Structured Pipeline Dashboard
- **Lab 9 (partial)**: Evaluation logic & scoring
- **Lab 10 (partial)**: FastAPI Docker & deployment

#### Detailed Breakdown

##### Week 1: LLM Integration Setup (8-10 hours)
1. **LLM Provider Setup** (3 hours)
   - Choose LLM: OpenAI GPT-4, Claude, or similar
   - Set up API keys & environment variables
   - Add dependencies: `openai`, `anthropic`, or `instructor`
   - Create `src/llm_client.py` wrapper

2. **Prompt Engineering** (3 hours)
   - Load `PE_Dashboard.md` prompt template
   - Test prompt with example payload
   - Handle token limits & context windows
   - Implement retry logic & error handling

3. **Response Parsing** (2 hours)
   - Validate 8-section structure
   - Handle markdown formatting
   - Ensure "Not disclosed" appears correctly
   - Test with edge cases

##### Week 2: Dashboard Pipelines (10-12 hours)
1. **Lab 8: Structured Pipeline** (5 hours)
   - Implement `POST /dashboard/structured` endpoint
   - Load payload from `data/payloads/<company_id>.json`
   - Serialize payload to JSON for LLM context
   - Call LLM with system prompt + payload
   - Return formatted markdown
   - Add error handling & validation
   - **File**: `src/structured_pipeline.py` + `src/api.py`

2. **Lab 7: RAG Pipeline** (6 hours)
   - Implement `POST /dashboard/rag` endpoint
   - Retrieve top-k context from vector DB (use Pipeline Engineer's implementation)
   - Build context string from chunks
   - Call LLM with system prompt + retrieved context
   - Return formatted markdown
   - Compare quality vs structured approach
   - **File**: `src/rag_pipeline.py` + `src/api.py`

##### Week 3: Evaluation & Deployment (8-10 hours)
1. **Lab 9: Evaluation Logic** (4 hours)
   - Implement scoring function in `src/evaluator.py`
   - Generate dashboards for 5+ companies using both methods
   - Calculate scores: factual (0-3), schema (0-2), provenance (0-2), hallucination (0-2), readability (0-1)
   - Create comparison report
   - Fill out `EVAL.md` table
   - Write 1-page reflection

2. **Additional API Endpoints** (2 hours)
   - `GET /companies` - return list with metadata
   - `GET /dashboard/{company_id}/history` - show previous versions
   - `POST /evaluate` - score a dashboard
   - API documentation (auto-generated from FastAPI)

3. **Docker & Deployment** (3 hours)
   - Test FastAPI in Docker
   - Deploy to GCP Cloud Run or AWS App Runner
   - Set environment variables for API keys
   - Update README with deployment URL

#### Dependencies
**Needs from Frontend Engineer**:
- UI requirements for API responses

**Needs from Pipeline Engineer**:
- Vector DB retrieval function: `retrieve_context(company_name, query, top_k=5)`
- At least 5 complete payloads in `data/payloads/`

#### Deliverables
- [ ] Working LLM integration (`src/llm_client.py`)
- [ ] Structured pipeline endpoint generating full dashboards
- [ ] RAG pipeline endpoint generating full dashboards
- [ ] Evaluation logic & completed `EVAL.md`
- [ ] FastAPI deployed to cloud
- [ ] API documentation
- [ ] 1-page reflection on RAG vs Structured

#### Skills Needed
- Python FastAPI
- LLM APIs (OpenAI/Anthropic)
- Prompt engineering
- Docker & cloud deployment (GCP/AWS)

---

## 🔄 Team Member 3: Pipeline & Embedding Engineer
**Focus**: Data Ingestion, Airflow, Vector DB, Structured Extraction

### Responsibilities (33%)

#### Core Tasks
- **Lab 0**: Forbes AI 50 seed data
- **Lab 1**: Web scraping
- **Lab 2**: Full ingestion DAG
- **Lab 3**: Daily refresh DAG
- **Lab 4**: Vector DB & RAG index
- **Lab 5**: Structured extraction with instructor
- **Lab 6**: Payload assembly
- **Lab 11**: DAG ↔ App integration

#### Detailed Breakdown

##### Week 1: Data Ingestion (12-15 hours)
1. **Lab 0: Seed Data** (2 hours)
   - Scrape https://www.forbes.com/lists/ai50/
   - Extract all 50 companies
   - Populate `data/forbes_ai50_seed.json` with:
     - company_name, website, linkedin, hq_city, hq_country, category
   - **File**: `data/forbes_ai50_seed.json`

2. **Lab 1: Web Scraper** (6 hours)
   - Create `src/scraper.py`
   - Use BeautifulSoup or Playwright
   - Fetch for each company:
     - Homepage, /about, /product, /careers, /blog
   - Save raw HTML + clean text
   - Handle errors, rate limiting, timeouts
   - Create metadata JSON (source_url, crawled_at)
   - Store in `data/raw/<company_id>/YYYY-MM-DD/`
   - **File**: `src/scraper.py`

3. **Lab 2: Full Ingestion DAG** (4 hours)
   - Implement `dags/ai50_full_ingest_dag.py`
   - Task 1: Load company list
   - Task 2: Scrape all 50 (dynamic task mapping)
   - Task 3: Store metadata
   - Test in Airflow (local or Docker)
   - **File**: `dags/ai50_full_ingest_dag.py`

##### Week 2: Knowledge Extraction (12-15 hours)
1. **Lab 5: Structured Extraction** (8 hours)
   - Install `instructor` library
   - Create `src/extractor.py`
   - For each company's scraped pages:
     - Extract Company info → `Company` model
     - Extract funding events → `Event` model
     - Extract job openings → `Snapshot` model
     - Extract products → `Product` model
     - Extract leadership → `Leadership` model
     - Extract visibility → `Visibility` model
   - Use instructor pattern for structured output
   - Validate with Pydantic
   - Save to `data/structured/<company_id>.json`
   - Test on 5 companies first
   - **File**: `src/extractor.py`

2. **Lab 6: Payload Assembly** (3 hours)
   - Implement `assemble_payload()` in `src/structured_pipeline.py`
   - Combine all extracted models
   - Add notes and provenance_policy
   - Validate against `Payload` model
   - Save to `data/payloads/<company_id>.json`
   - **File**: `src/structured_pipeline.py`

3. **Lab 4: Vector DB** (4 hours)
   - Choose: ChromaDB (recommended for simplicity)
   - Create `src/vector_db.py`
   - Chunk scraped text (500-1000 tokens)
   - Generate embeddings (OpenAI or sentence-transformers)
   - Store in vector DB with metadata
   - Implement `retrieve_context(company_name, query, top_k=5)`
   - Add FastAPI endpoint: `POST /rag/search` for testing
   - **File**: `src/vector_db.py`

##### Week 3: Automation & Integration (8-10 hours)
1. **Lab 3: Daily Refresh DAG** (3 hours)
   - Implement `dags/ai50_daily_refresh_dag.py`
   - Detect changed pages (hash comparison)
   - Re-scrape About, Careers, Blog only
   - Create timestamped folders
   - Log success/failure
   - Schedule: `0 3 * * *`
   - **File**: `dags/ai50_daily_refresh_dag.py`

2. **Lab 11: DAG Integration** (3 hours)
   - Add tasks to daily DAG:
     - After scraping → trigger extraction
     - Generate payloads
     - Update vector DB
   - Write to `data/payloads/` or cloud bucket
   - Add notification on failure (optional)
   - **File**: Update both DAG files

3. **Testing & Documentation** (3 hours)
   - End-to-end test: DAG → data → payloads
   - Document data schemas
   - Create data flow diagram
   - Update README with pipeline instructions

#### Dependencies
**Needs from Backend Engineer**:
- LLM API key for structured extraction

**Needs from Frontend Engineer**:
- None (independent work)

#### Deliverables
- [ ] Populated `forbes_ai50_seed.json` (50 companies)
- [ ] Working web scraper (`src/scraper.py`)
- [ ] Raw scraped data for all 50 companies
- [ ] Full ingestion Airflow DAG
- [ ] Daily refresh Airflow DAG
- [ ] Structured extraction logic (`src/extractor.py`)
- [ ] Vector DB implementation (`src/vector_db.py`)
- [ ] Payload assembly (`src/structured_pipeline.py`)
- [ ] 5+ complete payloads in `data/payloads/`
- [ ] DAG ↔ App integration

#### Skills Needed
- Python web scraping (BeautifulSoup/Playwright)
- Apache Airflow
- LLM structured output (`instructor` library)
- Vector databases (ChromaDB/FAISS)
- Embeddings (OpenAI or Sentence Transformers)

---

## 🔗 Integration Points & Handoffs

### Week 1 Handoffs
**Pipeline → Backend** (End of Week 1):
- [ ] At least 2 companies with scraped data in `data/raw/`
- [ ] At least 1 company with payload in `data/payloads/`
- [ ] Vector DB retrieval function working

**Backend → Frontend** (End of Week 1):
- [ ] LLM integration working
- [ ] Sample dashboard output from structured pipeline
- [ ] API endpoints returning mock data

### Week 2 Handoffs
**Pipeline → Backend** (End of Week 2):
- [ ] 5+ companies with complete payloads
- [ ] Vector DB populated with all scraped data
- [ ] `retrieve_context()` function ready

**Backend → Frontend** (End of Week 2):
- [ ] Both dashboard endpoints working (`/dashboard/rag`, `/dashboard/structured`)
- [ ] `/companies` endpoint with full metadata
- [ ] API deployed to cloud (or Docker working)

**Frontend → Backend** (End of Week 2):
- [ ] UI mockups/requirements for any missing endpoints

### Week 3 Handoffs
**All → All** (End of Week 3):
- [ ] Full integration testing
- [ ] Docker compose working end-to-end
- [ ] Evaluation completed
- [ ] Demo video filmed
- [ ] Final documentation

---

## 📋 Shared Responsibilities

### Everyone
- [ ] Daily standup (async or sync)
- [ ] Update `CONTRIBUTION_ATTESTATION.txt` with % split
- [ ] Git commits with clear messages
- [ ] Code review each other's PRs
- [ ] Test integration points

### Suggested Workflow
1. **Frontend Engineer**: Create branch `feature/ui-enhancement`
2. **Backend Engineer**: Create branch `feature/llm-integration`
3. **Pipeline Engineer**: Create branch `feature/data-pipeline`
4. **All**: Merge to `main` after review

---

## 📊 Time Estimates (33% each)

| Engineer | Week 1 | Week 2 | Week 3 | Total |
|----------|--------|--------|--------|-------|
| Frontend | 8-10h  | 7-8h   | 8-10h  | 23-28h |
| Backend  | 8-10h  | 10-12h | 8-10h  | 26-32h |
| Pipeline | 12-15h | 12-15h | 8-10h  | 32-40h |

**Note**: Pipeline Engineer has slightly more work in Weeks 1-2 but less in Week 3. Backend Engineer has peak in Week 2. Frontend Engineer is more consistent.

---

## 🎯 Success Criteria

### By Week 1
- [ ] Real Forbes AI 50 data loaded
- [ ] Web scraper working for 5+ companies
- [ ] LLM integration tested
- [ ] Basic Streamlit UI showing data

### By Week 2
- [ ] All 50 companies scraped
- [ ] 5+ complete payloads generated
- [ ] Both dashboard pipelines working
- [ ] Vector DB retrieval working
- [ ] UI showing generated dashboards

### By Week 3
- [ ] Airflow DAGs running automatically
- [ ] Evaluation completed
- [ ] Docker deployed to cloud
- [ ] Demo video published
- [ ] All documentation complete

---

## 🚀 Getting Started

### Setup (Everyone - Day 1)
```bash
# Clone repo
cd pe-dashboard-ai50

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
OPENAI_API_KEY=your_key_here
# or ANTHROPIC_API_KEY=your_key_here
EOF

# Test basic setup
python -c "from src.models import Payload; print('Models OK')"
uvicorn src.api:app --reload &
streamlit run src/streamlit_app.py
```

### Independent Work
Each engineer can then work in their respective files:
- **Frontend**: `src/streamlit_app.py`, demo video
- **Backend**: `src/api.py`, `src/structured_pipeline.py`, `src/rag_pipeline.py`, `src/llm_client.py`
- **Pipeline**: `src/scraper.py`, `src/extractor.py`, `src/vector_db.py`, `dags/*.py`

---

## 📞 Communication Plan

### Daily Check-ins (15 mins)
- What did you complete yesterday?
- What are you working on today?
- Any blockers?

### Weekly Sync (30 mins)
- Demo progress
- Integration testing
- Adjust timeline if needed

### Tools
- **Git**: Feature branches + PRs
- **Slack/Discord**: Quick questions
- **GitHub Issues**: Track tasks
- **Google Docs**: Shared evaluation notes

---

## ⚠️ Risk Mitigation

### If Pipeline Engineer falls behind
- Backend Engineer can use `starter_payload.json` for testing
- Frontend Engineer can mock API responses

### If Backend Engineer falls behind
- Frontend Engineer can build UI with mock data
- Pipeline Engineer continues data work independently

### If Frontend Engineer falls behind
- Backend Engineer can test with Postman/curl
- Demo video can be simpler (screen recording + voiceover)

---

## 📝 Final Deliverables (Shared)

- [ ] **Frontend**: Streamlit UI, demo video, screenshots
- [ ] **Backend**: API deployed, EVAL.md, reflection
- [ ] **Pipeline**: All data, DAGs, extraction logic
- [ ] **All**: Updated README, contribution attestation, clean repo

Good luck team! 🎉
