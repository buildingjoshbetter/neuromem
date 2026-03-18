# Neuromem

A 6-layer memory system for AI agents. Stores conversations in SQLite, indexes them with full-text search (FTS5) and vector embeddings (Model2Vec), then uses LLM-generated episode summaries to bridge vocabulary gaps during retrieval. All storage and retrieval is local and free — LLM costs only for episode extraction and answer generation.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  NeuromemEngine                      │
├─────────────────────────────────────────────────────┤
│  L0  Personality Engram                             │
│      Entity profiles, communication patterns,       │
│      preferences, Dunbar hierarchy                  │
│                                                     │
│  L1  Working Memory (deferred)                      │
│                                                     │
│  L2  Episodic (FTS5)                                │
│      Full-text keyword search with BM25 ranking     │
│      Porter stemming + unicode tokenizer            │
│      Auto-synced via INSERT/DELETE triggers          │
│                                                     │
│  L3  Semantic (Model2Vec + sqlite-vec)              │
│      potion-base-8M, 256-dim embeddings             │
│      Reciprocal Rank Fusion with FTS5               │
│                                                     │
│  L4  Salience Guard                                 │
│      Noise filtering, entity boosting               │
│      Mode-aware thresholds (spotlight vs diffuse)   │
│                                                     │
│  L5  Consolidation + Predictive Coding              │
│      Summaries, contradiction detection,            │
│      surprise scoring, structured facts             │
│                                                     │
│  +   Episode Extraction (LLM)                       │
│      Third-person narratives + atomic facts          │
│      per conversation session                       │
│                                                     │
│  +   Agentic Search                                 │
│      HyDE, multi-round retrieval, cross-encoder     │
│      reranking, HDBSCAN clustering                  │
└─────────────────────────────────────────────────────┘
```

## Stack

- **Storage:** SQLite + WAL mode + FTS5 (full-text) + sqlite-vec (vectors)
- **Embeddings:** Model2Vec (potion-base-8M, 256-dim) — runs locally, no API
- **Reranker:** ms-marco-MiniLM-L6-v2 cross-encoder — runs locally
- **Episode extraction:** Claude Haiku (LLM generates session summaries + atomic facts)
- **Search fusion:** Reciprocal Rank Fusion (RRF) combining FTS5 + vector scores
- **Cost:** $0/month for storage and retrieval. LLM costs only for episode extraction + HyDE query expansion.

## Modules

| Module | File | Purpose |
|--------|------|---------|
| Storage | `storage.py` | SQLite schema, message CRUD, FTS5 triggers |
| FTS Search | `fts_search.py` | BM25 full-text search with score normalization |
| Vector Search | `vector_search.py` | Model2Vec embeddings via sqlite-vec |
| Hybrid | `hybrid.py` | RRF fusion of FTS5 + vector results |
| Temporal | `temporal.py` | Date parsing, time-window filtering, episode detection |
| Salience | `salience.py` | Noise filtering, entity disambiguation |
| Personality | `personality.py` | L0 entity profiles, preferences, communication style |
| Consolidation | `consolidation.py` | Summaries, contradiction tracking, structured facts |
| Predictive | `predictive.py` | Surprise scoring, predictive coding filter |
| Episodes | `episodes.py` | LLM-based episode extraction (narratives + facts) |
| HyDE | `hyde.py` | Hypothetical document embeddings for query enhancement |
| Reranker | `reranker.py` | Cross-encoder reranking (MiniLM-L6-v2) |
| Clustering | `clustering.py` | HDBSCAN scene clustering for episode-scoped retrieval |
| Query Classifier | `query_classifier.py` | Query type detection + adaptive search weights |
| Engine | `engine.py` | Main orchestrator — ties all layers together |

## Search Pipeline

### Standard Search (6-layer)
1. Classify query → adaptive FTS/vector weights
2. Hybrid search: FTS5 (BM25) + Vector (cosine) → RRF fusion
3. Temporal filtering if time-related query detected
4. Personality supplementation if personality query detected
5. Contradiction/fact timeline check
6. Salience guard with mode-aware threshold

### Agentic Search (multi-round)
1. **Round 1:** Standard 6-layer + HyDE + cluster search + entity-focused search
2. **Sufficiency check:** Are top-5 results high-quality and diverse?
3. **Round 2** (if insufficient): LLM generates 2-3 refined sub-queries → each runs through 6-layer pipeline
4. **Final:** Cross-encoder reranking (40% original + 60% reranker score)

## Design Principles

1. **Graceful degradation** — every module is optional. If vectors fail → FTS5 only. If reranker missing → skip. Engine always returns results.
2. **$0 infrastructure** — SQLite for everything. No Elasticsearch, no Redis, no Milvus, no cloud vector DB.
3. **Composable** — each layer can be toggled on/off independently for A/B testing.
4. **Measurable** — every step is timed so you can see which layers add value.

## Benchmark Results

See [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) for detailed results.

### LoCoMo (10 conversations, 1540 questions)

Fair benchmark run on 2026-03-18. All systems used identical answer model (GPT-4.1-mini), judge model (GPT-4o-mini), 3 judge runs at temp=0, Category 5 excluded.

| System | J-Score | Cat 1 | Cat 2 | Cat 3 | Cat 4 |
|--------|---------|-------|-------|-------|-------|
| EverMemOS | 92.77% | 91.1% | 89.4% | 78.1% | 96.2% |
| **Neuromem** | **72.34%** | 59.2% | 72.9% | 52.1% | 79.0% |
| No Retrieval | 5.67% | 2.1% | 0.9% | 13.5% | 7.6% |

### LongMemEval

| System | Score |
|--------|-------|
| Neuromem (Opus 4.6) | 72.4% |

### Custom Benchmark (V3)

| System | Score |
|--------|-------|
| **Neuromem** | **75.8% (91/120)** |
| All competitors | Lower |

## Quick Start

```python
from neuromem import NeuromemEngine

engine = NeuromemEngine("my_memory.db")
stats = engine.ingest("conversations.json")

# Standard search
results = engine.search("What did they talk about?", limit=10)

# Agentic search (with LLM for HyDE + refined queries)
results = engine.search_agentic(
    "When did they go on vacation?",
    llm_fn=my_llm_function,
    use_hyde=True,
    use_reranker=True,
)
```

## License

MIT
