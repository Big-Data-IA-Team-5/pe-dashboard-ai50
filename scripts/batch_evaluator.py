"""Evaluate ALL companies - RAG vs Structured."""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.evaluator import compare_dashboards

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None


def evaluate_all_companies():
    """
    Evaluate all companies with both dashboards.
    
    Compares RAG vs Structured using the rubric:
    - Factual correctness (0-3)
    - Schema adherence (0-2)
    - Provenance use (0-2)
    - Hallucination control (0-2)
    - Readability (0-1)
    """
    print("📊 BATCH EVALUATION - ALL COMPANIES", flush=True)
    print("=" * 80, flush=True)
    
    # Find companies with both dashboards
    structured_dir = Path("data/dashboards/structured")
    rag_dir = Path("data/dashboards/rag")
    
    if not structured_dir.exists() or not rag_dir.exists():
        print("❌ ERROR: Dashboard directories not found", flush=True)
        print("   Run: python scripts/batch_dashboard_generator.py first", flush=True)
        return None
    
    structured_files = {f.stem: f for f in structured_dir.glob("*.md")}
    rag_files = {f.stem: f for f in rag_dir.glob("*.md")}
    
    # Companies with both dashboards
    common = sorted(set(structured_files.keys()) & set(rag_files.keys()))
    
    print(f"Found {len(common)} companies with both dashboards\n", flush=True)
    
    if len(common) < 5:
        print(f"⚠️  Only {len(common)} companies ready (need at least 5)", flush=True)
        return None
    
    print(f"Evaluating {len(common)} companies...\n", flush=True)
    
    results = []
    
    for i, company_id in enumerate(common, 1):
        print(f"[{i}/{len(common)}] {company_id:25}", end=" → ", flush=True)
        
        try:
            # Load both dashboards
            struct_md = structured_files[company_id].read_text()
            rag_md = rag_files[company_id].read_text()
            
            # Compare using evaluator
            comparison = compare_dashboards(rag_md, struct_md, company_id)
            results.append(comparison)
            
            # Display result
            winner_symbol = "🏆 S" if comparison['winner'] == 'structured' else "⭐ R"
            print(f"{winner_symbol} (Struct:{comparison['structured']['total']} vs RAG:{comparison['rag']['total']})", flush=True)
            
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}", flush=True)
            continue
    
    if not results:
        print("\n❌ No successful evaluations", flush=True)
        return None
    
    # Calculate summary statistics
    rag_wins = sum(1 for r in results if r['winner'] == 'rag')
    struct_wins = sum(1 for r in results if r['winner'] == 'structured')
    avg_rag = sum(r['rag']['total'] for r in results) / len(results)
    avg_struct = sum(r['structured']['total'] for r in results) / len(results)
    
    summary = {
        'evaluation_date': datetime.now().isoformat(),
        'total_evaluated': len(results),
        'rag_wins': rag_wins,
        'structured_wins': struct_wins,
        'avg_rag_score': round(avg_rag, 2),
        'avg_structured_score': round(avg_struct, 2),
        'score_difference': round(abs(avg_struct - avg_rag), 2),
        'results': results
    }
    
    # Print summary
    print("\n" + "=" * 80, flush=True)
    print("📊 EVALUATION SUMMARY", flush=True)
    print("=" * 80, flush=True)
    print(f"Companies evaluated: {len(results)}", flush=True)
    print(f"RAG wins: {rag_wins} ({rag_wins/len(results)*100:.1f}%)", flush=True)
    print(f"Structured wins: {struct_wins} ({struct_wins/len(results)*100:.1f}%)", flush=True)
    print(f"Average RAG score: {avg_rag:.2f}/10", flush=True)
    print(f"Average Structured score: {avg_struct:.2f}/10", flush=True)
    print(f"Score difference: {abs(avg_struct - avg_rag):.2f} points", flush=True)
    print(flush=True)
    
    winner = "Structured Pipeline" if struct_wins > rag_wins else "RAG Pipeline"
    print(f"🏆 Overall Winner: {winner}", flush=True)
    print("=" * 80, flush=True)
    
    # Save results JSON
    results_path = Path("data/evaluation_results.json")
    results_path.write_text(json.dumps(summary, indent=2))
    print(f"\n💾 Results saved to: {results_path}", flush=True)
    
    return summary


