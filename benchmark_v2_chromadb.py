"""
ChromaDB v2 Benchmark — Raw vector search on the expanded dataset.
Tests pure embedding similarity without any LLM intelligence.
This is the BASELINE — if other systems can't beat raw vectors, they're not adding value.
"""

import json
import time
import chromadb
from sentence_transformers import SentenceTransformer

from test_queries_v2 import TEST_QUERIES_V2

def run_benchmark():
    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
        messages = json.load(f)

    print(f"Loading {len(messages)} messages into ChromaDB...")
    print("=" * 60)

    client = chromadb.EphemeralClient()
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    collection = client.create_collection(
        name="benchmark_v2",
        metadata={"hnsw:space": "cosine"},
    )

    # Batch add for speed
    batch_size = 100
    for i in range(0, len(messages), batch_size):
        batch = messages[i:i+batch_size]
        ids = [f"msg_{i+j}" for j in range(len(batch))]
        docs = [m["content"] for m in batch]
        metas = [{
            "sender": m["sender"],
            "recipient": m["recipient"],
            "timestamp": m["timestamp"],
            "category": m["category"],
            "modality": m.get("modality", "unknown"),
            "date": m["timestamp"][:10],
            "month": m["timestamp"][:7],
        } for m in batch]

        embeddings = embed_model.encode(docs).tolist()
        collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

        if (i + batch_size) % 200 == 0 or i + batch_size >= len(messages):
            print(f"  Loaded {min(i + batch_size, len(messages))}/{len(messages)} messages")

    print(f"\nCollection has {collection.count()} documents")

    # Run queries
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")

        start = time.time()
        query_embedding = embed_model.encode([q["query"]]).tolist()

        # Get top 10 results
        search_results = collection.query(
            query_embeddings=query_embedding,
            n_results=10,
            include=["documents", "metadatas", "distances"],
        )

        elapsed = time.time() - start

        memories = []
        if search_results and search_results["documents"]:
            for j, (doc, meta, dist) in enumerate(zip(
                search_results["documents"][0],
                search_results["metadatas"][0],
                search_results["distances"][0],
            )):
                score = round(1 - dist, 4)  # Convert distance to similarity
                memories.append({
                    "memory": doc[:500],
                    "score": score,
                    "sender": meta.get("sender", ""),
                    "timestamp": meta.get("timestamp", ""),
                    "modality": meta.get("modality", ""),
                })

        print(f"  Time: {elapsed:.3f}s | Results: {len(memories)}")
        for j, mem in enumerate(memories[:3]):
            print(f"  [{j+1}] (sim: {mem['score']}) [{mem['modality']}] {mem['memory'][:100]}")

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
        print()

    # Save
    output = {
        "system": "ChromaDB",
        "version": "1.5.5",
        "embedding_model": "all-MiniLM-L6-v2",
        "architecture": "Pure vector similarity search (no LLM)",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_queries": len(results),
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_chromadb_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_chromadb_results.json")


if __name__ == "__main__":
    print("BENCHMARK: ChromaDB v2 (Pure Vector Search)")
    print(f"{'=' * 60}\n")
    run_benchmark()
