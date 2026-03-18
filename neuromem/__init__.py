"""
Neuromem - A 6-layer memory system for AI agents.

Core modules:
    storage        - SQLite + WAL database layer with schema and CRUD operations
    fts_search     - FTS5 full-text search with BM25 ranking and score normalization
    vector_search  - Model2Vec (potion-base-8M) semantic search via sqlite-vec
    hybrid         - Reciprocal Rank Fusion combining FTS5 + vector search
    temporal       - L2 temporal reasoning (date parsing, time-window filtering)
    salience       - L4 salience guard (noise filtering, entity disambiguation)
    personality    - L0 Personality Engram (entity profiles, preferences, communication style)
    consolidation  - L5 Consolidation (timelines, contradiction detection, summaries)
    predictive     - Predictive Coding Filter (surprise scoring, noise reduction)
    reranker       - Cross-encoder reranking (ms-marco-MiniLM-L6-v2)
    hyde           - HyDE hypothetical document embeddings for query enhancement
    clustering     - HDBSCAN scene clustering for episode-scoped retrieval
"""

from neuromem.storage import create_db, load_messages, load_messages_from_file
from neuromem.fts_search import search_fts, search_fts_by_sender, search_fts_in_range
from neuromem.vector_search import init_vec_table, build_vectors, search_vector, build_separation_vectors, search_vector_separation
from neuromem.hybrid import search_hybrid, reciprocal_rank_fusion
from neuromem.temporal import detect_temporal_intent, parse_date_reference, search_temporal, get_timeline, detect_episodes, get_episode_messages, expand_to_episodes, detect_landmark_events
from neuromem.salience import apply_salience_guard, compute_message_salience, detect_entities
from neuromem.personality import (
    build_entity_profiles, extract_preferences, search_personality,
    get_entity_profile, get_communication_pattern,
    resolve_entity, build_dunbar_hierarchy,
)
from neuromem.consolidation import (
    build_entity_timelines, detect_contradictions, build_summaries,
    search_contradictions, search_consolidated,
    build_entity_summary_sheets, build_structured_facts,
)
from neuromem.predictive import (
    compute_surprise_score, extract_facts, build_surprise_index,
    get_high_surprise_messages,
)
from neuromem.query_classifier import classify_query, get_search_mode, QUERY_TYPES, DEFAULT_WEIGHTS
from neuromem.reranker import rerank, rerank_with_fusion, get_reranker
from neuromem.hyde import (
    hyde_search, hyde_multi_search,
    generate_hypothetical_doc, generate_multi_hypothetical_docs,
)
from neuromem.clustering import cluster_messages, search_clustered, get_cluster_info
from neuromem.engine import NeuromemEngine

__all__ = [
    "create_db",
    "load_messages",
    "load_messages_from_file",
    "search_fts",
    "search_fts_by_sender",
    "search_fts_in_range",
    "init_vec_table",
    "build_vectors",
    "search_vector",
    "build_separation_vectors",
    "search_vector_separation",
    "search_hybrid",
    "reciprocal_rank_fusion",
    "detect_temporal_intent",
    "parse_date_reference",
    "search_temporal",
    "get_timeline",
    "detect_episodes",
    "get_episode_messages",
    "expand_to_episodes",
    "apply_salience_guard",
    "compute_message_salience",
    "detect_entities",
    # L0 Personality Engram
    "build_entity_profiles",
    "extract_preferences",
    "search_personality",
    "get_entity_profile",
    "get_communication_pattern",
    "resolve_entity",
    "build_dunbar_hierarchy",
    # L5 Consolidation
    "build_entity_timelines",
    "detect_contradictions",
    "build_summaries",
    "search_contradictions",
    "search_consolidated",
    "build_entity_summary_sheets",
    "build_structured_facts",
    # Temporal
    "detect_landmark_events",
    # Predictive Coding Filter
    "compute_surprise_score",
    "extract_facts",
    "build_surprise_index",
    "get_high_surprise_messages",
    # Query Classifier
    "classify_query",
    "get_search_mode",
    "QUERY_TYPES",
    "DEFAULT_WEIGHTS",
    # Reranker
    "rerank",
    "rerank_with_fusion",
    "get_reranker",
    # HyDE
    "hyde_search",
    "hyde_multi_search",
    "generate_hypothetical_doc",
    "generate_multi_hypothetical_docs",
    # Clustering
    "cluster_messages",
    "search_clustered",
    "get_cluster_info",
    # Engine
    "NeuromemEngine",
]
