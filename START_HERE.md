# Quick Start Guide - Project ORBIT
**Choose your role and get the detailed task guide!**

---

## 🎯 Team Roles & Task Files

### 👥 Frontend Engineer
**Your File**: `TASK_FRONTEND.md`  
**Focus**: Streamlit UI, Visualization, Demo Video  
**Time**: ~23-28 hours  
**Key Deliverables**:
- Enhanced Streamlit UI with filters & search
- Side-by-side dashboard comparison
- Interactive evaluation interface
- Company analytics dashboard
- Demo video (≤10 mins)

**Start Here**:
```bash
streamlit run src/streamlit_app.py
# Then read TASK_FRONTEND.md for detailed tasks
```

---

### 🔧 Backend Engineer
**Your File**: `TASK_BACKEND.md`  
**Focus**: FastAPI, LLM Integration, Dashboard Generation  
**Time**: ~26-32 hours  
**Key Deliverables**:
- LLM client wrapper (`src/llm_client.py`)
- Structured pipeline dashboard
- RAG pipeline dashboard
- Evaluation logic & EVAL.md
- Cloud deployment

**Start Here**:
```bash
export OPENAI_API_KEY=sk-your-key-here
uvicorn src.api:app --reload
# Then read TASK_BACKEND.md for detailed tasks
```

---

### 🔄 Pipeline Engineer
**Your File**: `TASK_PIPELINE.md`  
**Focus**: Data Ingestion, Airflow, Vector DB, Extraction  
**Time**: ~32-40 hours  
**Key Deliverables**:
- Forbes AI 50 seed data (50 companies)
- Web scraper (`src/scraper.py`)
- Airflow DAGs (full + daily)
- Structured extraction (`src/extractor.py`)
- Vector DB (`src/vector_db.py`)
- Payload assembly

**Start Here**:
```bash
# Populate data/forbes_ai50_seed.json first
# Then read TASK_PIPELINE.md for detailed tasks
```

---

## 📋 What Each File Contains

### `TASK_FRONTEND.md`
- ✅ Current folder structure & what exists
- 🔴 6 detailed tasks with code examples
- 📦 Dependencies to install
- 🔗 Integration points with Backend/Pipeline
- ✅ Deliverables checklist
- 🚀 10-day timeline
- 💡 Tips & troubleshooting

### `TASK_BACKEND.md`
- ✅ Current folder structure & what exists
- 🔴 7 detailed tasks with code examples
- 📦 Dependencies to install (OpenAI, etc.)
- 🔗 Integration points with Frontend/Pipeline
- ✅ Deliverables checklist
- 🚀 10-day timeline
- 💡 Prompt engineering tips

### `TASK_PIPELINE.md`
- ✅ Current folder structure & what exists
- 🔴 8 detailed tasks (most work!)
- 📦 Dependencies to install (instructor, chromadb)
- 🔗 Integration points with Backend/Frontend
- ✅ Deliverables checklist
- 🚀 10-day timeline
- 💡 Scraping & extraction tips

---

## 🔗 Integration Timeline

### Week 1 Handoffs
**By Friday**:
- **Pipeline** → **Backend**: 2+ scraped companies, 1 payload
- **Backend** → **Frontend**: Sample dashboard JSON

### Week 2 Handoffs
**By Friday**:
- **Pipeline** → **Backend**: 5+ complete payloads, vector DB ready
- **Backend** → **Frontend**: Both API endpoints working

### Week 3 Integration
**All team members**:
- Full integration testing
- Evaluation completed
- Docker working
- Demo video
- Final documentation

---

## 🚀 Everyone: Day 1 Setup

### 1. Clone & Setup
```bash
cd pe-dashboard-ai50
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Create .env File
```bash
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
EOF
```

### 3. Test Existing Code
```bash
# Test models
python -c "from src.models import Payload; print('✓ Models OK')"

# Test FastAPI
uvicorn src.api:app --reload &

# Test Streamlit
streamlit run src/streamlit_app.py
```

### 4. Create Your Branch
```bash
# Frontend
git checkout -b feature/ui-enhancement

# Backend
git checkout -b feature/llm-integration

