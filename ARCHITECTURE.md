# Neuromem: 6-Layer Memory Architecture

## System Design for a Local-First AI Memory Engine

**Version:** 0.1 (March 2026)
**Status:** Pre-implementation (architecture specification)
**Target:** 70%+ on the Neuromem 60-query benchmark (12 categories, 797 synthetic messages)

---

## Table of Contents

1. [Design Thesis](#design-thesis)
2. [Architecture Overview](#architecture-overview)
3. [Layer Specifications](#layer-specifications)
   - [L0: Personality Engram](#l0-personality-engram)
   - [L1: Working Memory](#l1-working-memory)
   - [L2: Episodic Memory](#l2-episodic-memory)
   - [L3: Semantic Memory](#l3-semantic-memory)
   - [L4: Salience Guard](#l4-salience-guard)
   - [L5: Consolidation + Predictive Coding](#l5-consolidation--predictive-coding)
4. [Database Schema](#database-schema)
5. [Search Pipeline](#search-pipeline)
6. [Benchmark Targets](#benchmark-targets)
7. [Stack and Dependencies](#stack-and-dependencies)
8. [Design Decisions and Tradeoffs](#design-decisions-and-tradeoffs)

---

## Design Thesis

Every funded memory system in the market today follows one of two failing patterns:

1. **LLM extraction destroys information.** Mem0 ($24M raised) compresses rich contextual messages into decontextualized facts. When you search for "What was the scope 1 accuracy on the Meridian Steel pilot?", the extracted memory "Set up the carbonsense.io domain on 2024-07-30" is irrelevant. The specific number (96.1%) was never extracted. Mem0 scored 9.2% on our benchmark -- below raw vector search.

2. **Vector similarity has no concept of time, negation, or entity boundaries.** ChromaDB returns whatever is semantically closest. Ask about "Jordan's dog" and you also get emotionally charged messages like "omg jordan!!" because the character name creates false cosine similarity. This is the query pollution problem. ChromaDB scored 49.2%.

Neuromem takes a different approach: **preserve raw data, search it intelligently, and build structure on top -- never instead of.**

The architecture is six layers, each targeting specific failure modes observed in competitor benchmarks. Every layer earns its place by addressing categories where all tested systems scored 2/10 or worse.

### Core Constraints

- **Zero network calls** for memory operations. No API keys, no cloud dependencies.
- **Single-file database.** SQLite with FTS5 and sqlite-vec in one `.db` file.
- **No LLM in the retrieval path.** LLMs are used only at ingest-time (L0 profile building, L5 consolidation) and never at query time.
- **Sub-100ms query latency.** The search pipeline must return results faster than a human notices a delay.
- **$0-2/month operating cost.** All compute is local. The only ongoing cost is disk space.

---

## Architecture Overview

```
                    +-----------------------+
                    |     Query Input       |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |   Query Analyzer      |
                    |  (temporal intent,    |
                    |   entity detection,   |
                    |   negation flags)      |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
            +------>   Parallel Search      <------+
            |       +-----------+-----------+      |
            |                   |                  |
   +--------+-------+   +------v------+   +-------+--------+
   | L2: FTS5       |   | L3: Vector  |   | L0: Engram     |
   | BM25 keyword   |   | Cosine sim  |   | Personality    |
   | + timestamp    |   | 256-dim     |   | profiles       |
   +--------+-------+   +------+------+   +-------+--------+
            |                   |                  |
            +--------+  +------+                   |
                     |  |                          |
            +--------v--v-----------+              |
            |   L3: RRF Fusion      |              |
            |   1/(k + rank_fts) +  |              |
            |   1/(k + rank_vec)    |              |
            +-----------+-----------+              |
                        |                          |
            +-----------v-----------+              |
            |   L4: Salience Guard  |              |
            |   Entity filtering    |              |
            |   Noise reduction     |              |
            |   Query-aware scoring |              |
            +-----------+-----------+              |
                        |                          |
            +-----------v-----------+              |
            |   Temporal Filter     |              |
            |   (if time intent     |              |
            |    detected)          |              |
            +-----------+-----------+              |
                        |                          |
            +-----------v-----------+   +----------v--------+
            |   Ranked Results      |   | Profile Answers   |
            |   (retrieval queries) |   | (personality/     |
            |                       |   |  analytical)      |
            +-----------------------+   +-------------------+
```

### Layer Interaction Model

Layers are not a sequential pipeline. They interact in three distinct modes:

1. **Ingest-time layers** (L0, L5): Process messages when they are stored. Build profiles, summaries, and fact timelines asynchronously. These layers make the data smarter before any query arrives.

2. **Query-time layers** (L2, L3, L4): Execute in parallel and fuse results at search time. These layers find and rank relevant information.

3. **Deferred layer** (L1): Working memory is session-scoped context. It is not exercised by the benchmark (all queries are stateless) and is deferred to the Paradox integration phase.

---

## Layer Specifications

### L0: Personality Engram

**Purpose:** Extract and maintain per-entity personality profiles from message patterns. Answer questions that require synthesizing behavioral data scattered across hundreds of messages.

**Why it exists:** Every system we benchmarked scored 0-3/10 on personality inference queries. "What kind of person is Jordan?" requires aggregating traits from months of messages -- no retrieval system can do this by returning 10 results. The answer must be pre-computed.

**Target categories:** `personality` (0H 3P across competitors), `analytical` (0H 2P across competitors)

#### Data Model

Each entity (person, organization) gets a profile document built from all their messages. Profiles contain:

```
Entity: "Jordan Chen"
Role: protagonist / primary user
Communication patterns:
  - With Dev: technical, direct, tactical ("can you check the gRPC latency?")
  - With Sam: casual, emotional, vulnerable ("dude i almost cried")
  - With Riley: loving, sometimes apologetic ("i know i've been MIA")
  - With Mom: reassuring, filters bad news ("everything's great mom")
Personality traits (with evidence counts):
  - Driven/ambitious: 47 messages
  - Anxious about failure: 23 messages
  - Loyal to friends: 18 messages
  - Self-aware: 12 messages (therapy, journaling)
Preferences:
  - Food: oat milk lattes, breakfast tacos, ramen, sushi
  - Activities: running, gym, yoga (inconsistent)
  - Values: impact over money, authenticity
Fears/insecurities:
  - Running out of money (early stage)
  - Losing Riley due to work obsession
  - Tying self-worth to company performance
```

#### Implementation

- **Ingest-time processing.** When messages are loaded, iterate over all messages grouped by entity. For each entity, build a profile by analyzing:
  - Vocabulary and tone patterns per relationship
  - Topics discussed (via keyword clustering)
  - Emotional valence signals (exclamation marks, hedging language, apologies)
  - Stated preferences (explicit "I love X" / "I hate Y")
  - Behavioral patterns (routine mentions, habit changes)

- **Profile storage.** Profiles are stored in the `entity_profiles` table as structured JSON. They are queryable directly -- when a personality or analytical query is detected, the search pipeline retrieves the profile instead of (or in addition to) searching messages.

- **Update strategy.** Profiles are rebuilt on bulk ingest. For streaming ingest (future), profiles are updated incrementally using a delta merge: new evidence is appended, trait scores are recalculated, contradicting evidence triggers re-evaluation.

- **No LLM at query time.** Profiles are built at ingest time. Querying a profile is a direct lookup, not an LLM call.

#### Scoring Logic

For personality queries, the system:
1. Identifies the target entity from the query
2. Retrieves their profile from `entity_profiles`
3. Returns the relevant profile sections based on query intent (traits, preferences, fears, communication style)
4. Supplements with top matching messages from L2/L3 for evidence

---

### L1: Working Memory

**Purpose:** Short-term context buffer holding the current conversation or session state.

**Status:** Deferred. The benchmark operates on stateless queries against a static dataset. Working memory provides no advantage here.

**Future role:** When Neuromem integrates with Paradox (macOS context engine), L1 will hold the current session context: what the user is looking at, what they asked 30 seconds ago, what app is in the foreground. This context biases search toward recency and relevance.

**Implementation notes (for future):**
- Fixed-size ring buffer (last N messages or last T minutes)
- Influences L4 salience scoring by boosting results related to current context
- Cleared on session end
- Never persisted to disk

---

### L2: Episodic Memory

**Purpose:** Timestamp-aware full-text search over raw message content. Find specific facts by keyword, filter by time range, reconstruct event sequences.

**Why it exists:** Temporal queries are the single biggest gap in the market. ChromaDB scored 1H 1P, LangMem scored 0H 2P, Mem0 scored 0H 1P on temporal queries. None of them can answer "What happened in the month after Demo Day?" because vector similarity has no concept of time.

**Target categories:** `exact_recall`, `temporal`, `ocr_retrieval`

#### FTS5 Configuration

```sql
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    sender,
    recipient,
    category,
    modality,
    content_rowid='id',
    tokenize='porter unicode61'
);
```

- **Porter stemming** reduces words to stems: "running" matches "run", "manufacturers" matches "manufacturing". This is critical for recall on keyword searches.
- **Unicode61 tokenizer** handles non-ASCII content (names, technical terms, emoji-adjacent text).
- **BM25 ranking** is built into FTS5. It penalizes common terms and rewards rare, query-specific terms. This is superior to raw cosine similarity for exact recall.

#### Temporal Query Processing

When the query analyzer detects temporal intent (keywords like "after", "before", "last month", "in 2025", "recently", date references), L2 adds timestamp constraints:

```sql
-- "What happened in the month after Demo Day (June 15, 2025)?"
SELECT m.*, messages_fts.rank AS bm25_score
FROM messages m
JOIN messages_fts ON m.id = messages_fts.rowid
WHERE messages_fts MATCH ?
  AND m.timestamp >= '2025-06-15'
  AND m.timestamp <= '2025-07-15'
ORDER BY messages_fts.rank;
```

Temporal intent detection is rule-based, not LLM-based:
- Regex patterns for date formats (ISO, natural language months, relative terms)
- Keyword triggers: "after", "before", "during", "between", "since", "until", "last [week/month/year]", "in [month/year]"
- Reference resolution: "after Demo Day" requires a lookup of known events (from L5 summaries or message content) to resolve "Demo Day" to a date

#### Strengths Over Competitors

- **ChromaDB** has no time awareness at all. Metadata filters exist but require the caller to know exact date ranges.
- **Mem0** strips timestamps during LLM extraction. The extracted fact "Jordan has a dog named Biscuit" has no temporal context.
- **LangMem** preserves some timestamps but cannot query by time range.
- **FTS5** with timestamp columns gives Neuromem native temporal filtering that none of these systems have.

---

### L3: Semantic Memory

**Purpose:** Vector similarity search using dense embeddings, fused with FTS5 results via Reciprocal Rank Fusion. Finds conceptually related content that keyword search misses.

**Why it exists:** FTS5 alone cannot find "stress management techniques" when the messages say "therapy", "meditation", "Headspace app", "7pm work boundary". Semantic search bridges the vocabulary gap.

**Target categories:** `semantic`, `cross_modal`

#### Embedding Model

**Model2Vec potion-base-8M**

| Property | Value |
|----------|-------|
| Dimensions | 256 |
| Model size | 30 MB |
| Speed | 500x faster than transformer models |
| Hardware | CPU only, no GPU required |
| Per-chunk latency | <1ms |
| API calls | Zero (fully offline) |

This model was selected for three reasons:
1. **Privacy.** No message content leaves the machine.
2. **Speed.** Embedding 797 messages takes under 1 second. Re-indexing the full dataset is trivial.
3. **Size.** 30 MB is acceptable for a local application.

The quality tradeoff is real -- sentence-transformers models (384-dim, ~100MB) produce better embeddings. But for personal memory retrieval at this scale (thousands to tens of thousands of messages), 256-dim Model2Vec is sufficient. If benchmark results prove otherwise, upgrading to a larger model is a one-line change.

#### Vector Storage

```sql
CREATE VIRTUAL TABLE vec_messages USING vec0(
    id INTEGER PRIMARY KEY,
    embedding float[256]
);
```

sqlite-vec provides:
- Cosine similarity search via `vec_distance_cosine()`
- Exact nearest neighbor (no approximate indexing at this scale)
- Pure C extension, zero dependencies
- In-process with the same SQLite connection as FTS5

#### Reciprocal Rank Fusion (RRF)

RRF combines ranked lists from different retrieval systems without requiring score normalization. This is critical because BM25 scores and cosine similarity scores are on incomparable scales.

**Formula:**

```
score(d) = sum( 1 / (k + rank_i(d)) )    where k = 60
```

- `k = 60` is the standard constant from Cormack, Clarke & Buettcher (2009). No tuning required.
- `rank_i(d)` is document d's rank in the i-th retrieval system (FTS5 BM25 or vector cosine).
- A document ranked #1 in both systems gets: `1/(60+1) + 1/(60+1) = 0.0328`
- A document ranked #1 in FTS5 but #50 in vectors gets: `1/61 + 1/110 = 0.0255`
- A document that appears in only one system still gets scored, just with a single term.

**Implementation:**

```python
def rrf_fusion(fts5_results: list, vec_results: list, k: int = 60) -> list:
    """Fuse FTS5 and vector search results using Reciprocal Rank Fusion."""
    scores = {}

    for rank, doc_id in enumerate(fts5_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    for rank, doc_id in enumerate(vec_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

#### Why RRF Over Alternatives

- **Score normalization** (min-max or z-score) requires knowing the distribution of all scores, which varies per query. Fragile and requires tuning.
- **Weighted linear combination** (alpha * BM25 + (1-alpha) * cosine) requires choosing alpha, which is dataset-dependent.
- **RRF** is parameter-free (k=60 is stable across domains), treats each system as a black box, and has been validated in production at Zep/Graphiti, Obsidian hybrid search, and academic IR literature.

---

### L4: Salience Guard

**Purpose:** Filter noise from search results. Disambiguate entities. Prevent query pollution -- the problem where semantically similar but contextually irrelevant messages dominate results.

**Why it exists:** ChromaDB's biggest failure mode is returning messages like "omg jordan!! you won't believe this" as top results for queries about Jordan's dog, Jordan's company, or Jordan's health. The character name "Jordan" creates false cosine similarity across unrelated messages. Similarly, no system correctly handles "Who is Marcus?" when there are two different people named Marcus.

**Target categories:** `entity`, `negation`

#### Query Pollution Problem

Observed in ChromaDB benchmark results:

| Query | Top ChromaDB Result | Relevant? |
|-------|-------------------|-----------|
| "What is Jordan's dog's name?" | "omg jordan guess what just happened" | No |
| "CarbonSense pricing" | "Jordan told Sam about the pitch" | No |
| "Jordan's health stats" | "Jordan is so excited about Demo Day" | No |

The problem: high-frequency entity names (like the protagonist's name) create semantic gravity. Every message mentioning "Jordan" gets pulled toward every query mentioning "Jordan", regardless of topical relevance.

#### Entity Disambiguation

The salience guard maintains an entity index that maps names to distinct real-world entities:

```
"Marcus" -> [
    {entity_id: "marcus_johnson", role: "gym buddy", context: "Olympic lifts, met through Jake"},
    {entity_id: "marcus_lily_ex", role: "Lily's ex-boyfriend", context: "CrossFit, broke up Aug 2025, wanted Seattle"}
]

"Rachel" -> [
    {entity_id: "rachel_torres", role: "VP Sales CarbonSense", context: "hired Aug 2025, enterprise SaaS"},
    {entity_id: "rachel_kim", role: "Riley's friend", context: "doctor in Seattle, college friend"}
]
```

When a query references an ambiguous name, the salience guard:
1. Detects the entity reference in the query
2. Looks up all matching entities
3. Uses query context to determine which entity is intended (or returns both if the query is explicitly asking for disambiguation)
4. Filters results to messages associated with the correct entity

#### Noise Reduction Scoring

For each candidate result from L3 fusion, the salience guard computes a relevance penalty:

1. **Entity overlap score.** Does the result mention entities relevant to the query, or just the same name in an unrelated context?
2. **Topic coherence.** Does the result discuss the same topic as the query? (Measured by comparing the result's category/modality metadata against the query's detected intent.)
3. **Negation awareness.** If the query contains negation ("Did CarbonSense acquire EcoTrace?"), the guard boosts results that contain explicit negation ("Nina said absolutely not") and penalizes results that merely mention the topic without addressing the negation.

#### Implementation Approach

- **Entity index** is built at ingest time by scanning all messages for named entities (regex-based for known entities, with a fallback to capitalized proper nouns).
- **Per-message entity tags** are stored in a separate `message_entities` junction table linking message IDs to entity IDs.
- **Query-time filtering** adds entity constraints to the SQL query when entity references are detected.
- **Negation detection** is rule-based: scan the query for negation markers ("not", "didn't", "never", "no", "isn't", question patterns like "Did X do Y?").

---

### L5: Consolidation + Predictive Coding

**Purpose:** Hierarchical summarization, fact evolution tracking, contradiction resolution, and information-theoretic filtering. This layer makes the memory system smarter over time by compressing, connecting, and curating stored information.

**Why it exists:** Three critical failure modes in competitors:
1. **Contradiction blindness.** ChromaDB returns "CarbonSense uses PostgreSQL" and "CarbonSense migrated to ClickHouse" with equal confidence. No system tracks fact evolution.
2. **No consolidation.** Asking "Summarize the CarbonSense journey" requires synthesizing 100+ messages. No retrieval system returns 100 results.
3. **Storage bloat.** Every message is stored with equal weight. "haha nice" gets the same treatment as "We closed the Series A at $55M pre-money".

**Target categories:** `contradiction`, `multi_hop`, `consolidation`

#### Fact Timeline

The fact timeline tracks how specific facts evolve over time, enabling contradiction resolution:

```
Fact: "CarbonSense time-series database"
Timeline:
  2024-07-25  PostgreSQL          (source: msg #42)
  2025-05-10  Considering TimescaleDB  (source: msg #312)
  2025-05-18  Migrated to ClickHouse   (source: msg #327)
  CURRENT ->  ClickHouse (Postgres still used for users/auth/billing)

Fact: "CarbonSense pricing per facility"
Timeline:
  2024-10-15  $2,000 base / $5,000 enterprise    (source: msg #89)
  2025-03-20  $5,000 base / $12,000 enterprise   (source: msg #201, Nina's advice)
  CURRENT ->  $5,000 / $12,000 (Meridian grandfathered at $2K)
```

When a query asks "What database does CarbonSense use?", the system returns the CURRENT value with the evolution context, not a random historical mention.

#### Hierarchical Summarization

Messages are summarized at increasing levels of abstraction:

```
Level 0: Raw messages (797 messages)
Level 1: Daily summaries ("March 15, 2025: Jordan discussed ClickHouse migration
          with Dev, had therapy session, ran 5.2 miles")
Level 2: Weekly summaries ("Week of March 10-16, 2025: Database migration decision,
          3 new customer onboardings, Riley's birthday planning")
Level 3: Monthly summaries ("March 2025: Hired Aisha Rahman, migrated to ClickHouse,
          pricing raised to $5K/facility, 7 customers reached")
Level 4: Epoch summaries ("Q1 2025: Seed funded, team grew to 6, product-market fit
          confirmed with 7 customers and $43K MRR")
```

Summaries are stored in the `summaries` table and are searchable via both FTS5 and vector similarity. For consolidation and multi-hop queries, the system searches summaries in addition to raw messages, giving it access to pre-computed aggregations that span hundreds of messages.

#### Predictive Coding Filter

Inspired by the brain's predictive coding framework: only store information that violates expectations. If a message is predictable given existing context, it carries low information-theoretic value and can be de-prioritized.

**Target storage rate: ~7% of messages are high-salience.** This does not mean 93% are deleted -- all messages are preserved in L2 episodic memory. The predictive coding filter determines which messages are tagged as high-information for priority retrieval.

Criteria for high-information messages:
- **Fact changes.** Any message that contradicts or updates a previously established fact. ("We're switching to ClickHouse" -- contradicts "We use PostgreSQL".)
- **New entities.** First mention of a new person, company, or concept. ("Met Nina Vasquez at Epoch Coffee" -- new entity introduction.)
- **Emotional extremes.** Messages with high emotional valence. ("I almost cried when I saw the term sheet" -- significant emotional event.)
- **Quantitative data.** Messages containing numbers, percentages, dollar amounts, dates. ("96.1% accuracy on scope 1" -- specific measurable fact.)
- **Decision points.** Messages that record a decision. ("We're going with WeWork, not the Springdale lease" -- decision with alternatives.)

Messages that are NOT high-information:
- Greetings, acknowledgments ("sounds good", "haha nice", "omg")
- Scheduling logistics without substance ("let's do 3pm")
- Repeated mentions of already-known facts

#### Contradiction Resolution Strategy

When a query touches a fact that has evolved:
1. Check the `fact_timeline` table for the queried fact
2. Return the CURRENT value as the primary answer
3. Include the evolution history as supporting context
4. Flag if the query references a specific historical version (e.g., "What was the original pricing?" should return $2K, not $5K)

This is deterministic -- no LLM judgment required at query time. Zep/Graphiti achieves similar results with bi-temporal graph invalidation, but requires Neo4j. Neuromem achieves it with a simple timeline table in SQLite.

---

## Database Schema

All data lives in a single SQLite database file. The schema uses five core tables, two virtual tables (FTS5 and sqlite-vec), and one junction table.

```sql
-- ============================================================
-- Core Messages Table
-- Every message, in every modality, with full original content
-- ============================================================
CREATE TABLE messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    content     TEXT NOT NULL,
    sender      TEXT,
    recipient   TEXT,
    timestamp   TEXT NOT NULL,          -- ISO 8601 (YYYY-MM-DDTHH:MM:SS)
    category    TEXT,                   -- startup, personal, health, etc.
    modality    TEXT,                   -- imessage, email, ocr_receipt, calendar, note, etc.
    salience    REAL DEFAULT 0.0,      -- L5 predictive coding score (0.0 - 1.0)
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_messages_timestamp ON messages(timestamp);
CREATE INDEX idx_messages_sender ON messages(sender);
CREATE INDEX idx_messages_modality ON messages(modality);

-- ============================================================
-- FTS5 Full-Text Search (L2: Episodic Memory)
-- Porter stemming + unicode support
-- ============================================================
CREATE VIRTUAL TABLE messages_fts USING fts5(
    content,
    sender,
    recipient,
    category,
    modality,
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Sync triggers: keep FTS5 in lockstep with messages table
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content, sender, recipient, category, modality)
    VALUES (new.id, new.content, new.sender, new.recipient, new.category, new.modality);
END;

CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content, sender, recipient, category, modality)
    VALUES ('delete', old.id, old.content, old.sender, old.recipient, old.category, old.modality);
END;

CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content, sender, recipient, category, modality)
    VALUES ('delete', old.id, old.content, old.sender, old.recipient, old.category, old.modality);
    INSERT INTO messages_fts(rowid, content, sender, recipient, category, modality)
    VALUES (new.id, new.content, new.sender, new.recipient, new.category, new.modality);
END;

-- ============================================================
-- Vector Embeddings (L3: Semantic Memory)
-- Model2Vec potion-base-8M, 256 dimensions
-- ============================================================
CREATE VIRTUAL TABLE vec_messages USING vec0(
    id INTEGER PRIMARY KEY,
    embedding float[256]
);

-- ============================================================
-- Entity Profiles (L0: Personality Engram)
-- Pre-computed personality and behavioral data per entity
-- ============================================================
CREATE TABLE entity_profiles (
    entity_id       TEXT PRIMARY KEY,       -- e.g., "jordan_chen", "dev_patel"
    entity_name     TEXT NOT NULL,          -- display name
    entity_type     TEXT DEFAULT 'person',  -- person, organization, place
    profile_data    TEXT NOT NULL,          -- JSON: traits, preferences, patterns
    message_count   INTEGER DEFAULT 0,     -- number of messages analyzed
    first_seen      TEXT,                  -- earliest message timestamp
    last_seen       TEXT,                  -- latest message timestamp
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ============================================================
-- Message-Entity Junction (L4: Salience Guard)
-- Maps messages to the entities they reference
-- ============================================================
CREATE TABLE message_entities (
    message_id  INTEGER NOT NULL REFERENCES messages(id),
    entity_id   TEXT NOT NULL REFERENCES entity_profiles(entity_id),
    role        TEXT,                   -- 'sender', 'mentioned', 'about'
    PRIMARY KEY (message_id, entity_id)
);

CREATE INDEX idx_me_entity ON message_entities(entity_id);

-- ============================================================
-- Summaries (L5: Consolidation)
-- Hierarchical summaries at daily/weekly/monthly/epoch levels
-- ============================================================
CREATE TABLE summaries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    level       TEXT NOT NULL,          -- 'daily', 'weekly', 'monthly', 'epoch'
    period      TEXT NOT NULL,          -- '2025-03-15', '2025-W11', '2025-03', 'Q1-2025'
    entity_id   TEXT,                   -- NULL for global summaries, entity_id for per-entity
    content     TEXT NOT NULL,          -- summary text
    source_ids  TEXT,                   -- JSON array of message IDs this summarizes
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_summaries_level_period ON summaries(level, period);

-- ============================================================
-- Fact Timeline (L5: Contradiction Resolution)
-- Tracks how specific facts evolve over time
-- ============================================================
CREATE TABLE fact_timeline (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    fact_key    TEXT NOT NULL,          -- normalized fact identifier ("carbonsense_database")
    fact_value  TEXT NOT NULL,          -- the fact at this point in time
    timestamp   TEXT NOT NULL,          -- when this version became true
    source_id   INTEGER REFERENCES messages(id),
    is_current  INTEGER DEFAULT 1,     -- 1 = current version, 0 = superseded
    superseded_by INTEGER,             -- id of the fact_timeline row that replaced this
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_ft_fact_key ON fact_timeline(fact_key);
CREATE INDEX idx_ft_current ON fact_timeline(fact_key, is_current);
```

### Schema Size Estimates

For the benchmark dataset (797 messages):

| Table | Rows | Estimated Size |
|-------|------|----------------|
| messages | 797 | ~200 KB |
| messages_fts | 797 | ~300 KB (FTS5 index) |
| vec_messages | 797 | ~800 KB (797 x 256 x 4 bytes) |
| entity_profiles | ~35 | ~50 KB |
| message_entities | ~2,000 | ~40 KB |
| summaries | ~100 | ~50 KB |
| fact_timeline | ~50 | ~10 KB |
| **Total** | | **~1.5 MB** |

At 100K messages (production scale), the database would be approximately 150-200 MB. Easily fits on any device. Easily backed up by copying one file.

---

## Search Pipeline

A query flows through the system in six stages. The entire pipeline targets sub-100ms end-to-end latency.

### Stage 1: Query Analysis

Parse the incoming query to extract structured intent signals. This is rule-based, not LLM-based.

**Extracted signals:**

| Signal | Detection Method | Example |
|--------|-----------------|---------|
| Temporal intent | Regex for dates, relative time words | "after Demo Day" -> date_start=2025-06-15 |
| Entity references | Lookup against known entity names | "Marcus" -> [marcus_johnson, marcus_lily_ex] |
| Negation | Keyword scan (not, didn't, never, no) | "Did CarbonSense acquire EcoTrace?" -> negation=true |
| Modality hint | Keyword scan (receipt, email, calendar) | "What does the cap table show?" -> modality=ocr_document |
| Query type | Pattern matching | "What kind of person..." -> type=personality |
| Sender filter | Entity detection in "from" patterns | "What does Dev think about..." -> sender=dev_patel |

**Cost:** <1ms (string operations only)

### Stage 2: Parallel FTS5 + Vector Search

Both search systems execute simultaneously against the same query.

**FTS5 path (L2):**
```sql
SELECT m.id, m.content, m.sender, m.timestamp, messages_fts.rank AS bm25_score
FROM messages m
JOIN messages_fts ON m.id = messages_fts.rowid
WHERE messages_fts MATCH ?
ORDER BY messages_fts.rank
LIMIT 50;
```

**Vector path (L3):**
```python
query_embedding = model2vec.encode(query_text)  # <1ms
# sqlite-vec cosine similarity search
results = conn.execute("""
    SELECT id, vec_distance_cosine(embedding, ?) AS distance
    FROM vec_messages
    ORDER BY distance
    LIMIT 50
""", [query_embedding])
```

If the query analyzer detected a personality or analytical query type, L0 profile retrieval is also triggered in parallel.

**Cost:** ~5-15ms for both searches combined

### Stage 3: RRF Fusion

Merge the two ranked result lists using Reciprocal Rank Fusion.

```python
fused = {}
for rank, (doc_id, _) in enumerate(fts5_results):
    fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (60 + rank + 1)

for rank, (doc_id, _) in enumerate(vec_results):
    fused[doc_id] = fused.get(doc_id, 0.0) + 1.0 / (60 + rank + 1)

ranked = sorted(fused.items(), key=lambda x: x[1], reverse=True)
```

Documents that appear in both result sets get boosted. Documents that appear in only one still contribute. No tuning required.

**Cost:** <1ms (in-memory sort)

### Stage 4: Salience Filtering (L4)

Apply entity and noise filters to the fused results.

1. **Entity constraint.** If the query references a specific entity, filter results to messages tagged with that entity in `message_entities`.
2. **Ambiguity resolution.** If the entity reference is ambiguous (two Marcuses), either:
   - Use query context to select the right one ("Marcus from the gym" -> marcus_johnson)
   - Return results for both with clear labels (if the query explicitly asks for disambiguation)
3. **Noise penalty.** Demote results where the entity match is incidental (the message mentions "Jordan" but is not about the query topic).
4. **Negation boost.** If negation was detected, boost results containing negation language.

**Cost:** ~1-5ms (SQL lookups + re-ranking)

### Stage 5: Temporal Filtering

If the query analyzer detected temporal intent, apply date range constraints.

```sql
-- Filter already-ranked results by timestamp
WHERE id IN (?, ?, ?, ...)
  AND timestamp >= ?
  AND timestamp <= ?
ORDER BY timestamp [ASC|DESC]
```

For recency queries ("most recent", "latest"), sort by timestamp descending.
For sequence queries ("what happened after X"), sort by timestamp ascending.

**Cost:** <1ms (indexed column filter)

### Stage 6: Result Assembly

Return the top-K results (default K=10) with metadata:

```python
{
    "results": [
        {
            "id": 327,
            "content": "dev just finished the clickhouse migration...",
            "sender": "Jordan Chen",
            "timestamp": "2025-05-18T14:30:00",
            "modality": "imessage",
            "rrf_score": 0.0328,
            "matched_entities": ["dev_patel", "jordan_chen"],
        },
        # ...
    ],
    "profile_data": {  # Only for personality/analytical queries
        "entity_id": "jordan_chen",
        "traits": ["driven", "anxious", "loyal"],
        # ...
    },
    "fact_timeline": {  # Only for contradiction-prone queries
        "fact_key": "carbonsense_database",
        "current": "ClickHouse",
        "history": [...]
    },
    "query_analysis": {
        "temporal_intent": false,
        "entity_refs": ["jordan_chen"],
        "negation": false,
        "query_type": "exact_recall"
    }
}
```

**Total pipeline cost:** 10-30ms typical, 50-100ms worst case

---

## Benchmark Targets

### Per-Category Projections

Scoring: HIT = 2 points, PARTIAL = 1 point, MISS = 0. Each category has 5 queries (max 10 points per category, 120 total).

| Category | ChromaDB (49.2%) | LangMem (56.7%) | Neuromem Target | Key Layer | Mechanism |
|----------|-----------------|-----------------|-----------------|-----------|-----------|
| exact_recall | 4H 1P 0M (9) | 3H 2P 0M (8) | 5H 0P 0M (10) | L2 FTS5 | Porter stemming + BM25 finds exact facts better than cosine |
| semantic | 1H 1P 3M (3) | 2H 1P 2M (5) | 4H 1P 0M (9) | L3 Hybrid RRF | Dual retrieval catches both keyword and meaning matches |
| temporal | 1H 1P 3M (3) | 0H 2P 3M (2) | 4H 1P 0M (9) | L2 Temporal | FTS5 + timestamp filtering -- no competitor has this |
| entity | 3H 2P 0M (8) | 3H 2P 0M (8) | 5H 0P 0M (10) | L4 Salience | Entity disambiguation handles "two Marcuses" problem |
| contradiction | 3H 2P 0M (8) | 2H 2P 1M (6) | 4H 1P 0M (9) | L5 Fact Timeline | Deterministic temporal fact tracking, not LLM guessing |
| multi_hop | 0H 3P 2M (3) | 1H 3P 1M (5) | 2H 3P 0M (7) | L5 + L3 | Summaries pre-compute multi-message connections |
| cross_modal | 1H 2P 2M (4) | 1H 2P 2M (4) | 3H 2P 0M (8) | L3 Hybrid | Unified storage treats OCR, email, text equally |
| personality | 0H 1P 4M (1) | 0H 3P 2M (3) | 3H 2P 0M (8) | L0 Engram | Pre-computed profiles answer synthesis questions directly |
| negation | 1H 4P 0M (6) | 2H 2P 1M (6) | 4H 1P 0M (9) | L4 Salience | Negation detection + explicit "no" evidence boosting |
| ocr_retrieval | 3H 1P 1M (7) | 3H 1P 1M (7) | 5H 0P 0M (10) | L2 FTS5 | FTS5 searches OCR text identically to messages |
| consolidation | 1H 3P 1M (5) | 2H 2P 1M (6) | 3H 2P 0M (8) | L5 Summaries | Hierarchical summaries provide pre-computed aggregations |
| analytical | 0H 2P 3M (2) | 0H 1P 4M (1) | 1H 3P 1M (5) | L0 + L5 | Profiles + summaries, but this category inherently needs LLM reasoning |
| **TOTAL** | **59/120 (49.2%)** | **68/120 (56.7%)** | **102/120 (85.0%)** | | |

### Confidence Levels

| Category | Confidence | Rationale |
|----------|------------|-----------|
| exact_recall | High | FTS5 with BM25 is proven technology for keyword retrieval |
| temporal | High | This is the single biggest gap in every competitor. FTS5 + timestamps is a straightforward win |
| ocr_retrieval | High | FTS5 treats OCR text identically to any other text. No special handling needed |
| entity | High | Entity disambiguation is solvable with a lookup table. The data model supports it cleanly |
| negation | Medium-High | Rule-based negation detection handles most cases. Edge cases may need refinement |
| contradiction | Medium-High | Fact timeline is deterministic but requires accurate fact extraction at ingest time |
| semantic | Medium | Hybrid RRF is proven, but Model2Vec 256-dim may underperform larger models on semantic similarity |
| cross_modal | Medium | Depends on RRF quality and whether 256-dim embeddings capture cross-modal semantics |
| personality | Medium | Profile quality depends on ingest-time analysis. Novel approach, limited prior art |
| consolidation | Medium | Summary quality depends on how well we group and compress messages |
| multi_hop | Low-Medium | Multi-hop reasoning fundamentally requires connecting distant facts. Summaries help but may not be enough |
| analytical | Low | These queries require judgment ("What mistakes has Jordan made?"). No retrieval system solves this well |

### Why 70% is the Realistic Floor

The conservative target (70%) assumes:
- Full points on exact_recall, temporal, ocr_retrieval (categories where FTS5 is a near-certain win)
- Majority points on entity, negation, contradiction (structured data solutions)
- Partial points on semantic, personality, cross_modal, consolidation, multi_hop (novel approaches, some uncertainty)
- Minimal points on analytical (inherently hard without LLM reasoning in the retrieval path)

The aggressive target (85%) assumes the novel layers (L0, L4, L5) work as designed. This is achievable but depends on implementation quality.

---

## Stack and Dependencies

### Runtime Dependencies

| Component | Purpose | Version | Size | License |
|-----------|---------|---------|------|---------|
| Python | Runtime | 3.12+ | System | PSF |
| SQLite | Database | 3.45+ | System (built into Python) | Public domain |
| sqlite-vec | Vector search | 0.1.x | ~2 MB (C extension) | MIT / Apache-2.0 |
| Model2Vec | Embeddings | 0.4.x | ~30 MB model file | MIT |
| model2vec (potion-base-8M) | Model weights | - | 30 MB | MIT |

### Ingest-Time Dependencies (optional, for L0/L5)

| Component | Purpose | Notes |
|-----------|---------|-------|
| Qwen 7B (via Ollama) | L5 consolidation summarization | Runs on GPU box (192.168.1.182) or local |
| regex / spaCy | L0 entity extraction | Lightweight NER for profile building |

### What is NOT in the stack

- **No ChromaDB, Qdrant, Weaviate, or LanceDB.** sqlite-vec handles vector search in-process.
- **No Neo4j, KuzuDB, or any graph database.** Entity relationships are modeled with junction tables and foreign keys.
- **No OpenAI, Anthropic, or any cloud API** in the retrieval path. LLMs are used only at ingest time for L5 summarization, and even that is optional (can run on local Qwen 7B).
- **No Docker, Kubernetes, or microservices.** Single Python process, single database file.

---

## Design Decisions and Tradeoffs

### Decision 1: Preserve raw data, never replace it

**Choice:** All original message content is stored verbatim in the `messages` table. L0 profiles, L5 summaries, and fact timelines are additive structures built on top.

**Alternative rejected:** Mem0 and LangMem replace raw messages with LLM-extracted facts. This destroys information. Mem0 scored 9.2% on our benchmark because the specific details needed to answer queries (96.1% accuracy, $1.5M at $10M post-money) were never extracted.

**Tradeoff:** Higher storage cost (storing raw messages + derived structures). At personal scale (10K-100K messages), storage is irrelevant -- the entire database fits in a few hundred MB.

### Decision 2: No LLM in the query path

**Choice:** The search pipeline uses only FTS5, vector similarity, SQL filters, and pre-computed data. No LLM call happens at query time.

**Alternative rejected:** Several systems (SimpleMem, Letta) use LLMs to reason about queries at search time. This adds 500ms-60s of latency and costs money per query.

**Tradeoff:** Cannot answer questions that require reasoning beyond retrieval ("What mistakes has Jordan made?"). This is why `analytical` is the lowest-confidence category. A future version could add optional LLM post-processing on results, but the core retrieval pipeline stays LLM-free.

### Decision 3: SQLite over specialized databases

**Choice:** Single SQLite file with FTS5 and sqlite-vec extensions.

**Alternative rejected:** Zep/Graphiti achieves excellent results with Neo4j + PostgreSQL + vector DB. But it requires running three separate servers.

**Tradeoff:** No graph traversal capability. Multi-hop queries that would benefit from following entity relationship edges must instead rely on pre-computed summaries (L5). This limits multi-hop performance but eliminates operational complexity.

### Decision 4: Model2Vec over sentence-transformers

**Choice:** potion-base-8M (256-dim, 30MB, CPU-only, <1ms per embedding).

**Alternative rejected:** sentence-transformers all-MiniLM-L6-v2 (384-dim, ~100MB, ~10ms per embedding). Better embedding quality but 10x slower.

**Tradeoff:** Lower semantic similarity quality, especially for nuanced queries. Mitigated by RRF fusion with FTS5 -- the keyword search compensates for weaker embeddings. If benchmarks show the 256-dim embeddings are the bottleneck, upgrading is a single configuration change.

### Decision 5: Rule-based query analysis over LLM-based

**Choice:** Regex patterns and keyword matching for temporal intent, entity detection, negation.

**Alternative rejected:** Using an LLM to parse query intent. More accurate but adds latency and cost.

**Tradeoff:** Edge cases will be missed. "What happened around the time Jordan got the term sheet?" requires knowing that "term sheet" maps to August 10, 2025. This would require either a keyword-to-date lookup table (populated from L5 fact timeline) or LLM reasoning. The current design uses the lookup table approach.

### Decision 6: Ingest-time intelligence over query-time intelligence

**Choice:** L0 profiles and L5 summaries are computed when messages are ingested. Query time is fast and deterministic.

**Alternative rejected:** Compute profiles and summaries on-demand at query time (like SimpleMem's compression pipeline).

**Tradeoff:** Stale profiles if new messages arrive without re-processing. Mitigated by incremental updates -- new messages trigger delta profile/summary updates rather than full recomputation.

---

*Architecture version 0.1. Subject to revision based on benchmark results during implementation.*
