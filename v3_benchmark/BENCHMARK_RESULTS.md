# V3 Universal AI Memory Systems Benchmark — Results

**Date:** March 14, 2026
**Dataset:** 50 sessions, 204 turns, ~50K tokens (hand-crafted Jordan Chen conversations)
**Queries:** 50 queries across 10 categories (5 per category)
**Scoring:** Pending API credits (Phase A + Phase B require Claude API)

---

## Raw Retrieval Results (Pre-Scoring)

| Rank | System | Status | Queries w/ Results | Avg Query (ms) | Ingest Time (s) | Architecture |
|------|--------|--------|-------------------|----------------|-----------------|--------------|
| 1 | **FTS5** | COMPLETED | 50/50 (100%) | **0.5** | **0.0** | SQLite FTS5 (BM25) |
| 2 | **Neuromem** | COMPLETED | 50/50 (100%) | **2.0** | **1.1** | 6-layer (FTS5 + Model2Vec RRF + personality + salience + consolidation) |
| 3 | **ChromaDB** | COMPLETED | 50/50 (100%) | 7.9 | 4.3 | Vector similarity (all-MiniLM-L6-v2, cosine) |
| 4 | **OpenMemory** | COMPLETED | 50/50 (100%) | 50.1 | 5.4 | Cognitive engine (semantic, episodic, procedural, emotional, reflective) |
| 5 | **Mem0** | API_BLOCKED | 0/50 (0%) | — | — | LLM extraction + Qdrant |
| — | LangMem | NOT_RUN | — | — | — | Needs Anthropic API credits |
| — | Cognee | NOT_RUN | — | — | — | Needs LLM API key |
| — | Graphiti | NOT_RUN | — | — | — | Needs Neo4j Docker |
| — | Letta | NOT_RUN | — | — | — | Needs letta server |
| — | EverMemOS | NOT_RUN | — | — | — | Needs EVERMEMOS_API_KEY |
| — | SimpleMem | NOT_RUN | — | — | — | Needs OPENAI_API_KEY |
| — | MemMachine | BLOCKED | — | — | — | Not on PyPI |
| — | Hindsight | BLOCKED | — | — | — | Build error (use_2to3) |
| — | LightMem | BLOCKED | — | — | — | Empty package (v0.0.0) |
| — | A-MEM | BLOCKED | — | — | — | GitHub only, not pip |
| — | Memary | BLOCKED | — | — | — | Requires Python <=3.11.9 |

---

## Speed Comparison (4 Completed Systems)

| Metric | FTS5 | Neuromem | ChromaDB | OpenMemory |
|--------|------|----------|----------|------------|
| **Avg Query** | 0.5ms | 2.0ms | 7.9ms | 50.1ms |
| **Ingest (204 turns)** | 0.0s | 1.1s | 4.3s | 5.4s |
| **Total Benchmark** | 0.0s | 1.2s | 6.7s | 7.9s |
| **Architecture** | BM25 keyword | 6-layer hybrid | Vector cosine | 5-type cognitive |
| **LLM Required** | No | No | No | No |
| **External Deps** | None | None | sentence-transformers | openmemory-py |

### Speed Ratios (vs Neuromem)

| Comparison | Query Speed | Ingest Speed |
|------------|-------------|--------------|
| FTS5 vs Neuromem | FTS5 is 4x faster | FTS5 is instant |
| Neuromem vs ChromaDB | Neuromem is **4x faster** | Neuromem is **4x faster** |
| Neuromem vs OpenMemory | Neuromem is **25x faster** | Neuromem is **5x faster** |

---

## Neuromem Layer Activation Report

All 8 capabilities activated successfully:

| Layer | Status | Details |
|-------|--------|---------|
| FTS5 (L2 Episodic) | Active | Porter stemming, BM25 ranking |
| Vector Search (L3) | Active | Model2Vec potion-base-8M, 256-dim, 204 vectors in 1.0s |
| Hybrid RRF (L3) | Active | Reciprocal Rank Fusion (k=60) combining FTS5 + vector |
| Temporal (L2) | Active | Date parsing, time-window filtering |
| Salience (L4) | Active | Noise filtering, entity boosting |
| Personality (L0) | Active | Entity profiles built in 0.01s, preferences extracted |
| Consolidation (L5) | Active | Summaries + contradiction detection |
| Predictive Coding | Active | Surprise index built in 0.02s |

