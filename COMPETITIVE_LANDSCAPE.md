# AI Memory Systems: Competitive Landscape Analysis
## March 2026 — Compiled for Neuromem Benchmarking

---

## THE FIELD AT A GLANCE

| System | Funding | Architecture | LoCoMo Score | Temporal | Contradiction | Entity Filter | Local? |
|--------|---------|-------------|-------------|----------|---------------|---------------|--------|
| **Mem0** | $24M | LLM extraction → vector + graph | 66.9% | None | LLM-dependent | None | Yes (OSS) |
| **Zep/Graphiti** | Series A | Temporal knowledge graph | 75.1% (disputed) | **Best in class** | Bi-temporal invalidation | Graph traversal | Yes (OSS) |
| **SuperMemory** | $2.6M | Fact DB + temporal tracking | 81.6% (GPT-4o) | Good | Timestamp-aware updates | Container tags | Cloud API |
| **Letta (MemGPT)** | Series A | OS-inspired 3-tier hierarchy | 74.0% | Basic | LLM reasoning | Via archival search | Yes (OSS) |
| **LangMem** | LangChain | LLM extraction → InMemoryStore | 58.1% | None | Supports updates | Namespace scoping | Yes (OSS) |
| **Cognee** | Seed | Knowledge graph + LLM extraction | N/A | Via graph edges | Via graph updates | Entity nodes | Yes (OSS) |
| **ChromaDB** | N/A | Raw vector DB + metadata filters | N/A (baseline) | Via date metadata | None | Via metadata | Yes (OSS) |
| **SimpleMem** | Academic | Semantic compression → retrieval | +64% vs Claude-Mem | Via compression | Via synthesis | N/A | Yes |
| **Hindsight** | Enterprise | Proprietary agent memory | 91.4% (Gemini-3) | Yes | Yes | Yes | Cloud |
| **OpenMemory** | OSS | Cognitive engine + temporal graph | ~95% recall (claimed) | Temporal graph | Hierarchical decomp | Memory types | Yes (OSS) |
| **PowerMem** | OSS | Hybrid vector+FTS+graph + decay | N/A | Ebbinghaus curve | Via graph | Via graph | Yes (OSS) |
| **MemoRAG** | Academic | Memory-based + dual-system RAG | WebConf 2025 | Via memory model | Via reasoning | N/A | Yes |
| **A-MEM** | NeurIPS 2025 | Zettelkasten dynamic indexing | Superior vs SOTA | Via dynamic linking | Via memory evolution | Via tags/keywords | Yes |
| **Engram** | OSS | SQLite + FTS5 + vector (E2EE) | N/A | FTS5 date queries | None | None | Yes (local-first) |

---

## TIER 1: THE MAIN COMPETITORS

### 1. Mem0 ($24M raised)
**What it is:** LLM-powered fact extraction + vector/graph storage
**What it was designed for:** Production AI assistant memory — simple API, fast retrieval, cost reduction (90% fewer tokens)
**Architecture:**
- Phase 1: LLM extracts discrete facts from conversations
- Phase 2: LLM decides ADD/UPDATE/DELETE/MERGE vs existing memories
- Storage: 20+ vector DBs supported, optional Neo4j graph (v1.1+)
- Retrieval: Cosine similarity on embeddings

**Strengths:**
- Simple API (3 methods: add, search, get)
- Production-grade: async, caching, reranking
- Best documentation and ecosystem
- Graph memory (v1.1) adds entity relationships
- 26% accuracy improvement over OpenAI memory

**Weaknesses (from our M1 test + research):**
- "Name is Josh" pollution: high-frequency facts dominate unrelated queries
- Zero temporal awareness in base version
- Contradiction resolution is LLM-dependent (inconsistent)
- Multi-agent memory cross-pollination by default
- LLM failure cascade: if extraction LLM produces bad JSON, memories silently drop
- Gemini produces malformed JSON, breaking extraction entirely
- Long-running agents (>10K turns) show performance degradation
- Pricing cliff: $19 → $249/mo (no mid-tier)

**Our M1 Score: 5/20 hits, 5/20 partial, 10/20 fail**

---

