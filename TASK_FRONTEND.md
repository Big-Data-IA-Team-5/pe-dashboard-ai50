# Frontend Engineer - Task Guide
**Role**: Streamlit UI, User Experience, Visualization  
**Your Responsibility**: 33% of the project

---

## 📂 Current Folder Structure (What You Have)

```
pe-dashboard-ai50/
├── src/
│   └── streamlit_app.py          ✅ Basic skeleton EXISTS
├── docker/
│   ├── Dockerfile                ✅ Ready to use
│   └── docker-compose.yml        ✅ Ready to use
├── data/
│   ├── forbes_ai50_seed.json     🟡 Placeholder (Pipeline Engineer will populate)
│   ├── starter_payload.json      ✅ Example payload for testing
│   └── sample_dashboard.md       ✅ Example dashboard output
└── requirements.txt              🟡 Need to add: plotly, altair
```

---

## 🎯 Your Tasks & What's Left to Do

### ✅ What You Already Have (Starter Code)
- **File**: `src/streamlit_app.py` - Basic skeleton with:
  - Company dropdown selector
  - Two columns for RAG vs Structured
  - Buttons to generate dashboards
  - API calls to backend
  - Basic markdown rendering

### 🔴 What You Need to Build

---

## TASK 1: Enhanced Company Selection UI
**File**: `src/streamlit_app.py`  
**Location**: Replace/enhance the current company selection logic (lines 9-11)  
**Estimated Time**: 3 hours

### What to Add:
```python
# Add after imports
import pandas as pd

# Replace the basic selectbox with enhanced version
st.sidebar.header("Company Filter")

# Load company data
companies_df = pd.DataFrame(companies)

# Add filters
categories = st.sidebar.multiselect(
    "Filter by Category",
    options=companies_df['category'].unique() if 'category' in companies_df else [],
    default=None
)

hq_countries = st.sidebar.multiselect(
    "Filter by HQ Country",
    options=companies_df['hq_country'].unique() if 'hq_country' in companies_df else [],
    default=None
)

# Search box
search = st.sidebar.text_input("Search company name")

# Filter logic
filtered_companies = companies_df.copy()
if categories:
    filtered_companies = filtered_companies[filtered_companies['category'].isin(categories)]
if hq_countries:
    filtered_companies = filtered_companies[filtered_companies['hq_country'].isin(hq_countries)]
if search:
    filtered_companies = filtered_companies[
        filtered_companies['company_name'].str.contains(search, case=False, na=False)
    ]

# Enhanced selectbox with metadata
choice = st.selectbox(
    "Select company",
    filtered_companies['company_name'].tolist(),
    format_func=lambda x: f"{x} • {filtered_companies[filtered_companies['company_name']==x]['hq_country'].values[0] if len(filtered_companies[filtered_companies['company_name']==x]) > 0 else ''}"
)

# Show company card
if choice:
    company_data = filtered_companies[filtered_companies['company_name'] == choice].iloc[0]
    st.sidebar.markdown(f"""
    **Website**: {company_data.get('website', 'N/A')}  
    **HQ**: {company_data.get('hq_city', 'N/A')}, {company_data.get('hq_country', 'N/A')}  
    **Category**: {company_data.get('category', 'N/A')}
    """)
```

**Dependencies**: Need `data/forbes_ai50_seed.json` populated by Pipeline Engineer

---

## TASK 2: Side-by-Side Dashboard Comparison
**File**: `src/streamlit_app.py`  
**Location**: Replace the current column layout (lines 15-26)  
**Estimated Time**: 4 hours

