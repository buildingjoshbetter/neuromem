"""
Cognee v2 Benchmark — Knowledge graph + LLM extraction on expanded dataset.
Cognee builds a knowledge graph from text, then uses graph traversal for retrieval.
Architecture: Text → LLM extraction → Knowledge graph (NetworkX) → LanceDB vectors.

Configuration: Uses Anthropic Claude as LLM provider (avoids OpenAI dependency).
"""

import json
import time
import asyncio
import os
import sys

sys.path.insert(0, "/Users/j/Desktop/neuromem")
from test_queries_v2 import TEST_QUERIES_V2


async def run_benchmark():
    import cognee

    # Configure Cognee to use Anthropic instead of OpenAI
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        return

    print("Configuring Cognee for Anthropic LLM + HuggingFace embeddings...")
    cognee.config.set_llm_provider("anthropic")
    cognee.config.set_llm_model("claude-sonnet-4-5-20250929")
    cognee.config.set_llm_api_key(anthropic_key)

    # Set embedding to use fastembed locally (avoid OpenAI)
    # NOTE: Must be set BEFORE cognee initializes embedding engine
    os.environ["EMBEDDING_PROVIDER"] = "fastembed"
    os.environ["EMBEDDING_MODEL"] = "BAAI/bge-small-en-v1.5"
    os.environ["EMBEDDING_DIMENSIONS"] = "384"
    os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

    # Reset any previous data
    try:
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)
        print("Previous data cleared")
    except Exception as e:
        print(f"Prune warning (OK if first run): {e}")

    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
        messages = json.load(f)

    print(f"\nDataset: {len(messages)} messages")
    print("=" * 60)

    # Add messages to Cognee in batches
    print("\nAdding messages to Cognee...")
    load_start = time.time()

    # Cognee expects text input — combine messages into chunks
    batch_size = 50
    loaded = 0
    errors = 0

    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        batch_text = "\n\n".join([
            f"[{m['timestamp']}] [{m.get('modality', 'imessage')}] {m['sender']} -> {m['recipient']}: {m['content']}"
            for m in batch
        ])

        try:
            await cognee.add(batch_text, dataset_name="jordan_messages")
            loaded += len(batch)
            if (i + batch_size) % 100 == 0 or i + batch_size >= len(messages):
                print(f"  Added {min(i + batch_size, len(messages))}/{len(messages)} messages")
        except Exception as e:
            errors += len(batch)
            print(f"  Error at batch {i}: {e}")

    print(f"\nLoaded: {loaded}, Errors: {errors}")

    if loaded == 0:
        print("No messages loaded. Aborting.")
        return

    # Run Cognee's knowledge graph construction
    print("\nRunning cognify (knowledge graph construction)...")
    cognify_start = time.time()
    try:
        await cognee.cognify()
        cognify_time = time.time() - cognify_start
        print(f"Cognify completed in {cognify_time:.1f}s")
    except Exception as e:
        cognify_time = time.time() - cognify_start
        print(f"Cognify error after {cognify_time:.1f}s: {e}")
        print("Attempting to continue with whatever was processed...")

    load_time = time.time() - load_start

    # Run queries
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")
        try:
            start = time.time()

            # Try different search types
            search_results = await cognee.search(
                cognee.SearchType.INSIGHTS,
                query_text=q["query"],
            )
            elapsed = time.time() - start

            memories = []
            if search_results:
                for item in search_results[:10]:
                    if isinstance(item, dict):
                        mem_text = item.get("text", item.get("content", item.get("insight", str(item))))
                        score = item.get("score", item.get("relevance", "N/A"))
                    elif isinstance(item, (list, tuple)):
                        mem_text = str(item)
                        score = "N/A"
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
        "system": "Cognee",
        "version": "0.5.4",
        "llm": "claude-sonnet-4-5-20250929",
        "architecture": "Knowledge graph (NetworkX) + LanceDB vectors + LLM extraction",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_queries": len(results),
        "load_time_seconds": round(load_time, 1),
        "cognify_time_seconds": round(cognify_time, 1),
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_cognee_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_cognee_results.json")


if __name__ == "__main__":
    print("BENCHMARK: Cognee v2 (Knowledge Graph + LLM Extraction)")
    print(f"{'=' * 60}\n")
    asyncio.run(run_benchmark())
