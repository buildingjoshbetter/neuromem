"""
Benchmark runner for v3 — orchestrates ingest + query for any adapter.

Usage:
    python benchmark_runner.py --adapter chromadb
    python benchmark_runner.py --adapter mem0 --smoke-test
"""

import argparse
import importlib
import json
import sys
import time
from pathlib import Path

# Add v3_benchmark to path
V3_DIR = Path(__file__).parent
sys.path.insert(0, str(V3_DIR))
sys.path.insert(0, str(V3_DIR / "adapters"))

from base_adapter import BaseAdapter, Session


SESSIONS_PATH = V3_DIR / "sessions.json"
RESULTS_DIR = V3_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def load_sessions(path: Path = SESSIONS_PATH) -> list[Session]:
    """Load sessions from JSON file."""
    with open(path) as f:
        raw = json.load(f)

    sessions = []
    for s in raw:
        sessions.append(Session(
            session_id=s["session_id"],
            timestamp=s["timestamp"],
            turns=s["turns"],
            facts_introduced=s.get("facts_introduced", []),
            facts_updated=s.get("facts_updated", []),
        ))
    return sessions


def load_queries() -> list[dict]:
    """Load v3 test queries."""
    from test_queries_v3 import TEST_QUERIES_V3
    return TEST_QUERIES_V3


def load_adapter(adapter_name: str) -> BaseAdapter:
    """Dynamically load an adapter by name."""
    module_name = f"{adapter_name}_adapter"
    try:
        mod = importlib.import_module(module_name)
    except ImportError:
        # Try from adapters subdirectory
        try:
            mod = importlib.import_module(f"adapters.{module_name}")
        except ImportError:
            raise ImportError(f"Could not find adapter module: {module_name}")

    # Find the adapter class (subclass of BaseAdapter)
    adapter_cls = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if (isinstance(obj, type) and issubclass(obj, BaseAdapter)
                and obj is not BaseAdapter):
            adapter_cls = obj
            break

    if adapter_cls is None:
        raise ValueError(f"No BaseAdapter subclass found in {module_name}")

    return adapter_cls()


