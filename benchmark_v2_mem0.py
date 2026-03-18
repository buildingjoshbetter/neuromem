"""
Mem0 v2 Benchmark — LLM extraction + vector search on expanded dataset.
Uses Anthropic Claude for LLM extraction, HuggingFace embeddings, Qdrant vector store.
Mem0 is the $24M-funded product — this tests its full pipeline on 797 messages.
"""

import json
import time
import os
import sys

# Must run from neuromem dir for imports
sys.path.insert(0, "/Users/j/Desktop/neuromem")
from test_queries_v2 import TEST_QUERIES_V2


def run_benchmark():
    from mem0 import Memory

    config = {
        "llm": {
            "provider": "anthropic",
            "config": {
                "model": "claude-sonnet-4-5-20250929",
                "temperature": 0.0,
                "top_p": None,
                "max_tokens": 2000,
            }
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": "all-MiniLM-L6-v2",
                "model_kwargs": {"device": "cpu"},
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "v2_benchmark",
                "embedding_model_dims": 384,
                "path": "/Users/j/Desktop/neuromem/v2_qdrant_data",
            }
        },
        "version": "v1.1",
    }

    m = Memory.from_config(config)

    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
        messages = json.load(f)

    print(f"Loading {len(messages)} messages into Mem0...")
    print("=" * 60)

    loaded = 0
    errors = 0
    start_time = time.time()
    for i, msg in enumerate(messages):
        try:
            content = f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"
            m.add(
                content,
                user_id="jordan",
                metadata={
                    "sender": msg["sender"],
                    "recipient": msg["recipient"],
                    "category": msg["category"],
                    "timestamp": msg["timestamp"],
                    "modality": msg.get("modality", "imessage"),
                }
            )
            loaded += 1
            if (i + 1) % 50 == 0:
                elapsed = time.time() - start_time
                rate = loaded / elapsed
                print(f"  Loaded {i + 1}/{len(messages)} ({rate:.1f} msg/s)...")
        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR on message {i}: {e}")

    load_time = time.time() - start_time
    print(f"\nLoaded: {loaded}, Errors: {errors}, Time: {load_time:.1f}s")

    # Run queries
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")
        try:
            start = time.time()
            search_results = m.search(q["query"], user_id="jordan", limit=10)
            elapsed = time.time() - start

            memories = []
            if isinstance(search_results, dict) and "results" in search_results:
                raw = search_results["results"]
            elif isinstance(search_results, list):
                raw = search_results
            else:
                raw = []

            for item in raw[:10]:
                if isinstance(item, dict):
                    mem_text = item.get("memory", item.get("text", str(item)))
                    score = item.get("score", "N/A")
                else:
                    mem_text = str(item)
                    score = "N/A"
                memories.append({
                    "memory": str(mem_text)[:500],
                    "score": score,
                })

            print(f"  Time: {elapsed:.3f}s | Results: {len(memories)}")
            for j, mem in enumerate(memories[:3]):
                print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:100]}")

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
            print(f"  ERROR: {e}")
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
        print()

    output = {
        "system": "Mem0",
        "version": "1.0.5",
        "llm": "claude-sonnet-4-5-20250929",
        "embedding_model": "all-MiniLM-L6-v2",
        "architecture": "LLM extraction + Qdrant vector search",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_queries": len(results),
        "load_time_seconds": round(load_time, 1),
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_mem0_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_mem0_results.json")


if __name__ == "__main__":
    print("BENCHMARK: Mem0 v2 (LLM Extraction + Vector Search)")
    print(f"{'=' * 60}\n")
    run_benchmark()
