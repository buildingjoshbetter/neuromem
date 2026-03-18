"""
Benchmark: Neuromem (Full 6-Layer Engine) vs 60 v2 Queries.

Tests the full Neuromem pipeline — FTS5, vector search, RRF hybrid fusion,
temporal filtering, salience guard, personality, consolidation — against the
same 60-query benchmark used for ChromaDB, Mem0, LangMem, and Cognee.

Output format matches the existing benchmark scripts so results can be
compared side-by-side.
"""

import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from neuromem.engine import NeuromemEngine
from test_queries_v2 import TEST_QUERIES_V2

RESULTS_PATH = Path(__file__).parent / "benchmark_v2_neuromem_results.json"
DATA_PATH = Path(__file__).parent / "synthetic_v2_messages.json"
DB_PATH = Path(__file__).parent / "neuromem_benchmark.db"


def run_benchmark():
    print("=" * 60)
    print("BENCHMARK: Neuromem (Full 6-Layer) vs 60 Queries")
    print("=" * 60)

    # ── Initialize and ingest ─────────────────────────────────────────────
    engine = NeuromemEngine(db_path=DB_PATH)
    ingest_stats = engine.ingest(DATA_PATH)

    print(f"\nIngestion complete:")
    for step, timing in ingest_stats.items():
        print(f"  {step}: {timing}")

    capabilities = engine.stats.get("capabilities", {})
    active_layers = [k for k, v in capabilities.items() if v]
    print(f"\nActive layers: {', '.join(active_layers)}")

    # ── Run queries ───────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES_V2:
        t_start = time.time()
        search_results = engine.search(q["query"], limit=10)
        query_time = time.time() - t_start

        result = {
            "id": q["id"],
            "query": q["query"],
            "category": q["category"],
            "expected": q["expected"],
            "scoring_notes": q["scoring_notes"],
            "num_results": len(search_results),
            "query_time_ms": round(query_time * 1000, 2),
            "results": [
                {
                    "rank": i + 1,
                    "content": r["content"][:500],
                    "sender": r.get("sender", ""),
                    "recipient": r.get("recipient", ""),
                    "timestamp": r.get("timestamp", ""),
                    "modality": r.get("modality", ""),
                    "score": r.get("score", 0),
                    "source": r.get("source", "unknown"),
                }
                for i, r in enumerate(search_results)
            ],
        }
        results.append(result)

        has_results = "HIT?" if len(search_results) > 0 else "MISS?"
        print(
            f"  Q{q['id']:2d} [{q['category']:15s}] {has_results:5s} "
            f"({query_time * 1000:.1f}ms) {q['query'][:60]}"
        )

    # ── Summary ───────────────────────────────────────────────────────────
    total_time = sum(r["query_time_ms"] for r in results)
    avg_time = total_time / len(results) if results else 0
    queries_with_results = sum(1 for r in results if r["num_results"] > 0)

    summary = {
        "system": "Neuromem (6-Layer)",
        "dataset": "synthetic_v2_messages.json",
        "message_count": engine.stats.get("message_count", 0),
        "query_count": len(results),
        "active_layers": active_layers,
        "ingest_stats": ingest_stats,
        "total_query_time_ms": round(total_time, 2),
        "avg_query_time_ms": round(avg_time, 2),
        "queries_with_results": queries_with_results,
        "queries_empty": len(results) - queries_with_results,
    }

    # Checkpoint WAL before measuring size (WAL mode defers writes).
    try:
        engine.conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    except Exception:
        pass

    # Include DB size if the file exists.
    try:
        if DB_PATH.exists():
            summary["db_size_kb"] = round(DB_PATH.stat().st_size / 1024, 1)
    except Exception:
        pass

    output = {"summary": summary, "results": results}

    with open(RESULTS_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Messages: {summary['message_count']}")
    print(f"  Active layers: {', '.join(active_layers)}")
    print(f"  Queries with results: {queries_with_results}/{len(results)}")
    print(f"  Queries empty: {summary['queries_empty']}/{len(results)}")
    print(f"  Avg query time: {avg_time:.2f}ms")
    print(f"  Total query time: {total_time:.1f}ms")
    if "db_size_kb" in summary:
        print(f"  DB size: {summary['db_size_kb']} KB")
    print(f"  Results saved to: {RESULTS_PATH}")

    # ── Category breakdown ────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print("BY CATEGORY")
    print(f"{'=' * 60}")

    cats: dict[str, dict] = {}
    for r in results:
        cat = r["category"]
        if cat not in cats:
            cats[cat] = {"total": 0, "with_results": 0, "avg_time_ms": 0.0}
        cats[cat]["total"] += 1
        cats[cat]["avg_time_ms"] += r["query_time_ms"]
        if r["num_results"] > 0:
            cats[cat]["with_results"] += 1

    for cat in sorted(cats.keys()):
        c = cats[cat]
        c["avg_time_ms"] /= c["total"]
        bar = "#" * c["with_results"] + "." * (c["total"] - c["with_results"])
        print(f"  {cat:20s} {c['with_results']}/{c['total']} [{bar}] avg {c['avg_time_ms']:.1f}ms")

    # ── Source breakdown (where did results come from?) ───────────────────
    print(f"\n{'=' * 60}")
    print("RESULT SOURCES")
    print(f"{'=' * 60}")

    source_counts: dict[str, int] = {}
    for r in results:
        for hit in r["results"]:
            src = hit.get("source", "unknown")
            source_counts[src] = source_counts.get(src, 0) + 1

    for src in sorted(source_counts.keys()):
        print(f"  {src:20s} {source_counts[src]} results")

    engine.close()
    return output


if __name__ == "__main__":
    run_benchmark()
