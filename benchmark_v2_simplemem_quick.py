"""
SimpleMem v2 Benchmark — Quick version.
add_dialogue is instant (no LLM needed).
ask() needs OpenAI gpt-4.1-mini — will fallback to hybrid_retriever if no key.
"""

import json
import time
import sys

sys.path.insert(0, "/Users/j/Desktop/neuromem")
sys.stdout.reconfigure(line_buffering=True)  # Force line-buffered output
from test_queries_v2 import TEST_QUERIES_V2

import simplemem
from simplemem import Dialogue

print(f"SimpleMem version: {simplemem.__version__}", flush=True)

system = simplemem.create_system()
print(f"System created. LLM: {system.llm_client.model} (key: {'set' if system.llm_client.api_key else 'EMPTY'})", flush=True)

with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
    messages = json.load(f)

print(f"\nDataset: {len(messages)} messages", flush=True)

# Load messages
print("Loading messages...", flush=True)
start_time = time.time()
loaded = 0
errors = 0

for i, msg in enumerate(messages):
    try:
        content = f"[{msg.get('modality', 'imessage')}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"
        system.add_dialogue(
            speaker=msg["sender"],
            content=content,
            timestamp=msg["timestamp"],
        )
        loaded += 1
    except Exception as e:
        errors += 1
        if errors <= 3:
            print(f"  Error at msg {i}: {e}", flush=True)

load_time = time.time() - start_time
print(f"Loaded: {loaded}, Errors: {errors}, Time: {load_time:.1f}s", flush=True)

# Check stored memories
try:
    all_mems = system.get_all_memories()
    print(f"Total stored memories: {len(all_mems)}", flush=True)
except Exception as e:
    print(f"get_all_memories: {e}", flush=True)

# Try retriever directly (skip ask() which needs OpenAI)
print(f"\n{'=' * 60}", flush=True)
print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES (hybrid retriever)", flush=True)
print(f"{'=' * 60}\n", flush=True)

results = []
for q in TEST_QUERIES_V2:
    print(f"Q{q['id']} [{q['category']}]: {q['query']}", flush=True)
    try:
        start = time.time()

        # Try ask() first (needs OpenAI)
        try:
            answer = system.ask(q["query"])
            elapsed = time.time() - start
            print(f"  Time: {elapsed:.3f}s | ask() answer: {str(answer)[:150]}", flush=True)
            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "num_results": 1,
                "elapsed_seconds": round(elapsed, 3),
                "results": [{"memory": str(answer)[:500], "score": "N/A"}],
                "mode": "ask",
            })
        except Exception as ask_err:
            # Fallback: use vector store search directly
            elapsed_ask = time.time() - start
            print(f"  ask() failed ({elapsed_ask:.1f}s): {str(ask_err)[:80]}", flush=True)
            print(f"  Trying vector store...", flush=True)

            start2 = time.time()
            try:
                vs = system.vector_store
                # Try search on vector store
                search_method = None
                for method_name in ['search', 'query', 'similarity_search']:
                    if hasattr(vs, method_name):
                        search_method = getattr(vs, method_name)
                        break

                if search_method:
                    vs_results = search_method(q["query"])
                    elapsed = time.time() - start2
                    memories = []
                    if vs_results:
                        for item in vs_results[:10]:
                            if isinstance(item, dict):
                                memories.append({"memory": str(item)[:500], "score": "N/A"})
                            else:
                                memories.append({"memory": str(item)[:500], "score": "N/A"})
                    print(f"  Vector store: {len(memories)} results in {elapsed:.3f}s", flush=True)
                    for j, mem in enumerate(memories[:3]):
                        print(f"  [{j+1}] {mem['memory'][:100]}", flush=True)
                    results.append({
                        "query_id": q["id"],
                        "query": q["query"],
                        "category": q["category"],
                        "expected": q["expected"],
                        "scoring_notes": q["scoring_notes"],
                        "num_results": len(memories),
                        "elapsed_seconds": round(elapsed, 3),
                        "results": memories,
                        "mode": "vector_store",
                    })
                else:
                    print(f"  No search method found on vector store", flush=True)
                    # Try embedding-based search manually
                    query_emb = system.embedding_model.encode([q["query"]])
                    vs_table = vs.table if hasattr(vs, 'table') else None
                    if vs_table:
                        search_results = vs_table.search(query_emb[0].tolist()).limit(10).to_list()
                        elapsed = time.time() - start2
                        memories = [{"memory": str(r)[:500], "score": r.get('_distance', 'N/A')} for r in search_results]
                        print(f"  LanceDB search: {len(memories)} results in {elapsed:.3f}s", flush=True)
                        results.append({
                            "query_id": q["id"],
                            "query": q["query"],
                            "category": q["category"],
                            "expected": q["expected"],
                            "scoring_notes": q["scoring_notes"],
                            "num_results": len(memories),
                            "elapsed_seconds": round(elapsed, 3),
                            "results": memories,
                            "mode": "lancedb_direct",
                        })
                    else:
                        raise Exception("No search method available")
            except Exception as e2:
                elapsed = time.time() - start2
                print(f"  Fallback also failed: {e2}", flush=True)
                results.append({
                    "query_id": q["id"],
                    "query": q["query"],
                    "category": q["category"],
                    "expected": q["expected"],
                    "scoring_notes": q["scoring_notes"],
                    "error": f"ask: {str(ask_err)[:200]}; fallback: {str(e2)[:200]}",
                    "num_results": 0,
                    "elapsed_seconds": round(elapsed, 3),
                    "results": [],
                })
    except Exception as e:
        print(f"  ERROR: {e}", flush=True)
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
    print(flush=True)

output = {
    "system": "SimpleMem",
    "version": "0.1.0",
    "embedding_model": "Qwen3-Embedding-0.6B (1024-dim)",
    "llm": f"{system.llm_client.model} (key: {'set' if system.llm_client.api_key else 'EMPTY'})",
    "architecture": "Semantic compression + Qwen3 embeddings + LanceDB",
    "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
    "num_queries": len(results),
    "load_time_seconds": round(load_time, 1),
    "results": results,
}

with open("/Users/j/Desktop/neuromem/benchmark_v2_simplemem_results.json", "w") as f:
    json.dump(output, f, indent=2)
print("Results saved to benchmark_v2_simplemem_results.json", flush=True)
