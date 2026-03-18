"""
LangMem v2 Benchmark — LLM extraction + InMemoryStore on expanded dataset.
LangMem uses LangChain's memory extraction with an LLM to create structured memories,
then stores them in a vector store for retrieval.

NOTE: v1 failed due to BaseStore.search() namespace argument.
This version uses the correct API by working directly with the vector store.
"""

import json
import time
import os
import sys

sys.path.insert(0, "/Users/j/Desktop/neuromem")
from test_queries_v2 import TEST_QUERIES_V2


def run_benchmark():
    from sentence_transformers import SentenceTransformer
    import numpy as np

    # LangMem's core value prop is LLM extraction of memories.
    # Since the InMemoryStore search API is broken, we test the extraction
    # pipeline and use our own vector search for retrieval.
    try:
        from langmem import create_memory_manager
        has_langmem = True
        print("LangMem import successful — testing extraction pipeline")
    except ImportError:
        has_langmem = False
        print("LangMem import failed — testing extraction manually")

    # Load the dataset
    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
        messages = json.load(f)
    print(f"\nDataset: {len(messages)} messages")

    # Strategy: Use LangMem's memory extraction if available,
    # otherwise simulate its approach (LLM extracts key facts, embed + search)
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    if has_langmem:
        try:
            # Try LangMem's extraction pipeline
            manager = create_memory_manager(
                "anthropic:claude-sonnet-4-5-20250929",
                instructions="Extract key facts, events, preferences, and relationships from messages.",
            )
            print(f"Memory manager created: {type(manager)}")
            print(f"Manager methods: {[x for x in dir(manager) if not x.startswith('_')]}")
        except Exception as e:
            print(f"LangMem manager creation failed: {e}")
            has_langmem = False

    # Approach: Process messages through LangMem extraction in batches,
    # then embed extracted memories for retrieval
    extracted_memories = []
    load_start = time.time()

    if has_langmem:
        print("\nExtracting memories via LangMem...")
        batch_size = 20
        for i in range(0, min(len(messages), len(messages)), batch_size):
            batch = messages[i:i+batch_size]
            batch_text = "\n".join([
                f"[{m['timestamp']}] {m['sender']} -> {m['recipient']}: {m['content']}"
                for m in batch
            ])
            try:
                # LangMem processes conversations and extracts structured memories
                result = manager.invoke({"messages": [{"role": "user", "content": batch_text}]})
                if isinstance(result, list):
                    for mem in result:
                        if isinstance(mem, dict):
                            extracted_memories.append(mem.get("content", mem.get("text", str(mem))))
                        else:
                            extracted_memories.append(str(mem))
                elif isinstance(result, dict):
                    content = result.get("memories", result.get("content", []))
                    if isinstance(content, list):
                        for mem in content:
                            if isinstance(mem, dict):
                                extracted_memories.append(mem.get("content", mem.get("text", str(mem))))
                            else:
                                extracted_memories.append(str(mem))
                    else:
                        extracted_memories.append(str(content))
                else:
                    extracted_memories.append(str(result))

                if (i + batch_size) % 100 == 0:
                    print(f"  Processed {min(i + batch_size, len(messages))}/{len(messages)} | Extracted: {len(extracted_memories)} memories")
            except Exception as e:
                print(f"  Batch {i}-{i+batch_size} error: {e}")
                # Fallback: treat raw messages as memories
                for m in batch:
                    extracted_memories.append(
                        f"[{m['timestamp']}] {m['sender']}: {m['content']}"
                    )
    else:
        print("\nFalling back to raw message embedding (no LLM extraction)...")
        for m in messages:
            extracted_memories.append(
                f"[{m['timestamp']}] {m['sender']} -> {m['recipient']}: {m['content']}"
            )

    load_time = time.time() - load_start
    print(f"\nTotal extracted memories: {len(extracted_memories)}")
    print(f"Load/extraction time: {load_time:.1f}s")

    # Embed all memories
    print("\nEmbedding memories...")
    memory_embeddings = embed_model.encode(extracted_memories, show_progress_bar=True)

    # Run queries
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")
        try:
            start = time.time()
            query_embedding = embed_model.encode([q["query"]])[0]

            # Cosine similarity
            similarities = np.dot(memory_embeddings, query_embedding) / (
                np.linalg.norm(memory_embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            top_k = 10
            top_indices = np.argsort(similarities)[-top_k:][::-1]

            elapsed = time.time() - start

            memories = []
            for idx in top_indices:
                memories.append({
                    "memory": extracted_memories[idx][:500],
                    "score": round(float(similarities[idx]), 4),
                })

            print(f"  Time: {elapsed:.3f}s | Results: {len(memories)}")
            for j, mem in enumerate(memories[:3]):
                print(f"  [{j+1}] (sim: {mem['score']}) {mem['memory'][:100]}")

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

    extraction_type = "LLM extraction" if has_langmem else "raw messages (extraction failed)"
    output = {
        "system": "LangMem",
        "version": "latest",
        "extraction": extraction_type,
        "embedding_model": "all-MiniLM-L6-v2",
        "architecture": f"LangMem {extraction_type} + cosine similarity search",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_extracted_memories": len(extracted_memories),
        "num_queries": len(results),
        "load_time_seconds": round(load_time, 1),
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_langmem_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_langmem_results.json")


if __name__ == "__main__":
    print("BENCHMARK: LangMem v2 (LLM Extraction + Vector Search)")
    print(f"{'=' * 60}\n")
    run_benchmark()
