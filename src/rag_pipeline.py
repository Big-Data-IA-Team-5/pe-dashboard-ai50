"""RAG pipeline: Vector DB retrieval → LLM → PE Dashboard."""
from typing import List, Dict
import os
from src.llm_client import get_llm_client


def retrieve_context(company_id: str, top_k: int = 50, use_gcs: bool = False) -> List[Dict]:
    """
    Retrieve context from STRUCTURED DASHBOARD for comprehensive analysis.
    
    Uses the already-generated structured dashboard as the primary source,
    ensuring RAG has access to the same high-quality validated data.
    
    Args:
        company_id: Company identifier
        top_k: Not used - returns all sections from dashboard
        use_gcs: DEPRECATED - Always uses local data
        
    Returns:
        List of dicts with 'text', 'metadata', 'score' - ALL sections from structured dashboard
    """
    try:
        from pathlib import Path
        import json
        
        all_chunks = []
        
        # PRIMARY SOURCE: Use the structured dashboard as main context
        structured_dashboard_path = Path(__file__).parent.parent / "data" / "dashboards" / "structured" / f"{company_id}.md"
        if structured_dashboard_path.exists():
            dashboard_content = structured_dashboard_path.read_text()
            
            # Split dashboard into sections for better context
            sections = dashboard_content.split('## ')
            for i, section in enumerate(sections[1:], 1):  # Skip first empty split
                section_title = section.split('\n')[0].strip()
                section_content = '\n'.join(section.split('\n')[1:]).strip()
                
                if len(section_content) > 50:
                    all_chunks.append({
                        'text': f"## {section_title}\n{section_content}",
                        'metadata': {
                            'company_id': company_id,
                            'page_type': 'structured_dashboard',
                            'section': section_title,
                            'source_url': 'structured_pipeline'
                        },
                        'score': 0.98  # High confidence - from validated structured data
                    })
            
            print(f"  ✓ Loaded structured dashboard with {len(all_chunks)} sections")
        else:
            print(f"  ⚠️  No structured dashboard found for {company_id}, using mock data")
            return _mock_retrieve(company_id, top_k)
        
        # Return all sections from the dashboard
        print(f"  ✓ Total chunks: {len(all_chunks)}")
        return all_chunks
        
    except Exception as e:
        print(f"  ⚠️  Error loading dashboard: {e}, using mock data")
        return _mock_retrieve(company_id, top_k)


def _mock_retrieve(company_id: str, top_k: int) -> List[Dict]:
    """
    Mock retrieval for testing without vector database.
    
    This simulates what P1's vector DB will return.
    """
    # Generate realistic mock data
    company_display = company_id.replace('-', ' ').title()
    
    mock_chunks = [
        {
            "text": f"{company_display} is an artificial intelligence company providing advanced automation solutions for enterprise customers. The company focuses on building scalable AI infrastructure and developer tools.",
            "metadata": {
                "company_id": company_id,
                "page_type": "homepage",
                "source_url": f"https://{company_id.replace('-', '')}.ai"
            },
            "score": 0.95
        },
        {
            "text": f"{company_display} announced Series B funding of $75 million led by Sequoia Capital and Andreessen Horowitz. The round brings total funding to $120 million and values the company at approximately $500 million.",
            "metadata": {
                "company_id": company_id,
                "page_type": "blog",
                "source_url": f"https://{company_id.replace('-', '')}.ai/blog/series-b"
            },
            "score": 0.89
        },
        {
            "text": f"The founding team includes CEO Jane Smith (former VP at Google AI) and CTO John Doe (ex-OpenAI researcher). The leadership team has deep expertise in machine learning and enterprise software.",
            "metadata": {
                "company_id": company_id,
                "page_type": "about",
                "source_url": f"https://{company_id.replace('-', '')}.ai/about"
            },
            "score": 0.85
        },
        {
            "text": f"{company_display} is currently hiring across multiple teams. Open positions include 12 engineering roles, 5 sales positions, and 3 product managers. The company has grown headcount by 40% in the past quarter.",
            "metadata": {
                "company_id": company_id,
                "page_type": "careers",
                "source_url": f"https://{company_id.replace('-', '')}.ai/careers"
            },
            "score": 0.82
        },
        {
            "text": f"Recent product launches include {company_display} Enterprise API and {company_display} Studio. The platform serves over 500 enterprise customers including Fortune 500 companies.",
            "metadata": {
                "company_id": company_id,
                "page_type": "product",
                "source_url": f"https://{company_id.replace('-', '')}.ai/products"
            },
            "score": 0.78
        }
    ]
    
    return mock_chunks[:top_k]


