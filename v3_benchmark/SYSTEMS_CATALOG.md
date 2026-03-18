# Universal AI Memory Systems Benchmark v3 — Systems Catalog
## 15 Systems Under Test | March 2026

---

## QUICK REFERENCE TABLE

| # | System | Tier | Architecture | Install | External Deps | Risk |
|---|--------|------|-------------|---------|---------------|------|
| 1 | ChromaDB | T1 | Raw Vector+Metadata | `pip install chromadb` | None | LOW |
| 2 | Mem0 | T1 | LLM Extraction→Vector | `pip install mem0ai` | OpenAI key | LOW |
| 3 | LangMem | T1 | LLM Extraction→Vector | `pip install langmem` | OpenAI key | LOW |
| 4 | Zep/Graphiti | T1 | Temporal KG | `pip install graphiti-core` | Neo4j 5.26+ | MEDIUM |
| 5 | Letta | T1 | OS-Inspired | `pip install letta` | Server process | MEDIUM |
| 6 | MemMachine | T1 | Cognitive/Bio-Inspired | `pip install memmachine` | PostgreSQL+pgvector, Neo4j, OpenAI key | HIGH |
| 7 | EverMemOS | T1 | Cognitive/Bio-Inspired | GitHub clone + Docker | Docker, MongoDB, Elasticsearch, Milvus, Redis, LLM key | HIGH |
| 8 | Hindsight | T1 | Semantic Compression | `pip install hindsight-client` | Hindsight server (Docker or pip) | MEDIUM |
| 9 | Cognee | T2 | Temporal KG | `pip install cognee` | OpenAI key (default) | MEDIUM |
| 10 | SimpleMem | T2 | Semantic Compression | `pip install simplemem` | OpenAI key (required) | LOW |
| 11 | LightMem | T2 | Semantic Compression | GitHub clone + pip install -e . | OpenAI or Qwen key | MEDIUM |
| 12 | A-MEM | T2 | Cognitive/Bio-Inspired | GitHub clone + requirements.txt | OpenAI key | MEDIUM |
| 13 | Memary | T2 | Temporal KG | `pip install memary` | Neo4j, Ollama or OpenAI key | HIGH |
| 14 | OpenMemory | T2 | Cognitive/Bio-Inspired | `pip install openmemory-py` | None (SQLite default) | LOW |
| 15 | FTS5 Baseline | T1 | Raw Vector+Metadata | Built-in (sqlite3) | None | LOW |

---

## TIER 1 — MUST TEST

---

### 1. ChromaDB (Baseline)

**Version:** 1.5.5 (March 10, 2026)
**Architecture:** Raw Vector DB + Metadata Filters
**Purpose in benchmark:** Dumb baseline. Pure cosine similarity with no intelligence layer. Every system must beat this to justify its existence.

**Install:**
```bash
pip install chromadb
```

**External Dependencies:** None. Fully self-contained, runs in-process.

**Python Requirements:** >=3.9

**Published Benchmark Scores:**
- LoCoMo: N/A (not designed for conversational memory)
- Serves as our zero-intelligence baseline

**What They Claim:** Embedding database for AI applications. Not a memory system — just storage + retrieval.

**Key API Methods:**
```python
import chromadb

client = chromadb.Client()                         # In-memory
client = chromadb.PersistentClient(path="./db")     # On-disk

collection = client.create_collection("memories")
collection.add(
    documents=["Josh likes coffee"],
    metadatas=[{"timestamp": "2026-03-14", "source": "chat"}],
    ids=["mem_001"]
)
results = collection.query(
    query_texts=["what does josh drink"],
    n_results=5,
    where={"source": "chat"}                       # Metadata filter
)
collection.update(ids=["mem_001"], documents=["Josh switched to tea"])
collection.delete(ids=["mem_001"])
```

**Known Issues:**
- No semantic understanding — returns whatever is closest in embedding space
- No temporal reasoning, contradiction detection, or consolidation
- Metadata filters compensate for some use cases but require manual schema design
- Large collections (>1M docs) can have slow query times without tuning

**Risk Level: LOW** — battle-tested, no external deps, will definitely work.

---

### 2. Mem0

**Version:** 1.0.0+ (March 3, 2026)
**Architecture:** LLM Extraction → Vector Search (+ optional graph via Neo4j)
**Funding:** $24M

**Install:**
```bash
pip install mem0ai
```

**External Dependencies:**
- OpenAI API key (default LLM: gpt-4.1-nano-2025-04-14 for extraction)
- Default vector store: Qdrant (on-disk, bundled)
- Optional: Neo4j for graph memory (v1.1+)

**Python Requirements:** >=3.9

**Published Benchmark Scores:**
- LoCoMo: **66.9%**
- Claims 26% accuracy improvement over OpenAI built-in memory
- Claims 90% token cost reduction

