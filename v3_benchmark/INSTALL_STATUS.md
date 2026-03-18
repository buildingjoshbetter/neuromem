# V3 Benchmark — Install Status

Venv: `/Users/j/Desktop/neuromem/.venv_v3` (Python 3.12)

## Install Results

| # | System | Package | Version | Import | Status | Notes |
|---|--------|---------|---------|--------|--------|-------|
| 1 | ChromaDB | chromadb | 1.5.5 | OK | READY | Baseline, no deps |
| 2 | Mem0 | mem0ai | 1.0.5 | OK | READY | Needs ANTHROPIC_API_KEY |
| 3 | LangMem | langmem | 0.0.30 | OK | READY | Needs ANTHROPIC_API_KEY |
| 4 | Graphiti | graphiti-core | 0.28.2 | OK | BLOCKED | Needs Neo4j (Docker) |
| 5 | Letta | letta + letta-client | 0.16.6 / 1.7.12 | OK (letta_client) | BLOCKED | Needs letta server running |
| 6 | MemMachine | memmachine | N/A | N/A | BLOCKED | Package not on PyPI |
| 7 | EverMemOS | evermemos | 0.3.13 | OK | READY | Needs API testing |
| 8 | Hindsight | hindsight | N/A | N/A | BLOCKED | Build error (use_2to3 invalid) |
| 9 | Cognee | cognee | 0.5.5 | OK | READY | Had issues in v2, verbose logs |
| 10 | SimpleMem | simplemem | 0.1.0 | OK | BLOCKED | Needs OPENAI_API_KEY |
| 11 | LightMem | lightmem | 0.0.0 | OK | READY | Version 0.0.0, may be stub |
| 12 | A-MEM | N/A | N/A | N/A | BLOCKED | GitHub clone only |
| 13 | Memary | memary | N/A | N/A | BLOCKED | Requires Python <=3.11.9 |
| 14 | OpenMemory | openmemory-py | 1.3.2 | OK | READY | Needs API testing |
| 15 | FTS5 | Built-in | SQLite 3.x | OK | READY | No deps |

## Summary

- **READY (can test):** ChromaDB, Mem0, LangMem, EverMemOS, Cognee, LightMem, OpenMemory, FTS5 = **8 systems**
- **BLOCKED (need services):** Graphiti (Neo4j), Letta (server), SimpleMem (OpenAI key) = **3 systems**
- **BLOCKED (install failed):** MemMachine (not on PyPI), Hindsight (build error), A-MEM (GitHub only), Memary (Python 3.11 only) = **4 systems**

## Package Conflicts
- Some deprecation warnings from pydantic v2 (letta, graphiti, cognee) — non-blocking
- urllib3/charset-normalizer version mismatch warning — non-blocking