### What to Add:
```python
# Create tabs instead of columns for better UX
tab1, tab2, tab3 = st.tabs(["📊 Comparison View", "🔍 RAG Pipeline", "📋 Structured Pipeline"])

with tab1:
    st.subheader("Side-by-Side Comparison")
    
    if st.button("Generate Both Dashboards", type="primary", use_container_width=True):
        col1, col2 = st.columns(2)
        
        with st.spinner("Generating dashboards..."):
            # Get company_id from choice
            company_id = "00000000-0000-0000-0000-000000000000"  # TODO: map from choice
            
            # Call both APIs
            with col1:
                st.markdown("### 🔍 RAG Pipeline")
                try:
                    resp_rag = requests.post(
                        f"{API_BASE}/dashboard/rag",
                        params={"company_name": choice},
                        timeout=30
                    )
                    resp_rag.raise_for_status()
                    rag_markdown = resp_rag.json()["markdown"]
                    
                    # Add collapsible sections
                    sections = rag_markdown.split('\n## ')
                    for i, section in enumerate(sections):
                        if i == 0:
                            st.markdown(section)
                        else:
                            section_title = section.split('\n')[0]
                            section_content = '\n'.join(section.split('\n')[1:])
                            with st.expander(f"## {section_title}", expanded=(i==1)):
                                st.markdown(section_content)
                    
                    # Export button
                    st.download_button(
                        "📥 Download RAG Dashboard",
                        rag_markdown,
                        file_name=f"{choice}_rag_dashboard.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            
            with col2:
                st.markdown("### 📋 Structured Pipeline")
                try:
                    resp_struct = requests.post(
                        f"{API_BASE}/dashboard/structured",
                        params={"company_id": company_id},
                        timeout=30
                    )
                    resp_struct.raise_for_status()
                    struct_markdown = resp_struct.json()["markdown"]
                    
                    # Same collapsible sections
                    sections = struct_markdown.split('\n## ')
                    for i, section in enumerate(sections):
                        if i == 0:
                            st.markdown(section)
                        else:
                            section_title = section.split('\n')[0]
                            section_content = '\n'.join(section.split('\n')[1:])
                            with st.expander(f"## {section_title}", expanded=(i==1)):
                                st.markdown(section_content)
                    
                    st.download_button(
                        "📥 Download Structured Dashboard",
                        struct_markdown,
                        file_name=f"{choice}_structured_dashboard.md",
                        mime="text/markdown"
                    )
                except Exception as e:
                    st.error(f"Error: {str(e)}")

with tab2:
    # Existing RAG pipeline code
    st.subheader("RAG Pipeline (Vector DB)")
    # ... existing code ...

with tab3:
    # Existing Structured pipeline code
    st.subheader("Structured Pipeline (Pydantic)")
    # ... existing code ...
```

**Dependencies**: Need Backend Engineer to have `/dashboard/rag` and `/dashboard/structured` working

---

## TASK 3: Interactive Evaluation Dashboard
**File**: Create new file `src/evaluation_ui.py` or add to `streamlit_app.py`  
**Location**: New section/page in Streamlit  
**Estimated Time**: 4 hours

### What to Add (as new page):
```python
# Create src/evaluation_ui.py
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Evaluation", layout="wide")

st.title("📊 Dashboard Evaluation - RAG vs Structured")

# Load evaluation data if exists
evaluation_file = "data/evaluation_results.json"

# Evaluation form
st.header("Evaluate Dashboards")

company = st.selectbox("Select Company", ["Company A", "Company B", "Company C"])

col1, col2 = st.columns(2)

with col1:
    st.subheader("RAG Pipeline")
    rag_factual = st.slider("Factual Correctness (0-3)", 0, 3, 0, key="rag_factual")
    rag_schema = st.slider("Schema Adherence (0-2)", 0, 2, 0, key="rag_schema")
    rag_provenance = st.slider("Provenance Use (0-2)", 0, 2, 0, key="rag_provenance")
    rag_hallucination = st.slider("Hallucination Control (0-2)", 0, 2, 0, key="rag_hallucination")
    rag_readability = st.slider("Readability (0-1)", 0, 1, 0, key="rag_readability")
    rag_total = rag_factual + rag_schema + rag_provenance + rag_hallucination + rag_readability
    st.metric("Total Score", f"{rag_total}/10")

with col2:
    st.subheader("Structured Pipeline")
    struct_factual = st.slider("Factual Correctness (0-3)", 0, 3, 0, key="struct_factual")
    struct_schema = st.slider("Schema Adherence (0-2)", 0, 2, 0, key="struct_schema")
    struct_provenance = st.slider("Provenance Use (0-2)", 0, 2, 0, key="struct_provenance")
    struct_hallucination = st.slider("Hallucination Control (0-2)", 0, 2, 0, key="struct_hallucination")
    struct_readability = st.slider("Readability (0-1)", 0, 1, 0, key="struct_readability")
    struct_total = struct_factual + struct_schema + struct_provenance + struct_hallucination + struct_readability
    st.metric("Total Score", f"{struct_total}/10")

# Comparison chart
st.header("Score Comparison")

categories = ['Factual', 'Schema', 'Provenance', 'Hallucination', 'Readability']

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=[rag_factual/3*100, rag_schema/2*100, rag_provenance/2*100, 
       rag_hallucination/2*100, rag_readability/1*100],
    theta=categories,
    fill='toself',
    name='RAG Pipeline'
))

fig.add_trace(go.Scatterpolar(
    r=[struct_factual/3*100, struct_schema/2*100, struct_provenance/2*100,
       struct_hallucination/2*100, struct_readability/1*100],
    theta=categories,
    fill='toself',
    name='Structured Pipeline'
))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)
```

