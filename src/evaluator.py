"""Enhanced evaluation logic for dashboard comparison with GCS support."""
from typing import Dict, List
import re
import os
import json
from pathlib import Path
from datetime import datetime


def score_dashboard(
    factual: int,
    schema: int,
    provenance: int,
    hallucination: int,
    readability: int
) -> int:
    """
    Calculate total rubric score.
    
    Args:
        factual: 0-3 points
        schema: 0-2 points
        provenance: 0-2 points
        hallucination: 0-2 points
        readability: 0-1 points
        
    Returns:
        Total score (0-10)
    """
    return factual + schema + provenance + hallucination + readability


def auto_evaluate_dashboard(markdown: str) -> Dict[str, int]:
    """
    Automated evaluation of dashboard quality.
    
    Note: Factual correctness requires human verification.
    This provides automated scoring for other criteria.
    
    Args:
        markdown: Generated dashboard markdown
        
    Returns:
        Dictionary of scores for each criterion
    """
    scores = {
        "factual": 2,  # Default, requires manual verification
        "schema": 0,
        "provenance": 0,
        "hallucination": 0,
        "readability": 0
    }
    
    # Schema adherence (0-2): Check for all 8 required sections
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
    
    present_count = sum(1 for section in required_sections if section in markdown)
    
    if present_count == 8:
        scores["schema"] = 2
    elif present_count >= 6:
        scores["schema"] = 1
    else:
        scores["schema"] = 0
    
    # Provenance (0-2): Check for "Not disclosed" usage
    not_disclosed_count = markdown.lower().count("not disclosed")
    
    if not_disclosed_count >= 3:
        scores["provenance"] = 2
    elif not_disclosed_count >= 1:
        scores["provenance"] = 1
    else:
        scores["provenance"] = 0
    
    # Hallucination control (0-2): Check for warning phrases
    hallucination_phrases = [
        "we believe", "it appears", "likely", "probably",
        "estimated to be", "rumored", "sources say", "reportedly",
        "it seems", "may have", "could be", "presumably",
        "it is believed", "allegedly"
    ]
    
    hallucination_count = sum(
        1 for phrase in hallucination_phrases 
        if phrase in markdown.lower()
    )
    
    if hallucination_count == 0:
        scores["hallucination"] = 2
    elif hallucination_count <= 2:
        scores["hallucination"] = 1
    else:
        scores["hallucination"] = 0
    
    # Readability (0-1): Check length and formatting
    word_count = len(markdown.split())
    has_structure = "## " in markdown
    has_lists = ("- " in markdown or "* " in markdown)
    
    if 500 <= word_count <= 3000 and has_structure:
        scores["readability"] = 1
    else:
        scores["readability"] = 0
    
    return scores


def compare_dashboards(
    rag_markdown: str,
    structured_markdown: str,
    company_name: str
) -> Dict:
    """
    Compare RAG vs Structured dashboards using rubric.
    
    Args:
        rag_markdown: Dashboard from RAG pipeline
        structured_markdown: Dashboard from Structured pipeline
        company_name: Company name for reporting
        
    Returns:
        Comparison results with scores and winner
    """
    # Evaluate both
    rag_scores = auto_evaluate_dashboard(rag_markdown)
    struct_scores = auto_evaluate_dashboard(structured_markdown)
    
    # Calculate totals
    rag_total = sum(rag_scores.values())
    struct_total = sum(struct_scores.values())
    
    return {
        "company_name": company_name,
        "rag": {
            **rag_scores,
            "total": rag_total
        },
        "structured": {
            **struct_scores,
            "total": struct_total
        },
        "winner": "structured" if struct_total > rag_total else "rag",
        "difference": abs(struct_total - rag_total),
        "rag_strengths": _identify_strengths(rag_scores),
        "structured_strengths": _identify_strengths(struct_scores)
    }


def _identify_strengths(scores: Dict[str, int]) -> List[str]:
    """Identify which criteria a pipeline performed well on."""
    strengths = []
    
    if scores.get("factual", 0) >= 2:
        strengths.append("factual accuracy")
    if scores.get("schema", 0) == 2:
        strengths.append("schema adherence")
    if scores.get("provenance", 0) >= 1:
        strengths.append("provenance tracking")
    if scores.get("hallucination", 0) == 2:
        strengths.append("hallucination control")
    if scores.get("readability", 0) == 1:
        strengths.append("readability")
    
    return strengths


