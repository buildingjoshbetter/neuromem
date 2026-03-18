"""
Cognee v2 Benchmark — SEARCH ONLY (cognify already done).
Re-runs the 60 queries against the already-built knowledge graph.
"""

import json
import time
import asyncio
import os
import sys

# Set env vars BEFORE importing cognee
os.environ["EMBEDDING_PROVIDER"] = "fastembed"
os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
os.environ["EMBEDDING_DIMENSIONS"] = "384"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"

sys.path.insert(0, "/Users/j/Desktop/neuromem")
sys.stdout.reconfigure(line_buffering=True)
from test_queries_v2 import TEST_QUERIES_V2


async def run_search():
    import cognee

    # Configure LLM for search
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    cognee.config.set_llm_provider("anthropic")
    cognee.config.set_llm_model("claude-sonnet-4-5-20250929")
    cognee.config.set_llm_api_key(anthropic_key)

    print("Cognee search-only benchmark", flush=True)
    print(f"Available search types: CHUNKS, SUMMARIES, GRAPH_COMPLETION, NATURAL_LANGUAGE, RAG_COMPLETION", flush=True)

    # Try multiple search types to find the best one
    search_types = [
        ("GRAPH_COMPLETION", cognee.SearchType.GRAPH_COMPLETION),
        ("CHUNKS", cognee.SearchType.CHUNKS),
        ("SUMMARIES", cognee.SearchType.SUMMARIES),
    ]

    # Quick test with Q1 to find working search type
    best_search_type = None
    for name, st in search_types:
        try:
            test_result = await cognee.search(
                query_text="What is the name of Jordan's dog?",
                query_type=st,
                top_k=10,
            )
            if test_result:
                print(f"  {name}: {len(test_result)} results - {str(test_result[0])[:200]}", flush=True)
                if best_search_type is None:
                    best_search_type = (name, st)
            else:
                print(f"  {name}: 0 results", flush=True)
        except Exception as e:
            print(f"  {name}: ERROR - {str(e)[:120]}", flush=True)

    if not best_search_type:
        print("No search type worked! Trying GRAPH_COMPLETION as default.", flush=True)
        best_search_type = ("GRAPH_COMPLETION", cognee.SearchType.GRAPH_COMPLETION)

    st_name, search_type = best_search_type
    print(f"\nUsing search type: {st_name}", flush=True)

    # Run all queries
    print(f"\n{'=' * 60}", flush=True)
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES", flush=True)
    print(f"{'=' * 60}\n", flush=True)

    results = []
    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}", flush=True)
        try:
            start = time.time()
            search_results = await cognee.search(
                query_text=q["query"],
                query_type=search_type,
                top_k=10,
            )
            elapsed = time.time() - start

            memories = []
            if search_results:
                for item in search_results[:10]:
                    if isinstance(item, dict):
                        mem_text = item.get("text", item.get("content", item.get("chunk_text", str(item))))
                        score = item.get("score", item.get("relevance", item.get("distance", "N/A")))
                    elif isinstance(item, (list, tuple)):
                        mem_text = " | ".join(str(x) for x in item)
                        score = "N/A"
                    elif hasattr(item, 'text'):
                        mem_text = str(item.text)
                        score = getattr(item, 'score', 'N/A')
                    else:
                        mem_text = str(item)
                        score = "N/A"
                    memories.append({
                        "memory": str(mem_text)[:500],
                        "score": str(score),
                    })

            print(f"  Time: {elapsed:.3f}s | Results: {len(memories)}", flush=True)
            for j, mem in enumerate(memories[:3]):
                print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:100]}", flush=True)

            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "num_results": len(memories),
                "elapsed_seconds": round(elapsed, 3),
                "results": memories,
            })
        except Exception as e:
            print(f"  ERROR: {e}", flush=True)
            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "error": str(e),
                "num_results": 0,
                "elapsed_seconds": 0,
                "results": [],
            })
        print(flush=True)

    output = {
        "system": "Cognee",
        "version": "0.5.4",
        "llm": "claude-sonnet-4-5-20250929",
        "embedding_model": "BAAI/bge-small-en-v1.5 (fastembed)",
        "search_type": st_name,
        "architecture": "Knowledge graph (Kuzu) + LanceDB vectors + LLM extraction + fastembed",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_queries": len(results),
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_cognee_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_cognee_results.json", flush=True)


if __name__ == "__main__":
    asyncio.run(run_search())