**Dependencies**: None (can work independently with mock data)

---

## TASK 4: Company Stats Visualization
**File**: `src/streamlit_app.py` or new page  
**Location**: New tab/page  
**Estimated Time**: 4 hours

### What to Add:
```python
# Add to main app as new tab
with st.tabs(["..."]):
    # ... existing tabs ...
    
    with st.tab("📈 Company Analytics"):
        st.header("Company Statistics & Trends")
        
        # Get payload data
        try:
            resp = requests.get(f"{API_BASE}/companies", timeout=5)
            companies = resp.json()
            
            # Funding visualization
            st.subheader("Funding Overview")
            funding_df = pd.DataFrame([
                {
                    'company': c['company_name'],
                    'total_raised': c.get('total_raised_usd', 0)
                }
                for c in companies
            ])
            
            import plotly.express as px
            fig = px.bar(
                funding_df.sort_values('total_raised', ascending=False).head(10),
                x='company',
                y='total_raised',
                title='Top 10 Companies by Funding'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Category distribution
            st.subheader("Category Distribution")
            category_counts = pd.DataFrame(companies)['category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index)
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Could not load analytics: {e}")
```

**Dependencies**: Need `/companies` endpoint from Backend Engineer

---

## TASK 5: Docker Testing & Integration
**File**: Test `docker/docker-compose.yml` and `docker/Dockerfile`  
**Location**: Command line testing  
**Estimated Time**: 3 hours

### What to Do:
```bash
# 1. Test local Docker build
cd docker
docker compose up --build

# 2. Verify Streamlit accessible at http://localhost:8501
# 3. Test all features in Docker environment
# 4. Check volume mounts work (data updates reflect in UI)

# 5. If issues, update docker-compose.yml:
# - Add environment variables for API_BASE
# - Fix port mappings
# - Ensure data volumes mounted correctly
```

### Potential Fixes Needed:
```yaml
# In docker-compose.yml, may need to add:
services:
  app:
    environment:
      - API_BASE=http://localhost:8000
      - STREAMLIT_SERVER_PORT=8501
```

---

## TASK 6: Demo Video Production
**File**: Create video, upload, add link to README  
**Location**: Root directory → README.md  
**Estimated Time**: 4 hours

### What to Create:
1. **Script** (1 hour):
   - Intro: Project overview (30 sec)
   - Data pipeline: Show Airflow DAGs (1 min)
   - UI demo: Company selection, dashboard generation (3 min)
   - Comparison: RAG vs Structured side-by-side (2 min)
   - Evaluation: Show scoring system (1 min)
   - Deployment: Docker/cloud deployment (1 min)
   - Outro: Learnings & future work (30 sec)

2. **Recording** (1 hour):
   - Use OBS Studio, Loom, or QuickTime
   - Screen recording with voiceover
   - Show actual working application

3. **Editing** (1.5 hours):
   - Trim unnecessary parts
   - Add captions/annotations
   - Add intro/outro slides
   - Keep under 10 minutes

4. **Upload & Link** (30 min):
   - Upload to YouTube or Vimeo
   - Update README.md with link

---

## 📦 Dependencies You Need to Install

### Add to `requirements.txt`:
```txt
# Visualization
plotly>=5.18.0
altair>=5.2.0

# Optional but recommended
pandas>=2.1.0
```

### Install:
```bash
pip install plotly altair pandas
```

---

## 🔗 Integration Points

### What You Need from Backend Engineer:
1. **API Endpoints Working**:
   - `GET /companies` → returns list of companies with metadata
   - `POST /dashboard/rag` → returns RAG-generated dashboard
   - `POST /dashboard/structured` → returns structured dashboard
   - `GET /health` → health check

