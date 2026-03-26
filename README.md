# Neuromem

A 6-layer memory system for AI agents that approaches human-like recall. Stores conversations in a single SQLite file, indexes them with hybrid search (FTS5 keyword + vector embeddings), and uses LLM-generated episodes to bridge vocabulary gaps during retrieval.

**91.2% on LoCoMo** — within 1.6 points of the leading system (EverMemOS, 92.8%) at a fraction of the cost and complexity.

## Why Neuromem

Most memory systems store flat facts in a vector database and call it done. That approach tops out around 68% accuracy on standard benchmarks because vector-only retrieval misses exact-match queries, has no concept of importance, and can't reason about time.

Neuromem takes a different approach: six specialized layers that each solve a distinct retrieval problem, fused together through Reciprocal Rank Fusion. The result is near-SOTA accuracy on a single SQLite file with zero cloud infrastructure.

| | Neuromem | Typical Memory System |
|--|----------|----------------------|
| **Search** | Hybrid (FTS5 keyword + vector semantic + cross-encoder reranking) | Vector-only |
| **Importance** | Multi-signal salience scoring (length, novelty, emotional weight, information density) | None — all memories treated equally |
| **Time** | Explicit temporal parsing with SQL-level date filtering | Timestamps exist but aren't used in retrieval |
| **Personality** | Pre-computed 5-dimension entity profiles | Text blob summaries |
| **Consolidation** | Active contradiction tracking + temporal fact timelines | Reactive only (on new data) |
| **Infrastructure** | Single SQLite file, runs offline | Qdrant/Pinecone + external embedding API + graph DB |

## Benchmark Results

All benchmarks use identical controlled methodology: same answer model (GPT-4.1-mini), same judge model (GPT-4o-mini), 3 judge runs at temperature 0.

### LoCoMo (10 conversations, 1,540 questions)

| System | J-Score | Notes |
|--------|---------|-------|
| EverMemOS | 92.77% | Multi-query + Qwen3-4B embeddings + sufficiency checking |
| **Neuromem** | **91.21% ± 0.50%** | Hybrid search + Qwen3-0.6B embeddings + mxbai reranker |
| Mem0 + Graph | 68.44% | Vector search + Neo4j graph |
| Mem0 | 66.88% | Vector search only |
| No Retrieval | 5.67% | Baseline (proves retrieval adds value) |

Neuromem's progression: **72.3%** (v2) → **87.7%** (v3, retrieval tuning) → **91.2%** (Phase 1, upgraded embedding + reranker models). Each jump came from architectural improvements, not prompt engineering.

### Cross-Benchmark Comparison

| Benchmark | Neuromem | Mem0 | Gap |
|-----------|----------|------|-----|
| LoCoMo | **91.2%** | 68.4% | +22.8 |
| LongMemEval | **72.4%** | 49.0% | +23.4 |
| Custom (120q) | **75.8%** | 55.0% | +20.8 |

See [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) for full methodology, per-category breakdowns, failure analysis, and runtime comparisons.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       NeuromemEngine                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  L0  Personality Engram                                      │
│      Entity profiles across 5 dimensions: communication      │
│      style, preferences, fears, routines, values             │
│                                                              │
│  L2  Episodic Search (FTS5)                                  │
│      BM25 keyword ranking + Porter stemming                  │
│      Auto-synced via INSERT/DELETE triggers                   │
│                                                              │
│  L3  Semantic Search (Qwen3-Embedding-0.6B + sqlite-vec)     │
│      1024-dim embeddings on GPU / 256-dim fallback on CPU    │
│      Reciprocal Rank Fusion with L2                          │
│                                                              │
│  L4  Salience Guard                                          │
│      Noise filtering, entity disambiguation, importance      │
│      scoring (length, novelty, emotional weight, specificity)│
│                                                              │
│  L5  Consolidation + Predictive Coding                       │
│      Contradiction tracking with temporal fact timelines      │
│      Entity summaries, surprise scoring (prediction errors)  │
│                                                              │
│  +   Episode Extraction (LLM)                                │
│      Third-person narratives + atomic facts per session       │
│                                                              │
│  +   Agentic Search                                          │
│      HyDE query expansion, multi-round retrieval,            │
│      cross-encoder reranking, HDBSCAN scene clustering       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Every module is optional. If vector search fails, the engine falls back to FTS5. If the reranker is missing, it skips reranking. The system always returns results.

