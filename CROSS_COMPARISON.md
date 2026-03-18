# Neuromem Benchmark — Cross-Comparison Scorecard
## March 14, 2026

---

## Executive Summary

We benchmarked 5 AI memory systems against a generalist dataset of 797 synthetic messages across 60 queries in 12 categories. Only 3 systems produced usable results. The findings are **devastating for the incumbents**.

**Key Finding: Mem0 ($24M in funding) scored 0 HITs on 60 queries. Raw vector search (ChromaDB) outperformed it 5:1.**

---

## Final Scores

| Rank | System | HITs | PARTIALs | MISSes | Weighted Score | % |
|------|--------|------|----------|--------|---------------|---|
| 1 | **LangMem** | 19 | 30 | 11 | 68/120 | **56.7%** |
| 2 | **ChromaDB** (baseline) | 18 | 23 | 19 | 59/120 | **49.2%** |
| 3 | **Mem0** ($24M funded) | 0 | 11 | 49 | 11/120 | **9.2%** |
| — | SimpleMem | BLOCKED | — | — | — | Requires OpenAI API key |
| — | Cognee | BLOCKED | — | — | — | Embedding config issues |
| — | Engram | SKIPPED | — | — | — | Go binary, not pip-installable |
| — | Letta/MemGPT | NOT RUN | — | — | — | Requires running server |

*Weighted score: HIT = 2 points, PARTIAL = 1 point, MISS = 0. Max = 120.*

---

## Category Breakdown

### Scoring by Category (H = HIT, P = PARTIAL, M = MISS)

| Category | ChromaDB | Mem0 | LangMem | Favors |
|----------|----------|------|---------|--------|
| **Exact Recall** (5q) | 4H 1P 0M | 0H 2P 3M | 3H 2P 0M | Vector search |
| **Semantic** (5q) | 1H 1P 3M | 0H 1P 4M | 2H 1P 2M | LLM extraction |
| **Temporal** (5q) | 1H 1P 3M | 0H 1P 4M | 0H 2P 3M | Temporal KGs |
| **Entity** (5q) | 3H 2P 0M | 0H 0P 5M | 3H 2P 0M | Knowledge graphs |
| **Contradiction** (5q) | 3H 2P 0M | 0H 1P 4M | 2H 2P 1M | Bi-temporal models |
| **Multi-hop** (5q) | 0H 3P 2M | 0H 0P 5M | 1H 3P 1M | Graph traversal |
| **Cross-modal** (5q) | 1H 2P 2M | 0H 1P 4M | 1H 2P 2M | Unified storage |
| **Personality** (5q) | 0H 1P 4M | 0H 3P 2M | 0H 3P 2M | LLM synthesis |
| **Negation** (5q) | 1H 4P 0M | 0H 0P 5M | 2H 2P 1M | Precise systems |
| **OCR Retrieval** (5q) | 3H 1P 1M | 0H 1P 4M | 3H 1P 1M | FTS5 |
| **Consolidation** (5q) | 1H 3P 1M | 0H 0P 5M | 2H 2P 1M | Hierarchical memory |
| **Analytical** (5q) | 0H 2P 3M | 0H 0P 5M | 0H 1P 4M | Comprehensive reasoning |

### Category Winners
- **ChromaDB wins**: Exact Recall (9pts), Entity (8pts), Contradiction (8pts), Negation (6pts), OCR Retrieval (7pts)
- **LangMem wins**: Semantic (5pts), Multi-hop (5pts), Negation (6pts tied), Consolidation (6pts)
- **Tied**: Cross-modal, Personality
- **Nobody wins**: Temporal (all bad), Analytical (all bad)

---

## Architecture Analysis

### Why Mem0 Failed So Catastrophically

Mem0's core architecture is **LLM extraction → vector search**. When messages are ingested, an LLM extracts "memories" like:
- "Name is Jordan Chen"
- "Works out with someone named Jordan"
- "Is pursuing carbon tracking for manufacturers startup called CarbonSense"

**The problem: LLM extraction destroys information.** The rich, contextual message data gets compressed into generic, de-contextualized facts. When you search for "What was the scope 1 accuracy on the Meridian Steel pilot?", the extracted memory "Set up the carbonsense.io domain on 2024-07-30" is irrelevant. The specific number (96.1%) was never extracted.

Load time: **538 seconds** (9 minutes) for 797 messages — making 797 API calls to Claude Sonnet.

### Why ChromaDB Performed Surprisingly Well

ChromaDB uses pure vector similarity with no intelligence. Its strength:
- **Raw messages contain the answers.** When you search for "Jordan's dog", messages mentioning "Biscuit" come up.
- **No information is lost.** Every detail from every message is preserved.
- **Fast.** 0.019s per query vs 0.014s for Mem0 (similar, but 0s vs 538s load time).

Its weakness: the **"query pollution" problem** — emotionally charged messages like "omg jordan!!" appear as top results for many unrelated queries because the character name creates semantic similarity.

### Why LangMem Was the Best

LangMem extracted **683 structured memories from 797 messages** plus retained some raw messages. This hybrid approach:
- **Preserves raw data** while adding extracted facts
- **Doesn't over-compress** — keeps details
- The extracted memories add semantic connections the raw text doesn't have

