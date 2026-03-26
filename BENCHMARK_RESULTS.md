# Neuromem Benchmark Results

## Fair LoCoMo Benchmark (2026-03-18)

### Methodology

We ran a controlled, fair benchmark comparing Neuromem against EverMemOS using EverMemOS's own evaluation framework. Every variable was held constant except the memory system itself.

**Controlled variables (identical for all systems):**

| Variable | Value |
|----------|-------|
| Answer model | GPT-4.1-mini (via OpenRouter) |
| Judge model | GPT-4o-mini |
| Judge runs | 3 per question |
| Judge temperature | 0 |
| Dataset | LoCoMo 10 conversations |
| Category 5 (adversarial) | Excluded |
| Total questions | 1,540 |

**Independent variables (each system's design):**

| | EverMemOS | Neuromem |
|--|-----------|----------|
| Ingestion | 17 LLM prompts/msg → MemCells | FTS5 + vectors + episode extraction |
| Index | BM25 + Qwen3-Embedding-4B | SQLite FTS5 + Model2Vec (256-dim) |
| Search | Agentic: BM25+embedding → sufficiency → multi-query → rerank | Agentic: HyDE + hybrid + entity + clustering + cross-encoder |

### Results

| System | J-Score (mean ± std) | Cat 1 (single_hop) | Cat 2 (multi_hop) | Cat 3 (temporal) | Cat 4 (open_domain) |
|--------|---------------------|---------------------|--------------------|--------------------|----------------------|
| No-Retrieval | 5.67% ± 0.04% | 2.1% (6/282) | 0.9% (3/321) | 13.5% (13/96) | 7.6% (64/841) |
| **Neuromem** | **72.34% ± 0.06%** | 59.2% (167/282) | 72.9% (234/321) | 52.1% (50/96) | 79.0% (664/841) |
| EverMemOS | 92.77% ± 0.10% | 91.1% (257/282) | 89.4% (287/321) | 78.1% (75/96) | 96.2% (809/841) |

### Per-Run Stability

All standard deviations < 0.10%, confirming the GPT-4o-mini judge at temp=0 is highly deterministic.

| System | Run 1 | Run 2 | Run 3 |
|--------|-------|-------|-------|
| No-Retrieval | 5.65% | 5.65% | 5.71% |
| Neuromem | 72.27% | 72.40% | 72.34% |
| EverMemOS | 92.86% | 92.66% | 92.79% |

### Runtime Comparison

| System | Total Time | Notes |
|--------|-----------|-------|
| No-Retrieval | 374s (~6 min) | No ingestion, LLM answers from training data |
| **Neuromem** | **515s (~9 min)** | Fast ingestion, efficient local retrieval |
| EverMemOS | 5,879s (~98 min) | 55 min on MemCell extraction alone |

Neuromem is **11x faster** than EverMemOS.

### Gap Analysis

| Category | EverMemOS | Neuromem | Gap | Root Cause |
|----------|-----------|----------|-----|------------|
| Cat 1 (single_hop) | 91.1% | 59.2% | -31.9 pp | Vocabulary mismatch — raw messages don't match question phrasing |
| Cat 2 (multi_hop) | 89.4% | 72.9% | -16.5 pp | Needs multiple evidence pieces — retrieval depth |
| Cat 3 (temporal) | 78.1% | 52.1% | -26.0 pp | Temporal reasoning hardest for both systems |
| Cat 4 (open_domain) | 96.2% | 79.0% | -17.2 pp | Episode narratives help but not enough context richness |

---

## Landscape Comparison

How Neuromem compares to published results from other memory systems:

| System | LoCoMo J-Score | Source |
|--------|---------------|--------|
| EverMemOS | 92.8% | Our fair test |
| MemMachine v0.2 | 91.7% | Published (agent mode, gpt-4.1-mini) |
| **Neuromem (Phase 1)** | **91.2%** | Our fair test (Qwen3 embeddings + mxbai reranker) |
| Neuromem (v3) | 87.7% | Our fair test |
| Mem0 | 80.0% | MemMachine's eval |
| Neuromem (v2) | 72.3% | Our fair test |
| Mem0-Graph | 68.4% | Mem0 published |
| Mem0 | 66.9% | Mem0 published |
| Zep | 58.4% | Corrected (originally claimed 84%) |
| OpenAI Memory | 52.9% | Mem0 comparison |
| GPT-4 (no memory) | 32.1% | LoCoMo paper baseline |
| No retrieval | 5.7% | Our fair test |

**Note:** Scores across rows are not perfectly comparable — different teams use different answer models, judge models, and evaluation prompts. The LoCoMo benchmark has been subject to controversy around methodology. Our Neuromem vs EverMemOS comparison is the most reliable because both ran through the same pipeline with identical settings.

---

## LongMemEval Results

| System | Score |
|--------|-------|
| Mastra Observational Memory | 95.0% |
| Hindsight (Gemini-3 Pro) | 91.4% |
| SuperMemory (Gemini-3 Pro) | 85.2% |
| SuperMemory (GPT-4o) | 81.6% |
| **Neuromem (Opus 4.6)** | **72.4%** |
| Mem0 | 49.0% |

---

## Custom Benchmark V3 (120 questions)

Our custom benchmark covering factual recall, temporal reasoning, personality understanding, and multi-hop inference:

| System | Score |
|--------|-------|
| **Neuromem** | **75.8% (91/120)** |
| Cognee | 62.5% |
| LangMem | 58.3% |
| Mem0 | 55.0% |
| ChromaDB (raw RAG) | 47.5% |

---

## Prompt Fairness Verification

We discovered the two systems used different answer prompts (EverMemOS: 380-word CoT, Neuromem: 80-word simple). To verify the gap wasn't from prompt engineering, we re-ran both systems with an identical neutral prompt using the same search results.

| Experiment | Neuromem | EverMemOS | Gap |
|---|---|---|---|
| Original (own prompts) | 72.34% | 92.77% | 20.4 pp |
| Identical neutral prompt | 66.10% | 86.88% | 20.8 pp |

Each system's custom prompt helped it by ~6 points. The gap stayed at ~20 points regardless. **The gap is retrieval quality, not prompt engineering.**

---

## Failure Analysis (357 questions)

We analyzed the 357 questions where Neuromem failed but EverMemOS succeeded:

| Root Cause | % of Failures | Description |
|---|---|---|
| Retrieval miss | 30% | Search didn't find the relevant message at all |
| Temporal | 25% | Failed to resolve time references ("when", "how long ago") |
| Multi-hop | 19% | Needed to connect 2+ separate messages |
| Insufficient detail | 16% | Found the right area, missed specific names/numbers |
| Wrong inference | 7% | Found right context, drew wrong conclusion |
| Vocab mismatch | 3% | Question used different words than message |

Vocabulary mismatch — originally assumed to be the main problem — is only 3% of failures. The real bottlenecks are retrieval depth (30%) and temporal reasoning (25%).

---

## Key Observations

1. **No knowledge leakage:** The 5.67% no-retrieval floor confirms LoCoMo questions genuinely require memory retrieval.

2. **Neuromem beats Mem0, Zep, and OpenAI Memory** on LoCoMo despite being pure SQLite with $0 infrastructure cost.

3. **The 20-point gap to EverMemOS/MemMachine comes from retrieval depth and temporal reasoning.** Failure analysis shows 30% of gaps are search misses (relevant messages not found) and 25% are temporal resolution failures. Only 3% are vocabulary mismatch.

4. **Temporal reasoning (Cat 3) is the hardest category for everyone.** Even EverMemOS only hits 78.1% here.

5. **Neuromem is 11x faster** — the tradeoff for lower scores is dramatically cheaper and faster operation.

6. **The gap is fixable.** Three targeted improvements (better retrieval, temporal date extraction, entity linking) would address 74% of failures, potentially bringing Neuromem to ~87-90%.
