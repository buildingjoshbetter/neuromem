# Embedding Model Research Journal

**Date:** March 18-19, 2026
**Purpose:** Comprehensive research into embedding model options for Neuromem's vector search upgrade
**Researcher:** 10 parallel sub-agents + synthesis
**Current Model:** Model2Vec potion-base-8M (8M params, 256-dim, static embeddings)

---

## Table of Contents

1. [Agent 1: MTEB Leaderboard by Size Tier](#agent-1-mteb-leaderboard-by-size-tier)
2. [Agent 2: Qwen Embedding Family](#agent-2-qwen-embedding-family)
3. [Agent 3: Nomic Embed Models](#agent-3-nomic-embed-models)
4. [Agent 4: BGE (BAAI) Family](#agent-4-bge-baai-family)
5. [Agent 5: GTE and E5 Models](#agent-5-gte-and-e5-models)
6. [Agent 6: Jina Embedding Models](#agent-6-jina-embedding-models)
7. [Agent 7: Snowflake Arctic Embed](#agent-7-snowflake-arctic-embed)
8. [Agent 8: CPU / Apple Silicon Performance](#agent-8-cpu--apple-silicon-performance)
9. [Agent 9: Conversational Retrieval Models](#agent-9-conversational-retrieval-models)
10. [Agent 10: Model2Vec and Distilled Models](#agent-10-model2vec-and-distilled-models)
11. [Cross-Agent Synthesis](#cross-agent-synthesis)
12. [Final Top 5 Shortlist](#final-top-5-shortlist)

---

## Agent 1: MTEB Leaderboard by Size Tier

**Task:** Survey the MTEB leaderboard across all size tiers, focusing on the retrieval sub-task (nDCG@10) which is most relevant to Neuromem's use case.

### Key Findings

**Important context:** There are now multiple MTEB versions (v1 legacy, v2 English, MMTEB multilingual). Cross-version comparisons are unreliable. MTEB scores are self-reported by model providers with no independent verification.

#### Top 5 Overall (Retrieval, Any Size)

| Rank | Model | Params | Retrieval nDCG@10 | License |
|------|-------|--------|-------------------|---------|
| 1 | Qwen3-Embedding-8B | 8B | 69.44 (Eng v2) | Apache 2.0 |
| 2 | Gemini Embedding 001 | Proprietary | 64.35 (Eng v2) | Proprietary |
| 3 | Qwen3-Embedding-4B | 4B | 68.46 (Eng v2) | Apache 2.0 |
| 4 | NV-Embed-v2 | 7.85B | 62.65 (v1) | CC-BY-NC-4.0 |
| 5 | Llama-Embed-Nemotron-8B | 7.5B | ~69.46 (MMTEB) | Non-commercial |

#### Top 5 Under 500M Parameters

| Rank | Model | Params | Retrieval Score | License |
|------|-------|--------|-----------------|---------|
| 1 | EmbeddingGemma-300M | 308M | MTEB overall 69.67 | Apache 2.0 |
| 2 | stella_en_400M_v5 | 400M | ~59-60 est. | MIT |
| 3 | Nomic Embed Text V2 (MoE) | 475M/305M active | ~62.39 overall | Open |
| 4 | snowflake-arctic-embed-l | 335M | 55.98 (BEIR) | Apache 2.0 |
| 5 | gte-multilingual-base | 305M | Competitive | Apache 2.0 |

#### Top 5 Under 100M Parameters

| Rank | Model | Params | Retrieval nDCG@10 | License |
|------|-------|--------|-------------------|---------|
| 1 | mdbr-leaf-ir (MongoDB LEAF) | 23M | 54.03 (asym) | Apache 2.0 |
| 2 | snowflake-arctic-embed-s | 33M | 51.98 | Apache 2.0 |
| 3 | bge-small-en-v1.5 | 33M | 51.68 | MIT |
| 4 | granite-embedding-30m-english | 30M | 49.1 | Apache 2.0 |
| 5 | e5-small-v2 | 33M | 49.04 | MIT |

#### Key Insight

Overall MTEB average is misleading for retrieval-specific use cases. NV-Embed-v2 has the highest overall MTEB v1 score (72.31) but its retrieval-specific score (62.65) is significantly lower than Qwen3-8B's retrieval score (69.44). **Always look at the retrieval sub-task score specifically.**

#### Surprise Finding: MongoDB LEAF-IR

At just 23M parameters, MongoDB's mdbr-leaf-ir achieves 54.03 nDCG@10 on BEIR — beating models with 33M+ params and coming close to OpenAI's text-embedding-3-small (51.08). It retains 95.8% of its 335M-parameter teacher model's performance through distillation.

---

## Agent 2: Qwen Embedding Family

**Task:** Deep dive into the Qwen/Alibaba embedding model family, particularly the Qwen3-Embedding series.

### Model Lineup

| Model | Params | Dims (max) | Max Tokens | MTEB-EN Retrieval | License |
|-------|--------|-----------|-----------|-------------------|---------|
| Qwen3-Embedding-0.6B | 600M | 1024 | 32,000 | 61.83 | Apache 2.0 |
| Qwen3-Embedding-4B | 4B | 2560 | 32,000 | 68.46 | Apache 2.0 |
| Qwen3-Embedding-8B | 8B | 4096 | 32,000 | 69.44 | Apache 2.0 |

### Key Features
- **Matryoshka Representation Learning (MRL):** Flexible dimensions from 32 to max. Can truncate to 256-dim for storage savings with graceful quality degradation.
- **Instruction-aware:** Supports task-specific instructions in the query (e.g., "Retrieve relevant facts about...").
- **32K context window:** Handles very long documents/conversations.
- **100+ languages** including code.
- **GGUF quantized versions** available on Ollama for local inference.

### Qwen3-Embedding-0.6B Deep Dive

This is the most relevant model for Neuromem:
- 600M params — runs on CPU, ~1.5GB RAM
- 1024-dim embeddings (or truncate to 256 for compatibility)
- MTEB English Retrieval: 61.83 — a massive leap from Model2Vec's ~30-35 estimated retrieval score
- Supports instruction prefixes: query gets "Instruct: Given a question, find relevant conversation excerpts\nQuery: ..."
- Apache 2.0 license

### Predecessor: GTE-Qwen2

| Model | Params | Dims | MTEB Avg | License |
|-------|--------|------|----------|---------|
| gte-Qwen2-1.5B-instruct | 1.5B | 1536 | 67.16 | Apache 2.0 |
| gte-Qwen2-7B-instruct | 7.0B | 3584 | 70.24 | Apache 2.0 |

Qwen3-Embedding-0.6B is the first sub-1B model in this lineage — a significant step toward efficiency.

### Distilled Version Discovery

`Pringled/m2v-Qwen3-Embedding-0.6B` — a Model2Vec distillation of Qwen3-0.6B that is a **drop-in replacement** for current potion-base-8M. Same Model2Vec API, same inference speed (microseconds), but trained from a much better teacher model.

---

## Agent 3: Nomic Embed Models

**Task:** Research the Nomic AI embedding model family.

### Model Lineup

| Model | Params | Max Context | Dims | Matryoshka | License |
|-------|--------|-------------|------|------------|---------|
| nomic-embed-text-v1 | 137M | 8192 | 768 | No | Apache 2.0 |
| nomic-embed-text-v1.5 | 137M | 8192 | 64-768 | Yes | Apache 2.0 |
| nomic-embed-text-v2-moe | 475M (305M active) | 512 | 256-768 | Yes | Open |

### v1.5 Matryoshka Dimensions

| Dimension | MTEB Average |
|-----------|-------------|
| 768 | 62.28 |
| 512 | 61.96 |
| 256 | 61.04 |
| 128 | 59.34 |
| 64 | 56.10 |

At 256-dim (matching Neuromem's current setup), v1.5 scores 61.04 — substantially better than Model2Vec.

### Critical v2-moe Context Regression

v2-moe drops from 8192 tokens to **512 tokens** max context. For Neuromem's episodes and facts (which can be long), v1.5 at 8192 tokens is more practical.

### Why Nomic Is Interesting
- **Fully open source** — training data AND training code released (unique in the space)
- **GGUF available** for local inference via llama.cpp/Ollama
- Heavy Reddit training data (730M post-comment pairs) — closest to conversational text of any general-purpose model
- Apache 2.0 license

### Long Context Performance

| Model | LoCo (8192 ctx) |
|-------|-----------------|
| nomic-embed-text-v1 | 85.53 |
| jina-embeddings-v2-base | 85.45 |
| text-embedding-ada-002 | 52.70 |

Nomic v1/v1.5 excels on long-context retrieval, which is relevant for Neuromem's episodes.

---

## Agent 4: BGE (BAAI) Family

**Task:** Research the BAAI BGE embedding model family.

### Model Evolution

| Generation | Model | Params | Dims | Max Len | MTEB Retrieval |
|-----------|-------|--------|------|---------|----------------|
| v1.5 | bge-small-en-v1.5 | 33.4M | 384 | 512 | 51.68 |
| v1.5 | bge-base-en-v1.5 | 109M | 768 | 512 | 53.25 |
| v1.5 | bge-large-en-v1.5 | 335M | 1024 | 512 | 54.29 |
| M3 | bge-m3 | 568M | 1024 | 8192 | ~46-48 (Eng) |
| LLM | bge-en-icl | 7.11B | 4096 | 32768 | ~60+ |

### BGE-M3 Triple Retrieval

BGE-M3 is unique — it supports three retrieval modes simultaneously from a single model:
1. **Dense:** Standard single-vector embedding (1024-dim)
2. **Sparse (Lexical):** Learned BM25/SPLADE-like sparse vectors
3. **Multi-Vector (ColBERT):** Per-token vectors for late-interaction scoring

On MIRACL (18 languages): Dense only = 67.8, Hybrid (dense+sparse+ColBERT) = 70.0

### License
All core BGE models are **MIT licensed** — fully permissive for commercial use.

### Relevance to Neuromem
BGE-M3's built-in sparse retrieval could theoretically replace FTS5, and its ColBERT mode could replace the cross-encoder reranker — all from one model. But at 568M params it's 71x larger than potion-base-8M. The tradeoff may not be worth it when Neuromem's FTS5 + reranker combo already works well.

---

## Agent 5: GTE and E5 Models

**Task:** Research the GTE (Alibaba) and E5 (Microsoft) embedding model families.

### GTE Evolution

| Model | Params | Dims | Max Tokens | MTEB Retrieval | License |
|-------|--------|------|-----------|----------------|---------|
| gte-small | 33.4M | 384 | 512 | 49.46 | MIT |
| gte-base | 109M | 768 | 512 | 51.14 | MIT |
| gte-large | 335M | 1024 | 512 | 52.22 | MIT |
| gte-base-en-v1.5 | 137M | 768 | 8192 | 54.09 | Apache 2.0 |
| gte-large-en-v1.5 | 409M | 1024 | 8192 | 57.91 | Apache 2.0 |
| gte-modernbert-base | 149M | 768 | 8192 | 55.33 | Apache 2.0 |

### Best Discovery: gte-modernbert-base

At 149M params with Flash Attention 2, this model achieves 55.33 retrieval nDCG@10 — the **best retrieval score in the sub-200M param class**. It has an 8K context window and is built on the modern ModernBERT backbone.

### E5 Family Status

Microsoft's E5 line appears stalled — no significant releases since e5-mistral-7b-instruct (late 2023/early 2024). The latest E5 models:
- e5-small-v2 (33.4M, MIT)
- e5-base-v2 (109M, MIT)
- e5-large-v2 (335M, MIT)
- e5-mistral-7b-instruct (7.2B, MIT)

### Key Insight for Neuromem

gte-modernbert-base is a dark horse — at just 149M params it beats models 2-3x its size on retrieval, with an 8K context window for long episodes.

---

## Agent 6: Jina Embedding Models

**Task:** Research the Jina AI embedding model family.

### Critical License Warning

**All Jina v3+ models are CC BY-NC 4.0 (non-commercial).** This is a dealbreaker for any commercial or productized use. Only jina-embeddings-v2 (Apache 2.0) is commercially viable.

### Model Lineup

| Model | Params | Dims | Max Tokens | License |
|-------|--------|------|-----------|---------|
| jina-embeddings-v2-small-en | 33M | 512 | 8192 | Apache 2.0 |
| jina-embeddings-v2-base-en | 137M | 768 | 8192 | Apache 2.0 |
| jina-embeddings-v3 | 572M | 1024 | 8192 | **CC BY-NC 4.0** |
| jina-embeddings-v4 | 2B | Varies | 8192 | **CC BY-NC 4.0** |
| jina-embeddings-v5-text-small | ~600M | 1024 | 8192 | **CC BY-NC 4.0** |

### v5-text-small Architecture Insight

Jina v5-text-small is built on the **Qwen3-Embedding-0.6B backbone** — independently validating Qwen3-0.6B as the right architecture for a high-quality small embedding model. Jina adds task-specific LoRA adapters on top, but the base is the same.

### Recommendation
Avoid Jina v3+ for any non-research use. If you want a Jina-class small model, just use Qwen3-Embedding-0.6B directly (Apache 2.0).

---

## Agent 7: Snowflake Arctic Embed

**Task:** Research the Snowflake Arctic Embed model family.

### Model Lineup

| Model | Params | Dims | Max Tokens | BEIR nDCG@10 | License |
|-------|--------|------|-----------|-------------|---------|
| arctic-embed-xs | 22M | 384 | 512 | 50.15 | Apache 2.0 |
| arctic-embed-s | 33M | 384 | 512 | 51.98 | Apache 2.0 |
| arctic-embed-m | 110M | 768 | 512 | 54.00 | Apache 2.0 |
| arctic-embed-m-v1.5 | 109M | 256-768 | 512 | Beats Google Gecko | Apache 2.0 |
| arctic-embed-l | 335M | 1024 | 512 | 55.98 | Apache 2.0 |
| arctic-embed-m-v2.0 | 109M | 768 | 8192 | Competitive | Apache 2.0 |
| arctic-embed-l-v2.0 | 568M | 1024 | 8192 | 59.22 | Apache 2.0 |

### Key Finding

**arctic-embed-m-v1.5** at 109M params with 256 dimensions **beats Google Gecko (1.2B params)** at the same dimensionality. This demonstrates that retrieval-optimized training can overcome a 10x parameter gap.

### v2.0 Improvements
- Extended context from 512 to 8192 tokens
- Matryoshka support for flexible dimensions
- arctic-embed-l-v2.0 achieves 59.22 nDCG@10 on BEIR — competitive with much larger models

### Relevance to Neuromem
arctic-embed-m-v2.0 (109M, 768-dim, 8K context) is a strong candidate for the "retrieval specialist" role in a dual-model setup. Its retrieval-first training makes it complementary to a general-purpose model.

---

## Agent 8: CPU / Apple Silicon Performance

**Task:** Research embedding model inference performance on consumer hardware (MacBooks, no GPU).

### Throughput Estimates on CPU

| Model | Params | Approx. Throughput | Notes |
|-------|--------|--------------------|-------|
| Model2Vec potion-base-8M | 8M | ~25,000+ sents/sec | Static embeddings, no neural forward pass |
| Model2Vec potion-retrieval-32M | 32M | ~25,000+ sents/sec | Best static retrieval model |
| all-MiniLM-L6-v2 (ONNX int8) | 22M | ~150-300 sents/sec | 3.08x speedup from quantization |
| bge-small-en-v1.5 (FastEmbed) | 33M | ~100-200 sents/sec | Default FastEmbed model |
| nomic-embed-text-v1.5 (GGUF) | 137M | ~50-200 sents/sec | Via llama.cpp |

### RAM Requirements

| Params | FP32 | INT8 | Practical Loaded (INT8) |
|--------|------|------|------------------------|
| 8M | 32 MB | 8 MB | ~15 MB |
| 33M | 132 MB | 33 MB | ~60 MB |
| 100M | 400 MB | 100 MB | ~200 MB |
| 137M | 548 MB | 137 MB | ~250 MB |
| 335M | 1.34 GB | 335 MB | ~600 MB |
| 560M | 2.24 GB | 560 MB | ~1 GB |

### ONNX vs PyTorch vs CoreML on Apple Silicon

| Runtime | Best For | Speedup |
|---------|----------|---------|
| ONNX Runtime (int8) | CPU-only embedding | 3.08x over PyTorch |
| PyTorch MPS (Metal) | GPU-accelerated | Variable, ~2-5x for large batches |
| CoreML/ANE | Maximum Apple Silicon efficiency | 10x theoretically |
| MLX | Apple-native ML | Good for LLMs, less ecosystem for embeddings |

### Critical Insight for Neuromem

**At 100 queries/day, speed is irrelevant.** Even the slowest model (500ms/query) handles 100 queries in under a minute. The only scenario where speed matters is bulk re-ingestion (re-embedding all stored messages when changing models). At 100K messages:
- Model2Vec: ~4 seconds
- ONNX int8 (33M): ~5.5 minutes
- Full transformer (137M): ~33 minutes

All are acceptable. **Optimize for retrieval quality, not speed.**

### Upgrade Path Discovery

`potion-retrieval-32M` — a newer Model2Vec model specifically trained for retrieval tasks. Drop-in replacement for potion-base-8M with better retrieval quality and Matryoshka dimension support (32-512 dim). Still instant (500x faster than transformers).

---

## Agent 9: Conversational Retrieval Models

**Task:** Research models specifically trained on conversational data and evaluate whether general-purpose models work for chat retrieval.

### Critical Finding: The Embedding Model Is NOT the Bottleneck

Every top-performing conversational memory system achieves its edge through **structuring and reranking**, not through better embedding models.

| System | LoCoMo Score | Embedding Approach |
|--------|-------------|-------------------|
| SmartSearch | 93.5% | **No embeddings at all** — substring + ColBERT/CrossEncoder reranking |
| EverMemOS | 92.77% | Qwen3-Embedding-4B + rich extraction |
| MemMachine v0.2 | 91.7% | text-embedding-3-small + Cohere Rerank |
| Neuromem v3 | 87.71% | Model2Vec 8M + cross-encoder reranker |
| Zep | ~71.2% | BGE-M3 + knowledge graph |

SmartSearch proves this definitively: **no embedding model + good reranking = 93.5% on LoCoMo.** Their pipeline uses only CrossEncoder (mxbai-rerank-large-v1, 435M) + ColBERT fused via RRF.

### SmartSearch Architecture Insight

- Raw substring retrieval achieves **98.6% recall** — the information is almost always retrieved
- But without reranking, only 22.5% of gold evidence survives token-budget truncation
- ColBERT + CrossEncoder reranking bridges this gap
- 650ms latency on CPU, no GPU needed

### Reranker Upgrade Suggestion

Neuromem's current reranker (ms-marco-MiniLM-L6-v2) is decent but small. The highest-impact upgrade might be the **reranker**, not the embedder:
- **mxbai-rerank-large-v1** (435M, DeBERTaV3) — what SmartSearch uses
- Adding **ColBERT reranking** fused with cross-encoder via RRF

### MTEB-to-Conversational Mismatch

MTEB's retrieval datasets (MS MARCO, Natural Questions, SciFact) are formal/document-focused. None involve casual friend-to-friend messaging. A model scoring 0.89 nDCG@10 on BEIR could easily drop to 0.50 on real chat retrieval due to domain mismatch.

### Recent Papers (March 2026)

| Paper | Score | Approach |
|-------|-------|---------|
| Chronos | 95.6% (LongMemEval-S) | Temporal SVO event decomposition |
| SmartSearch | 93.5% (LoCoMo) | Ranking over raw text, no embeddings |
| TA-Mem | — | Tool-augmented memory retrieval |
| MemX | — | Local-first long-term memory |
| AdaMem | — | Adaptive user-centric memory |

---

## Agent 10: Model2Vec and Distilled Models

**Task:** Research Model2Vec improvements and distilled embedding models.

### Model2Vec Family Evolution

| Model | Params | Size | MTEB Avg | Retrieval | Dims |
|-------|--------|------|----------|-----------|------|
| potion-base-2M | 2M | ~2 MB | 44.77 | — | 256 |
| potion-base-4M | 4M | ~4 MB | 48.23 | — | 256 |
| potion-base-8M (current) | 8M | ~8 MB | 50.03 | — | 256 |
| potion-base-32M | 32M | ~32 MB | 51.66 | — | 512 |
| potion-retrieval-32M | 32M | ~32 MB | 49.76 | 36.35 | 32-512 |

### potion-retrieval-32M

Best static retrieval model from Model2Vec, with Matryoshka support. Going from potion-base-8M to potion-retrieval-32M gives a meaningful quality jump with only 24MB more memory. Retrieval score of 36.35 is still far below transformer models (~50+ nDCG@10), but much better than potion-base-8M.

### Distilled Transformer Models

You can distill any sentence-transformer into a Model2Vec model in ~30 seconds:
```python
from model2vec.distill import distill
model = distill(model_name="BAAI/bge-base-en-v1.5", pca_dims=256)
model.save_pretrained("distilled_bge_base")
```

### Key Distilled Option

`Pringled/m2v-Qwen3-Embedding-0.6B` — Model2Vec distillation of Qwen3-0.6B. Drop-in replacement for potion-base-8M with the same API and inference speed, but trained from a much better teacher model. This is the **zero-effort first experiment** for Neuromem.

---

## Cross-Agent Synthesis

### Model Comparison Matrix

| Model | Params | Retrieval nDCG@10 | Dims | Context | Speed (CPU) | RAM | License |
|-------|--------|-------------------|------|---------|-------------|-----|---------|
| potion-base-8M (current) | 8M | ~30-35 est. | 256 | N/A | 25,000/s | 15 MB | MIT |
| potion-retrieval-32M | 32M | 36.35 | 32-512 | N/A | 25,000/s | 60 MB | MIT |
| m2v-Qwen3-0.6B (distilled) | ~32M | TBD | 256 | N/A | 25,000/s | ~50 MB | Apache 2.0 |
| mdbr-leaf-ir (MongoDB) | 23M | 54.03 | 1024 | — | ~300/s | ~50 MB | Apache 2.0 |
| snowflake-arctic-embed-s | 33M | 51.98 | 384 | 512 | ~200/s | ~60 MB | Apache 2.0 |
| bge-small-en-v1.5 | 33M | 51.68 | 384 | 512 | ~200/s | ~60 MB | MIT |
| nomic-embed-text-v1.5 | 137M | 52.8 | 64-768 | 8192 | ~100/s | ~250 MB | Apache 2.0 |
| gte-modernbert-base | 149M | 55.33 | 768 | 8192 | ~80/s | ~300 MB | Apache 2.0 |
| Qwen3-Embedding-0.6B | 600M | 61.83 | 32-1024 | 32,000 | ~20/s | ~1.5 GB | Apache 2.0 |
| Qwen3-Embedding-4B | 4B | 68.46 | 32-2560 | 32,000 | ~2/s (GPU) | ~8 GB | Apache 2.0 |
| Qwen3-Embedding-8B | 8B | 69.44 | 32-4096 | 32,000 | GPU only | ~16 GB | Apache 2.0 |

### Themes Across All Agents

1. **Qwen3 dominates the leaderboard** — #1 at 8B, #1 sub-1B at 0.6B, all Apache 2.0
2. **Retrieval score != overall MTEB score** — always check the retrieval sub-task specifically
3. **Reranking matters more than embedding quality** — SmartSearch proves 93.5% with NO embeddings
4. **License landmines exist** — Jina v3+ is non-commercial, NV-Embed-v2 is non-commercial
5. **Model2Vec is fast but quality-limited** — static embeddings can't compete with transformers on semantic understanding
6. **MTEB scores don't predict conversational retrieval well** — domain mismatch between formal documents and casual chat
7. **Dual-model approaches work** — research (arXiv 2510.04626) shows compressed concatenation of two small models beats single larger ones

---

## Final Top 5 Shortlist

Based on all 10 agents' research, synthesized for Neuromem's specific use case:

### Tier 1: Recommended

| Rank | Model | Params | Why |
|------|-------|--------|-----|
| **1** | **Qwen3-Embedding-0.6B** | 600M | Highest retrieval quality in its class (61.83), instruction-aware, MRL, 32K context, Apache 2.0. The upgrade with the highest expected impact. |
| **2** | **Nomic-embed-text-v1.5** | 137M | Best balance of quality/size, 8K context for long episodes, Matryoshka to 256-dim, Reddit-trained (closest to conversational), Apache 2.0. |
| **3** | **Snowflake Arctic-embed-m-v2.0** | 109M | Retrieval-specialized, 8K context, Matryoshka, beats Google Gecko at same dims. Best as a complementary model in dual setup. |

### Tier 2: GPU / High Quality

| Rank | Model | Params | Why |
|------|-------|--------|-----|
| **4** | **Qwen3-Embedding-4B** | 4B | For users with GPU access. 68.46 retrieval — massive quality jump. MRL down to 256-dim. |
| **5** | **Qwen3-Embedding-8B** | 8B | Maximum quality ceiling (69.44 retrieval). GPU-only. For benchmarking "what's the best possible score." |

### Bonus: Zero-Code-Change Options

| Model | Why |
|-------|-----|
| **Pringled/m2v-Qwen3-Embedding-0.6B** | Drop-in Model2Vec replacement, zero code changes needed |
| **potion-retrieval-32M** | Another drop-in, slightly better than current potion-base-8M |

### Dual-Model Recommendation

**Nomic-embed-text-v1.5 + Qwen3-Embedding-0.6B** with 3-lane RRF fusion (FTS5 + Nomic vectors + Qwen3 vectors). Research shows complementary small models outperform single larger ones when fused properly.

### Alternative Path: Upgrade the Reranker Instead

Agent 9 (Conversational Retrieval) revealed that SmartSearch achieves 93.5% on LoCoMo with **no embedding model at all** — just reranking. Neuromem's current reranker (ms-marco-MiniLM-L6-v2, ~22M) could be upgraded to **mxbai-rerank-large-v1 (435M, DeBERTaV3)** for potentially higher impact than changing the embedding model.

---

*Research conducted March 18-19, 2026. All benchmark scores are self-reported by model providers unless otherwise noted. Scores from different MTEB versions are not directly comparable.*