**What They Claim:** Universal memory layer for AI apps. Simple 3-method API, production-grade.

**Key API Methods:**
```python
from mem0 import Memory

m = Memory()
# Or with config:
m = Memory.from_config({"llm": {"provider": "openai", "config": {"model": "gpt-4.1-mini"}}})

m.add("I'm allergic to peanuts", user_id="josh")
m.add([{"role": "user", "content": "I moved to Austin"}], user_id="josh")

results = m.search("allergies", user_id="josh")
memories = m.get_all(user_id="josh")
m.update(memory_id="xxx", data="allergic to peanuts and shellfish")
m.delete(memory_id="xxx")
m.delete_all(user_id="josh")
```

**Known Issues (from v2 testing + research):**
- "Name is Josh" pollution: high-frequency facts dominate unrelated queries
- Zero temporal awareness in base version
- Contradiction resolution is LLM-dependent and inconsistent
- Multi-agent memory cross-pollination by default (no namespace isolation without config)
- LLM failure cascade: bad JSON from extraction LLM silently drops memories
- Gemini as extraction LLM produces malformed JSON
- Long-running agents (>10K turns) show performance degradation
- Our M1 test: 5/20 hits, 5/20 partial, 10/20 fail

**Risk Level: LOW** — widely used, well-documented, will install and run without issues. Performance issues are architectural, not operational.

---

### 3. LangMem

**Version:** 0.0.30 (latest)
**Architecture:** LLM Extraction → InMemoryStore / PostgresStore
**Maintainer:** LangChain (official)

**Install:**
```bash
pip install langmem
```

**External Dependencies:**
- OpenAI API key (or other LLM provider)
- Optional: PostgreSQL for persistent storage (default is InMemoryStore)
- Requires langchain, langgraph, trustcall as transitive deps

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LoCoMo: **58.1%** (worst of major systems)
- 60-second latency on benchmark runs (impractical for interactive use)

**What They Claim:** Drop-in memory for LangChain/LangGraph agents. Structured extraction with custom Pydantic schemas.

**Key API Methods:**
```python
from langmem import create_memory_manager, create_memory_store_manager

# Create memory manager
manager = create_memory_manager(
    "anthropic:claude-sonnet-4-5-20250929",
    instructions="Extract key facts about the user",
    enable_inserts=True,
    enable_updates=True
)

# Process conversation
memories = await manager.ainvoke(
    {"messages": [{"role": "user", "content": "I moved to Austin last month"}]}
)

# With store
from langgraph.store.memory import InMemoryStore
store = InMemoryStore()
memory_manager = create_memory_store_manager(store, namespace=("user", "josh"))
```

**Known Issues:**
- Extremely slow (60s per operation in benchmarks)
- v0.0.x — still pre-1.0, API may change
- Limited documentation compared to Mem0
- No temporal reasoning whatsoever
- No entity filtering or scoping beyond namespace
- Tightly coupled to LangChain ecosystem

**Risk Level: LOW** — pip install works fine, but performance expectations should be very low.

---

### 4. Zep / Graphiti

**Version:** graphiti-core (latest on PyPI, active development)
**Architecture:** Temporal Knowledge Graph (bi-temporal model)
**Funding:** Series A

**Install:**
```bash
pip install graphiti-core
```

**External Dependencies:**
- **Neo4j 5.26+** (required — graph storage backend)
  - Install via Neo4j Desktop, Docker, or brew
  - `docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.26`
- OpenAI API key (for entity extraction)
- Supports FalkorDB 1.1.2, Kuzu 0.11.2, or Amazon Neptune as alternatives to Neo4j

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LoCoMo: **75.1%** (methodology disputed with Mem0)
- Claims +38-48% improvement in temporal reasoning

**What They Claim:** Best-in-class temporal reasoning. Bi-temporal model tracks fact validity windows. Non-lossy — old facts preserved with timestamps.

**Key API Methods:**
```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import OpenAIClient

client = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient()
)
await client.build_indices_and_constraints()

# Add episode (raw conversation)
await client.add_episode(
    name="chat_001",
    episode_body="Josh moved from NYC to Austin in January 2026",
    source_description="user_conversation",
    reference_time=datetime.now()
)

# Search with hybrid retrieval (cosine + BM25 + graph traversal via RRF)
results = await client.search("Where does Josh live?")
# Results include temporal validity, provenance, entity relationships

# _search also available for advanced queries
await client._search("Josh's address history", num_results=10)
```

