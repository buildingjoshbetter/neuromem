"""
Benchmark: LangMem (LangChain Memory SDK)
==========================================
LangMem uses LLM extraction + vector store, similar to Mem0.
Key differences: LangChain ecosystem, different extraction prompts,
supports updates/consolidation of memories.

Uses Anthropic Claude as the LLM (same as our Mem0 test).
"""

import json
import os
import time
import sys

from test_queries import TEST_QUERIES

def run_benchmark():
    from langmem import create_memory_manager, create_memory_store_manager
    from langgraph.store.memory import InMemoryStore

    with open("/Users/j/Desktop/neuromem/synthetic_messages.json") as f:
        messages = json.load(f)

    # Set up in-memory store with embeddings
    # Use sentence-transformers locally (same model as ChromaDB/Mem0 for fair comparison)
    from sentence_transformers import SentenceTransformer
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_fn(texts):
        return embed_model.encode(texts).tolist()

    store = InMemoryStore(
        index={
            "dims": 384,
            "embed": embed_fn,
        }
    )

    # Create memory manager using Anthropic Claude
    manager = create_memory_manager(
        "anthropic:claude-sonnet-4-5-20250929",
        instructions="Extract key facts, preferences, relationships, events, and decisions from these messages. Preserve specific details like names, dates, numbers, and locations.",
        enable_inserts=True,
        enable_updates=True,
    )

    print(f"Loading {len(messages)} messages into LangMem...")
    print("=" * 60)

    # Process messages in batches (LangMem expects conversation format)
    loaded = 0
    errors = 0

    # Process each message individually through the memory manager
    for i, msg in enumerate(messages):
        try:
            content = f"[{msg['timestamp']}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"

            # Extract memories from this message
            extracted = manager.invoke({
                "messages": [{"role": "user", "content": content}]
            })

            # Store each extracted memory
            if extracted:
                for j, mem in enumerate(extracted):
                    mem_content = mem.text if hasattr(mem, 'text') else str(mem)
                    store.put(
                        namespace=("memories", "josh"),
                        key=f"msg_{i}_mem_{j}",
                        value={"text": mem_content, "source_msg": i},
                    )

            loaded += 1
            if (i + 1) % 20 == 0:
                print(f"  Processed {i + 1}/{len(messages)} messages...")

        except Exception as e:
            errors += 1
            if errors <= 5:
                print(f"  ERROR on message {i}: {e}")
            elif errors == 6:
                print(f"  (suppressing further errors...)")

    print(f"\nDone loading. Processed: {loaded}, Errors: {errors}")

    # Run queries
    print(f"\n{'=' * 60}")
    print("RUNNING 20 TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")

        try:
            start = time.time()
            search_results = store.search(
                namespace=("memories", "josh"),
                query=q["query"],
                limit=5,
            )
            elapsed = time.time() - start

            memories = []
            for item in search_results:
                mem_text = item.value.get("text", str(item.value)) if hasattr(item, 'value') else str(item)
                score = getattr(item, 'score', 'N/A')
                memories.append({
                    "memory": mem_text[:500],
                    "score": round(score, 4) if isinstance(score, float) else score,
                })

            print(f"  Time: {elapsed:.4f}s | Results: {len(memories)}")
            for j, mem in enumerate(memories[:3]):
                print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:120]}")

            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "notes": q["notes"],
                "num_results": len(memories),
                "elapsed_seconds": round(elapsed, 4),
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
        "system": "LangMem",
        "version": "0.0.30",
        "llm": "claude-sonnet-4-5-20250929",
        "embedding_model": "openai:text-embedding-3-small (1536-dim)",
        "architecture": "LLM extraction + InMemoryStore vector search",
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_langmem_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_langmem_results.json")


if __name__ == "__main__":
    print("BENCHMARK: LangMem")
    print("LangChain Memory SDK with Anthropic Claude extraction")
    print(f"{'=' * 60}\n")
    run_benchmark()