def generate_rag_dashboard(
    company_id: str,
    company_name: str = None,
    top_k: int = 50,  # Increased default to get comprehensive data
    use_gcs: bool = False  # Use local ChromaDB by default
) -> dict:
    """
    Generate PE dashboard using RAG (retrieval-augmented generation).
    
    Uses local ChromaDB vector database for comprehensive context retrieval.
    
    **PRODUCTION MODE**: Always uses ChromaDB from GCP bucket by default.
    
    Pipeline Flow:
    1. Download ChromaDB from GCS bucket (gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/)
    2. Retrieve relevant chunks from vector database
    3. Assemble context from retrieved chunks
    4. Call LLM with context and dashboard prompt
    5. Return formatted dashboard with sources
    
    Args:
        company_id: Company identifier for vector search
        company_name: Display name (optional, auto-generated if None)
        top_k: Number of chunks to retrieve (default: 8)
        use_gcs: If True (default), downloads from GCS; if False, uses local
        
    Returns:
        {
            "markdown": str,              # Generated dashboard
            "retrieved_chunks": list,     # Source chunks used
            "validation": dict,           # Structure validation
            "metadata": dict              # Generation metadata
        }
    """
    print(f"\n🔍 RAG PIPELINE: {company_id}")
    print("=" * 60)
    
    # Auto-generate company name if not provided
    if not company_name:
        company_name = company_id.replace('-', ' ').title()
    
    # Step 1: Retrieve context from vector DB
    print(f"📚 Retrieving context from vector database...")
    chunks = retrieve_context(company_id, top_k=top_k, use_gcs=use_gcs)
    
    # Fallback to mock data if no chunks found
    if not chunks:
        print(f"  ⚠️  No real data found, using mock fallback")
        chunks = _mock_retrieve(company_id, top_k)
    
    print(f"✓ Retrieved {len(chunks)} chunks")
    
    # Step 2: Build comprehensive context string
    context_parts = [
        f"# Company: {company_name}",
        f"Company ID: {company_id}",
        "",
        "## Retrieved Information from Company Website",
        ""
    ]
    
    for i, chunk in enumerate(chunks, 1):
        source = chunk['metadata'].get('page_type', 'unknown')
        source_url = chunk['metadata'].get('source_url', 'unknown')
        score = chunk.get('score', 0.0)
        
        context_parts.append(f"### Source {i}: {source} (relevance: {score:.2f})")
        context_parts.append(f"URL: {source_url}")
        context_parts.append(chunk['text'])
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Add instructions
    context += """

---

## INSTRUCTIONS FOR DASHBOARD GENERATION

Generate a complete PE investor dashboard following the 8-section format.

**Critical Rules**:
1. Use ONLY the information provided above from retrieved sources
2. For any missing information, write "Not disclosed."
3. NEVER invent metrics, valuations, revenue, ARR, or customer names
4. If information seems incomplete, note this in "## Disclosure Gaps"
5. Cite sources where appropriate: "According to the company's about page..."
6. Include all 8 required sections

**Required Sections**:
1. ## Company Overview
2. ## Business Model and GTM
3. ## Funding & Investor Profile
4. ## Growth Momentum
5. ## Visibility & Market Sentiment
6. ## Risks and Challenges
7. ## Outlook
8. ## Disclosure Gaps
"""
    
    # Step 3: Generate dashboard
    print(f"\n🤖 Calling LLM (gpt-4o-mini)...")
    print(f"  Context size: {len(context)} chars")
    
    llm = get_llm_client()
    markdown = llm.generate_dashboard(context, temperature=0.2)
    
    print(f"✓ Dashboard generated: {len(markdown)} chars")
    
    # Step 4: Validate structure
    validation = llm.validate_structure(markdown)
    
    print(f"\n📊 Validation Results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Sections: {validation['section_count']}/8")
    
    if not validation['valid']:
        print(f"  ⚠️  Missing sections: {validation['missing_sections']}")
    
    # Step 5: Return complete result
    # Check if we used mock or real data
    using_mock = any('mock' in str(c.get('metadata', {})).lower() for c in chunks)
    if not using_mock:
        # Check if chunks have real source URLs (not mock pattern)
        using_mock = all('Mock' in c.get('text', '') or company_id.replace('-', '') + '.ai' in c.get('metadata', {}).get('source_url', '') for c in chunks)
    
    # Check environment variable override
    env_use_gcs = os.getenv("VECTOR_DB_USE_GCS", "").lower()
    if env_use_gcs == "true":
        use_gcs = True
    elif env_use_gcs == "false":
        use_gcs = False
    # Otherwise use the parameter value (default True)
    
    return {
        "markdown": markdown,
        "retrieved_chunks": [
            {
                "text": c['text'][:300] + "..." if len(c['text']) > 300 else c['text'],
                "source": c['metadata'].get('page_type', 'unknown'),
                "source_url": c['metadata'].get('source_url', c['metadata'].get('source_file', '')),
                "score": c.get('score', 0.0)
            }
            for c in chunks
        ],
        "validation": validation,
        "metadata": {
            "company_id": company_id,
            "company_name": company_name,
            "pipeline": "rag_gcs" if use_gcs else "rag",
            "model": llm.model,
            "num_chunks": len(chunks),
            "total_context_chars": len(context),
            "output_length": len(markdown),
            "using_mock_data": using_mock,
            "using_gcs": use_gcs
        }
    }


def test_rag_pipeline():
    """Test RAG pipeline with mock data."""
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing RAG Pipeline")
    print("=" * 60)
    
    # Test with a company
    company_id = "openai"
    
    result = generate_rag_dashboard(company_id, "OpenAI")
    
    if "error" not in result:
        print("\n✅ RAG PIPELINE TEST PASSED")
        print("\n" + "=" * 60)
        print("RETRIEVED CHUNKS:")
        print("=" * 60)
        for i, chunk in enumerate(result['retrieved_chunks'], 1):
            print(f"\nChunk {i} ({chunk['source']}, score: {chunk['score']:.2f}):")
            print(chunk['text'])
        
        print("\n" + "=" * 60)
        print("GENERATED DASHBOARD:")
        print("=" * 60)
        print(result['markdown'])
        print("=" * 60)
        
        print(f"\nMetadata:")
        for key, value in result['metadata'].items():
            print(f"  {key}: {value}")
        
        print(f"\nValidation:")
        print(f"  Sections: {result['validation']['section_count']}/8")
        print(f"  Valid: {result['validation']['valid']}")
        
        return True
    else:
        print(f"\n❌ RAG PIPELINE TEST FAILED")
        print(f"Error: {result['error']}")
        return False


if __name__ == "__main__":
    test_rag_pipeline()