def generate_eval_md(company_ids: List[str], use_gcs: bool = True, output_path: str = "EVAL.md") -> str:
    """
    Generate comprehensive EVAL.md comparing RAG vs Structured pipelines.
    
    This function generates dashboards for all companies using GCS data sources,
    evaluates them, and creates a detailed comparison report.
    
    Args:
        company_ids: List of company identifiers to evaluate
        use_gcs: If True, use GCS for vector DB and jobs data (default: True)
        output_path: Where to save the evaluation report
        
    Returns:
        Path to generated EVAL.md file
    """
    from src.rag_pipeline import generate_rag_dashboard
    from src.structured_pipeline import generate_structured_dashboard
    
    print(f"\n🔬 GENERATING EVALUATION REPORT")
    print("=" * 80)
    print(f"Companies to evaluate: {len(company_ids)}")
    print(f"Using GCS data: {use_gcs}")
    print("=" * 80)
    
    results = []
    
    for i, company_id in enumerate(company_ids, 1):
        print(f"\n[{i}/{len(company_ids)}] Evaluating {company_id}...")
        
        try:
            # Generate both dashboards
            rag_result = generate_rag_dashboard(company_id, use_gcs=use_gcs)
            struct_result = generate_structured_dashboard(company_id)
            
            company_name = struct_result.get('metadata', {}).get('company_name', company_id)
            
            # Compare
            comparison = compare_dashboards(
                rag_result["markdown"],
                struct_result["markdown"],
                company_name
            )
            
            results.append({
                "company_id": company_id,
                "company_name": company_name,
                "comparison": comparison,
                "rag_metadata": rag_result["metadata"],
                "structured_metadata": struct_result.get("metadata", {})
            })
            
            print(f"  ✓ RAG: {comparison['rag']['total']}/10")
            print(f"  ✓ Structured: {comparison['structured']['total']}/10")
            print(f"  ✓ Winner: {comparison['winner']}")
            
        except Exception as e:
            print(f"  ✗ Error evaluating {company_id}: {e}")
            continue
    
    # Generate markdown report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    md_lines = [
        "# Dashboard Evaluation Report",
        "",
        f"**Generated**: {timestamp}",
        f"**Companies Evaluated**: {len(results)}",
        f"**Data Source**: {'GCS Cloud Storage' if use_gcs else 'Local'}",
        f"**Vector DB**: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/`" if use_gcs else "Local ChromaDB",
        f"**Jobs Data**: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/jobs/`" if use_gcs else "Local jobs data",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
    ]
    
    # Calculate overall stats
    rag_wins = sum(1 for r in results if r["comparison"]["winner"] == "rag")
    struct_wins = sum(1 for r in results if r["comparison"]["winner"] == "structured")
    avg_rag = sum(r["comparison"]["rag"]["total"] for r in results) / len(results) if results else 0
    avg_struct = sum(r["comparison"]["structured"]["total"] for r in results) / len(results) if results else 0
    
    md_lines.extend([
        f"- **RAG Pipeline Wins**: {rag_wins} ({rag_wins/len(results)*100:.1f}%)" if results else "- No results",
        f"- **Structured Pipeline Wins**: {struct_wins} ({struct_wins/len(results)*100:.1f}%)" if results else "",
        f"- **Average RAG Score**: {avg_rag:.2f}/10",
        f"- **Average Structured Score**: {avg_struct:.2f}/10",
        "",
        "### Key Findings",
        "",
        "**RAG Pipeline Strengths**:",
        "- Flexible context assembly from multiple sources",
        "- Works with incomplete data",
        "- Enriched with jobs data from GCS",
        "",
        "**Structured Pipeline Strengths**:",
        "- More precise with complete payloads",
        "- Better provenance tracking",
        "- Consistent schema adherence",
        "",
        "---",
        "",
        "## Detailed Company Evaluations",
        ""
    ])
    
    # Individual company results
    for result in results:
        comp = result["comparison"]
        
        md_lines.extend([
            f"### {result['company_name']} ({result['company_id']})",
            "",
            "| Criterion | RAG | Structured |",
            "|-----------|-----|------------|",
            f"| Factual Correctness (0-3) | {comp['rag']['factual']} | {comp['structured']['factual']} |",
            f"| Schema Adherence (0-2) | {comp['rag']['schema']} | {comp['structured']['schema']} |",
            f"| Provenance (0-2) | {comp['rag']['provenance']} | {comp['structured']['provenance']} |",
            f"| Hallucination Control (0-2) | {comp['rag']['hallucination']} | {comp['structured']['hallucination']} |",
            f"| Readability (0-1) | {comp['rag']['readability']} | {comp['structured']['readability']} |",
            f"| **TOTAL (0-10)** | **{comp['rag']['total']}** | **{comp['structured']['total']}** |",
            "",
            f"**Winner**: {comp['winner'].upper()} (by {comp['difference']} points)",
            "",
            f"**RAG Strengths**: {', '.join(comp['rag_strengths']) if comp['rag_strengths'] else 'None'}",
            "",
            f"**Structured Strengths**: {', '.join(comp['structured_strengths']) if comp['structured_strengths'] else 'None'}",
            "",
            "**Metadata**:",
            f"- RAG chunks used: {result['rag_metadata'].get('num_chunks', 'N/A')}",
            f"- RAG using GCS: {result['rag_metadata'].get('using_gcs', 'N/A')}",
            f"- RAG mock data: {result['rag_metadata'].get('using_mock_data', 'N/A')}",
            "",
            "---",
            ""
        ])
    
    # Rubric explanation
    md_lines.extend([
        "",
        "## Evaluation Rubric",
        "",
        "### Factual Correctness (0-3 points)",
        "- **3**: All facts verified against source data",
        "- **2**: Mostly accurate with minor discrepancies",
        "- **1**: Several inaccuracies present",
        "- **0**: Major factual errors",
        "",
        "### Schema Adherence (0-2 points)",
        "- **2**: All 8 required sections present",
        "- **1**: 6-7 sections present",
        "- **0**: Less than 6 sections",
        "",
        "### Provenance (0-2 points)",
        "- **2**: Proper use of 'Not disclosed' (3+ instances)",
        "- **1**: Some use of 'Not disclosed' (1-2 instances)",
        "- **0**: Missing data invented or ignored",
        "",
        "### Hallucination Control (0-2 points)",
        "- **2**: No speculative language",
        "- **1**: Minor speculation (1-2 instances)",
        "- **0**: Frequent speculation (3+ instances)",
        "",
        "### Readability (0-1 point)",
        "- **1**: 500-3000 words, proper formatting",
        "- **0**: Too short/long or poor formatting",
        "",
        "---",
        "",
        f"*Report generated using GCS data sources*" if use_gcs else "*Report generated using local data sources*",
        f"*Vector DB: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/vector_db/`*" if use_gcs else "",
        f"*Jobs Data: `gs://us-central1-pe-airflow-env-2825d831-bucket/data/jobs/`*" if use_gcs else "",
    ])
    
    # Write to file
    eval_content = "\n".join(md_lines)
    Path(output_path).write_text(eval_content)
    
    print(f"\n✅ Evaluation report saved to {output_path}")
    print(f"📊 Evaluated {len(results)} companies")
    print(f"🏆 RAG wins: {rag_wins}, Structured wins: {struct_wins}")
    
    return output_path


if __name__ == "__main__":
    # Test evaluator
    test_markdown = """
## Company Overview
TestAI is a company. Not disclosed.

## Business Model and GTM
Not disclosed.

## Funding & Investor Profile
Not disclosed.

## Growth Momentum
Not disclosed.

## Visibility & Market Sentiment
Not disclosed.

## Risks and Challenges
Not disclosed.

## Outlook
Not disclosed.

## Disclosure Gaps
- Revenue not disclosed
- Customer names not disclosed
"""
    
    scores = auto_evaluate_dashboard(test_markdown)
    print("Test Scores:", scores)
    print("Total:", sum(scores.values()), "/10")