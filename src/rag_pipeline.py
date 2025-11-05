"""RAG pipeline: Vector DB retrieval → LLM → PE Dashboard."""
from typing import List, Dict
from src.llm_client import get_llm_client


def retrieve_context(company_id: str, top_k: int = 8) -> List[Dict]:
    """
    Retrieve relevant context from vector database.
    
    This function will use P1's VectorDatabase once it's ready.
    For now, it uses mock data for testing.
    
    Args:
        company_id: Company identifier
        top_k: Number of chunks to retrieve
        
    Returns:
        List of dicts with 'text', 'metadata', 'score'
    """
    try:
        # Try to import P1's vector database
        from src.vector_db import VectorDatabase
        
        print(f"  📚 Using real vector database")
        vdb = VectorDatabase()
        
        # Search for different aspects to get comprehensive context
        queries = [
            "company overview business model products",
            "funding investors valuation series",
            "leadership team CEO executives founders",
            "growth momentum hiring expansion",
            "news announcements partnerships"
        ]
        
        all_chunks = []
        seen_texts = set()
        
        for query in queries:
            try:
                chunks = vdb.search(company_id, query, k=2)
                
                for chunk in chunks:
                    text = chunk['text']
                    # Deduplicate
                    if text not in seen_texts and len(text) > 100:
                        seen_texts.add(text)
                        all_chunks.append(chunk)
                    
                    if len(all_chunks) >= top_k:
                        break
                
                if len(all_chunks) >= top_k:
                    break
                    
            except Exception as e:
                print(f"    ⚠️  Query '{query}' failed: {e}")
                continue
        
        return all_chunks[:top_k]
        
    except ImportError:
        print(f"  ⚠️  VectorDatabase not available yet, using mock data")
        return _mock_retrieve(company_id, top_k)
    
    except Exception as e:
        print(f"  ⚠️  Vector DB error: {e}, using mock data")
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
    top_k: int = 8
) -> dict:
    """
    Generate PE dashboard using RAG (retrieval-augmented generation).
    
    This is Lab 7: RAG Pipeline Dashboard.
    
    Pipeline Flow:
    1. Retrieve relevant chunks from vector database
    2. Assemble context from retrieved chunks
    3. Call LLM with context and dashboard prompt
    4. Return formatted dashboard with sources
    
    Args:
        company_id: Company identifier for vector search
        company_name: Display name (optional, auto-generated if None)
        top_k: Number of chunks to retrieve (default: 8)
        
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
    chunks = retrieve_context(company_id, top_k=top_k)
    
    if not chunks:
        return {
            "error": "No context found",
            "markdown": f"## Error\n\nNo data found for {company_name} in vector database.\n\nPlease ensure P1 has scraped and indexed this company.",
            "retrieved_chunks": [],
            "validation": {"valid": False, "error": "No data"}
        }
    
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
    return {
        "markdown": markdown,
        "retrieved_chunks": [
            {
                "text": c['text'][:300] + "..." if len(c['text']) > 300 else c['text'],
                "source": c['metadata'].get('page_type', 'unknown'),
                "source_url": c['metadata'].get('source_url', ''),
                "score": c.get('score', 0.0)
            }
            for c in chunks
        ],
        "validation": validation,
        "metadata": {
            "company_id": company_id,
            "company_name": company_name,
            "pipeline": "rag",
            "model": llm.model,
            "num_chunks": len(chunks),
            "total_context_chars": len(context),
            "output_length": len(markdown),
            "using_mock_data": True  # Will be False once vector DB integrated
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