# Backend Engineer - Task Guide
**Role**: FastAPI, LLM Integration, Dashboard Generation  
**Your Responsibility**: 33% of the project

---

## 📂 Current Folder Structure (What You Have)

```
pe-dashboard-ai50/
├── src/
│   ├── api.py                    ✅ Basic FastAPI skeleton EXISTS
│   ├── models.py                 ✅ Complete Pydantic models (READY)
│   ├── structured_pipeline.py    ✅ Load function exists
│   ├── rag_pipeline.py          ✅ Stub function exists
│   ├── evaluator.py             ✅ Simple scoring function
│   └── prompts/
│       └── dashboard_system.md   ✅ Complete LLM prompt (READY)
├── PE_Dashboard.md               ✅ Detailed prompt instructions
├── data/
│   ├── starter_payload.json      ✅ Example payload for testing
│   ├── sample_dashboard.md       ✅ Example output
│   └── payloads/                 🔴 Pipeline Engineer will create
├── docker/
│   ├── Dockerfile                ✅ Ready to use
│   └── docker-compose.yml        ✅ Ready to use
└── requirements.txt              🟡 Need to add: openai, instructor
```

---

## 🎯 Your Tasks & What's Left to Do

### ✅ What You Already Have (Starter Code)

**File: `src/api.py`** - Basic FastAPI with stubs:
- `GET /health` ✅ Working
- `GET /companies` ✅ Reads forbes_ai50_seed.json
- `POST /dashboard/structured` 🔴 Returns hardcoded text (YOU NEED TO FIX)
- `POST /dashboard/rag` 🔴 Returns hardcoded text (YOU NEED TO FIX)