### 2. Zep / Graphiti (Temporal Knowledge Graph)
**What it is:** Bi-temporal knowledge graph with hybrid search
**What it was designed for:** Enterprise agents needing temporal reasoning and fact evolution tracking
**Architecture:**
- 3-layer graph: Episode (raw) → Semantic Entity → Community
- Bi-temporal model: event timeline (T) + transaction timeline (T')
- Each fact has validity window (t_valid → t_invalid)
- Hybrid retrieval: cosine similarity + BM25 keyword + graph traversal, fused via RRF
- Entity resolution: entropy-gated fuzzy matching (MinHash + LSH)

**Strengths:**
- **Best temporal reasoning** in the field (+38-48% improvement)
- Contradiction resolution via deterministic temporal invalidation (not LLM judgment)
- Non-lossy: old facts preserved with timestamps, not deleted
- Sub-second latency (P95: 300ms) despite graph complexity
- Full provenance: every derived fact traces back to source episode
- Community detection for high-level summaries

**Weaknesses:**
- Requires Neo4j (vendor lock-in for graph store)
- Higher upfront cost: 4-6 LLM calls per episode for entity extraction
- Docker image severely outdated (v0.10 vs v0.22)
- SDK integration gaps (zep-cloud/zep-python don't support Graphiti natively)
- Community Edition deprecated (cloud push)
- Still relies on LLM for entity extraction (garbage in, garbage out)

**LoCoMo Score: 75.1% (disputed with Mem0)**

---

### 3. SuperMemory ($2.6M raised)
**What it is:** Fact database with temporal tracking, marketed as "living knowledge graph"
**What it was designed for:** Fast, cheap memory API with auto-ingestion (Google Drive, Notion, GitHub, Gmail)
**Architecture:**
- Not a true graph DB — PostgreSQL + Cloudflare KV + Drizzle ORM
- Memory relationships: Updates (supersedes), Extends (enriches), Derives (infers)
- Dual-layer timestamps: documentDate + eventDate
- isLatest field tracking for contradiction resolution
- Hybrid search: semantic + keyword + memory-specific lookup

**Strengths:**
- **10x faster than Zep, 25x faster than Mem0** (sub-300ms recall)
- **Much cheaper**: $19/mo Pro vs Mem0's $249/mo Pro
- Built-in auto-sync connectors (Google Drive, Notion, GitHub, Gmail)
- Better UX than Mem0 (Scira AI publicly switched from Mem0 to SuperMemory)
- 16K GitHub stars

**Weaknesses:**
- "Living knowledge graph" is marketing — it's a fact DB with version tracking
- **Worst False Memory Ratio** in HaluMem study — extracts excessive info without filtering
- Production stability issues (platform downtime, SSL errors, SDK bugs)
- Benchmark rankings outdated (Hindsight now exceeds on LongMemEval)
- Contradiction resolution mechanisms not publicly documented in detail
- Cloud-only (no self-hosted option)

**LoCoMo Score: 81.6% (GPT-4o) but contested**

---

### 4. Letta / MemGPT (OS-Inspired Hierarchy)
**What it is:** 3-tier memory hierarchy where the LLM actively manages its own memory
**What it was designed for:** Agents that need unlimited context through deliberate memory management
**Architecture:**
- Core Memory = RAM (always in context, ~2KB, writeable via function calls)
- Archival Memory = Disk (unlimited, requires semantic search to retrieve)
- Recall Memory = Logs (conversation history, searchable)
- LLM uses function calls to move data between tiers (append, replace, search, archive)
- "Heartbeat" mechanism: LLM chains multiple memory operations in one step

**Strengths:**
- **Reduces context pollution**: only essential facts consume tokens
- **Agent autonomy**: LLM decides what to keep vs archive (like human working memory)
- **Infinite scalability**: archival memory grows without degrading retrieval
- **Complete agent runtime**: REST API, tool ecosystems, orchestration
- Research finding: agent tool proficiency matters more than memory infrastructure

**Weaknesses:**
- No native temporal versioning (Zep does this better)
- Function call overhead adds latency for multi-hop queries
- Quality depends on LLM making good keep/archive decisions
- More complex to debug than simple vector retrieval
- No built-in contradiction detection
- Requires running a Letta server (not just a library)

**LoCoMo Score: 74.0% (GPT-4o mini, filesystem memory)**

---

### 5. LangMem (LangChain Memory SDK)
**What it is:** LangChain's official memory extraction + storage layer
**What it was designed for:** Drop-in memory for LangChain/LangGraph agents
**Architecture:**
- create_memory_manager: LLM extracts memories from conversations
- InMemoryStore or PostgresStore for persistence
- Supports custom Pydantic schemas for structured memories
- enable_inserts + enable_updates for memory lifecycle

**Strengths:**
- Tight LangChain/LangGraph integration
- Supports custom memory schemas (structured extraction)
- Can run fully local with InMemoryStore
- Configurable embedding providers

**Weaknesses:**
- **60s latency** on benchmarks (impractical for interactive use)
- Relatively new (v0.0.30)
- Limited documentation compared to Mem0
- No temporal reasoning
- No entity filtering
- Accuracy: 58.1% on LoCoMo (below Mem0)

**LoCoMo Score: 58.1% (worst of major systems)**

---

## TIER 2: EMERGING COMPETITORS

### 6. Hindsight (vectorize.io)
- **Most accurate** on LongMemEval: 91.4% (Gemini-3 Pro)
- Enterprise-focused, Fortune 500 clients
- Proprietary, cloud-only
- Limited public information on architecture

### 7. SimpleMem
- Academic: semantic lossless compression (3-stage pipeline)
- **+64% performance boost** over Claude-Mem on LoCoMo
- Compression → Synthesis → Retrieval
- Available on PyPI

### 8. OpenMemory (CaviraOSS)
- Cognitive memory engine with hierarchical decomposition
- 5 memory types: semantic, episodic, procedural, emotional, reflective
- Claims ~95% recall, 338 QPS
- Claims to outperform Zep/Mem0/SuperMemory
- Native MCP server for Claude Desktop

### 9. A-MEM (NeurIPS 2025)
- Zettelkasten-inspired dynamic memory networks
- Memories evolve: new memories trigger updates to connected memories
- Superior to SOTA on 6 foundation models
- Dynamic indexing + interconnected knowledge

### 10. PowerMem
- Hybrid: vector + FTS + graph DB
- **Ebbinghaus forgetting curve** implementation
- Memory naturally decays based on access patterns

### 11. Engram
- Privacy-first (E2EE, local-first)
- SQLite + FTS5 + vector search
- Works with Claude, Cursor, any MCP tool
- Interesting for Neuromem: uses same FTS5 approach you're building

---

## ARCHITECTURE TAXONOMY

### Pattern 1: LLM Extraction → Vector Search
**Systems:** Mem0, LangMem, SuperMemory
**How it works:** LLM processes raw text → extracts discrete facts → embeds facts → cosine similarity retrieval
**Good at:** Simple fact recall, user preferences, named entity lookup
**Bad at:** Temporal queries, multi-hop reasoning, contradiction resolution
**Why:** Vector similarity has no concept of time, relationships, or fact validity

### Pattern 2: Temporal Knowledge Graph
**Systems:** Zep/Graphiti, PowerMem
**How it works:** Extract entities + relationships → build timestamped graph → graph traversal + vector search
**Good at:** Temporal reasoning, fact evolution, contradiction detection, multi-hop queries
**Bad at:** Simple deployments (requires graph DB), high-throughput ingestion
**Why:** Graph construction is expensive but enables reasoning vector search can't do

### Pattern 3: OS-Inspired Hierarchy
**Systems:** Letta/MemGPT, MMAG
**How it works:** Tier context into core (always-on) vs archival (searchable) → LLM manages movement
**Good at:** Token efficiency, agent autonomy, infinite scaling
**Bad at:** Temporal versioning, fast retrieval of specific facts
**Why:** Designed for agent context management, not memory retrieval

### Pattern 4: Raw Vector DB + Metadata
**Systems:** ChromaDB, Qdrant, Weaviate (as memory layers)
**How it works:** Store raw text with metadata → embed → cosine similarity + metadata filters
**Good at:** Speed, simplicity, metadata filtering (date, sender, category)
**Bad at:** Semantic understanding, consolidation, anything requiring intelligence
**Why:** No processing intelligence, but metadata filters compensate for some use cases

### Pattern 5: Semantic Compression
**Systems:** SimpleMem, LightMem, MemoRAG
**How it works:** Compress information semantically → synthesize summaries → retrieve compressed form
**Good at:** Token efficiency (117x reduction), long-context handling
**Bad at:** Preserving exact details, real-time ingestion
**Why:** Compression trades detail for efficiency

### Pattern 6: Cognitive/Bio-Inspired
**Systems:** OpenMemory, A-MEM, PowerMem, Memoripy
**How it works:** Model human memory processes (forgetting curves, consolidation, episodic/semantic split)
**Good at:** Natural information lifecycle, reducing memory bloat
**Bad at:** Predictability (decay can lose important info), complexity
**Why:** Human memory isn't perfect — bio-inspired systems inherit both strengths and weaknesses

---

## BENCHMARK LANDSCAPE

### Available Standardized Benchmarks

| Benchmark | Size | Focus | Available? |
|-----------|------|-------|-----------|
| **LoCoMo** | 10 convos, 300 turns each | Long-term conversational memory | GitHub (public) |
| **LongMemEval** | 500 QA, 1.5M tokens | Multi-session reasoning, temporal | GitHub (public) |
| **ConvoMem** | 75K QA pairs | Realistic conversation distribution | Salesforce |
| **Minerva** | Programmable | Search, recall, edit, compare | GitHub (Microsoft) |
| **MEMTRACK** | Procedural | Multi-platform workflow (Slack/Git/Linear) | NeurIPS 2025 |
| **PerLTQA** | 8.5K QA pairs | Personal long-term memory | GitHub |
| **EpBench** | Synthetic narratives | Episodic memory (time/space events) | GitHub |

### Known Scores (LoCoMo)
1. MemMachine v0.2: **84.87%**
2. SuperMemory (GPT-5): **84.6%**
3. SuperMemory (GPT-4o): **81.6%**
4. Zep: **75.14%** (methodology disputed)
5. Memobase: **75.78%**
6. Letta: **74.0%**
7. Mem0: **66.9%**
8. LangMem: **58.1%**

**Critical note:** Vendors dispute each other's LoCoMo scores. Zep and Mem0 have publicly argued about methodology. Independent evaluation recommended.

---

## WHERE NEUROMEM FITS

Based on the 6-layer architecture (L0-L5):

| Neuromem Layer | Competitive Advantage | Who Currently Does This |
|----------------|----------------------|------------------------|
| L0 Personality Engram | Identity-stable persona | Letta (core memory) — but no drift protection |
| L1 Working Memory | Session context | Everyone (basic) |
| L2 Episodic Memory | Timestamped events with FTS5 | Zep/Graphiti (temporal KG) — but requires Neo4j |
| L3 Semantic (Hybrid RRF) | FTS5 + vector + RRF fusion | Zep does this, but tied to Neo4j graph |
| L4 Salience Guard | Contextual relevance scoring | Nobody does this well — all use raw cosine |
| L5 Consolidation + Predictive Coding | 7% storage rate, supersession logic | SuperMemory attempts; Zep's temporal invalidation is closest |

### Neuromem's Unique Differentiators:
1. **L4 Salience Guard**: No competitor contextually scores relevance — they all return whatever cosine similarity says
2. **Predictive Coding Filter (7% storage)**: Only PowerMem attempts decay, but not predictive filtering
3. **Local-first with no external dependencies**: Engram is closest, but lacks the full architecture
4. **SQLite + FTS5 + sqlite-vec stack**: Zero network calls, single-file database
5. **EWC identity drift protection**: Nobody protects against personality drift

### Key Competitive Threats:
1. **Zep/Graphiti** solves temporal reasoning (your L2/L5) but requires Neo4j
2. **SuperMemory** is faster and cheaper but has false memory problems
3. **Hindsight** has highest accuracy but is proprietary/cloud-only
4. **A-MEM** (NeurIPS 2025) has interesting Zettelkasten approach to memory evolution

---

## CRITICAL FINDING: THE MEMTRACK REVELATION

The MEMTRACK benchmark (Patronus AI, NeurIPS 2025) tested real-world workflows across Slack, Linear, and Git. Key finding:

> **Memory backends (Zep, Mem0) show negligible improvement or slight degradation compared to no memory system at all in multi-platform scenarios.**

This suggests current memory systems are optimized for single-conversation recall but **fail at cross-platform information synthesis** — exactly the kind of real-world problem Neuromem's consolidation engine could solve.

---

## WHAT THE HALU-MEM STUDY REVEALS

The HaluMem academic benchmark tested hallucinations in memory systems:
- **SuperMemory**: Worst False Memory Ratio — extracts excessive info without filtering
- **Mem0**: Moderate false memories — LLM extraction introduces hallucinated facts
- **Implication for Neuromem**: The Predictive Coding Filter (L5, 7% storage rate) directly addresses this — by storing less, you hallucinate less

---

*Last updated: March 14, 2026*
*Sources: 8 research agents, 150+ URLs, GitHub surveys, academic papers, Reddit discussions*
