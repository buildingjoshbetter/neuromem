"""
Benchmark: Cognee (Graph-Based Memory)
=======================================
Cognee uses a knowledge graph approach to memory.
It extracts entities and relationships, building a graph
that can be traversed for complex queries.

Different architecture from Mem0/LangMem's flat vector approach.
"""

import asyncio
import json
import time
import os

from test_queries import TEST_QUERIES


async def run_benchmark():
    import cognee

    with open("/Users/j/Desktop/neuromem/synthetic_messages.json") as f:
        messages = json.load(f)

    # Configure cognee to use Anthropic
    cognee.config.set_llm_provider("anthropic")
    cognee.config.set_llm_model("claude-sonnet-4-5-20250929")
    cognee.config.set_llm_api_key(os.environ.get("ANTHROPIC_API_KEY"))

    print(f"Loading {len(messages)} messages into Cognee...")
    print("=" * 60)

    # Reset any existing data
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    # Add messages as text data
    loaded = 0
    errors = 0

    for i, msg in enumerate(messages):
        try:
            content = f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"
            await cognee.add(content, dataset_name="benchmark")
            loaded += 1

            if (i + 1) % 20 == 0:
                print(f"  Added {i + 1}/{len(messages)} messages...")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR adding message {i}: {e}")

    print(f"\nAdded {loaded} messages. Errors: {errors}")

    # Process/cognify the data (builds knowledge graph)
    print("\nBuilding knowledge graph (cognify)...")
    start = time.time()
    try:
        await cognee.cognify()
        elapsed = time.time() - start
        print(f"Knowledge graph built in {elapsed:.2f}s")
    except Exception as e:
        print(f"ERROR during cognify: {e}")
        elapsed = time.time() - start
        print(f"Failed after {elapsed:.2f}s")

    # Run queries
    print(f"\n{'=' * 60}")
    print("RUNNING 20 TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")

        try:
            start = time.time()
            search_results = await cognee.search("GRAPH_COMPLETION", query_text=q["query"])
            elapsed = time.time() - start

            memories = []
            if search_results:
                for item in search_results[:5]:
                    if isinstance(item, dict):
                        mem_text = item.get("text", item.get("content", str(item)))
                        score = item.get("score", "N/A")
                    else:
                        mem_text = str(item)
                        score = "N/A"

                    memories.append({
                        "memory": str(mem_text)[:500],
                        "score": score,
                    })

            print(f"  Time: {elapsed:.2f}s | Results: {len(memories)}")
            for j, mem in enumerate(memories[:3]):
                print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:120]}")

            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "notes": q["notes"],
                "num_results": len(memories),
                "elapsed_seconds": round(elapsed, 2),
                "results": memories,
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

    # Save results
    output = {
        "system": "Cognee",
        "version": "0.5.4",
        "llm": "claude-sonnet-4-5-20250929",
        "architecture": "Knowledge graph extraction + graph traversal",
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_cognee_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_cognee_results.json")


if __name__ == "__main__":
    print("BENCHMARK: Cognee")
    print("Graph-based knowledge extraction with Anthropic Claude")
    print(f"{'=' * 60}\n")
    asyncio.run(run_benchmark())
