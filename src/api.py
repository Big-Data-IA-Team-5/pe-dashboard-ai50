"""FastAPI endpoints for PE Dashboard Factory."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import List
import json

from src.structured_pipeline import generate_structured_dashboard, load_payload
from src.models import Payload


app = FastAPI(
    title="PE Dashboard Factory API",
    description="Automated PE intelligence for Forbes AI 50",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "service": "PE Dashboard Factory",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "companies": "/companies",
            "structured_dashboard": "/dashboard/structured?company_id={id}",
            "rag_dashboard": "/dashboard/rag?company_id={id}",
            "compare": "/compare?company_id={id}",
            "metadata": "/company/{company_id}/metadata"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "PE Dashboard Factory",
        "pipeline_status": {
            "structured": "operational",
            "rag": "operational"
        }
    }


@app.get("/companies")
def list_companies():
    """
    Get list of all Forbes AI 50 companies with metadata.
    
    Returns:
        {
            "companies": [...],
            "count": int,
            "data_status": {...}
        }
    """
    # Load from seed file
    seed_path = Path("data/forbes_ai50_seed.json")
    
    if not seed_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Forbes AI 50 seed data not found. P1 needs to create data/forbes_ai50_seed.json"
        )
    
    try:
        companies = json.loads(seed_path.read_text())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading seed data: {str(e)}"
        )
    
    # Check payload availability for each company
    payload_dir = Path("data/payloads")
    
    for company in companies:
        company_id = company.get("company_id", "")
        payload_path = payload_dir / f"{company_id}.json"
        company["has_payload"] = payload_path.exists()
        company["has_vector_data"] = True  # Assume yes if scraped
    
    # Calculate stats
    total = len(companies)
    with_payloads = sum(1 for c in companies if c.get("has_payload", False))
    
    return {
        "companies": companies,
        "count": total,
        "data_status": {
            "total_companies": total,
            "with_structured_data": with_payloads,
            "completion_rate": f"{with_payloads/total*100:.1f}%" if total > 0 else "0%"
        }
    }


@app.post("/rag/search")
def rag_search_endpoint(company_id: str, query: str, top_k: int = 5):
    """
    Test RAG retrieval for a company.
    
    Lab 4 checkpoint: Test vector DB search.
    
    Args:
        company_id: Company identifier
        query: Search query (e.g., "funding", "leadership")
        top_k: Number of results
        
    Returns:
        Retrieved chunks
    """
    from src.rag_pipeline import retrieve_context
    
    chunks = retrieve_context(company_id, top_k)
    
    return {
        "company_id": company_id,
        "query": query,
        "results": chunks,
        "count": len(chunks)
    }
@app.post("/dashboard/structured")
def dashboard_structured_endpoint(
    company_id: str = "00000000-0000-0000-0000-000000000000"
):
    """
    Generate PE dashboard using structured Pydantic payload.
    
    Lab 8: Structured Pipeline Dashboard
    
    Pipeline: Payload JSON → Pydantic Validation → LLM → Markdown Dashboard
    
    Args:
        company_id: Company UUID from payload filename (default: starter payload)
        
    Returns:
        {
            "company_id": str,
            "method": "structured",
            "markdown": str,
            "validation": dict,
            "metadata": dict,
            "payload_summary": dict
        }
    """
    result = generate_structured_dashboard(company_id)
    
    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )
    
    return {
        "company_id": company_id,
        "method": "structured",
        "markdown": result["markdown"],
        "validation": result["validation"],
        "metadata": result["metadata"],
        "payload_summary": {
            "company_name": result["payload"]["company_record"]["legal_name"],
            "total_events": len(result["payload"]["events"]),
            "total_products": len(result["payload"]["products"]),
            "total_leadership": len(result["payload"]["leadership"]),
            "has_snapshots": len(result["payload"]["snapshots"]) > 0
        }
    }


@app.post("/dashboard/rag")
def dashboard_rag_endpoint(
    company_id: str,
    company_name: str = None,
    top_k: int = 8
):
    """
    Generate PE dashboard using RAG (retrieval-augmented generation).
    
    Lab 7: RAG Pipeline Dashboard
    
    Pipeline: Vector DB Retrieval → Context Assembly → LLM → Markdown Dashboard
    
    Args:
        company_id: Company identifier (e.g., 'openai')
        company_name: Display name (optional, auto-generated if not provided)
        top_k: Number of chunks to retrieve from vector DB (default: 8)
        
    Returns:
        {
            "company_id": str,
            "method": "rag",
            "markdown": str,
            "validation": dict,
            "retrieved_chunks": list,
            "metadata": dict
        }
    """
    from src.rag_pipeline import generate_rag_dashboard
    
    result = generate_rag_dashboard(company_id, company_name, top_k)
    
    if "error" in result:
        raise HTTPException(
            status_code=404,
            detail=result["error"]
        )
    
    return {
        "company_id": company_id,
        "method": "rag",
        "markdown": result["markdown"],
        "validation": result["validation"],
        "retrieved_chunks": result["retrieved_chunks"],
        "metadata": result["metadata"]
    }


@app.get("/company/{company_id}/metadata")
def get_company_metadata(company_id: str):
    """
    Get metadata about a specific company's data availability.
    
    Args:
        company_id: Company identifier
        
    Returns:
        Company metadata and data quality metrics
    """
    payload = load_payload(company_id)
    
    if not payload:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for company: {company_id}"
        )
    
    return {
        "company_id": company_id,
        "company_name": payload.company_record.legal_name,
        "website": payload.company_record.website,
        "headquarters": payload.company_record.headquarters,
        "founded_year": payload.company_record.founded_year,
        "categories": payload.company_record.categories,
        "has_structured": True,
        "has_rag": True,
        "last_updated": payload.company_record.as_of,
        "data_quality": {
            "num_events": len(payload.events),
            "num_snapshots": len(payload.snapshots),
            "num_products": len(payload.products),
            "num_leadership": len(payload.leadership),
            "has_visibility": len(payload.visibility) > 0,
            "completeness_score": calculate_completeness(payload)
        }
    }


@app.post("/compare")
def compare_dashboards_endpoint(company_id: str):
    """
    Generate and compare both RAG and Structured dashboards for a company.
    
    Args:
        company_id: Company identifier
        
    Returns:
        Both dashboards plus comparison scores
    """
    from src.rag_pipeline import generate_rag_dashboard
    from src.evaluator import compare_dashboards
    
    # Generate both dashboards
    rag_result = generate_rag_dashboard(company_id)
    struct_result = generate_structured_dashboard(company_id)
    
    # Check for errors
    if "error" in rag_result or "error" in struct_result:
        errors = []
        if "error" in rag_result:
            errors.append(f"RAG: {rag_result['error']}")
        if "error" in struct_result:
            errors.append(f"Structured: {struct_result['error']}")
        
        raise HTTPException(
            status_code=404,
            detail=f"Cannot generate comparison. Errors: {'; '.join(errors)}"
        )
    
    # Get company name
    company_name = struct_result['metadata'].get('company_name', company_id)
    
    # Compare dashboards
    comparison = compare_dashboards(
        rag_result["markdown"],
        struct_result["markdown"],
        company_name
    )
    
    return {
        "company_id": company_id,
        "company_name": company_name,
        "rag_dashboard": rag_result["markdown"],
        "structured_dashboard": struct_result["markdown"],
        "rag_metadata": rag_result["metadata"],
        "structured_metadata": struct_result["metadata"],
        "comparison": comparison,
        "winner": comparison["winner"]
    }


def calculate_completeness(payload: Payload) -> float:
    """
    Calculate data completeness score (0-100).
    
    Args:
        payload: Company payload
        
    Returns:
        Completeness percentage
    """
    score = 0
    max_score = 10
    
    # Company basic info (2 points)
    if payload.company_record.legal_name:
        score += 1
    if payload.company_record.headquarters:
        score += 1
    
    # Events/Funding (2 points)
    if len(payload.events) > 0:
        score += 1
    if len(payload.events) >= 3:
        score += 1
    
    # Products (2 points)
    if len(payload.products) > 0:
        score += 1
    if len(payload.products) >= 2:
        score += 1
    
    # Leadership (2 points)
    if len(payload.leadership) > 0:
        score += 1
    if len(payload.leadership) >= 2:
        score += 1
    
    # Snapshots (1 point)
    if len(payload.snapshots) > 0:
        score += 1
    
    # Visibility (1 point)
    if len(payload.visibility) > 0:
        score += 1
    
    return (score / max_score) * 100


@app.get("/stats")
def get_statistics():
    """
    Get overall system statistics.
    
    Returns:
        Statistics about data processing and availability
    """
    # Count files
    payload_dir = Path("data/payloads")
    raw_dir = Path("data/raw")
    
    payload_count = len(list(payload_dir.glob("*.json"))) if payload_dir.exists() else 0
    scraped_count = len(list(raw_dir.iterdir())) if raw_dir.exists() else 0
    
    # Load seed for total count
    seed_path = Path("data/forbes_ai50_seed.json")
    total_companies = 0
    if seed_path.exists():
        companies = json.loads(seed_path.read_text())
        total_companies = len(companies)
    
    return {
        "total_companies": total_companies,
        "companies_scraped": scraped_count,
        "companies_with_payloads": payload_count,
        "scraping_completion": f"{scraped_count/total_companies*100:.1f}%" if total_companies > 0 else "0%",
        "extraction_completion": f"{payload_count/total_companies*100:.1f}%" if total_companies > 0 else "0%",
        "pipelines_available": {
            "structured": payload_count > 0,
            "rag": scraped_count > 0
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)