def run_benchmark(adapter: BaseAdapter, sessions: list[Session],
                  queries: list[dict], smoke_test: bool = False) -> dict:
    """Run full benchmark: setup → ingest → query → teardown."""

    if smoke_test:
        sessions = sessions[:5]
        queries = queries[:5]
        print(f"SMOKE TEST: Using {len(sessions)} sessions, {len(queries)} queries")

    system_name = adapter.system_name
    print(f"\n{'=' * 60}")
    print(f"BENCHMARK: {system_name} v{adapter.system_version}")
    print(f"Architecture: {adapter.architecture}")
    print(f"Sessions: {len(sessions)} | Queries: {len(queries)}")
    print(f"{'=' * 60}\n")

    # Phase 1: Setup
    print("[1/4] Setting up...")
    t0 = time.time()
    try:
        adapter.setup()
    except Exception as e:
        print(f"  SETUP FAILED: {e}")
        return {
            "system": system_name,
            "version": adapter.system_version,
            "status": "SETUP_FAILED",
            "error": str(e),
        }
    setup_time = time.time() - t0
    print(f"  Setup complete ({setup_time:.1f}s)")

    # Phase 2: Ingest
    print(f"\n[2/4] Ingesting {len(sessions)} sessions...")
    t0 = time.time()
    try:
        ingest_result = adapter.ingest_sessions(sessions)
    except Exception as e:
        print(f"  INGEST FAILED: {e}")
        adapter.teardown()
        return {
            "system": system_name,
            "version": adapter.system_version,
            "status": "INGEST_FAILED",
            "error": str(e),
        }
    ingest_time = time.time() - t0
    print(f"  Ingested: {ingest_result.get('ingested', '?')} | "
          f"Errors: {ingest_result.get('errors', '?')} | "
          f"Time: {ingest_time:.1f}s")

    # Phase 3: Query
    print(f"\n[3/4] Running {len(queries)} queries...")
    query_results = []
    total_query_time = 0

    for q in queries:
        t0 = time.time()
        try:
            results = adapter.query(q["query"], top_k=10)
            elapsed = time.time() - t0
            total_query_time += elapsed

            retrieved = []
            for r in results:
                retrieved.append({
                    "content": r.content[:500],
                    "score": r.score,
                    "metadata": r.metadata,
                })

            query_results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "hit_criteria": q.get("hit_criteria", ""),
                "partial_criteria": q.get("partial_criteria", ""),
                "num_results": len(retrieved),
                "elapsed_seconds": round(elapsed, 3),
                "results": retrieved,
            })

            status = f"{len(retrieved)} results" if retrieved else "EMPTY"
            print(f"  Q{q['id']:2d} [{q['category']:25s}] {status:12s} ({elapsed*1000:.0f}ms) {q['query'][:50]}")

        except Exception as e:
            elapsed = time.time() - t0
            total_query_time += elapsed
            print(f"  Q{q['id']:2d} [{q['category']:25s}] ERROR      ({elapsed*1000:.0f}ms) {str(e)[:50]}")
            query_results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "hit_criteria": q.get("hit_criteria", ""),
                "partial_criteria": q.get("partial_criteria", ""),
                "num_results": 0,
                "elapsed_seconds": round(elapsed, 3),
                "error": str(e),
                "results": [],
            })

    avg_query_time = total_query_time / len(queries) if queries else 0

    # Phase 4: Teardown
    print(f"\n[4/4] Tearing down...")
    stats = adapter.get_stats()
    adapter.teardown()

    # Build output
    output = {
        "system": system_name,
        "version": adapter.system_version,
        "architecture": adapter.architecture,
        "status": "COMPLETED",
        "dataset": f"{len(sessions)} sessions",
        "num_queries": len(query_results),
        "timing": {
            "setup_seconds": round(setup_time, 1),
            "ingest_seconds": round(ingest_time, 1),
            "total_query_seconds": round(total_query_time, 1),
            "avg_query_ms": round(avg_query_time * 1000, 1),
        },
        "ingest_stats": ingest_result,
        "system_stats": stats,
        "results": query_results,
    }

    # Save raw results
    suffix = "_smoke" if smoke_test else ""
    output_path = RESULTS_DIR / f"{system_name.lower().replace(' ', '_').replace('/', '_')}_raw{suffix}.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to: {output_path}")

    # Summary
    queries_with_results = sum(1 for r in query_results if r["num_results"] > 0)
    queries_empty = sum(1 for r in query_results if r["num_results"] == 0)
    queries_errored = sum(1 for r in query_results if "error" in r)

    print(f"\n{'=' * 60}")
    print(f"SUMMARY: {system_name}")
    print(f"{'=' * 60}")
    print(f"  Queries with results: {queries_with_results}/{len(query_results)}")
    print(f"  Empty results: {queries_empty}/{len(query_results)}")
    print(f"  Errors: {queries_errored}/{len(query_results)}")
    print(f"  Avg query time: {avg_query_time*1000:.1f}ms")
    print(f"  Total time: {setup_time + ingest_time + total_query_time:.1f}s")

    # Category breakdown
    cats = {}
    for r in query_results:
        cat = r["category"]
        if cat not in cats:
            cats[cat] = {"total": 0, "with_results": 0}
        cats[cat]["total"] += 1
        if r["num_results"] > 0:
            cats[cat]["with_results"] += 1

    print(f"\nBy category:")
    for cat in sorted(cats.keys()):
        c = cats[cat]
        bar = "#" * c["with_results"] + "." * (c["total"] - c["with_results"])
        print(f"  {cat:30s} {c['with_results']}/{c['total']} [{bar}]")

    return output


def main():
    parser = argparse.ArgumentParser(description="V3 Memory Benchmark Runner")
    parser.add_argument("--adapter", required=True, help="Adapter name (e.g., chromadb, mem0, fts5)")
    parser.add_argument("--smoke-test", action="store_true", help="Run with 5 sessions + 5 queries")
    parser.add_argument("--sessions", default=str(SESSIONS_PATH), help="Path to sessions.json")
    args = parser.parse_args()

    sessions = load_sessions(Path(args.sessions))
    queries = load_queries()
    adapter = load_adapter(args.adapter)

    run_benchmark(adapter, sessions, queries, smoke_test=args.smoke_test)


if __name__ == "__main__":
    main()