**Known Issues:**
- **Neo4j dependency is heavy** — requires running a separate database server
- Docker image severely outdated (v0.10 vs v0.22 in code)
- SDK integration gaps (zep-cloud/zep-python don't support Graphiti natively)
- Community Edition deprecated (cloud push from Zep)
- 4-6 LLM calls per episode for entity extraction (expensive at scale)
- Still relies on LLM for entity extraction (garbage in, garbage out)

**Risk Level: MEDIUM** — Neo4j setup can fail. Docker image outdated. But core graphiti-core pip package works.

---

### 5. Letta (formerly MemGPT)

**Version:** Latest release (March 4, 2026)
**Architecture:** OS-Inspired 3-Tier Memory Hierarchy
**Funding:** Series A
**Research:** Based on MemGPT paper (ICLR 2024)

**Install:**
```bash
pip install letta
```

**External Dependencies:**
- **Letta server process** must be running (`letta server` command)
- Default DB: SQLite (or external PostgreSQL via LETTA_PG_URI)
- OpenAI or other LLM provider API key
- Server runs on port 8283

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LoCoMo: **74.0%** (GPT-4o mini, filesystem memory)
- Research finding: agent tool proficiency matters more than memory infrastructure

**What They Claim:** LLM manages its own memory like an OS manages RAM/disk. Infinite context through deliberate memory management.

**Key API Methods:**
```python
from letta_client import Letta

client = Letta(base_url="http://localhost:8283")

# Create agent with memory
agent = client.agents.create(
    name="memory_test",
    model="openai/gpt-4.1",
    embedding="openai/text-embedding-3-small"
)

# Core Memory (always in context, ~2KB, like RAM)
client.agents.core_memory.update(
    agent_id=agent.id,
    section="human",
    value="Name: Josh. Lives in Austin."
)

# Archival Memory (unlimited, like disk — requires search to retrieve)
client.agents.archival_memory.insert(
    agent_id=agent.id,
    content="Josh moved from NYC to Austin in January 2026"
)
results = client.agents.archival_memory.search(
    agent_id=agent.id,
    query="where did Josh live before"
)

# Send message (agent auto-manages memory via function calls)
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{"role": "user", "content": "I just got a dog named Luna"}]
)
```

**Known Issues:**
- Requires running a server process (not just a library import)
- No native temporal versioning
- Quality depends on LLM making good keep/archive decisions
- Function call overhead adds latency for multi-hop queries
- No built-in contradiction detection
- More complex to debug than simple vector retrieval

**Risk Level: MEDIUM** — server process adds complexity. SQLite default is fine but server must stay running during benchmark.

---

### 6. MemMachine

**Version:** 0.1.10 (latest on PyPI)
**Architecture:** Hybrid Cognitive (Episodic + Semantic + Procedural + Profile memory)
**Creator:** MemVerge

**Install:**
```bash
# Client library
pip install memmachine

# Server (Docker recommended)
docker compose up -d  # Starts PostgreSQL + Neo4j + MemMachine server

# Or from source with GPU support:
# git clone https://github.com/MemMachine/MemMachine
# uv pip install ".[gpu]"
```

**External Dependencies:**
- **PostgreSQL with pgvector extension** (profile memory storage)
- **Neo4j** (episodic memory with vector similarity)
- **OpenAI API key** (required for extraction)
- MemMachine server process on port 8080
- Docker Compose recommended for dependency management

**Python Requirements:** >=3.12

**Published Benchmark Scores:**
- LoCoMo: **84.87%** (weighted average across all categories)
- Outperforms Mem0, Zep, Memobase on LoCoMo

**What They Claim:** Universal memory layer for AI agents. 4 memory types (episodic, semantic, procedural, profile) that persist across sessions, models, and environments.

**Key API Methods:**
```python
from memmachine import MemMachineClient

client = MemMachineClient(base_url="http://localhost:8080")

# Add memory (auto-categorized into episodic/semantic/procedural/profile)
client.add(
    content="Josh moved to Austin in January 2026",
    user_id="josh",
    metadata={"source": "conversation"}
)

# Search across all memory types
results = client.search(query="where does Josh live", user_id="josh")

# Type-specific retrieval
episodes = client.get_episodes(user_id="josh", limit=10)
profile = client.get_profile(user_id="josh")
```

**Known Issues:**
- Heavy dependency stack (PostgreSQL + Neo4j + server process)
- Python 3.12+ requirement excludes some environments
- Docker Compose setup can be fragile with port conflicts
- Relatively new (v0.1.x) — API stability not guaranteed
- Configuration via cfg.yml can be confusing
- GPU support requires additional setup

**Risk Level: HIGH** — multiple external services (Postgres, Neo4j, server). Docker Compose is the realistic path, but port conflicts and service startup order can cause failures.

---

### 7. EverMemOS

**Version:** Open-source release (2026, GitHub only — no PyPI package)
**Architecture:** Cognitive/Bio-Inspired (structured extraction + multi-strategy retrieval)
**Creator:** EverMind AI

**Install:**
```bash
git clone https://github.com/EverMind-AI/EverMemOS.git
cd EverMemOS

# Start dependency services (MongoDB, Elasticsearch, Milvus, Redis)
docker compose up -d

# Install Python dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Configure API keys in .env
# LLM_API_KEY=your_key       (for memory extraction)
# VECTORIZE_API_KEY=your_key  (for embeddings/reranking)

# Start server
uv run python src/run.py
# API available at http://localhost:1995/api/v1
```

**External Dependencies:**
- **Docker 20.10+** (required for dependency services)
- **MongoDB** (document storage)
- **Elasticsearch** (text search)
- **Milvus** (vector search)
- **Redis** (caching)
- **LLM API key** (extraction)
- **Vectorize API key** (embeddings/reranking)
- **uv package manager**
- **4GB+ RAM**

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LoCoMo: **92.3%** (SOTA — highest reported score)
- Claims to outperform full-context LLM inputs while using far fewer tokens
- LongMemEval: competitive (exact score varies by configuration)

**What They Claim:** Brain-inspired long-term memory OS. Only system to outperform LLMs using full-context inputs. Structured extraction into episodes, profiles, foresights, event logs.

**Key API Methods:**
```python
import httpx

BASE = "http://localhost:1995/api/v1"

# Add conversation episode
httpx.post(f"{BASE}/episodes", json={
    "content": "Josh moved to Austin in January 2026",
    "user_id": "josh",
    "session_id": "session_001"
})

# Search with retrieval strategy
results = httpx.get(f"{BASE}/memories/search", params={
    "query": "where does josh live",
    "user_id": "josh",
    "retrieve_method": "hybrid"  # 5 strategies available
})

# Get profile
profile = httpx.get(f"{BASE}/profiles/josh")

# Get foresights (predictive memories)
foresights = httpx.get(f"{BASE}/foresights", params={"user_id": "josh"})
```

**Known Issues:**
- **No PyPI package** — must clone from GitHub
- **Heaviest dependency stack** in the entire benchmark (MongoDB + Elasticsearch + Milvus + Redis)
- Docker Compose setup is complex — 4+ services must be healthy before server starts
- uv package manager may not be installed on all systems
- API documentation is sparse compared to Mem0/ChromaDB
- Relatively new open-source release — community support is thin
- 92.3% score uses their own evaluation framework — independent verification needed

**Risk Level: HIGH** — most complex setup in the benchmark. Four database services via Docker. If any container fails to start, the whole system is unusable. Budget extra time for debugging.

---

### 8. Hindsight

**Version:** Latest (hindsight-client on PyPI, hindsight server via Docker/pip)
**Architecture:** Structured Memory with Observation Synthesis
**Creator:** Vectorize.io
**Research:** "Hindsight is 20/20" paper (arXiv:2512.12818)

**Install:**
```bash
# Client library
pip install hindsight-client -U

# Server (Docker)
docker run -p 8888:8888 vectorize/hindsight:latest

# Or server via pip
pip install hindsight
hindsight serve
```

**External Dependencies:**
- Hindsight server process (Docker or pip install)
- LLM provider key (supports OpenAI, Ollama for local)
- Can run fully local with Ollama (no API keys needed)

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LongMemEval: **91.4%** (Gemini 3 Pro) — highest reported on this benchmark
- Multi-session: 21.1% → 79.7% improvement
- Temporal reasoning: 31.6% → 79.7% improvement
- Knowledge updates: 60.3% → 84.6% improvement

**What They Claim:** Most accurate agent memory ever tested. Memory as structured substrate for reasoning. Automatic consolidation of facts into synthesized observations.

**Key API Methods:**
```python
from hindsight_client import Hindsight

hs = Hindsight(base_url="http://localhost:8888")

# Retain — store information
hs.retain(
    namespace="josh",
    content="Josh moved from NYC to Austin in January 2026"
)

# Recall — retrieve relevant memories
memories = hs.recall(
    namespace="josh",
    query="Where does Josh live?"
)

# Reflect — synthesize observations from existing memories
observations = hs.reflect(
    namespace="josh",
    query="What patterns exist in Josh's life changes?"
)
```

**Known Issues:**
- Requires running a server process (not just a library)
- Best scores use Gemini 3 Pro (expensive, cloud-only)
- Enterprise-focused heritage — some features may be cloud-gated
- Four memory networks (world facts, experiences, entity summaries, beliefs) add complexity
- Limited info on self-hosted performance degradation at scale
- Observation synthesis adds latency

**Risk Level: MEDIUM** — pip install for both client and server works. Docker option provides clean isolation. Ollama support means we can test without API keys.

---

## TIER 2 — SHOULD TEST

---

### 9. Cognee

**Version:** 0.5.5 (latest on PyPI)
**Architecture:** Knowledge Graph + LLM Extraction (multi-hop reasoning)
**Funding:** Seed round

**Install:**
```bash
pip install cognee
```

**External Dependencies:**
- OpenAI API key (default LLM + embeddings provider)
- Default storage: SQLite + LanceDB + Kuzu (all file-based, zero infrastructure)
- Optional: PostgreSQL, Neo4j, Weaviate for production deployments

**Python Requirements:** >=3.10

**Published Benchmark Scores:**
- LoCoMo: N/A (no published scores)
- Claims strong multi-hop reasoning via knowledge graph

**What They Claim:** Knowledge engine for AI agent memory in 5 lines of code. Transforms raw data into persistent, dynamic AI memory. Combines vector search with graph databases.

**Key API Methods:**
```python
import cognee

# Configure
cognee.config.set_llm_config({"provider": "openai", "model": "gpt-4.1-mini"})

# Ingest data
await cognee.add("Josh moved to Austin. He works at a startup.")

# Build knowledge graph
await cognee.cognify()

# Refine graph post-ingestion
await cognee.memify()

# Search (hybrid vector + graph)
results = await cognee.search("Where does Josh work?")
```

**Known Issues (from v2 testing):**
- Embedding dimension mismatch errors in v2 benchmarks
- API is fully async — requires asyncio event loop
- `cognify()` step can be slow for large documents
- Graph construction quality depends on LLM extraction
- Default file-based storage (Kuzu) has limited community support
- Still pre-1.0 (v0.5.x)

**Risk Level: MEDIUM** — pip install works, file-based defaults eliminate infra issues. But embedding errors from v2 need monitoring. Async-only API requires careful adapter design.

---

### 10. SimpleMem

**Version:** Latest on PyPI (released January 20, 2026)
**Architecture:** Semantic Lossless Compression (3-stage pipeline)
**Creator:** Aiming Lab (academic)

**Install:**
```bash
pip install simplemem
```

**External Dependencies:**
- **OpenAI API key** (required — no local alternative documented)
- Supports OpenAI-compatible endpoints (Qwen, Azure OpenAI) via OPENAI_BASE_URL

**Python Requirements:** >=3.9

**Published Benchmark Scores:**
- LoCoMo: **+64% performance boost** over Claude-Mem baseline
- 43% F1 on long-context benchmarks
- 98% token usage reduction
- 30x token compression ratio

**What They Claim:** Efficient lifelong memory via semantic lossless compression. Three-stage pipeline: Compression → Synthesis → Retrieval.

**Key API Methods:**
```python
from simplemem import SimpleMem

mem = SimpleMem(api_key="sk-...")

# Create memory (with on-the-fly synthesis)
mem.create_memory(
    content="Josh moved to Austin in January 2026",
    user_id="josh"
)

# Search memories
results = mem.search_memories(
    query="where does Josh live",
    user_id="josh"
)

# Read specific memory
memory = mem.read_memory(memory_id="xxx")

# Also available: HybridRetriever.retrieve() and AnswerGenerator.generate_answer()
```

**Known Issues:**
- OpenAI API key is mandatory — cannot run fully local
- Academic project — may have limited production hardening
- Compression trades some detail for efficiency
- Token reduction claims need independent verification
- MCP server integration is separate package (SimpleMem-MCP)

**Risk Level: LOW** — straightforward pip install, simple API. Only blocker is OpenAI key requirement.

---

### 11. LightMem

**Version:** ICLR 2026 paper release
**Architecture:** Semantic Compression (Atkinson-Shiffrin inspired 3-stage: Sensory → Short-term → Long-term)
**Creator:** ZJU NLP Lab (Zhejiang University)

**Install:**
```bash
git clone https://github.com/zjunlp/LightMem.git
cd LightMem
conda create -n lightmem python=3.11 -y
conda activate lightmem
pip install -e .
```

**External Dependencies:**
- OpenAI API key or Qwen API key (for LLM operations)
- No database dependencies — memory stored in structured files

**Python Requirements:** 3.11 (recommended via conda)

**Published Benchmark Scores:**
- LongMemEval + LoCoMo: up to **117x token reduction** with competitive accuracy
- Up to 310x fewer API calls (offline batch processing)
- GPT and Qwen backbone evaluations published

**What They Claim:** Most token-efficient memory system. Inspired by Atkinson-Shiffrin human memory model. Separates online inference from offline consolidation ("sleep-time update").

**Key API Methods:**
```python
# LightMem uses a pipeline-based API (academic code style)
from lightmem import LightMem

lm = LightMem(config_path="config.yaml")

# Stage 1: Sensory memory — lightweight compression + topic grouping
lm.compress(conversation_turns)

# Stage 2: Short-term memory — topic-aware consolidation
lm.consolidate()

# Stage 3: Long-term memory — offline "sleep-time" update
lm.sleep_update()

# Retrieval
results = lm.retrieve(query="where does Josh live")
```

**Known Issues:**
- **No PyPI package** — must clone from GitHub and install from source
- Academic code — not production-hardened
- Conda environment recommended (not just pip)
- Config file setup required before use
- "Sleep-time update" (offline batch consolidation) adds complexity to benchmarking
- Limited documentation beyond the paper and README

**Risk Level: MEDIUM** — install from source works but is more fragile than pip. Academic code may have edge cases. Config setup required.

---

### 12. A-MEM

**Version:** NeurIPS 2025 paper release
**Architecture:** Cognitive/Bio-Inspired (Zettelkasten dynamic indexing)
**Creator:** Wujiang Xu et al.

**Install:**
```bash
# Research code (paper reproduction)
git clone https://github.com/WujiangXu/A-mem.git
cd A-mem
python -m venv a-mem
source a-mem/bin/activate
pip install -r requirements.txt

# Alternative: agiresearch implementation
git clone https://github.com/agiresearch/A-mem.git
```

**External Dependencies:**
- OpenAI API key (or compatible LLM provider)
- No database dependencies — memories stored in structured format

**Python Requirements:** >=3.9

**Published Benchmark Scores:**
- Claims superior performance vs SOTA on 6 foundation models
- LoCoMo: outperforms baseline systems (exact scores vary by model)
- Key innovation: memories evolve dynamically, not just stored

**What They Claim:** Zettelkasten-inspired dynamic memory networks. Memories are interconnected and evolve — adding new memory triggers updates to connected memories. Dynamic indexing creates living knowledge networks.

**Key API Methods:**
```python
from a_mem import AMem

agent_memory = AMem(llm_provider="openai", model="gpt-4.1-mini")

# Add memory (triggers dynamic linking + connected memory updates)
agent_memory.add(
    content="Josh moved to Austin in January 2026",
    tags=["location", "life_change"]
)

# Agentic search (traverses dynamic memory network)
results = agent_memory.search(query="Josh's living situation")

# Get memory by ID
memory = agent_memory.get(memory_id="xxx")

# Memory network evolves: new additions trigger updates to related memories
agent_memory.add(
    content="Josh got a new job at an Austin startup",
    tags=["career", "location"]
)
# ^ This automatically updates the "moved to Austin" memory's connections
```

**Known Issues:**
- **No PyPI package** — GitHub clone only
- Two competing repositories (WujiangXu vs agiresearch) — unclear which is canonical
- Academic code — research reproduction focus, not production use
- Dynamic memory evolution adds LLM calls (expensive at scale)
- requirements.txt may have version pinning issues
- Limited documentation beyond paper

**Risk Level: MEDIUM** — straightforward Python setup but academic code quality. Two repos to choose from. Dynamic linking may cause unexpected behavior in benchmarks.

---

### 13. Memary

**Version:** 0.1.3 (latest on PyPI)
**Architecture:** Knowledge Graph + Multi-hop Reasoning
**Creator:** Julius Cederholm (kingjulio8238)

**Install:**
```bash
pip install memary
```

**External Dependencies:**
- **Neo4j** (required for knowledge graph storage)
- **Ollama** (recommended — Llama 3 8B/40B default) OR OpenAI API key
- Vision model support via Ollama (LLaVA) or GPT-4 Vision

**Python Requirements:** <=3.11 (llama-index dependency breaks on 3.12+)

**Published Benchmark Scores:**
- No published LoCoMo or LongMemEval scores
- Claims strong multi-hop reasoning via knowledge graph traversal

**What They Claim:** Open-source memory layer for autonomous agents. Multi-hop reasoning joins multiple subgraphs for complex queries. Memory Stream tracks all entities with timestamps.

**Key API Methods:**
```python
from memary import MemaryAgent

agent = MemaryAgent(
    neo4j_uri="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_model="llama3:8b"  # or "gpt-3.5-turbo"
)

# Route query through ReAct agent
response = agent.query("What are Josh's recent life changes?")

# Memory stream captures entities + timestamps
stream = agent.get_memory_stream()

# Knowledge graph retrieval with multi-hop
kg_results = agent.search_kg(query="Josh's connections in Austin")
```

**Known Issues:**
- **Python 3.12+ not supported** (llama-index dependency)
- Requires Neo4j running (same dependency as Zep/Graphiti)
- Ollama must be running if using local models
- v0.1.x — very early stage
- Limited documentation and examples
- ReAct agent routing adds latency and unpredictability
- Small community — 1 primary maintainer

**Risk Level: HIGH** — Python version constraint (<=3.11), Neo4j dependency, Ollama dependency. Triple points of failure. If our test environment is Python 3.12+, this system cannot participate.

---

### 14. OpenMemory

**Version:** Latest on PyPI (openmemory-py)
**Architecture:** Cognitive Memory Engine (5 memory types + temporal graph)
**Creator:** CaviraOSS

**Install:**
```bash
pip install openmemory-py
```

**External Dependencies:**
- **None for basic usage** — SQLite default, synthetic embeddings available
- Optional: OpenAI key for real embeddings
- Optional: External vector store for production scale

**Python Requirements:** >=3.9

**Published Benchmark Scores:**
- Claims ~**95% recall** on internal benchmarks
- Claims 338 QPS throughput
- Claims to outperform Zep, Mem0, SuperMemory
- No independent LoCoMo or LongMemEval scores published

**What They Claim:** Self-hosted, modular AI memory engine. 5 cognitive memory types (semantic, episodic, procedural, emotional, reflective). Composite scoring based on salience + recency + coactivation.

**Key API Methods:**
```python
from openmemory import OpenMemory

mem = OpenMemory(
    path="./memory.sqlite",
    tier="fast",
    embeddings={"provider": "synthetic"}  # or "openai"
)

# Simplified client
from openmemory.client import Memory
mem = Memory()  # sensible defaults

# Add memory
mem.add("Josh is allergic to peanuts", user_id="user123")

# Search with time filtering
results = mem.search(
    "allergies",
    user_id="user123",
    startTime="2026-01-01",
    endTime="2026-03-14"
)

# Delete
mem.delete(memory_id="xxx")
```

**Known Issues:**
- 95% recall claim is self-reported — no independent verification
- "5 memory types" may be more marketing than architecture (unclear how emotional/reflective differ in practice)
- Temporal graph features are newer additions — stability unknown
- Documentation is improving but still gaps vs Mem0
- Relatively small community (CaviraOSS is a small org)
- Adaptive decay engine could cause unexpected memory loss in benchmarks

**Risk Level: LOW** — SQLite default means zero external deps. Synthetic embeddings mean no API key needed for basic testing. Easy to get running.

---

### 15. FTS5 Baseline (SQLite Full-Text Search)

**Version:** Built into Python stdlib (sqlite3 module)
**Architecture:** Keyword Search + Temporal Metadata (no vectors, no AI)
**Purpose in benchmark:** Keyword/temporal baseline. How well does simple text search work before adding any intelligence?

**Install:**
```bash
# Nothing to install — built into Python
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

**External Dependencies:** None. Zero. Nada.

**Python Requirements:** Any (comes with Python stdlib)

**Published Benchmark Scores:**
- N/A (custom baseline for this benchmark)

**What It Is:** SQLite's Full-Text Search extension. BM25 ranking, boolean queries, phrase matching, prefix queries. Combined with timestamp metadata for temporal filtering.

**Key API Methods:**
```python
import sqlite3

db = sqlite3.connect("memory.db")
db.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS memories USING fts5(
        content,
        user_id,
        timestamp,
        source,
        tokenize='porter'
    )
""")

# Add memory
db.execute(
    "INSERT INTO memories(content, user_id, timestamp, source) VALUES (?, ?, ?, ?)",
    ("Josh moved to Austin in January 2026", "josh", "2026-01-15", "conversation")
)

# BM25-ranked search
results = db.execute("""
    SELECT content, rank FROM memories
    WHERE memories MATCH 'austin OR moved'
    ORDER BY rank
    LIMIT 10
""").fetchall()

# Temporal + keyword search
results = db.execute("""
    SELECT content FROM memories
    WHERE memories MATCH 'austin'
    AND timestamp >= '2026-01-01'
    ORDER BY rank
""").fetchall()

db.commit()
```

**Known Issues:**
- No semantic understanding — "where does Josh live" won't match "moved to Austin"
- No vector similarity, embedding, or AI layer
- BM25 ranking is keyword frequency based, not meaning based
- No consolidation, contradiction detection, or memory evolution
- Requires exact or stemmed keyword matches

**Risk Level: LOW** — literally cannot fail to install. It's Python stdlib.

---

## ARCHITECTURE TAXONOMY SUMMARY

### Pattern 1: LLM Extraction → Vector Search
**Systems:** Mem0 (#2), LangMem (#3)
- LLM extracts facts → embeds → cosine similarity retrieval
- Simple, well-understood, but no temporal/relational reasoning

### Pattern 2: Temporal Knowledge Graph
**Systems:** Zep/Graphiti (#4), Memary (#13)
- Entity + relationship extraction → timestamped graph → hybrid retrieval
- Best for temporal reasoning, but requires graph database

### Pattern 3: OS-Inspired Hierarchy
**Systems:** Letta (#5)
- Core memory (RAM) vs archival memory (disk) — LLM manages movement
- Good for token efficiency, bad for specific fact retrieval

### Pattern 4: Raw Vector DB + Metadata
**Systems:** ChromaDB (#1), FTS5 (#15)
- No intelligence layer — pure storage + retrieval baselines
- ChromaDB = vector baseline, FTS5 = keyword baseline

### Pattern 5: Semantic Compression
**Systems:** SimpleMem (#10), LightMem (#11), Hindsight (#8)
- Compress information semantically → synthesize → retrieve compressed form
- Best token efficiency, but may lose detail

### Pattern 6: Cognitive/Bio-Inspired
**Systems:** MemMachine (#6), EverMemOS (#7), A-MEM (#12), OpenMemory (#14)
- Model human memory processes (memory types, evolution, decay, consolidation)
- Most ambitious architectures, highest complexity

---

## DEPENDENCY MATRIX

| System | OpenAI Key | Neo4j | Docker | Server Process | Other |
|--------|-----------|-------|--------|----------------|-------|
| ChromaDB | - | - | - | - | - |
| Mem0 | Required | Optional | - | - | Qdrant (bundled) |
| LangMem | Required | - | - | - | - |
| Zep/Graphiti | Required | **Required** | Recommended | - | - |
| Letta | Required | - | Optional | **Required** | Port 8283 |
| MemMachine | Required | **Required** | **Recommended** | **Required** | PostgreSQL+pgvector, Port 8080 |
| EverMemOS | Required | - | **Required** | **Required** | MongoDB, Elasticsearch, Milvus, Redis |
| Hindsight | Optional* | - | Optional | **Required** | *Ollama for local |
| Cognee | Required | - | - | - | LanceDB+Kuzu (bundled) |
| SimpleMem | **Required** | - | - | - | No local option |
| LightMem | Required | - | - | - | Conda recommended |
| A-MEM | Required | - | - | - | - |
| Memary | Required | **Required** | - | - | Ollama recommended, Python <=3.11 |
| OpenMemory | Optional | - | - | - | SQLite (bundled) |
| FTS5 | - | - | - | - | - |

**Systems requiring zero API keys:** ChromaDB, FTS5, OpenMemory (synthetic embeddings), Hindsight (with Ollama)

**Systems requiring Neo4j:** Zep/Graphiti, MemMachine, Memary

**Systems requiring Docker:** EverMemOS (mandatory), MemMachine (recommended), Hindsight (optional)

**Systems requiring server processes:** Letta, MemMachine, EverMemOS, Hindsight

---

## INSTALLATION ORDER RECOMMENDATION

Install in order of risk (LOW first, HIGH last) to maximize early progress:

### Phase 1 — Zero-risk baselines (5 min)
1. **FTS5** — built-in, nothing to install
2. **ChromaDB** — `pip install chromadb`

### Phase 2 — Simple pip installs with API keys (15 min)
3. **Mem0** — `pip install mem0ai`
4. **LangMem** — `pip install langmem`
5. **SimpleMem** — `pip install simplemem`
6. **OpenMemory** — `pip install openmemory-py`
7. **Cognee** — `pip install cognee`

### Phase 3 — GitHub clones (20 min)
8. **A-MEM** — clone + venv + requirements.txt
9. **LightMem** — clone + conda env + pip install -e .

### Phase 4 — Server processes (30 min)
10. **Hindsight** — pip install client + server, or Docker
11. **Letta** — pip install + `letta server`

### Phase 5 — Heavy infrastructure (45+ min)
12. **Zep/Graphiti** — pip install + Neo4j setup
13. **Memary** — pip install + Neo4j + Ollama (Python <=3.11!)
14. **MemMachine** — Docker Compose (PostgreSQL + Neo4j + server)
15. **EverMemOS** — Docker Compose (MongoDB + Elasticsearch + Milvus + Redis + server)

---

## KNOWN RISKS AND MITIGATIONS

| Risk | Systems Affected | Mitigation |
|------|-----------------|------------|
| Python 3.12+ incompatibility | Memary (<=3.11 required) | Use separate venv with Python 3.11 |
| Neo4j setup failure | Zep, MemMachine, Memary | Use Docker: `docker run neo4j:5.26` |
| Docker Compose complexity | EverMemOS, MemMachine | Pre-pull images, check port conflicts |
| API key costs | All LLM-dependent systems | Use gpt-4.1-nano/mini for extraction, set spending limits |
| Server process crashes | Letta, MemMachine, EverMemOS, Hindsight | Wrap in subprocess with health checks |
| Stale/outdated packages | Memary, A-MEM, LightMem | Pin versions, check GitHub for recent commits |
| Async-only APIs | Cognee, EverMemOS | Use asyncio.run() wrapper in adapter |
| Vendor-disputed benchmarks | Mem0 vs Zep LoCoMo scores | Run our own evaluation — trust nothing |

---

*Last updated: March 14, 2026*
*Compiled for Neuromem v3 Benchmark from web research, PyPI, GitHub, and competitive landscape analysis*
