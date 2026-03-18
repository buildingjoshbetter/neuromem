"""
Neuromem Query Classifier
=========================
Rule-based query type detection with adaptive weight profiles.
Different query types benefit from different retrieval strategies.
"""

import re

# Query type definitions with detection patterns and weight profiles
QUERY_TYPES = {
    "factual": {
        "patterns": [
            r"\bwhat\s+(?:is|was|are|were)\b",
            r"\bhow\s+(?:much|many|long|often)\b",
            r"\bwhen\s+did\b",
            r"\bwhere\s+(?:is|was|did|does)\b",
            r"\bwho\s+(?:is|was|did)\b",
        ],
        "weights": {"fts": 1.2, "vec": 0.8, "temporal": 1.0, "personality": 0.3, "consolidation": 1.5},
    },
    "temporal": {
        "patterns": [
            r"\bwhen\b",
            r"\bbefore\b.*\bafter\b|\bafter\b.*\bbefore\b",
            r"\bin\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)",
            r"\b(?:early|mid|late)\s+20\d{2}\b",
            r"\bover\s+time\b",
            r"\btrajectory\b",
            r"\btimeline\b",
            r"\bhistory\b",
        ],
        "weights": {"fts": 0.8, "vec": 0.6, "temporal": 2.0, "personality": 0.2, "consolidation": 1.0},
    },
    "entity": {
        "patterns": [
            r"\bwho\s+is\b",
            r"\btell\s+me\s+about\b",
            r"\bwhat\s+(?:does|did)\s+\w+\s+(?:do|say|think|feel)\b",
            r"\brelationship\s+(?:with|between)\b",
        ],
        "weights": {"fts": 1.5, "vec": 0.7, "temporal": 0.5, "personality": 1.5, "consolidation": 1.0},
    },
    "personality": {
        "patterns": [
            r"\bkind\s+of\s+person\b",
            r"\bpersonality\b",
            r"\bcharacter\b",
            r"\btraits?\b",
            r"\bfears?\b",
            r"\bhobbies?\b",
            r"\broutine\b",
            r"\bprefer(?:ence|s)?\b",
            r"\bfavorite\b",
            r"\blike\s+to\s+(?:eat|do|watch|read)\b",
            r"\bcommunication\s+style\b",
        ],
        "weights": {"fts": 0.5, "vec": 0.5, "temporal": 0.3, "personality": 2.0, "consolidation": 0.5},
    },
    "analytical": {
        "patterns": [
            r"\bsummarize\b",
            r"\boverview\b",
            r"\bjourney\b",
            r"\bevolve[ds]?\b",
            r"\bkey\s+(?:events?|moments?|turning\s+points?)\b",
            r"\bhow\s+did\b.*\b(?:change|evolve|grow|progress)\b",
        ],
        "weights": {"fts": 0.7, "vec": 1.0, "temporal": 1.5, "personality": 0.5, "consolidation": 2.0},
    },
    "aggregation": {
        "patterns": [
            r"\ball\b.*\b(?:team|members?|people|entities)\b",
            r"\bfull\s+(?:team|roster|list)\b",
            r"\beveryone\b",
            r"\bhow\s+many\b",
            r"\blist\s+(?:all|every)\b",
        ],
        "weights": {"fts": 1.0, "vec": 0.5, "temporal": 0.3, "personality": 0.5, "consolidation": 2.0},
    },
}

# Default weights when no type matches
DEFAULT_WEIGHTS = {"fts": 1.0, "vec": 1.0, "temporal": 1.0, "personality": 1.0, "consolidation": 1.0}


def classify_query(query: str) -> dict:
    """
    Classify a query and return its type with adaptive weight profile.

    Returns:
        Dict with 'query_type' (str), 'confidence' (float 0-1),
        'weights' (dict of retrieval weights), 'detected_patterns' (list).
    """
    lower = query.lower()
    best_type = "general"
    best_score = 0
    best_patterns = []

    for qtype, config in QUERY_TYPES.items():
        matches = []
        for pattern in config["patterns"]:
            if re.search(pattern, lower):
                matches.append(pattern)

        score = len(matches)
        if score > best_score:
            best_score = score
            best_type = qtype
            best_patterns = matches

    if best_score == 0:
        return {
            "query_type": "general",
            "confidence": 0.5,
            "weights": dict(DEFAULT_WEIGHTS),
            "detected_patterns": [],
        }

    confidence = min(1.0, best_score * 0.4 + 0.3)
    weights = dict(QUERY_TYPES[best_type]["weights"])

    return {
        "query_type": best_type,
        "confidence": confidence,
        "weights": weights,
        "detected_patterns": best_patterns,
    }


def get_search_mode(query: str) -> str:
    """
    Determine if query needs 'spotlight' (focused) or 'diffuse' (broad) search.

    Spotlight: aggressive entity boosting, tight filters (specific queries).
    Diffuse: broad retrieval, lower salience threshold (general/exploratory queries).
    """
    lower = query.lower()

    # Diffuse patterns: broad, exploratory queries
    diffuse_patterns = [
        r"\bwhat\s+topics?\b",
        r"\bwhat\s+(?:does|did)\s+\w+\s+talk\s+about\b",
        r"\bhow\s+does\s+\w+\s+feel\b",
        r"\bsummarize\b",
        r"\boverview\b",
        r"\ball\b",
        r"\beverything\b",
        r"\bgeneral(?:ly)?\b",
        r"\btypical(?:ly)?\b",
    ]

    for pattern in diffuse_patterns:
        if re.search(pattern, lower):
            return "diffuse"

    return "spotlight"
