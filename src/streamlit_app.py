# import streamlit as st
# import requests

# API_BASE = "http://localhost:8000"

# st.set_page_config(page_title="PE Dashboard (AI 50)", layout="wide")
# st.title("Project ORBIT – PE Dashboard for Forbes AI 50")

# try:
#     companies = requests.get(f"{API_BASE}/companies", timeout=5).json()
# except Exception:
#     companies = []

# names = [c["company_name"] for c in companies] if companies else ["ExampleAI"]
# choice = st.selectbox("Select company", names)

# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("Structured pipeline")
#     if st.button("Generate (Structured)"):
#         resp = requests.post(f"{API_BASE}/dashboard/structured", params={"company_id": "00000000-0000-0000-0000-000000000000"})
#         st.markdown(resp.json()["markdown"])

# with col2:
#     st.subheader("RAG pipeline")
#     if st.button("Generate (RAG)"):
#         resp = requests.post(f"{API_BASE}/dashboard/rag", params={"company_name": choice})
#         st.markdown(resp.json()["markdown"])
#         with st.expander("Retrieved context"):
#             st.json(resp.json()["retrieved"])



"""
PE Company Dashboard - Streamlit Frontend
Integrated with FastAPI backend and Pydantic models
"""

import streamlit as st
import json
import requests
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

import os

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")  # Use localhost by default, Docker service name in containers
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

st.set_page_config(
    page_title="PE Dashboard - Forbes AI 50",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .success-box {
        padding: 15px;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 10px 0;
    }
    .warning-box {
        padding: 15px;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        padding: 15px;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_company_id' not in st.session_state:
    st.session_state.current_company_id = None
if 'generated_structured' not in st.session_state:
    st.session_state.generated_structured = None
if 'generated_rag' not in st.session_state:
    st.session_state.generated_rag = None
if 'comparison_result' not in st.session_state:
    st.session_state.comparison_result = None

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def check_api_health():
    """Check if API is accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_companies_list():
    """Fetch list of companies from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/companies", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching companies: {e}")
        return None

def generate_structured_dashboard(company_id: str):
    """Generate dashboard using structured pipeline."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/dashboard/structured",
            params={"company_id": company_id},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def generate_rag_dashboard(company_id: str, company_name: str = None, use_gcs: bool = True):
    """Generate dashboard using RAG pipeline with GCS by default."""
    try:
        params = {
            "company_id": company_id,
            "use_gcs": use_gcs  # Always send use_gcs parameter
        }
        if company_name:
            params["company_name"] = company_name
        
        response = requests.post(
            f"{API_BASE_URL}/dashboard/rag",
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def compare_dashboards(company_id: str):
    """Compare both pipeline outputs."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/compare",
            params={"company_id": company_id},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-header">🏢 Project ORBIT - PE Dashboard Factory</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Automated PE Intelligence for Forbes AI 50</div>', unsafe_allow_html=True)

# API Status
api_healthy = check_api_health()
if api_healthy:
    st.success("✅ API Connected")
else:
    st.error("⚠️ API Unavailable - Make sure the FastAPI backend is running")
    st.stop()

# ============================================================
# SIDEBAR - NAVIGATION
# ============================================================

st.sidebar.header("📋 Navigation")

page = st.sidebar.radio(
    "Select Page:",
    [
        "🏠 Home & Overview",
        "📊 Generate Dashboards",
        "🔬 Compare Pipelines",
        "📈 System Statistics"
    ]
)

st.sidebar.markdown("---")

# Company selector (shown on all pages except home)
if page != "🏠 Home & Overview":
    st.sidebar.subheader("🎯 Company Selection")
    
    companies_data = get_companies_list()
    
    if companies_data and companies_data.get('companies'):
        companies = companies_data['companies']
        company_names = [c.get('company_name', 'Unknown') for c in companies]
        
        selected_name = st.sidebar.selectbox(
            "Select Company:",
            company_names,
            index=0
        )
        
        # Get company_id for selected company
        selected_company = next((c for c in companies if c.get('company_name') == selected_name), None)
        if selected_company:
            st.session_state.current_company_id = selected_company.get('company_id', '00000000-0000-0000-0000-000000000000')
            
            # Show company info
            with st.sidebar.expander("ℹ️ Company Info"):
                st.write(f"**ID:** {st.session_state.current_company_id}")
                if selected_company.get('website'):
                    st.write(f"**Website:** {selected_company['website']}")
                if selected_company.get('hq_city'):
                    st.write(f"**Location:** {selected_company['hq_city']}, {selected_company.get('hq_country', '')}")
    else:
        st.sidebar.warning("No companies found. Using default.")
        st.session_state.current_company_id = "00000000-0000-0000-0000-000000000000"

st.sidebar.markdown("---")
st.sidebar.caption("PE Dashboard Factory v1.0")
st.sidebar.caption(f"[API Docs]({API_BASE_URL}/docs)")

# ============================================================
# PAGE: HOME & OVERVIEW
# ============================================================

if page == "🏠 Home & Overview":
    st.header("Welcome to Project ORBIT")
    
    st.markdown("""
    ### 🎯 Mission
    Automated generation of investor-facing PE diligence dashboards for Forbes AI 50 companies.
    
    ### 🔄 Two-Pipeline Architecture
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📊 Structured Pipeline
        - **Input:** Pydantic-validated JSON payload
        - **Process:** Direct data → LLM formatting
        - **Strength:** High accuracy, strong structure
        - **Use Case:** When structured data is available
        
        **Pipeline Flow:**
        ```
        Payload JSON
           ↓
        Pydantic Validation
           ↓
        JSON Context
           ↓
        LLM (GPT-4o-mini)
           ↓
        Markdown Dashboard
        ```
        """)
    
    with col2:
        st.markdown("""
        #### 🔍 RAG Pipeline
        - **Input:** Vector DB retrieval from scraped data
        - **Process:** Search → Context assembly → LLM
        - **Strength:** Works with raw unstructured data
        - **Use Case:** When only web scrapes available
        
        **Pipeline Flow:**
        ```
        Vector Database
           ↓
        Semantic Search
           ↓
        Retrieved Chunks
           ↓
        LLM (GPT-4o-mini)
           ↓
        Markdown Dashboard
        ```
        """)
    
    st.markdown("---")
    
    # System Status
    st.subheader("📊 System Status")
    
    try:
        stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Companies",
                    stats.get('total_companies', 0)
                )
            
            with col2:
                st.metric(
                    "Scraped",
                    stats.get('companies_scraped', 0),
                    delta=stats.get('scraping_completion', '0%')
                )
            
            with col3:
                st.metric(
                    "With Payloads",
                    stats.get('companies_with_payloads', 0),
                    delta=stats.get('extraction_completion', '0%')
                )
            
            with col4:
                pipelines = stats.get('pipelines_available', {})
                available = sum(pipelines.values())
                st.metric(
                    "Pipelines Ready",
                    f"{available}/2"
                )
    except Exception as e:
        st.error(f"Could not fetch system stats: {e}")
    
    st.markdown("---")
    
    # Quick Start
    st.subheader("🚀 Quick Start Guide")
    
    st.markdown("""
    1. **Select a company** from the sidebar
    2. **Generate dashboards** using one or both pipelines
    3. **Compare results** to evaluate pipeline performance
    4. **Download** generated dashboards as Markdown files
    
    ### 📋 Dashboard Format (8 Required Sections)
    
    All dashboards follow the PE standard format:
    1. Company Overview
    2. Business Model and GTM
    3. Funding & Investor Profile
    4. Growth Momentum
    5. Visibility & Market Sentiment
    6. Risks and Challenges
    7. Outlook
    8. Disclosure Gaps
    """)