**File: `src/models.py`** ✅ Complete (DON'T MODIFY):
- All Pydantic models ready: Company, Event, Snapshot, Product, Leadership, Visibility, Payload

**File: `src/prompts/dashboard_system.md`** ✅ Complete prompt template

---

## 🔴 What You Need to Build

## TASK 1: LLM Client Setup
**File**: Create new file `src/llm_client.py`  
**Location**: New file in `src/`  
**Estimated Time**: 3 hours

### What to Create:
```python
# src/llm_client.py
import os
from pathlib import Path
from typing import Optional
import openai
from openai import OpenAI

class LLMClient:
    """Wrapper for LLM API calls with retry logic and error handling."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for cheaper option
        
        # Load system prompt
        prompt_path = Path(__file__).parent / "prompts" / "dashboard_system.md"
        self.system_prompt = prompt_path.read_text()
    
    def generate_dashboard(
        self,
        context: str,
        max_tokens: int = 4000,
        temperature: float = 0.3
    ) -> str:
        """
        Generate PE dashboard from context.
        
        Args:
            context: Either JSON payload (structured) or retrieved text (RAG)
            max_tokens: Max tokens in response
            temperature: 0.0-1.0, lower = more deterministic
            
        Returns:
            Markdown dashboard string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Generate dashboard for:\n\n{context}"}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            return "Error: OpenAI rate limit exceeded. Please try again later."
        except openai.APIError as e:
            return f"Error: OpenAI API error - {str(e)}"
        except Exception as e:
            return f"Error generating dashboard: {str(e)}"
    
    def validate_dashboard_structure(self, markdown: str) -> dict:
        """
        Validate that dashboard has all 8 required sections.
        
        Returns:
            {
                "valid": bool,
                "missing_sections": list,
                "has_disclosure_gaps": bool
            }
        """
        required_sections = [
            "## Company Overview",
            "## Business Model and GTM",
            "## Funding & Investor Profile",
            "## Growth Momentum",
            "## Visibility & Market Sentiment",
            "## Risks and Challenges",
            "## Outlook",
            "## Disclosure Gaps"
        ]
        
        missing = [s for s in required_sections if s not in markdown]
        
        return {
            "valid": len(missing) == 0,
            "missing_sections": missing,
            "has_disclosure_gaps": "## Disclosure Gaps" in markdown
        }


# Singleton instance
_llm_client: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    """Get or create LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
```

### Environment Setup:
```bash
# Create .env file in project root
cat > .env << EOF
OPENAI_API_KEY=sk-your-key-here
EOF

# Add to .gitignore
echo ".env" >> .gitignore
```

### Add to `requirements.txt`:
```txt
openai>=1.12.0
python-dotenv>=1.0.0
```

### Install:
```bash
pip install openai python-dotenv
```

**Dependencies**: None (can work independently)

---

## TASK 2: Structured Pipeline Dashboard (Lab 8)
**File**: `src/structured_pipeline.py` and `src/api.py`  
**Location**: Enhance existing functions  
**Estimated Time**: 5 hours

### Step 1: Update `src/structured_pipeline.py`
```python
from pathlib import Path
from typing import Optional
import json
from .models import Payload
from .llm_client import get_llm_client

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "payloads"

def load_payload(company_id: str) -> Optional[Payload]:
    """Load payload from file."""
    fp = DATA_DIR / f"{company_id}.json"
    if not fp.exists():
        # fallback to starter
        starter = Path(__file__).resolve().parents[1] / "data" / "starter_payload.json"
        if starter.exists():
            return Payload.model_validate_json(starter.read_text())
        return None
    return Payload.model_validate_json(fp.read_text())


def generate_structured_dashboard(company_id: str) -> dict:
    """
    Generate dashboard using structured payload.
    
    Returns:
        {
            "markdown": str,
            "payload": dict,
            "validation": dict
        }
    """
    # Load payload
    payload = load_payload(company_id)
    if not payload:
        return {
            "error": "Payload not found",
            "markdown": "## Error\nPayload not found for this company.",
            "payload": None,
            "validation": {"valid": False}
        }
    
    # Convert payload to formatted JSON string for LLM
    payload_dict = payload.model_dump(mode='json')
    payload_json = json.dumps(payload_dict, indent=2)
    
    # Prepare context for LLM
    context = f"""Here is the structured data payload for the company:

```json
{payload_json}
```

Generate a complete PE dashboard following the 8-section format.
Use ONLY the data provided in this payload.
For any missing information, write "Not disclosed."
"""
    
    # Generate dashboard
    llm = get_llm_client()
    markdown = llm.generate_dashboard(context)
    
    # Validate structure
    validation = llm.validate_dashboard_structure(markdown)
    
    return {
        "markdown": markdown,
        "payload": payload_dict,
        "validation": validation
    }
```

### Step 2: Update `src/api.py`
```python
# Replace the existing /dashboard/structured endpoint

@app.post("/dashboard/structured")
def dashboard_structured(company_id: str = "00000000-0000-0000-0000-000000000000"):
    """Generate dashboard using structured Pydantic payload."""
    from .structured_pipeline import generate_structured_dashboard
    
    result = generate_structured_dashboard(company_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "company_id": company_id,
        "method": "structured",
        "markdown": result["markdown"],
        "validation": result["validation"],
        "payload_preview": {
            "company_name": result["payload"]["company_record"]["legal_name"],
            "total_events": len(result["payload"]["events"]),
            "total_snapshots": len(result["payload"]["snapshots"])
        }
    }
```

**Dependencies**: Need Pipeline Engineer to create payloads in `data/payloads/`

**Testing**:
```bash
# Test with starter payload
curl -X POST "http://localhost:8000/dashboard/structured?company_id=00000000-0000-0000-0000-000000000000"
```

---

## TASK 3: RAG Pipeline Dashboard (Lab 7)
**File**: `src/rag_pipeline.py` and `src/api.py`  
**Location**: Enhance existing functions  
**Estimated Time**: 6 hours

### Step 1: Update `src/rag_pipeline.py`
```python
from typing import List, Dict
from .llm_client import get_llm_client

def retrieve_context(company_name: str, top_k: int = 5) -> List[Dict]:
    """
    Retrieve relevant context from vector DB.
    
    This is a PLACEHOLDER - Pipeline Engineer will implement real vector DB.
    For now, return mock data.
    
    Args:
        company_name: Company to search for
        top_k: Number of chunks to retrieve
        
    Returns:
        List of dicts with 'source_url', 'text', 'score'
    """
    # TODO: Replace with real vector DB retrieval
    # This will be provided by Pipeline Engineer's vector_db.py
    
    # For now, return mock data
    return [
        {
            "source_url": f"https://{company_name.lower().replace(' ', '')}.ai/about",
            "text": f"{company_name} is an AI company providing automation tooling for enterprise customers.",
            "score": 0.95
        },
        {
            "source_url": f"https://{company_name.lower().replace(' ', '')}.ai/blog/funding",
            "text": f"{company_name} announced Series B funding of $50M led by Sequoia Capital.",
            "score": 0.89
        },
        {
            "source_url": f"https://{company_name.lower().replace(' ', '')}.ai/careers",
            "text": f"{company_name} is hiring across engineering and sales. Current openings: 18 roles.",
            "score": 0.82
        }
    ]


def generate_rag_dashboard(company_name: str, top_k: int = 10) -> dict:
    """
    Generate dashboard using RAG (retrieval-augmented generation).
    
    Returns:
        {
            "markdown": str,
            "retrieved_chunks": list,
            "validation": dict
        }
    """
    # Retrieve context
    chunks = retrieve_context(company_name, top_k=top_k)
    
    if not chunks:
        return {
            "error": "No context found",
            "markdown": f"## Error\nNo data found for {company_name}.",
            "retrieved_chunks": [],
            "validation": {"valid": False}
        }
    
    # Build context string
    context_parts = [f"Company: {company_name}\n\nRetrieved information:\n"]
    
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"\n--- Source {i}: {chunk['source_url']} ---")
        context_parts.append(chunk['text'])
        context_parts.append("")
    
    context = "\n".join(context_parts)
    
    # Add instruction
    context += """\n\nGenerate a complete PE dashboard following the 8-section format.
Use ONLY the information provided above.
For any missing information, write "Not disclosed."
Do not invent or infer data not explicitly stated.
"""
    
    # Generate dashboard
    llm = get_llm_client()
    markdown = llm.generate_dashboard(context, temperature=0.2)
    
    # Validate
    validation = llm.validate_dashboard_structure(markdown)
    
    return {
        "markdown": markdown,
        "retrieved_chunks": [
            {
                "source": c["source_url"],
                "preview": c["text"][:200] + "...",
                "score": c.get("score", 0.0)
            }
            for c in chunks
        ],
        "validation": validation
    }
```

### Step 2: Update `src/api.py`
```python
# Replace the existing /dashboard/rag endpoint

@app.post("/dashboard/rag")
def dashboard_rag(company_name: str, top_k: int = 10):
    """Generate dashboard using RAG (retrieval-augmented generation)."""
    from .rag_pipeline import generate_rag_dashboard
    
    result = generate_rag_dashboard(company_name, top_k=top_k)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "company_name": company_name,
        "method": "rag",
        "markdown": result["markdown"],
        "validation": result["validation"],
        "retrieved_chunks": result["retrieved_chunks"],
        "num_chunks": len(result["retrieved_chunks"])
    }
```

**Dependencies**: 
- Pipeline Engineer needs to implement real `retrieve_context()` in `src/vector_db.py`
- You can test with mock data first

**Integration Point**:
```python
# Pipeline Engineer will provide this function
from .vector_db import retrieve_context  # Replace mock version
```

**Testing**:
```bash
curl -X POST "http://localhost:8000/dashboard/rag?company_name=ExampleAI&top_k=5"
```

---

## TASK 4: Evaluation Logic (Lab 9)
**File**: `src/evaluator.py` and create `src/eval_runner.py`  
**Location**: Enhance evaluator.py, create eval_runner.py  
**Estimated Time**: 4 hours

### Step 1: Update `src/evaluator.py`
```python
from typing import Dict, List
import re

def score_dashboard(factual: int, schema: int, provenance: int, hallucination: int, readability: int) -> int:
    """Calculate total score."""
    return factual + schema + provenance + hallucination + readability


def auto_evaluate_dashboard(markdown: str, payload: dict = None) -> Dict[str, int]:
    """
    Automated evaluation of dashboard quality.
    
    Returns scores for each criterion (human should verify).
    """
    scores = {
        "factual": 0,
        "schema": 0,
        "provenance": 0,
        "hallucination": 0,
        "readability": 0
    }
    
    # Schema adherence (0-2)
    required_sections = [
        "## Company Overview",
        "## Business Model and GTM",
        "## Funding & Investor Profile",
        "## Growth Momentum",
        "## Visibility & Market Sentiment",
        "## Risks and Challenges",
        "## Outlook",
        "## Disclosure Gaps"
    ]
    present_sections = sum(1 for s in required_sections if s in markdown)
    scores["schema"] = 2 if present_sections == 8 else (1 if present_sections >= 6 else 0)
    
    # Provenance (0-2): Check for "Not disclosed" usage
    not_disclosed_count = markdown.count("Not disclosed")
    scores["provenance"] = 2 if not_disclosed_count > 0 else 0
    
    # Hallucination control (0-2): Check for warning signs
    hallucination_phrases = [
        "we believe", "it appears", "likely", "probably",
        "estimated to be", "rumored", "sources say"
    ]
    hallucination_count = sum(1 for phrase in hallucination_phrases if phrase.lower() in markdown.lower())
    scores["hallucination"] = 2 if hallucination_count == 0 else (1 if hallucination_count <= 2 else 0)
    
    # Readability (0-1): Check length and structure
    word_count = len(markdown.split())
    scores["readability"] = 1 if 800 <= word_count <= 3000 else 0
    
    # Factual (0-3): Needs human evaluation, default to 2
    scores["factual"] = 2  # Human must verify
    
    return scores


def compare_dashboards(rag_markdown: str, structured_markdown: str) -> Dict:
    """
    Compare RAG vs Structured dashboards.
    
    Returns comparison metrics.
    """
    rag_scores = auto_evaluate_dashboard(rag_markdown)
    struct_scores = auto_evaluate_dashboard(structured_markdown)
    
    return {
        "rag": {
            **rag_scores,
            "total": sum(rag_scores.values())
        },
        "structured": {
            **struct_scores,
            "total": sum(struct_scores.values())
        },
        "winner": "structured" if sum(struct_scores.values()) > sum(rag_scores.values()) else "rag"
    }
```

### Step 2: Create `src/eval_runner.py`
```python
"""Run evaluation for multiple companies and generate report."""
import json
from pathlib import Path
from .structured_pipeline import generate_structured_dashboard
from .rag_pipeline import generate_rag_dashboard
from .evaluator import compare_dashboards

def evaluate_companies(company_ids: list, company_names: list) -> dict:
    """
    Evaluate both pipelines for given companies.
    
    Args:
        company_ids: List of company IDs for structured pipeline
        company_names: List of company names for RAG pipeline
        
    Returns:
        Evaluation results dict
    """
    results = []
    
    for company_id, company_name in zip(company_ids, company_names):
        print(f"Evaluating {company_name}...")
        
        # Generate both dashboards
        rag_result = generate_rag_dashboard(company_name)
        struct_result = generate_structured_dashboard(company_id)
        
        # Compare
        comparison = compare_dashboards(
            rag_result["markdown"],
            struct_result["markdown"]
        )
        
        results.append({
            "company_id": company_id,
            "company_name": company_name,
            "rag_scores": comparison["rag"],
            "structured_scores": comparison["structured"],
            "winner": comparison["winner"]
        })
    
    return {
        "results": results,
        "summary": {
            "rag_wins": sum(1 for r in results if r["winner"] == "rag"),
            "structured_wins": sum(1 for r in results if r["winner"] == "structured"),
            "avg_rag_score": sum(r["rag_scores"]["total"] for r in results) / len(results),
            "avg_structured_score": sum(r["structured_scores"]["total"] for r in results) / len(results)
        }
    }


def generate_eval_markdown(results: dict) -> str:
    """Generate EVAL.md content from results."""
    md = "# RAG vs Structured Evaluation\n\n"
    
    # Table
    md += "| company | method       | factual (0–3) | schema (0–2) | provenance (0–2) | hallucination (0–2) | readability (0–1) | total |\n"
    md += "|---------|--------------|---------------|--------------|------------------|----------------------|-------------------|-------|\n"
    
    for r in results["results"]:
        company = r["company_name"]
        
        # RAG row
        rag = r["rag_scores"]
        md += f"| {company} | RAG          | {rag['factual']} | {rag['schema']} | {rag['provenance']} | {rag['hallucination']} | {rag['readability']} | {rag['total']} |\n"
        
        # Structured row
        struct = r["structured_scores"]
        md += f"| {company} | Structured   | {struct['factual']} | {struct['schema']} | {struct['provenance']} | {struct['hallucination']} | {struct['readability']} | {struct['total']} |\n"
    
    # Summary
    md += f"\n## Summary\n\n"
    md += f"- RAG wins: {results['summary']['rag_wins']}\n"
    md += f"- Structured wins: {results['summary']['structured_wins']}\n"
    md += f"- Average RAG score: {results['summary']['avg_rag_score']:.2f}\n"
    md += f"- Average Structured score: {results['summary']['avg_structured_score']:.2f}\n"
    
    return md


if __name__ == "__main__":
    # Example usage
    company_ids = [
        "00000000-0000-0000-0000-000000000000",
        # Add more as they become available
    ]
    
    company_names = [
        "ExampleAI",
        # Add more
    ]
    
    results = evaluate_companies(company_ids, company_names)
    
    # Save results
    Path("data/evaluation_results.json").write_text(json.dumps(results, indent=2))
    
    # Generate EVAL.md
    eval_md = generate_eval_markdown(results)
    Path("EVAL.md").write_text(eval_md)
    
    print("Evaluation complete! Check EVAL.md")
```

**Usage**:
```bash
python -m src.eval_runner
```

---

## TASK 5: Additional API Endpoints
**File**: `src/api.py`  
**Location**: Add new endpoints  
**Estimated Time**: 2 hours

### Add to `src/api.py`:
```python
from typing import List
from pathlib import Path

@app.get("/companies", response_model=List[dict])
def list_companies():
    """Get list of all Forbes AI 50 companies with metadata."""
    seed_path = DATA_DIR / "forbes_ai50_seed.json"
    if not seed_path.exists():
        return []
    
    companies = json.loads(seed_path.read_text())
    
    # Enrich with payload availability
    payload_dir = DATA_DIR / "payloads"
    for company in companies:
        # Check if payload exists (Pipeline Engineer will create these)
        company_id = company.get("company_id", "unknown")
        payload_path = payload_dir / f"{company_id}.json"
        company["has_payload"] = payload_path.exists()
    
    return companies


@app.get("/dashboard/{company_id}/metadata")
def get_dashboard_metadata(company_id: str):
    """Get metadata about available dashboards for a company."""
    from .structured_pipeline import load_payload
    
    payload = load_payload(company_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "company_id": company_id,
        "company_name": payload.company_record.legal_name,
        "has_structured": True,
        "has_rag": True,  # Assume RAG always available
        "last_updated": payload.company_record.as_of,
        "data_quality": {
            "num_events": len(payload.events),
            "num_snapshots": len(payload.snapshots),
            "num_products": len(payload.products),
            "num_leadership": len(payload.leadership),
            "has_visibility": len(payload.visibility) > 0
        }
    }


@app.post("/evaluate")
def evaluate_dashboard(
    markdown: str,
    factual: int = 2,
    schema: int = 2,
    provenance: int = 2,
    hallucination: int = 2,
    readability: int = 1
):
    """
    Manually score a dashboard.
    
    Returns total score and validation.
    """
    from .evaluator import score_dashboard
    from .llm_client import get_llm_client
    
    total = score_dashboard(factual, schema, provenance, hallucination, readability)
    
    llm = get_llm_client()
    validation = llm.validate_dashboard_structure(markdown)
    
    return {
        "scores": {
            "factual": factual,
            "schema": schema,
            "provenance": provenance,
            "hallucination": hallucination,
            "readability": readability,
            "total": total
        },
        "validation": validation,
        "grade": "A" if total >= 9 else "B" if total >= 7 else "C" if total >= 5 else "D"
    }
```

---

## TASK 6: Docker & Cloud Deployment
**File**: Test Docker, deploy to cloud  
**Location**: Command line  
**Estimated Time**: 3 hours

### Step 1: Test Docker Locally
```bash
# 1. Build Docker image
cd docker
docker compose up --build

# 2. Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/companies

# 3. Test in browser
# Open http://localhost:8000/docs for API documentation
```

### Step 2: Deploy to GCP Cloud Run
```bash
# Install gcloud CLI if not already installed
# brew install google-cloud-sdk  # macOS

# 1. Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/pe-dashboard

# 3. Deploy to Cloud Run
gcloud run deploy pe-dashboard-api \
  --image gcr.io/YOUR_PROJECT_ID/pe-dashboard \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY

# 4. Get URL
gcloud run services describe pe-dashboard-api --region us-central1 --format 'value(status.url)'
```

### Step 3: Update README
```markdown
## Deployment

**API Endpoint**: https://pe-dashboard-api-xxxxx.run.app

### Endpoints
- `GET /health` - Health check
- `GET /companies` - List all companies
- `POST /dashboard/structured?company_id=XXX` - Generate structured dashboard
- `POST /dashboard/rag?company_name=XXX` - Generate RAG dashboard
```

---

## TASK 7: Write 1-Page Reflection
**File**: Create `REFLECTION.md`  
**Location**: Root directory  
**Estimated Time**: 1 hour

### What to Write:
```markdown
# RAG vs Structured Pipeline - Reflection

## Overview
This document reflects on the comparison between RAG (Retrieval-Augmented Generation) and Structured (Pydantic-based) pipelines for generating PE dashboards.

## Key Findings

### RAG Pipeline
**Strengths**:
- Flexible: Works even without perfect data structure
- Natural language: Can extract from unstructured text
- Handles variety: Works with different page formats

**Weaknesses**:
- Hallucination risk: May infer facts not stated
- Inconsistent: Output varies based on retrieved chunks
- Provenance unclear: Hard to trace claims to sources

### Structured Pipeline
**Strengths**:
- Factually accurate: Only uses validated Pydantic data
- Consistent: Same payload always produces same output
- Provenance clear: Every field has source URL
- Type-safe: Pydantic validates all data

**Weaknesses**:
- Requires extraction: Need instructor to structure data first
- Brittle: Fails if web pages change format
- More complex: Two-step process (extract → generate)

## Evaluation Results
[Insert table from EVAL.md]

## Conclusion
For PE diligence, **Structured pipeline is superior** because:
1. Factual accuracy is critical for investment decisions
2. Provenance is required for due diligence
3. Consistency allows fair company comparisons
4. Type safety prevents data errors

However, RAG is useful for:
- Initial exploration of new companies
- Handling incomplete data
- Quick prototyping

## Recommendations
- Use Structured pipeline for final dashboards
- Use RAG for preliminary research
- Combine both: Use RAG to find data, then validate with Structured extraction

## Lessons Learned
1. Prompt engineering is crucial for quality
2. "Not disclosed" is better than guessing
3. Pydantic models prevent many errors
4. LLM temperature matters: 0.2 is better than 0.7 for facts
5. Token limits require careful context management
```

---

## 📦 Dependencies You Need to Install

### Add to `requirements.txt`:
```txt
# LLM
openai>=1.12.0
python-dotenv>=1.0.0

# Optional: Alternative LLMs
# anthropic>=0.18.0  # For Claude
```

### Install:
```bash
pip install openai python-dotenv
```

---

## 🔗 Integration Points

### What You Need from Frontend Engineer:
1. **UI Requirements**: What data to return in API responses
2. **Error Feedback**: What error messages are helpful

### What You Need from Pipeline Engineer:
1. **Vector DB Function**: `retrieve_context(company_name, query, top_k)`
   - Should return: `List[Dict[str, Any]]` with keys: `source_url`, `text`, `score`
   - Location: `src/vector_db.py`

2. **Payload Files**: 
   - At least 5 companies with complete payloads
   - Location: `data/payloads/<company_id>.json`
   - Format: Must match `Payload` Pydantic model

3. **Company ID Mapping**:
   - How to map company_name → company_id
   - Maybe add to `forbes_ai50_seed.json`

---

## ✅ Deliverables Checklist

- [ ] `src/llm_client.py` - LLM wrapper with error handling
- [ ] `src/structured_pipeline.py` - Complete structured dashboard generation
- [ ] `src/rag_pipeline.py` - Complete RAG dashboard generation
- [ ] `src/evaluator.py` - Automated evaluation logic
- [ ] `src/eval_runner.py` - Run evaluation on 5+ companies
- [ ] `src/api.py` - All endpoints working:
  - [ ] `GET /companies`
  - [ ] `POST /dashboard/structured`
  - [ ] `POST /dashboard/rag`
  - [ ] `GET /dashboard/{id}/metadata`
  - [ ] `POST /evaluate`
- [ ] `EVAL.md` - Filled with 5+ company comparisons
- [ ] `REFLECTION.md` - 1-page analysis
- [ ] Docker tested locally
- [ ] Deployed to GCP/AWS
- [ ] README updated with API docs & deployment URL

---

## 🚀 Getting Started (Your First Steps)

### Day 1:
```bash
# 1. Set up OpenAI
export OPENAI_API_KEY=sk-your-key-here
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. Install dependencies
pip install openai python-dotenv

# 3. Create LLM client
# Create src/llm_client.py (see TASK 1)

# 4. Test with starter payload
python -c "from src.llm_client import get_llm_client; print(get_llm_client())"

# 5. Create feature branch
git checkout -b feature/llm-integration
```

### Day 2-3:
- Implement TASK 1 (LLM client)
- Test prompt with starter_payload.json
- Implement TASK 2 (Structured pipeline)

### Day 4-5:
- Implement TASK 3 (RAG pipeline with mock data)
- Wait for Pipeline Engineer's vector DB
- Integrate real vector DB when ready

### Day 6-7:
- Implement TASK 4 (Evaluation)
- Run evaluation on available companies
- Fill out EVAL.md

### Day 8:
- TASK 5 (Additional endpoints)
- TASK 7 (Reflection)

### Day 9:
- TASK 6 (Docker & deployment)

### Day 10:
- Final testing & documentation

---

## 💡 Tips for Success

1. **Start with Structured, not RAG**: Easier to test with real data
   ```python
   # Test with starter_payload.json first
   result = generate_structured_dashboard("00000000-0000-0000-0000-000000000000")
   print(result["markdown"])
   ```

2. **Test Prompt Engineering**:
   - Try different temperatures (0.2 vs 0.7)
   - Adjust max_tokens based on output length
   - Add examples to system prompt if needed

3. **Handle Token Limits**:
   - GPT-4-turbo: 128k context, 4k output
   - GPT-3.5-turbo: 16k context, 4k output
   - Chunk large payloads if needed

4. **Mock First, Integrate Later**:
   - Use mock `retrieve_context()` for RAG testing
   - Replace with real vector DB when Pipeline Engineer provides it

5. **Automate Testing**:
   ```python
   # Create tests/test_api.py
   def test_structured_dashboard():
       response = client.post("/dashboard/structured?company_id=...")
       assert response.status_code == 200
       assert "## Company Overview" in response.json()["markdown"]
   ```

---

## 📞 Communication with Team

### What to Share in Daily Standups:
- "LLM client working, tested with GPT-4"
- "Structured pipeline generating dashboards"
- "Need vector DB function from Pipeline Engineer"

### What to Ask Pipeline Engineer:
- "What's the signature of retrieve_context()?"
- "When will first payloads be ready?"
- "Can you provide company_id mapping?"

### What to Ask Frontend Engineer:
- "What format do you want for /companies response?"
- "Should I add pagination?"
- "What error messages are most helpful?"

Good luck! 🚀
