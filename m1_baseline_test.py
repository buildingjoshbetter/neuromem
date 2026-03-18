"""
M1: The Baseline Test
=====================
Load synthetic data into Mem0, run 20 test queries, produce a scorecard.

This tests what a $24M-funded memory system actually does with realistic data.
"""

import json
import os
import time
from mem0 import Memory
from test_queries import TEST_QUERIES

# ============================================
# Configure Mem0 with Anthropic LLM + HuggingFace embeddings
# ============================================
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
            "collection_name": "m1_baseline",
            "embedding_model_dims": 384,
            "path": "/Users/j/Desktop/neuromem/m1_qdrant_data",
        }
    },
    "version": "v1.1",
}

def load_data():
    """Load synthetic messages into Mem0."""
    with open("/Users/j/Desktop/neuromem/synthetic_messages.json") as f:
        messages = json.load(f)

    m = Memory.from_config(config)

    print(f"Loading {len(messages)} messages into Mem0...")
    print("=" * 60)

    loaded = 0
    errors = 0
    for i, msg in enumerate(messages):
        try:
            # Format as a conversational message
            content = f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"

            # Add to mem0 with user_id = "josh" (the person whose memory this is)
            result = m.add(
                content,
                user_id="josh",
                metadata={
                    "sender": msg["sender"],
                    "recipient": msg["recipient"],
                    "category": msg["category"],
                    "timestamp": msg["timestamp"],
                }
            )
            loaded += 1

            if (i + 1) % 20 == 0:
                print(f"  Loaded {i + 1}/{len(messages)} messages...")

        except Exception as e:
            errors += 1
            print(f"  ERROR on message {i}: {e}")

    print(f"\nDone. Loaded: {loaded}, Errors: {errors}")
    return m


def run_queries(m):
    """Run all 20 test queries and collect results."""
    print(f"\n{'=' * 60}")
    print("RUNNING 20 TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []

    for q in TEST_QUERIES:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")

        try:
            start = time.time()
            search_results = m.search(q["query"], user_id="josh", limit=5)
            elapsed = time.time() - start

            # Extract the memories returned
            memories = []
            if isinstance(search_results, dict) and "results" in search_results:
                memories = search_results["results"]
            elif isinstance(search_results, list):
                memories = search_results

            print(f"  Time: {elapsed:.2f}s | Results: {len(memories)}")

            for j, mem in enumerate(memories[:3]):  # Show top 3
                if isinstance(mem, dict):
                    memory_text = mem.get("memory", mem.get("text", str(mem)))
                    score = mem.get("score", "N/A")
                    print(f"  [{j+1}] (score: {score}) {memory_text[:120]}...")
                else:
                    print(f"  [{j+1}] {str(mem)[:120]}...")

            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "notes": q["notes"],
                "num_results": len(memories),
                "elapsed_seconds": round(elapsed, 2),
                "results": [
                    {
                        "memory": m.get("memory", m.get("text", str(m)))[:500] if isinstance(m, dict) else str(m)[:500],
                        "score": m.get("score", "N/A") if isinstance(m, dict) else "N/A",
                    }
                    for m in memories[:5]
                ],
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "notes": q["notes"],
                "error": str(e),
                "num_results": 0,
                "elapsed_seconds": 0,
                "results": [],
            })

        print()

    return results


def print_scorecard(results):
    """Print the final scorecard for Josh to evaluate."""
    print(f"\n{'=' * 60}")
    print("M1 SCORECARD: MEM0 BASELINE")
    print(f"{'=' * 60}\n")

    print(f"{'ID':<4} {'Category':<16} {'Query':<45} {'Results':<8} {'Time':<6}")
    print("-" * 80)

    for r in results:
        print(f"Q{r['query_id']:<3} {r['category']:<16} {r['query'][:43]:<45} {r['num_results']:<8} {r['elapsed_seconds']:<6}s")

    print(f"\n{'=' * 60}")
    print("DETAILED RESULTS FOR SCORING")
    print(f"{'=' * 60}")

    for r in results:
        print(f"\n--- Q{r['query_id']} [{r['category']}] ---")
        print(f"Query:    {r['query']}")
        print(f"Expected: {r['expected'][:200]}")
        print(f"Results ({r['num_results']} returned):")
        if r.get("error"):
            print(f"  ERROR: {r['error']}")
        for j, mem in enumerate(r["results"]):
            print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:200]}")
        print()

    # Save results to JSON for later comparison
    with open("/Users/j/Desktop/neuromem/m1_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to m1_results.json")


if __name__ == "__main__":
    print("M1: THE BASELINE TEST")
    print("Testing Mem0 (the $24M product) with our synthetic data")
    print(f"{'=' * 60}\n")

    # Step 1: Load data
    m = load_data()

    # Step 2: Run queries
    results = run_queries(m)

    # Step 3: Print scorecard
    print_scorecard(results)