# ============================================================
# PAGE: GENERATE DASHBOARDS
# ============================================================

elif page == "📊 Generate Dashboards":
    st.header("Generate PE Dashboards")
    
    if not st.session_state.current_company_id:
        st.warning("Please select a company from the sidebar")
        st.stop()
    
    company_id = st.session_state.current_company_id
    
    st.markdown(f"**Selected Company ID:** `{company_id}`")
    st.markdown("---")
    
    # Two columns for two pipelines
    col1, col2 = st.columns(2)
    
    # ============================================================
    # STRUCTURED PIPELINE
    # ============================================================
    with col1:
        st.subheader("📊 Structured Pipeline")
        st.markdown("Generates dashboard from validated Pydantic payload")
        
        if st.button("🚀 Generate (Structured)", use_container_width=True, type="primary"):
            with st.spinner("Generating structured dashboard..."):
                result = generate_structured_dashboard(company_id)
                
                if result:
                    st.session_state.generated_structured = result
                    st.success("✅ Structured dashboard generated!")
                    st.rerun()
        
        # Display result if available
        if st.session_state.generated_structured:
            result = st.session_state.generated_structured
            
            st.markdown("#### Results")
            
            # Metadata
            with st.expander("📊 Metadata & Validation"):
                metadata = result.get('metadata', {})
                validation = result.get('validation', {})
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Model", metadata.get('model', 'N/A'))
                    st.metric("Events", metadata.get('num_events', 0))
                    st.metric("Products", metadata.get('num_products', 0))
                
                with col_b:
                    st.metric("Sections", f"{validation.get('section_count', 0)}/8")
                    st.metric("Leadership", metadata.get('num_leadership', 0))
                    st.metric("Snapshots", metadata.get('num_snapshots', 0))
                
                if not validation.get('valid', False):
                    st.warning(f"Missing sections: {validation.get('missing_sections', [])}")
            
            # Display dashboard
            with st.expander("📄 Generated Dashboard", expanded=True):
                markdown = result.get('markdown', '')
                st.markdown(markdown)
                
                # Download button
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown,
                    file_name=f"structured_{company_id}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
    
    # ============================================================
    # RAG PIPELINE
    # ============================================================
    with col2:
        st.subheader("🔍 RAG Pipeline")
        st.markdown("Generates dashboard from vector DB retrieval")
        
        if st.button("🚀 Generate (RAG)", use_container_width=True, type="primary"):
            with st.spinner("Generating RAG dashboard..."):
                result = generate_rag_dashboard(company_id, use_gcs=False)
                
                if result:
                    st.session_state.generated_rag = result
                    st.success("✅ RAG dashboard generated!")
                    st.rerun()
        
        # Display result if available
        if st.session_state.generated_rag:
            result = st.session_state.generated_rag
            
            st.markdown("#### Results")
            
            # Metadata
            with st.expander("📊 Metadata & Context"):
                metadata = result.get('metadata', {})
                validation = result.get('validation', {})
                chunks = result.get('retrieved_chunks', [])
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Model", metadata.get('model', 'N/A'))
                    st.metric("Chunks Retrieved", metadata.get('num_chunks', 0))
                    st.metric("Context Size", f"{metadata.get('total_context_chars', 0):,} chars")
                
                with col_b:
                    st.metric("Sections", f"{validation.get('section_count', 0)}/8")
                    st.metric("Output Length", f"{metadata.get('output_length', 0):,} chars")
                    mock_status = "⚠️ Mock" if metadata.get('using_mock_data') else "✅ Real"
                    st.metric("Data Source", mock_status)
                    gcs_status = "🌐 GCS" if metadata.get('using_gcs') else "📂 Local"
                    st.metric("Vector DB", gcs_status)
                
                # Show retrieved chunks
                if chunks:
                    st.markdown("**Retrieved Context:**")
                    for i, chunk in enumerate(chunks, 1):
                        st.markdown(f"**Chunk {i}**: {chunk.get('source', 'unknown')} (score: {chunk.get('score', 0):.2f})")
                        st.text_area(f"chunk_{i}", chunk.get('text', ''), height=100, label_visibility="collapsed")
                        if chunk.get('source_url'):
                            st.caption(f"Source: {chunk['source_url']}")
                        st.markdown("---")
            
            # Display dashboard
            with st.expander("📄 Generated Dashboard", expanded=True):
                markdown = result.get('markdown', '')
                st.markdown(markdown)
                
                # Download button
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown,
                    file_name=f"rag_{company_id}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