# Pipeline
git checkout -b feature/data-pipeline
```

### 5. Read Your Task File
- **Frontend**: Open `TASK_FRONTEND.md`
- **Backend**: Open `TASK_BACKEND.md`
- **Pipeline**: Open `TASK_PIPELINE.md`

---

## 📊 Quick Reference

### File Ownership (Avoid Conflicts)

**Frontend Engineer** owns:
- `src/streamlit_app.py`
- `src/evaluation_ui.py` (new)
- Demo video
- README screenshots

**Backend Engineer** owns:
- `src/api.py`
- `src/llm_client.py` (new)
- `src/structured_pipeline.py` (add to existing)
- `src/rag_pipeline.py` (replace stub)
- `src/evaluator.py` (enhance)
- `src/eval_runner.py` (new)
- `EVAL.md`
- `REFLECTION.md` (new)

**Pipeline Engineer** owns:
- `data/forbes_ai50_seed.json` (populate)
- `src/scraper.py` (new)
- `src/extractor.py` (new)
- `src/vector_db.py` (new)
- `dags/ai50_full_ingest_dag.py` (implement)
- `dags/ai50_daily_refresh_dag.py` (implement)
- `data/raw/` (create)
- `data/structured/` (create)
- `data/payloads/` (create)

### Shared Files
- `requirements.txt` - Everyone adds dependencies
- `README.md` - Everyone updates their section
- `CONTRIBUTION_ATTESTATION.txt` - Fill at end

---

## 🎯 Success Metrics

### Week 1 Goals
- [ ] Forbes AI 50 seed data complete (50 companies)
- [ ] Web scraper working on 5+ companies
- [ ] LLM client tested with GPT-4
- [ ] Basic UI improvements visible

### Week 2 Goals
- [ ] All 50 companies scraped
- [ ] 5+ complete payloads generated
- [ ] Both dashboard endpoints working
- [ ] Vector DB retrieval working
- [ ] UI showing generated dashboards

### Week 3 Goals
- [ ] Airflow DAGs running
- [ ] Evaluation complete (5+ companies)
- [ ] Docker deployed to cloud
- [ ] Demo video published
- [ ] All documentation complete

---

## 📞 Daily Communication

### Standup Template (15 mins)
**What I completed yesterday**:
- e.g., "Implemented company filter UI"

**What I'm working on today**:
- e.g., "Building RAG pipeline endpoint"

**Blockers**:
- e.g., "Waiting for payloads from Pipeline Engineer"

### Tools
- **Git**: Feature branches + pull requests
- **Slack/Discord**: Quick questions
- **GitHub Issues**: Track bugs/features
- **Shared Doc**: Evaluation notes

---

## ⚠️ Common Pitfalls & Solutions

### Problem: "I can't start because I need X from teammate"
**Solution**: Use mock data!
- **Frontend**: Use `data/starter_payload.json`
- **Backend**: Create mock `retrieve_context()` function
- **Pipeline**: Start with 1-2 companies, not 50

### Problem: "OpenAI API is too expensive"
**Solution**:
- Use GPT-3.5-turbo for development ($0.001/1K tokens)
- Switch to GPT-4 only for final evaluation
- Use local embeddings (sentence-transformers) for vector DB

### Problem: "Scraping is failing for many sites"
**Solution**:
- Start with 10-15 companies that work
- Use Playwright for JavaScript-heavy sites
- Focus on quality over quantity

### Problem: "Can't get Airflow running locally"
**Solution**:
- Use Airflow Docker (easier than local install)
- Or skip Airflow UI, just run Python functions directly
- Or use lightweight alternative like Prefect

---

## 🎓 Learning Resources

### Streamlit
- https://docs.streamlit.io/

### FastAPI
- https://fastapi.tiangolo.com/

### Instructor (Structured LLM)
- https://python.useinstructor.com/

### ChromaDB
- https://docs.trychroma.com/

### Apache Airflow
- https://airflow.apache.org/docs/

---

## 📝 Final Checklist (All Team Members)

Before submission, verify:

- [ ] All code committed to Git
- [ ] Feature branches merged to main
- [ ] README.md updated with:
  - [ ] Team member names
  - [ ] How to run locally
  - [ ] How to run in Docker
  - [ ] API documentation
  - [ ] Demo video link
  - [ ] Cloud deployment URL (if applicable)
- [ ] `CONTRIBUTION_ATTESTATION.txt` filled out
- [ ] `EVAL.md` completed with 5+ companies
- [ ] Demo video uploaded and linked
- [ ] All requirements in `requirements.txt`
- [ ] `.env` added to `.gitignore`
- [ ] No secrets committed to Git

---

## 🎉 Good Luck!

You have all the tools and detailed guides you need. 

**Remember**:
1. Start small (1-2 companies)
2. Test incrementally
3. Communicate daily
4. Use mock data when blocked
5. Focus on working > perfect

**Your detailed task guide has**:
- ✅ What you already have
- 🔴 What you need to build
- 📝 Complete code examples
- 🔗 Integration points
- ⏰ Time estimates
- 💡 Tips & tricks

Now go build! 🚀

---

## Quick Links

- **Overall Plan**: `PROJECT_STATUS.md`
- **Team Division**: `TEAM_WORK_DIVISION.md`
- **Frontend Tasks**: `TASK_FRONTEND.md`
- **Backend Tasks**: `TASK_BACKEND.md`
- **Pipeline Tasks**: `TASK_PIPELINE.md`
- **Assignment**: `Assignment.md`
- **Dashboard Prompt**: `PE_Dashboard.md`
- **Example Payload**: `data/starter_payload.json`
- **Example Dashboard**: `data/sample_dashboard.md`