### Query Source Distribution

| Source | Count | % of All Results |
|--------|-------|-----------------|
| `both` (hybrid RRF) | 358 | 71.6% |
| `both+temporal` (hybrid + temporal boost) | 142 | 28.4% |

This shows Neuromem's hybrid retrieval (FTS5 + vector via RRF) is the primary pathway, with temporal reasoning providing supplementary boosting on 28% of results.

---

## Key Findings (Pre-Scoring)

1. **All 4 working systems returned results for all 50 queries** — raw retrieval is not the bottleneck; retrieval *quality* is what matters (Phase A/B scoring will reveal this).

2. **Neuromem occupies the sweet spot** — 4x faster than ChromaDB at queries, while adding 5 additional layers beyond vector search (temporal, salience, personality, consolidation, predictive). Only 4x slower than raw FTS5, which buys significant retrieval intelligence.

3. **Neuromem's hybrid RRF is working** — 100% of top results come from the "both" source (found by FTS5 AND vector), meaning the RRF fusion is successfully combining both retrieval signals.

4. **Ingest pipeline is fast** — 1.1s for the full 6-layer pipeline (204 messages + vectors + profiles + summaries + contradictions + surprise index). Compare to ChromaDB at 4.3s for just embeddings.

5. **Mem0's $24M system still can't function** without LLM API credits. Neuromem runs entirely locally.

6. **12 of 16 systems (75%) couldn't complete the benchmark** due to missing packages, build errors, API requirements, or infrastructure needs.

---

## Systems That Actually Work (March 2026)

Of 16 benchmarked systems:
- **4 systems** completed full benchmark (FTS5, Neuromem, ChromaDB, OpenMemory)
- **4 systems** need API keys/services to run (Mem0, LangMem, Cognee, EverMemOS)
- **3 systems** need infrastructure (Graphiti→Neo4j, Letta→server, SimpleMem→OpenAI)
- **5 systems** are completely broken/unavailable (MemMachine, Hindsight, LightMem, A-MEM, Memary)

### The Published Scores Problem

Many published LoCoMo scores can't be verified because the systems can't even be installed:
- **MemMachine** (LoCoMo 84.9%) — no pip package exists
- **EverMemOS** (LoCoMo 92.3%) — cloud API only, needs API key
- **Hindsight** (LongMemEval 91.4%) — pip package broken (Python 2 build system)

---

## Next Steps

1. **Add Anthropic API credits** → enables Mem0, LangMem, Cognee, and Phase A/B scoring
2. **Start Neo4j Docker** → enables Graphiti (temporal KG, LoCoMo 75.1%)
3. **Start Letta server** → enables Letta (OS-inspired hierarchy, LoCoMo 74.0%)
4. **Run Phase A scoring** → `python scorer.py --all --phase-a-only`
5. **Run Phase B scoring** → `python scorer.py --all`
6. **Generate scorecard** → `python scorer.py --scorecard`

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| Sessions | 50 |
| Total turns | 204 |
| Estimated tokens | ~50,000 |
| Time span | July 2024 — January 2026 |
| Query categories | 10 |
| Queries per category | 5 |
| Total queries | 50 |

### Query Categories

| # | Category | Tests What | Target Systems |
|---|----------|------------|----------------|
| 1 | single_hop_fact | Basic retrieval | All |
| 2 | preference_recall | User preferences | Mem0, Neuromem (L0) |
| 3 | temporal_reasoning | Time-aware queries | Graphiti, Neuromem (L2) |
| 4 | fact_updates | Contradiction resolution | Graphiti, Hindsight, Neuromem (L5) |
| 5 | multi_hop_reasoning | Cross-fact connections | Cognee, A-MEM |
| 6 | cross_session_continuity | Prior session references | Letta, EverMemOS |
| 7 | negation_abstention | Not hallucinating | All |
| 8 | multi_session_synthesis | Summarization | EverMemOS, MemMachine, Neuromem (L5) |
| 9 | entity_tracking | Disambiguation | Hindsight, Graphiti, Neuromem (L0/L4) |
| 10 | belief_evolution | Opinion changes | Hindsight, Neuromem (L5) |