# ============================================================
# PAGE: COMPARE PIPELINES
# ============================================================

elif page == "🔬 Compare Pipelines":
    st.header("Pipeline Comparison")
    
    if not st.session_state.current_company_id:
        st.warning("Please select a company from the sidebar")
        st.stop()
    
    company_id = st.session_state.current_company_id
    
    st.markdown(f"**Selected Company ID:** `{company_id}`")
    st.markdown("---")
    
    st.info("""
    **Comparison Process:**
    - Generates dashboards from both pipelines
    - Evaluates based on rubric (factual, schema, provenance, hallucination, readability)
    - Provides side-by-side comparison and winner determination
    """)
    
    if st.button("🔬 Run Comparison", use_container_width=True, type="primary"):
        with st.spinner("Running comparison... This may take 30-60 seconds"):
            result = compare_dashboards(company_id)
            
            if result:
                st.session_state.comparison_result = result
                st.success("✅ Comparison complete!")
                st.rerun()
    
    # Display comparison results
    if st.session_state.comparison_result:
        result = st.session_state.comparison_result
        
        company_name = result.get('company_name', company_id)
        st.subheader(f"Results: {company_name}")
        
        # Winner announcement - get from comparison object
        comparison = result.get('comparison', {})
        winner = comparison.get('winner', result.get('winner', 'unknown'))
        difference = comparison.get('difference', result.get('difference', 0))
        
        if winner == 'structured':
            st.success(f"🏆 **Winner: Structured Pipeline** (by {difference} points)")
        else:
            st.success(f"🏆 **Winner: RAG Pipeline** (by {difference} points)")
        
        st.markdown("---")
        
        # Scores comparison
        st.subheader("📊 Rubric Scores")
        
        # Extract scores from comparison object
        comparison = result.get('comparison', {})
        rag_scores = comparison.get('rag', {})
        struct_scores = comparison.get('structured', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔍 RAG Pipeline")
            st.metric("Total Score", f"{rag_scores.get('total', 0)}/10")
            st.write(f"- Factual: {rag_scores.get('factual', 0)}/3")
            st.write(f"- Schema: {rag_scores.get('schema', 0)}/2")
            st.write(f"- Provenance: {rag_scores.get('provenance', 0)}/2")
            st.write(f"- Hallucination: {rag_scores.get('hallucination', 0)}/2")
            st.write(f"- Readability: {rag_scores.get('readability', 0)}/1")
            
            strengths = result.get('rag_strengths', [])
            if strengths:
                st.success(f"**Strengths:** {', '.join(strengths)}")
        
        with col2:
            st.markdown("### 📊 Structured Pipeline")
            st.metric("Total Score", f"{struct_scores.get('total', 0)}/10")
            st.write(f"- Factual: {struct_scores.get('factual', 0)}/3")
            st.write(f"- Schema: {struct_scores.get('schema', 0)}/2")
            st.write(f"- Provenance: {struct_scores.get('provenance', 0)}/2")
            st.write(f"- Hallucination: {struct_scores.get('hallucination', 0)}/2")
            st.write(f"- Readability: {struct_scores.get('readability', 0)}/1")
            
            strengths = result.get('structured_strengths', [])
            if strengths:
                st.success(f"**Strengths:** {', '.join(strengths)}")
        
        st.markdown("---")
        
        # Side-by-side dashboards
        st.subheader("📄 Side-by-Side Comparison")
        
        tab1, tab2 = st.tabs(["🔍 RAG Dashboard", "📊 Structured Dashboard"])
        
        with tab1:
            rag_markdown = result.get('rag_dashboard', '')
            st.markdown(rag_markdown)
            
            st.download_button(
                label="📥 Download RAG Dashboard",
                data=rag_markdown,
                file_name=f"rag_{company_id}_comparison.md",
                mime="text/markdown"
            )
        
        with tab2:
            struct_markdown = result.get('structured_dashboard', '')
            st.markdown(struct_markdown)
            
            st.download_button(
                label="📥 Download Structured Dashboard",
                data=struct_markdown,
                file_name=f"structured_{company_id}_comparison.md",
                mime="text/markdown"
            )

# ============================================================
# PAGE: SYSTEM STATISTICS
# ============================================================

elif page == "📈 System Statistics":
    st.header("System Statistics & Data Status")
    
    try:
        # Get companies list
        companies_data = get_companies_list()
        
        if companies_data:
            companies = companies_data.get('companies', [])
            data_status = companies_data.get('data_status', {})
            
            st.subheader("📊 Overview")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Companies",
                    data_status.get('total_companies', 0)
                )
            
            with col2:
                st.metric(
                    "With Structured Data",
                    data_status.get('with_structured_data', 0)
                )
            
            with col3:
                st.metric(
                    "Completion Rate",
                    data_status.get('completion_rate', '0%')
                )
            
            st.markdown("---")
            
            # Companies table
            st.subheader("📋 Companies List")
            
            # Convert to display format
            display_data = []
            for company in companies:
                display_data.append({
                    'Company': company.get('company_name', 'Unknown'),
                    'Website': company.get('website', 'N/A'),
                    'Location': f"{company.get('hq_city', 'N/A')}, {company.get('hq_country', 'N/A')}",
                    'Has Payload': '✅' if company.get('has_payload') else '❌',
                    'Has Vector Data': '✅' if company.get('has_vector_data') else '❌'
                })
            
            st.dataframe(display_data, use_container_width=True)
            
            st.markdown("---")
            
            # System stats
            st.subheader("🔧 System Details")
            
            stats_response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Data Processing")
                    st.write(f"- Scraped: {stats.get('companies_scraped', 0)}")
                    st.write(f"- With Payloads: {stats.get('companies_with_payloads', 0)}")
                    st.write(f"- Scraping: {stats.get('scraping_completion', '0%')}")
                    st.write(f"- Extraction: {stats.get('extraction_completion', '0%')}")
                
                with col2:
                    st.markdown("#### Pipeline Status")
                    pipelines = stats.get('pipelines_available', {})
                    st.write(f"- Structured: {'✅' if pipelines.get('structured') else '❌'}")
                    st.write(f"- RAG: {'✅' if pipelines.get('rag') else '❌'}")
        
        else:
            st.error("Could not fetch statistics from API")
    
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# Footer
st.markdown("---")
st.caption("Project ORBIT - PE Dashboard Factory | Built with Streamlit + FastAPI")