"""
Benchmark: Neuromem FTS5 search engine vs 60 v2 queries.
Same format as benchmark_v2_chromadb.py, benchmark_v2_mem0.py, etc.

Runs the 60 test queries from test_queries_v2.py against the FTS5 engine,
saves raw results for scoring.
"""

import json
import time
import sys
from pathlib import Path

# Add parent dir so we can import
sys.path.insert(0, str(Path(__file__).parent))

from neuromem_fts5 import create_db, load_messages, search, DB_PATH
from test_queries_v2 import TEST_QUERIES_V2


RESULTS_PATH = Path(__file__).parent / "benchmark_v2_fts5_results.json"


def run_benchmark():
    print("=" * 60)
    print("BENCHMARK: Neuromem FTS5 vs 60 Queries (v2 Dataset)")
    print("=" * 60)

    # Fresh database
    if DB_PATH.exists():
        DB_PATH.unlink()

    t0 = time.time()
    conn = create_db()
    count = load_messages(conn)
    load_time = time.time() - t0
    print(f"\nLoaded {count} messages in {load_time:.3f}s")

    results = []

    for q in TEST_QUERIES_V2:
        query = q["query"]
        t_start = time.time()
        search_results = search(conn, query, limit=10)
        query_time = time.time() - t_start

        result = {
            "id": q["id"],
            "query": query,
            "category": q["category"],
            "expected": q["expected"],
            "scoring_notes": q["scoring_notes"],
            "num_results": len(search_results),
            "query_time_ms": round(query_time * 1000, 2),
            "results": [
                {
                    "rank": i + 1,
                    "content": r["content"][:500],
                    "sender": r["sender"],
                    "recipient": r["recipient"],
                    "timestamp": r["timestamp"],
                    "modality": r["modality"],
                    "bm25_score": r["bm25_score"],
                }
                for i, r in enumerate(search_results)
            ]
        }
        results.append(result)

        # Progress
        status = "HIT?" if len(search_results) > 0 else "MISS?"
        print(f"  Q{q['id']:2d} [{q['category']:15s}] {status:5s} ({query_time*1000:.1f}ms) {query[:60]}")

    # Summary stats
    total_time = sum(r["query_time_ms"] for r in results)
    avg_time = total_time / len(results)
    queries_with_results = sum(1 for r in results if r["num_results"] > 0)
    queries_empty = sum(1 for r in results if r["num_results"] == 0)

    summary = {
        "system": "Neuromem FTS5 (SQLite)",
        "dataset": "synthetic_v2_messages.json",
        "message_count": count,
        "query_count": len(results),
        "load_time_s": round(load_time, 3),
        "total_query_time_ms": round(total_time, 2),
        "avg_query_time_ms": round(avg_time, 2),
        "queries_with_results": queries_with_results,
        "queries_empty": queries_empty,
        "db_size_kb": round(DB_PATH.stat().st_size / 1024, 1),
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Messages loaded: {count}")
    print(f"  Load time: {load_time:.3f}s")
    print(f"  Queries run: {len(results)}")
    print(f"  Queries with results: {queries_with_results}/60")
    print(f"  Queries empty: {queries_empty}/60")
    print(f"  Avg query time: {avg_time:.2f}ms")
    print(f"  Total query time: {total_time:.1f}ms")
    print(f"  DB size: {summary['db_size_kb']} KB")
    print(f"\n  Results saved to: {RESULTS_PATH}")

    # Category breakdown
    print(f"\n{'=' * 60}")
    print("BY CATEGORY (queries with results / total)")
    print(f"{'=' * 60}")
    cats = {}
    for r in results:
        cat = r["category"]
        if cat not in cats:
            cats[cat] = {"total": 0, "with_results": 0}
        cats[cat]["total"] += 1
        if r["num_results"] > 0:
            cats[cat]["with_results"] += 1

    for cat in sorted(cats.keys()):
        c = cats[cat]
        bar = "#" * c["with_results"] + "." * (c["total"] - c["with_results"])
        print(f"  {cat:20s} {c['with_results']}/{c['total']} [{bar}]")

    conn.close()
    return output


if __name__ == "__main__":
    run_benchmark()