## How Search Works

### Standard Search

```
Query → Classify intent → Hybrid search (FTS5 + vectors via RRF)
  → Temporal filtering (if time-related)
  → Personality lookup (if entity-related)
  → Contradiction check (if factual)
  → Salience scoring → Results
```

### Agentic Search

```
Query → Standard search + HyDE + cluster search + entity search
  → Sufficiency check: are top-5 results high-quality and diverse?
  → If insufficient: LLM generates refined sub-queries → re-search
  → Cross-encoder reranking (40% retrieval + 60% reranker score)
  → Results
```

## Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Storage | SQLite + WAL mode | $0 |
| Full-text search | FTS5 with BM25 ranking | $0 |
| Vector search | sqlite-vec (Qwen3-Embedding-0.6B, 1024-dim) | $0 (local GPU) |
| Reranker | mxbai-rerank-large-v1 (435M params) | $0 (local GPU) |
| Episode extraction | Claude Haiku | ~$0.50 per 10 conversations |
| Search fusion | Reciprocal Rank Fusion | $0 |
| HyDE query expansion | Any LLM | ~$0.001 per query |

**Total infrastructure cost: $0/month.** LLM costs for episode extraction and HyDE are the only variable expense (~$12/month at 100 queries/day).

## Modules

| Module | File | Purpose |
|--------|------|---------|
| Engine | `engine.py` | Main orchestrator — ties all layers together |
| Storage | `storage.py` | SQLite schema, message CRUD, FTS5 triggers |
| FTS Search | `fts_search.py` | BM25 full-text search with score normalization |
| Vector Search | `vector_search.py` | Embedding-based semantic search via sqlite-vec |
| Hybrid | `hybrid.py` | RRF fusion of FTS5 + vector results |
| Temporal | `temporal.py` | Date parsing, time-window filtering, episode detection |
| Salience | `salience.py` | Noise filtering, entity disambiguation, importance scoring |
| Personality | `personality.py` | L0 entity profiles, preferences, communication style |
| Consolidation | `consolidation.py` | Summaries, contradiction tracking, structured facts |
| Predictive | `predictive.py` | Surprise scoring, predictive coding filter |
| Episodes | `episodes.py` | LLM-based episode extraction (narratives + atomic facts) |
| HyDE | `hyde.py` | Hypothetical document embeddings for query enhancement |
| Reranker | `reranker.py` | Cross-encoder reranking |
| Clustering | `clustering.py` | HDBSCAN scene clustering for episode-scoped retrieval |
| Query Classifier | `query_classifier.py` | Query type detection + adaptive search weights |

## Quick Start

```python
from neuromem import NeuromemEngine

engine = NeuromemEngine("my_memory.db")
stats = engine.ingest("conversations.json")

# Standard 6-layer search
results = engine.search("What did they talk about?", limit=10)

# Agentic search (HyDE + multi-round + reranking)
results = engine.search_agentic(
    "When did they go on vacation?",
    llm_fn=my_llm_function,
    use_hyde=True,
    use_reranker=True,
    use_clustering=True,
)
```

## Design Principles

1. **Graceful degradation** — every module is optional. Partial failures never block the pipeline.
2. **$0 infrastructure** — SQLite for everything. No Elasticsearch, no Redis, no Milvus, no cloud vector DB.
3. **Composable** — each layer can be toggled on/off independently for A/B testing.
4. **Measurable** — every step is timed so you can see exactly which layers add value.
5. **Local-first** — embeddings and reranking run on-device. No data leaves your machine unless you opt into LLM-powered features.

## What's Next

- Richer episode extraction (multi-pass: profiles, QA pairs, entity relationships)
- Temporal normalization at ingest time (resolve "last month" → ISO dates during storage, not search)
- Multi-hop query decomposition (break complex questions into sub-queries automatically)
- Larger embedding models for further accuracy gains

## License

MIT