def generate_eval_markdown(summary):
    """Generate EVAL.md from evaluation results."""
    if not summary:
        return
    
    results = summary['results']
    
    md = "# RAG vs Structured Pipeline Evaluation\n\n"
    md += "**Project ORBIT - Forbes AI 50 PE Dashboard Factory**\n\n"
    md += f"**Evaluation Date**: {datetime.now().strftime('%B %d, %Y')}\n"
    md += f"**Companies Evaluated**: {summary['total_evaluated']}\n\n"
    
    # Executive Summary
    md += "## Executive Summary\n\n"
    winner = "Structured Pipeline" if summary['structured_wins'] > summary['rag_wins'] else "RAG Pipeline"
    md += f"After evaluating {summary['total_evaluated']} companies from the Forbes AI 50, "
    md += f"the **{winner}** demonstrated superior performance with "
    md += f"{max(summary['rag_wins'], summary['structured_wins'])} wins "
    md += f"compared to {min(summary['rag_wins'], summary['structured_wins'])}.\n\n"
    
    # Summary Stats
    md += "## Summary Statistics\n\n"
    md += f"- **Total Evaluated**: {summary['total_evaluated']} companies\n"
    md += f"- **RAG Wins**: {summary['rag_wins']} ({summary['rag_wins']/summary['total_evaluated']*100:.1f}%)\n"
    md += f"- **Structured Wins**: {summary['structured_wins']} ({summary['structured_wins']/summary['total_evaluated']*100:.1f}%)\n"
    md += f"- **Average RAG Score**: {summary['avg_rag_score']}/10\n"
    md += f"- **Average Structured Score**: {summary['avg_structured_score']}/10\n"
    md += f"- **Score Difference**: {summary['score_difference']} points\n\n"
    
    # Detailed Table
    md += "## Detailed Scores\n\n"
    md += "| Rank | Company | Method | Factual | Schema | Provenance | Hallucination | Readability | **Total** | Winner |\n"
    md += "|------|---------|--------|---------|--------|------------|---------------|-------------|-----------|--------|\n"
    
    for i, r in enumerate(results, 1):
        company = r['company_name']
        
        # Structured row
        s = r['structured']
        winner_mark = "🏆" if r['winner'] == 'structured' else ""
        md += f"| {i} | {company} | Structured | {s['factual']} | {s['schema']} | {s['provenance']} | {s['hallucination']} | {s['readability']} | **{s['total']}** | {winner_mark} |\n"
        
        # RAG row
        rg = r['rag']
        winner_mark = "🏆" if r['winner'] == 'rag' else ""
        md += f"| {i} | {company} | RAG | {rg['factual']} | {rg['schema']} | {rg['provenance']} | {rg['hallucination']} | {rg['readability']} | **{rg['total']}** | {winner_mark} |\n"
    
    # Analysis
    md += "\n## Analysis\n\n"
    
    if summary['structured_wins'] > summary['rag_wins']:
        md += "### Structured Pipeline Advantages\n\n"
        md += "The Structured pipeline outperformed RAG primarily due to:\n\n"
        md += "1. **Better Hallucination Control**: Pydantic validation prevents invented data\n"
        md += "2. **Consistent Provenance**: Every field has explicit source tracking\n"
        md += "3. **Type Safety**: Schema enforcement catches errors early\n"
        md += "4. **'Not disclosed' Usage**: More consistent handling of missing data\n\n"
        
        md += "### RAG Pipeline Advantages\n\n"
        md += "RAG performed better in:\n\n"
        md += "1. **Qualitative Insights**: Captures nuanced language from sources\n"
        md += "2. **Flexibility**: Works even with incomplete structured data\n"
        md += "3. **Context Richness**: More detailed descriptions\n\n"
    else:
        md += "### RAG Pipeline Advantages\n\n"
        md += "The RAG pipeline outperformed Structured primarily due to:\n\n"
        md += "1. **Richer Context**: Retrieved chunks provide more detail\n"
        md += "2. **Natural Language**: Better captures tone and positioning\n"
        md += "3. **Flexibility**: Handles varied data formats\n\n"
        
        md += "### Structured Pipeline Advantages\n\n"
        md += "Structured performed better in:\n\n"
        md += "1. **Data Accuracy**: Type-validated information\n"
        md += "2. **Consistency**: Same data produces same output\n"
        md += "3. **Traceability**: Clear provenance for every claim\n\n"
    
    # Conclusion
    md += "## Conclusion\n\n"
    md += "For private equity diligence, both pipelines offer value:\n\n"
    md += "- **Structured Pipeline**: Best for factual accuracy and investment decisions\n"
    md += "- **RAG Pipeline**: Best for initial research and qualitative analysis\n\n"
    md += "**Recommendation**: Use Structured as primary, RAG for supplementary context.\n"
    
    # Save EVAL.md
    eval_path = Path("EVAL.md")
    eval_path.write_text(md)
    print(f"\n📄 EVAL.md generated with {len(results)} companies", flush=True)
    
    return md


if __name__ == "__main__":
    print("Running batch evaluation...\n", flush=True)
    
    summary = evaluate_all_companies()
    
    if summary:
        generate_eval_markdown(summary)
        print("\n✅ Evaluation complete!", flush=True)
        print("   - Results: data/evaluation_results.json", flush=True)
        print("   - Report: EVAL.md", flush=True)
    else:
        print("\n❌ Evaluation failed", flush=True)
        sys.exit(1)
