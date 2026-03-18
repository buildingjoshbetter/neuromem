"""
Benchmark: ChromaDB (Raw Vector Search + Metadata Filtering)
============================================================
ChromaDB is a vector database, NOT a memory system. It stores raw documents
as embeddings and retrieves by cosine similarity. No LLM extraction.

This tests: how good is raw vector search compared to Mem0's LLM-extracted facts?
Key advantage: ChromaDB supports metadata filtering (by sender, date, etc.)

We test TWO modes:
1. "dumb" - pure semantic search (apples-to-apples with Mem0)
2. "smart" - semantic search + metadata filtering (what ChromaDB actually offers)
"""

import json
import time
import chromadb
from test_queries import TEST_QUERIES

# Use the same embedding model as Mem0 test for fair comparison
# ChromaDB defaults to all-MiniLM-L6-v2 (384-dim) which is what Mem0 used

def load_data():
    """Load synthetic messages into ChromaDB."""
    with open("/Users/j/Desktop/neuromem/synthetic_messages.json") as f:
        messages = json.load(f)

    client = chromadb.EphemeralClient()

    # Create collection with default embeddings (all-MiniLM-L6-v2)
    collection = client.create_collection(
        name="benchmark",
        metadata={"hnsw:space": "cosine"}
    )

    print(f"Loading {len(messages)} messages into ChromaDB...")

    ids = []
    documents = []
    metadatas = []

    for i, msg in enumerate(messages):
        # Store raw message content (NOT LLM-extracted facts)
        content = f"{msg['sender']} -> {msg['recipient']}: {msg['content']}"

        ids.append(f"msg_{i}")
        documents.append(content)
        metadatas.append({
            "sender": msg["sender"],
            "recipient": msg["recipient"],
            "category": msg["category"],
            "timestamp": msg["timestamp"],
            # Extract date for easier filtering
            "date": msg["timestamp"][:10],  # "2026-02-15"
        })

    # Batch add all at once
    start = time.time()
    collection.add(ids=ids, documents=documents, metadatas=metadatas)
    elapsed = time.time() - start
    print(f"Loaded {len(messages)} messages in {elapsed:.2f}s")

    return collection, messages


def run_queries_dumb(collection):
    """Mode 1: Pure semantic search, no metadata filtering. Like Mem0."""
    print(f"\n{'=' * 60}")
    print("MODE 1: DUMB (Pure Semantic Search - Mem0 equivalent)")
    print(f"{'=' * 60}\n")

    results = []
    for q in TEST_QUERIES:
        start = time.time()
        search_results = collection.query(
            query_texts=[q["query"]],
            n_results=5,
        )
        elapsed = time.time() - start

        memories = []
        if search_results and search_results["documents"]:
            for j, doc in enumerate(search_results["documents"][0]):
                memories.append({
                    "memory": doc[:500],
                    "score": round(1 - search_results["distances"][0][j], 4) if search_results["distances"] else "N/A",
                    "metadata": search_results["metadatas"][0][j] if search_results["metadatas"] else {},
                })

        print(f"Q{q['id']} [{q['category']}]: {q['query']}")
        print(f"  Time: {elapsed:.4f}s | Results: {len(memories)}")
        for j, mem in enumerate(memories[:3]):
            print(f"  [{j+1}] (score: {mem['score']}) {mem['memory'][:120]}")
        print()

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

    return results


def run_queries_smart(collection):
    """Mode 2: Semantic search + metadata filtering. ChromaDB's real strength."""
    print(f"\n{'=' * 60}")
    print("MODE 2: SMART (Semantic Search + Metadata Filtering)")
    print(f"{'=' * 60}\n")

    # Define smart filters for queries that benefit from metadata
    smart_filters = {
        # Temporal queries: filter by date range
        9: {"date": {"$gte": "2026-02-22"}},  # "this week" = last week of data
        10: {"date": {"$lte": "2026-02-14"}},  # "last month" = early data
        11: None,  # No useful filter for "when is parents visit"
        12: {"date": {"$gte": "2026-02-20"}},  # "upcoming events" = recent msgs

        # Entity queries: filter by sender/recipient
        13: {"$or": [{"sender": "marcus"}, {"recipient": "marcus"}]},  # Marcus convos
        14: None,  # "Alex vs Sarah" needs two separate queries
        15: None,  # "Who is Priya" - search across all
        16: {"$or": [{"sender": "alex"}, {"recipient": "alex"}]},  # Alex convos
    }

    results = []
    for q in TEST_QUERIES:
        where_filter = smart_filters.get(q["id"])

        start = time.time()
        kwargs = {
            "query_texts": [q["query"]],
            "n_results": 5,
        }
        if where_filter:
            kwargs["where"] = where_filter

        try:
            search_results = collection.query(**kwargs)
        except Exception as e:
            # Fall back to no filter if the filter fails
            print(f"  Filter failed for Q{q['id']}: {e}, falling back to no filter")
            search_results = collection.query(
                query_texts=[q["query"]],
                n_results=5,
            )
        elapsed = time.time() - start

        memories = []
        if search_results and search_results["documents"]:
            for j, doc in enumerate(search_results["documents"][0]):
                memories.append({
                    "memory": doc[:500],
                    "score": round(1 - search_results["distances"][0][j], 4) if search_results["distances"] else "N/A",
                    "metadata": search_results["metadatas"][0][j] if search_results["metadatas"] else {},
                })

        filtered = " [FILTERED]" if where_filter else ""
        print(f"Q{q['id']} [{q['category']}]{filtered}: {q['query']}")
        print(f"  Time: {elapsed:.4f}s | Results: {len(memories)}")
        for j, mem in enumerate(memories[:3]):
            ts = mem.get("metadata", {}).get("timestamp", "")
            print(f"  [{j+1}] (score: {mem['score']}) [{ts}] {mem['memory'][:100]}")
        print()

        results.append({
            "query_id": q["id"],
            "query": q["query"],
            "category": q["category"],
            "expected": q["expected"],
            "notes": q["notes"],
            "num_results": len(memories),
            "elapsed_seconds": round(elapsed, 4),
            "results": memories,
            "filter_used": str(where_filter) if where_filter else "none",
        })

    return results


def save_results(dumb_results, smart_results):
    """Save both sets of results."""
    output = {
        "system": "ChromaDB",
        "version": chromadb.__version__,
        "embedding_model": "all-MiniLM-L6-v2 (384-dim, default)",
        "architecture": "Raw vector search + metadata filtering (no LLM extraction)",
        "dumb_mode": dumb_results,
        "smart_mode": smart_results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_chromadb_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_chromadb_results.json")


if __name__ == "__main__":
    print("BENCHMARK: ChromaDB")
    print("Raw vector search baseline (no LLM extraction)")
    print(f"{'=' * 60}\n")

    collection, messages = load_data()

    # Mode 1: Dumb (pure semantic, like Mem0)
    dumb_results = run_queries_dumb(collection)

    # Mode 2: Smart (semantic + metadata filtering)
    smart_results = run_queries_smart(collection)

    save_results(dumb_results, smart_results)

    print(f"\n{'=' * 60}")
    print("DONE. Compare with m1_results.json (Mem0) to see if LLM extraction helps.")
