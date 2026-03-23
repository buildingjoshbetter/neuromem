# EverMemOS Architecture Deep Dive
## Supplementary Research — March 23, 2026

> Source: Exhaustive code analysis of `/Users/j/Desktop/neuromem/EverMemOS/`

---

## 1. Retrieval Pipeline: Three Modes

### Mode 1: Lightweight (no LLM calls)
- Pure algorithmic: BM25 only, embedding only, or hybrid
- No reranker, no sufficiency check
- Not used for LoCoMo benchmark

### Mode 2: Agentic Multi-Round (LoCoMo config)

**Two-Round Architecture:**

```
ROUND 1: Initial Hybrid → Rerank → Sufficiency Check
  - Hybrid search: BM25 + Embedding in parallel
  - RRF fusion (k=40)
  - Top 20 → rerank → Top 10
  - LLM sufficiency check
  - If sufficient: DONE (return Top 10)

ROUND 2: Multi-Query Refinement (only if insufficient)
  - Generate 2-3 complementary queries via LLM
  - Execute in parallel
  - Multi-RRF fusion → Top 40
  - Final rerank → Top 20
```

### Mode 3: Tool-based (Sauron-style)
- Not used in benchmark, designed for agent integration

---

## 2. MaxSim Scoring (Key Innovation)

```python
def compute_maxsim_score(query_emb, atomic_fact_embs):
    """
    For each document:
    - Extract all atomic_facts
    - Compute similarity between query and EACH fact
    - Take MAXIMUM similarity (not average)
    - Return max as document score
    """
    fact_matrix = np.array(atomic_fact_embs)
    sims = np.dot(fact_matrix, query_emb) / (norms * query_norm)
    return float(np.max(sims))
```

**Why it works:** A document with one highly relevant sentence buried in irrelevant context still scores high. Traditional averaging dilutes the score.

---

## 3. LLM Sufficiency Check (Key Innovation)

The sufficiency prompt is **temporal-aware**:
1. Identifies temporal requirements (start_time, end_time, ordering)
2. Decomposes temporal queries into components
3. Identifies missing temporal information
4. Returns structured JSON: {is_sufficient, reasoning, missing_information, key_info_found}

This is why EverMemOS handles temporal queries better — **explicit temporal completeness checking**.

---

## 4. Multi-Query Generation

The prompt includes **mandatory temporal reasoning**:
1. Boundary Decomposition: queries targeting START and END separately
2. Temporal Expression Expansion: relative → absolute + session numbers + "before/after"
3. Interval Reconstruction: declarative query with BOTH anchors
4. Standard diversity: question form, declarative/HyDE, alternative phrasing

---

## 5. Extraction Pipeline (12+ Prompts per MemCell)

```
Raw Conversation → Boundary Detection → MemCell Creation:
  ├─ Episode Memory (3rd person narrative, time-aware)
  ├─ Event Log (atomic facts with resolved timestamps)
  ├─ Profile Part 1 (basic attributes)
  ├─ Profile Part 2 (preferences/interests)
  ├─ Profile Part 3 (behavioral patterns)
  ├─ Profile Life (life events/milestones)
  ├─ Foresight (predicted future events)
  ├─ Group Profile (collective characteristics)
  ├─ Profile Merge (consolidation across sessions)
  ├─ Evidence Completion (missing context)
  ├─ Relationship Update
  └─ Conversation Context
  → Cluster Management → MongoDB Storage
```

**Cost:** ~612+ LLM calls per conversation (12 × 51 MemCells), ~6,120+ for full benchmark.

---

## 6. Embedding: Qwen3-Embedding-4B

- 4 billion parameters (vs Neuromem's 600M after upgrade, 8M before)
- 1024+ dimensions
- Provider: DeepInfra API ($100-150/month)
- Fallback: vLLM local → DeepInfra API

---

## 7. LoCoMo Configuration

```python
use_hybrid_search = True
use_multi_query = True
use_reranker = True
use_agentic_retrieval = True
hybrid_emb_candidates = 50
hybrid_bm25_candidates = 50
hybrid_rrf_k = 40
reranker_batch_size = 20
multi_query_num = 3
response_top_k = 10
emb_recall_top_n = 40
llm_model = "openai/gpt-4.1-mini"  # Via OpenRouter
```

---

## 8. Infrastructure Costs

| Component | Cost/Month |
|-----------|-----------|
| MongoDB (sharded) | ~$57 |
| DeepInfra Embedding | ~$100 |
| DeepInfra Reranking | ~$50 |
| Answer LLM | ~$20/1000q |
| **Total** | **~$207/month** |

---

## 9. The Six Critical Differences vs Neuromem

1. **Embedding Model (6.7x params)**: Qwen3-4B vs Qwen3-0.6B
2. **MaxSim Scoring**: Max similarity across atomic facts vs single vector per document
3. **Round 1 Multi-Query**: Always 3 queries upfront vs single query
4. **LLM Sufficiency Check**: Structured temporal-aware checking vs score threshold
5. **Extraction Depth**: 12+ prompts vs 1 combined prompt (22:1 ratio)
6. **API-Based Reranking**: Cloud cross-encoder vs local CPU

---

*This report is supplementary to the main NEUROMEM_DEEP_ANALYSIS.md synthesis document.*