Load time: **469 seconds** (8 minutes) — but the extraction quality was better than Mem0.

---

## What No System Could Do

All three systems failed badly on:

### 1. Temporal Reasoning (all scored ≤2/10)
No system can handle "What happened in the month after Demo Day?" because:
- ChromaDB has no time awareness
- Mem0's extracted facts lose timestamps
- LangMem's vector search doesn't filter by time

### 2. Analytical Queries (all scored ≤2/10)
"What mistakes has Jordan made as a founder?" requires:
- Aggregating information across hundreds of messages
- Applying judgment to classify events as "mistakes"
- No retrieval system can do this — it needs LLM reasoning on top

### 3. Personality Inference (all scored ≤3/10)
"What kind of person is Jordan?" requires:
- Synthesizing personality traits from scattered behavioral data
- No system extracted personality-level patterns

---

## Implications for Neuromem

### What Neuromem Must Beat
- **Minimum bar**: ChromaDB baseline (49.2%). Any "intelligent" memory system that can't beat raw vectors is wasting computation.
- **Target**: LangMem (56.7%). This is the current best.
- **Realistic goal**: 70%+ would be world-class.

### Where Neuromem's Architecture Could Win

| Neuromem Layer | Target Categories | Expected Advantage |
|----------------|-------------------|--------------------|
| L0 Personality Engram | Personality, Analytical | Extract and maintain personality profile |
| L2 Episodic (FTS5+timestamps) | Temporal, OCR Retrieval | Time-aware full-text search |
| L3 Semantic (hybrid RRF) | Semantic, Cross-modal | Better than pure cosine similarity |
| L4 Salience Guard | Exact Recall, Entity | Filter noise, reduce query pollution |
| L5 Consolidation | Consolidation, Multi-hop | Hierarchical summarization over time |
| Predictive Coding | Contradiction | Only store information-theoretic surprises |

### Specific Opportunities
1. **Temporal queries**: FTS5 with timestamp filtering would immediately beat all tested systems
2. **Contradiction resolution**: Bi-temporal storage (L5) can track fact evolution
3. **Query pollution**: Salience Guard (L4) would filter "omg jordan!!" from irrelevant queries
4. **Entity disambiguation**: Per-entity memory (L4) separates "Marcus the gym buddy" from "Marcus, Lily's ex"
5. **Personality**: Dedicated L0 Personality Engram — something no competitor has
6. **Analytical**: Consolidation layer pre-computes summaries, enabling better analytical answers

---

## How Anthropic/OpenAI Would Test Memory Systems

Based on this benchmark experience:

### What They'd Test
1. **Scale**: 10K-100K messages, not 797. Real users generate thousands of messages.
2. **Long-term drift**: Facts that change over months/years, not just contradictions
3. **Real-world noise**: Typos, slang, emoji, multi-language, empty messages
4. **Adversarial queries**: "What did Jordan NOT do?" — testing for hallucination
5. **Latency at scale**: p50/p95/p99 query times with 100K+ stored memories
6. **Token efficiency**: Cost per ingestion and per query (LLM calls are expensive)
7. **Privacy**: Can the system be prompted to leak memories from other users?

### Benchmark Design Principles
1. **Always include a raw vector baseline** — if your system can't beat vectors, it adds no value
2. **Test categories that favor different architectures** — don't bias toward your own
3. **Include negation/false premise queries** — test what the system DOESN'T know
4. **Measure load time, not just query time** — Mem0 took 538s to load 797 messages
5. **Score with clear rubrics** — HIT/PARTIAL/MISS with explicit criteria
6. **Test cross-modal** — real memory isn't just text (emails, receipts, calendar, notes)

---

## System Comparison Table

| Feature | ChromaDB | Mem0 | LangMem | SimpleMem | Cognee |
|---------|----------|------|---------|-----------|--------|
| Architecture | Pure vectors | LLM extract + vectors | LLM extract + vectors | Semantic compression | Knowledge graph + vectors |
| Embedding Model | MiniLM-L6 (384d) | MiniLM-L6 (384d) | MiniLM-L6 (384d) | Qwen3-0.6B (1024d) | BGE-small (384d) |
| LLM Required | No | Yes (extraction) | Yes (extraction) | Yes (compression) | Yes (graph building) |
| Load Time (797 msgs) | 2s | 538s | 469s | N/A | 285s |
| Query Time (avg) | 0.019s | 0.014s | 0.094s | N/A | N/A |
| Weighted Score | 49.2% | 9.2% | 56.7% | Blocked | Blocked |
| Open Source | Yes | Partial (OSS core) | Yes | Yes | Yes |
| Pricing | Free | $97/mo cloud | Free | Free | Free |
| Funding | N/A | $24M | N/A | N/A | $2.1M |

---

## Files
- Results: `benchmark_v2_*_results.json` (raw) and `benchmark_v2_*_scored.json` (scored)
- Dataset: `synthetic_v2_messages.json` (797 messages)
- Queries: `test_queries_v2.py` (60 queries, 12 categories)
- Competitive analysis: `COMPETITIVE_LANDSCAPE.md`
