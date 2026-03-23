# Implementation Verification Report
**Generated:** March 23, 2026 — from source code analysis

## Summary: What's Actually Implemented

### engine.py
- `search_agentic()` — FULLY IMPLEMENTED (multi-round retrieval, sufficiency checking, HyDE, clustering, entity-focused, reranking)
- Query classification — IMPLEMENTED (calls external `query_classifier` module, detects spotlight/diffuse modes)
- `_scent_trail()` — FULLY IMPLEMENTED (2-hop search, entity/term trails, 0.7x discount on follow-ups)
- Entity saturation penalty — IMPLEMENTED (in salience.py, penalizes 4th+ occurrence of same sender)
- Personality intent detection — IMPLEMENTED (strong personality signals + aspect keyword matching)

### consolidation.py
- `build_summaries()` — FULLY IMPLEMENTED (monthly summaries with proportional "ring width", per-entity summaries, EXTRACTIVE not abstractive)
- `detect_contradictions()` — FULLY IMPLEMENTED (pattern matching, pricing/location/status changes, fact_timeline with supersession)
- `search_contradictions()` — IMPLEMENTED (returns latest non-superseded fact first)
- `search_consolidated()` — IMPLEMENTED (searches summaries + fact_timeline, entity/time filtering)
- `build_entity_summary_sheets()` — IMPLEMENTED (builds searchable entity profiles)
- `build_structured_facts()` — IMPLEMENTED (team roster + location extraction)

### salience.py
- `compute_message_salience()` — FULLY IMPLEMENTED (base 0.3 + length/number/modality bonuses, noise/emoji penalties)
- Emotional arousal scoring — IMPLEMENTED (HIGH_AROUSAL words + life event markers)
- Entity saturation penalty — IMPLEMENTED (active when >5 unique senders)
- `_HIGH_SIGNAL_MODALITIES` — DEFINED (ocr, email, calendar, note, health_data, etc.)
- Document-type boosting — IMPLEMENTED via modality check

### temporal.py
- `detect_temporal_intent()` — FULLY IMPLEMENTED (trajectory, ranges, month parsing, after/before, relative dates)
- Episode detection — IMPLEMENTED (6-hour gap heuristic, stores in episodes table)
- Landmark events — IMPLEMENTED (`detect_landmark_events()` with regex, stores in landmark_events table)
- Timeline building — IMPLEMENTED (`get_timeline()` with entity/time filtering)
- Bi-temporal validity — PARTIAL (valid_from/valid_to fields exist in fact_timeline)

### predictive.py
- `build_surprise_index()` — IMPLEMENTED (novelty ratio: new_facts/total_facts * 0.6 + bonuses)
- Fact extraction — IMPLEMENTED (regex: numbers, dates, proper nouns, events, definitions)
- **NOT Bayesian surprise** — simple novelty ratio
- **NO EMA** — not implemented

### personality.py
- `build_dunbar_hierarchy()` — FULLY IMPLEMENTED (4 layers: intimate/close/friend/acquaintance)
- `build_entity_profiles()` — FULLY IMPLEMENTED (message count, topics, style, relationships, traits)
- `extract_preferences()` — IMPLEMENTED (food, activities, fears, routines, values, people)
- `search_personality()` — IMPLEMENTED (aspect detection, FTS + profile injection)
- Entity resolution — IMPLEMENTED (3-stage: direct → partial/fuzzy → context)
- **Behavioral delta vectors — NOT IMPLEMENTED**

### storage.py
- Tables: messages, messages_fts, entity_profiles, fact_timeline, summaries, episodes, landmark_events, causal_edges, entity_relationships
- **storage_tier column — NOT IMPLEMENTED**
- **retrieval_count / last_retrieved — NOT IMPLEMENTED**
- episode_id on messages — EXISTS
- entity_scope on fact_timeline — EXISTS
- valid_from/valid_to on fact_timeline — EXISTS

### fts_search.py
- search_fts() — FULLY IMPLEMENTED (BM25, score normalization, safe query fallback)
- search_fts_by_sender() — IMPLEMENTED
- search_fts_in_range() — IMPLEMENTED (temporal filtering)
- **Synonym expansion — NOT IMPLEMENTED**
- **Domain synonym dictionaries — NOT IMPLEMENTED**

## Additional modules found
- `query_classifier.py` — External query classification module
- `rich_extraction.py` — Rich extraction module
- `temporal_v2.py` — Temporal v2 module (exists!)

## Key Corrections for Document
1. Improvement #40 (OCR routing): Tables exist but no OCR-specific routing in engine.py
2. Improvement #41 (Synonym expansion): NOT in fts_search.py
3. Improvement #44 (Entity saturation): IS in salience.py
4. Improvement #17 (Episodes): IMPLEMENTED in temporal.py
5. Improvement #18 (Landmarks): IMPLEMENTED in temporal.py
6. Improvement #13 (Dunbar): IMPLEMENTED in personality.py
7. Improvement #23 (Entity-scoped facts): entity_scope EXISTS in schema
8. Improvement #6 (Record/Consolidate mode): No explicit mode separation
9. Improvement #43 (Structured facts): `build_structured_facts()` EXISTS in consolidation.py
10. Improvement #46 (Entity summaries): `build_entity_summary_sheets()` EXISTS in consolidation.py
