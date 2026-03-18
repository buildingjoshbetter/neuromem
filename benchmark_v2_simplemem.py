"""
SimpleMem v2 Benchmark — Semantic compression + retrieval.
SimpleMem uses a 3-stage pipeline: Compression -> Synthesis -> Retrieval.
From the academic paper: +64% over Claude-Mem on LoCoMo.

API: add_dialogue(speaker, content, timestamp) and ask(question) -> str
Uses Qwen3-Embedding-0.6B for embeddings (local, no API key needed for embeddings).
NOTE: ask() likely needs an LLM — may need OpenAI or we test retrieval only.
"""

import json
import time
import os
import sys

sys.path.insert(0, "/Users/j/Desktop/neuromem")
from test_queries_v2 import TEST_QUERIES_V2


def run_benchmark():
    import simplemem
    from simplemem import Dialogue

    print(f"SimpleMem version: {simplemem.__version__}")

    system = simplemem.create_system()
    print(f"System created: {type(system)}")

    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
        messages = json.load(f)

    print(f"\nDataset: {len(messages)} messages")
    print("=" * 60)

    # Load messages using add_dialogue
    print("\nLoading messages...")
    loaded = 0
    errors = 0
    start_time = time.time()

    for i, msg in enumerate(messages):
        try:
            # SimpleMem expects speaker, content, timestamp
            content = f"[{msg.get('modality', 'imessage')}] {msg['sender']} -> {msg['recipient']}: {msg['content']}"
            system.add_dialogue(
                speaker=msg["sender"],
                content=content,
                timestamp=msg["timestamp"],
            )
            loaded += 1
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = loaded / elapsed
                print(f"  Loaded {i + 1}/{len(messages)} ({rate:.1f} msg/s)...")
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"  Error at msg {i}: {e}")
            if errors == 4:
                print(f"  (suppressing further errors)")

    load_time = time.time() - start_time
    print(f"\nLoaded: {loaded}, Errors: {errors}, Time: {load_time:.1f}s")

    if loaded == 0:
        print("No messages loaded. Aborting.")
        return

    # Try to finalize (some systems need this)
    try:
        system.finalize()
        print("System finalized")
    except Exception as e:
        print(f"Finalize: {e}")

    # Check stored memories
    try:
        all_mems = system.get_all_memories()
        print(f"Total stored memories: {len(all_mems)}")
        if all_mems:
            print(f"Sample memory: {str(all_mems[0])[:200]}")
    except Exception as e:
        print(f"get_all_memories: {e}")

    # Run queries using ask()
    print(f"\n{'=' * 60}")
    print(f"RUNNING {len(TEST_QUERIES_V2)} TEST QUERIES")
    print(f"{'=' * 60}\n")

    results = []
    ask_available = True

    for q in TEST_QUERIES_V2:
        print(f"Q{q['id']} [{q['category']}]: {q['query']}")
        try:
            start = time.time()

            if ask_available:
                try:
                    answer = system.ask(q["query"])
                    elapsed = time.time() - start
                    print(f"  Time: {elapsed:.3f}s")
                    print(f"  Answer: {str(answer)[:200]}")

                    results.append({
                        "query_id": q["id"],
                        "query": q["query"],
                        "category": q["category"],
                        "expected": q["expected"],
                        "scoring_notes": q["scoring_notes"],
                        "num_results": 1 if answer else 0,
                        "elapsed_seconds": round(elapsed, 3),
                        "results": [{"memory": str(answer)[:500], "score": "N/A"}] if answer else [],
                        "answer": str(answer)[:1000],
                    })
                except Exception as e:
                    err_msg = str(e)
                    if "api_key" in err_msg.lower() or "openai" in err_msg.lower() or "authentication" in err_msg.lower():
                        print(f"  ask() needs API key: {err_msg[:100]}")
                        print("  Switching to retrieval-only mode...")
                        ask_available = False
                        # Fall through to retrieval
                    else:
                        raise

            if not ask_available:
                # Use hybrid_retriever directly
                try:
                    retrieval_results = system.hybrid_retriever.search(q["query"], top_k=10)
                    elapsed = time.time() - start

                    memories = []
                    if retrieval_results:
                        for item in retrieval_results[:10]:
                            if isinstance(item, dict):
                                mem_text = item.get("text", item.get("content", str(item)))
                                score = item.get("score", "N/A")
                            elif hasattr(item, 'content'):
                                mem_text = str(item.content)
                                score = getattr(item, 'score', 'N/A')
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
                except Exception as e2:
                    print(f"  Retriever also failed: {e2}")
                    results.append({
                        "query_id": q["id"],
                        "query": q["query"],
                        "category": q["category"],
                        "expected": q["expected"],
                        "scoring_notes": q["scoring_notes"],
                        "error": str(e2),
                        "num_results": 0,
                        "elapsed_seconds": 0,
                        "results": [],
                    })

        except Exception as e:
            elapsed = time.time() - start
            print(f"  ERROR: {e}")
            results.append({
                "query_id": q["id"],
                "query": q["query"],
                "category": q["category"],
                "expected": q["expected"],
                "scoring_notes": q["scoring_notes"],
                "error": str(e),
                "num_results": 0,
                "elapsed_seconds": round(elapsed, 3),
                "results": [],
            })
        print()

    mode = "ask (LLM answer)" if ask_available else "retrieval only"
    output = {
        "system": "SimpleMem",
        "version": "0.1.0",
        "embedding_model": "Qwen3-Embedding-0.6B",
        "architecture": f"Semantic compression + retrieval ({mode})",
        "dataset": "synthetic_v2 (797 messages, 21 months, 7 modalities)",
        "num_queries": len(results),
        "load_time_seconds": round(load_time, 1),
        "mode": mode,
        "results": results,
    }

    with open("/Users/j/Desktop/neuromem/benchmark_v2_simplemem_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print("Results saved to benchmark_v2_simplemem_results.json")


if __name__ == "__main__":
    print("BENCHMARK: SimpleMem v2")
    print(f"{'=' * 60}\n")
    run_benchmark()