2. **Response Format**:
   ```json
   {
     "markdown": "## Company Overview\n...",
     "retrieved": [...] // for RAG only
   }
   ```

3. **Error Handling**: Proper HTTP status codes (404, 500, etc.)

### What You Need from Pipeline Engineer:
1. **Data Files**:
   - `data/forbes_ai50_seed.json` → populated with 50 companies
   - `data/payloads/*.json` → at least 5 complete payloads

2. **Company ID Mapping**: Way to map company name → company_id

---

## ✅ Deliverables Checklist

- [ ] Enhanced company selection with filters
- [ ] Side-by-side dashboard comparison view
- [ ] Collapsible sections for 8 dashboard parts
- [ ] Export to Markdown functionality
- [ ] Interactive evaluation interface
- [ ] Radar chart comparison visualization
- [ ] Company analytics dashboard (funding, categories)
- [ ] Loading states & error handling
- [ ] Docker tested and working
- [ ] Demo video (≤10 mins) uploaded
- [ ] README updated with:
  - [ ] Screenshots of UI
  - [ ] Demo video link
  - [ ] How to run Streamlit
  - [ ] Feature list

---

## 🚀 Getting Started (Your First Steps)

### Day 1:
```bash
# 1. Set up environment
cd pe-dashboard-ai50
source .venv/bin/activate
pip install plotly altair pandas

# 2. Run existing Streamlit app
streamlit run src/streamlit_app.py

# 3. Test with mock data (use starter_payload.json)

# 4. Create feature branch
git checkout -b feature/ui-enhancement
```

### Day 2-3:
- Implement TASK 1 (Company selection)
- Test with mock company list

### Day 4-5:
- Implement TASK 2 (Dashboard comparison)
- Mock API responses if backend not ready

### Day 6-7:
- Implement TASK 3 (Evaluation UI)

### Day 8-9:
- Implement TASK 4 (Analytics)
- Docker testing (TASK 5)

### Day 10:
- Demo video (TASK 6)
- Final polish & documentation

---

## 💡 Tips for Success

1. **Work with Mock Data First**: Don't wait for backend/pipeline
   ```python
   # Use this if API not ready
   mock_companies = json.loads(Path("data/forbes_ai50_seed.json").read_text())
   mock_dashboard = Path("data/sample_dashboard.md").read_text()
   ```

2. **Test Incrementally**: After each task, test in browser

3. **Handle Errors Gracefully**: Always wrap API calls in try-except

4. **Make It Pretty**: Streamlit has great built-in components
   - Use `st.metric()` for numbers
   - Use `st.expander()` for collapsible content
   - Use `st.tabs()` for organization
   - Use `st.spinner()` for loading states

5. **Ask for Help**: If backend API isn't ready, ask Backend Engineer for:
   - Expected response format
   - Sample JSON response
   - Error codes

---

## 🎬 Demo Video Outline

**Total: 10 minutes**

1. **Introduction** (30 sec)
   - Project name, team, goals
   
2. **Architecture Overview** (1 min)
   - Show diagram: Scraper → Airflow → Vector DB → LLM → Dashboard
   
3. **Data Pipeline** (1 min)
   - Show Airflow UI (ask Pipeline Engineer for screenshot)
   - Explain daily refresh
   
4. **UI Walkthrough** (5 min)
   - Company selection & filters
   - Generate RAG dashboard
   - Generate Structured dashboard
   - Side-by-side comparison
   - Evaluation scoring
   - Analytics view
   
5. **Technical Deep Dive** (2 min)
   - Show code snippets
   - Explain RAG vs Structured approach
   - Show evaluation results
   
6. **Deployment** (30 sec)
   - Docker demo
   - Cloud deployment (if done)
   
7. **Conclusion** (30 sec)
   - Key learnings
   - Future improvements

---

## 📞 Communication with Team

### What to Share in Daily Standups:
- "Completed company filter UI"
- "Working on dashboard comparison view"
- "Blocked: need /companies endpoint from Backend"

### What to Ask Backend Engineer:
- "Can you provide sample JSON response for /companies?"
- "When will /dashboard/structured be ready?"
- "What error codes should I handle?"

### What to Ask Pipeline Engineer:
- "How many companies have payloads ready?"
- "What's the company_id format?"
- "Can you share sample payload for testing?"

Good luck! 🚀
