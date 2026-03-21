"""
Neuromem Temporal V2 - Zero-Cost Temporal Reasoning
====================================================

Enhanced temporal resolution using local compute only:
- spaCy for NLP-based temporal entity extraction
- dateutil for flexible date parsing
- Regex patterns for common relative expressions
- Optional Qwen 7B fallback for complex cases (GPU box)

Design doc: /Users/j/Desktop/neuromem/ZERO_COST_TEMPORAL_DESIGN.md
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timedelta
from typing import Callable

try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except (ImportError, OSError):
    HAS_SPACY = False
    print("Warning: spaCy not available. Run: pip install spacy && python -m spacy download en_core_web_sm")

try:
    from dateutil.parser import parse as dateutil_parse
    from dateutil.relativedelta import relativedelta
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False
    print("Warning: python-dateutil not available. Run: pip install python-dateutil")


# ───────────────────────────────────────────────────────────────────────────
# Temporal Pattern Dictionary
# ───────────────────────────────────────────────────────────────────────────

RELATIVE_PATTERNS = {
    # Year-based
    r'\blast\s+year\b': lambda sd: sd.replace(year=sd.year - 1, month=1, day=1),
    r'\bnext\s+year\b': lambda sd: sd.replace(year=sd.year + 1, month=1, day=1),
    r'\bthis\s+year\b': lambda sd: sd.replace(month=1, day=1),

    # Month-based
    r'\blast\s+month\b': lambda sd: sd - relativedelta(months=1) if HAS_DATEUTIL else sd - timedelta(days=30),
    r'\bnext\s+month\b': lambda sd: sd + relativedelta(months=1) if HAS_DATEUTIL else sd + timedelta(days=30),
    r'\bthis\s+month\b': lambda sd: sd.replace(day=1),

    # Week-based
    r'\blast\s+week\b': lambda sd: sd - timedelta(days=7),
    r'\bnext\s+week\b': lambda sd: sd + timedelta(days=7),
    r'\bthis\s+week\b': lambda sd: sd - timedelta(days=sd.weekday()),

    # Day-based
    r'\byesterday\b': lambda sd: sd - timedelta(days=1),
    r'\btomorrow\b': lambda sd: sd + timedelta(days=1),
    r'\btoday\b': lambda sd: sd,

    # Seasonal (Northern Hemisphere)
    r'\bin\s+the?\s*spring\b': lambda sd: datetime(sd.year, 3, 20),
    r'\bin\s+the?\s*summer\b': lambda sd: datetime(sd.year, 6, 21),
    r'\bin\s+the?\s*fall\b': lambda sd: datetime(sd.year, 9, 22),
    r'\bin\s+the?\s*autumn\b': lambda sd: datetime(sd.year, 9, 22),
    r'\bin\s+the?\s*winter\b': lambda sd: datetime(sd.year, 12, 21),

    # Time of day
    r'\bthis\s+morning\b': lambda sd: sd.replace(hour=8, minute=0, second=0),
    r'\bthis\s+afternoon\b': lambda sd: sd.replace(hour=14, minute=0, second=0),
    r'\bthis\s+evening\b': lambda sd: sd.replace(hour=18, minute=0, second=0),
    r'\btonight\b': lambda sd: sd.replace(hour=20, minute=0, second=0),
}


# ───────────────────────────────────────────────────────────────────────────
# Core Resolution Functions
# ───────────────────────────────────────────────────────────────────────────

def resolve_temporal_expressions(text: str, session_date: datetime) -> list[dict]:
    """
    Extract and resolve ALL temporal expressions in text using local NLP.

    Strategy:
        1. spaCy DATE entity extraction (if available)
        2. Regex pattern matching for relative dates
        3. Numeric duration expressions ("3 months ago", "in 2 weeks")
        4. Day-of-week references ("next Tuesday", "last Friday")

    Args:
        text: Message content to analyze
        session_date: The date this message was sent (for resolving relative dates)

    Returns:
        List of dicts with keys:
            - original: str (exact text matched)
            - resolved_date: datetime (absolute date)
            - confidence: float 0-1 (how certain we are)
            - type: str (absolute|relative|seasonal|duration|weekday)
            - granularity: str (year|month|week|day|hour)
            - span: tuple (start_char, end_char) for highlighting
    """
    results = []

    # Strategy 1: spaCy DATE entities
    if HAS_SPACY and nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "DATE":
                resolved = _resolve_spacy_entity(ent.text, session_date)
                if resolved:
                    results.append({
                        'original': ent.text,
                        'resolved_date': resolved['date'],
                        'confidence': resolved['confidence'],
                        'type': resolved['type'],
                        'granularity': resolved['granularity'],
                        'span': (ent.start_char, ent.end_char),
                    })

    # Strategy 2: Regex relative patterns
    for pattern, resolver_fn in RELATIVE_PATTERNS.items():
        for match in re.finditer(pattern, text, re.IGNORECASE):
            try:
                resolved = resolver_fn(session_date)
                results.append({
                    'original': match.group(0),
                    'resolved_date': resolved,
                    'confidence': 0.9,
                    'type': 'relative',
                    'granularity': _infer_granularity_from_pattern(pattern),
                    'span': (match.start(), match.end()),
                })
            except Exception:
                pass  # Skip invalid resolutions

    # Strategy 3: Numeric duration expressions
    duration_results = _extract_duration_expressions(text, session_date)
    results.extend(duration_results)

    # Strategy 4: Day-of-week references
    weekday_results = _extract_weekday_references(text, session_date)
    results.extend(weekday_results)

    # Deduplicate overlapping matches (keep highest confidence)
    results = _deduplicate_temporal_refs(results)

    return results


def _resolve_spacy_entity(text: str, session_date: datetime) -> dict | None:
    """Resolve a spaCy DATE entity to absolute datetime."""
    if not HAS_DATEUTIL:
        return None

    try:
        # dateutil handles most natural date formats
        parsed = dateutil_parse(text, default=session_date, fuzzy=True)
        granularity = _infer_granularity_from_text(text)

        return {
            'date': parsed,
            'confidence': 0.85,
            'type': 'absolute',
            'granularity': granularity,
        }
    except Exception:
        return None


def _extract_duration_expressions(text: str, session_date: datetime) -> list[dict]:
    """
    Extract numeric duration expressions like "3 months ago", "in 2 weeks".

    Patterns:
        - "N unit(s) ago"
        - "N unit(s) from now"
        - "in N unit(s)"
        - "N unit(s) later"
    """
    results = []

    pattern = r'(?:in|about|around)?\s*(\d+)\s+(year|month|week|day)s?\s+(?:ago|from\s+now|later|earlier)'

    for match in re.finditer(pattern, text, re.IGNORECASE):
        try:
            amount = int(match.group(1))
            unit = match.group(2).lower()
            matched_text = match.group(0).lower()

            # Determine direction
            is_future = any(kw in matched_text for kw in ['from now', 'later', 'in '])
            is_past = any(kw in matched_text for kw in ['ago', 'earlier'])

            if not is_future and not is_past:
                continue

            # Calculate delta
            if HAS_DATEUTIL:
                if unit == 'year':
                    delta = relativedelta(years=amount if is_future else -amount)
                elif unit == 'month':
                    delta = relativedelta(months=amount if is_future else -amount)
                    resolved = session_date + delta
                else:
                    if unit == 'week':
                        days = amount * 7
                    else:  # day
                        days = amount
                    resolved = session_date + timedelta(days=days if is_future else -days)
            else:
                # Fallback without dateutil (approximate months as 30 days)
                if unit == 'year':
                    days = amount * 365
                elif unit == 'month':
                    days = amount * 30
                elif unit == 'week':
                    days = amount * 7
                else:
                    days = amount
                resolved = session_date + timedelta(days=days if is_future else -days)

            if HAS_DATEUTIL and unit in ['year', 'month']:
                resolved = session_date + delta

            results.append({
                'original': match.group(0),
                'resolved_date': resolved,
                'confidence': 0.95,
                'type': 'duration',
                'granularity': unit,
                'span': (match.start(), match.end()),
            })

        except Exception:
            pass

    return results


def _extract_weekday_references(text: str, session_date: datetime) -> list[dict]:
    """
    Extract weekday references like "next Tuesday", "last Friday".
    """
    results = []

    weekdays = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
        'friday': 4, 'saturday': 5, 'sunday': 6,
    }

    pattern = r'(?:next|last)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)'

    for match in re.finditer(pattern, text, re.IGNORECASE):
        try:
            direction = match.group(0).split()[0].lower()
            weekday_name = match.group(1).lower()
            target_weekday = weekdays[weekday_name]
            current_weekday = session_date.weekday()

            # Calculate days ahead/behind
            if direction == 'next':
                days_ahead = (target_weekday - current_weekday) % 7
                if days_ahead == 0:
                    days_ahead = 7  # "next X" means at least next week
            else:  # last
                days_behind = (current_weekday - target_weekday) % 7
                if days_behind == 0:
                    days_behind = 7
                days_ahead = -days_behind

            resolved = session_date + timedelta(days=days_ahead)

            results.append({
                'original': match.group(0),
                'resolved_date': resolved,
                'confidence': 0.9,
                'type': 'weekday',
                'granularity': 'day',
                'span': (match.start(), match.end()),
            })

        except Exception:
            pass

    return results


def _deduplicate_temporal_refs(refs: list[dict]) -> list[dict]:
    """Remove overlapping temporal references, keeping highest confidence."""
    if not refs:
        return []

    # Sort by span start, then confidence descending
    refs.sort(key=lambda r: (r['span'][0], -r['confidence']))

    deduplicated = []
    last_end = -1

    for ref in refs:
        start, end = ref['span']
        # Only keep if it doesn't overlap with previous
        if start >= last_end:
            deduplicated.append(ref)
            last_end = end

    return deduplicated


# ───────────────────────────────────────────────────────────────────────────
# Temporal Feature Computation
# ───────────────────────────────────────────────────────────────────────────

def compute_temporal_features(message: dict, resolved_refs: list[dict]) -> dict:
    """
    Compute rich temporal metadata from resolved references.

    Args:
        message: Message dict with 'content', 'timestamp'
        resolved_refs: List of resolved temporal references

    Returns:
        Dict with temporal features (stored as JSON in DB):
            - has_temporal: bool
            - temporal_refs: list of simplified ref dicts
            - earliest_date: ISO string (earliest date mentioned)
            - latest_date: ISO string (latest date mentioned)
            - time_scope: "past"|"present"|"future"|"mixed"
            - is_planning: bool (contains future plans)
            - is_narrative: bool (recounting past events)
            - avg_confidence: float
    """
    if not resolved_refs:
        return {"has_temporal": False}

    session_date = datetime.fromisoformat(message['timestamp'])
    dates = [r['resolved_date'] for r in resolved_refs]

    # Date range
    earliest = min(dates)
    latest = max(dates)

    # Time scope classification
    past_count = sum(1 for d in dates if d < session_date)
    future_count = sum(1 for d in dates if d > session_date)

    if future_count > past_count:
        time_scope = "future"
    elif past_count > future_count:
        time_scope = "past"
    elif past_count == future_count and past_count > 0:
        time_scope = "mixed"
    else:
        time_scope = "present"

    # Content-based flags
    content_lower = message['content'].lower()
    planning_keywords = ['will', 'going to', 'plan to', 'scheduled', 'meeting', 'appointment', 'upcoming']
    narrative_keywords = ['was', 'were', 'used to', 'remember when', 'back when', 'at the time']

    is_planning = any(kw in content_lower for kw in planning_keywords)
    is_narrative = any(kw in content_lower for kw in narrative_keywords)

    # Average confidence
    avg_confidence = sum(r['confidence'] for r in resolved_refs) / len(resolved_refs)

    return {
        "has_temporal": True,
        "temporal_refs": [
            {
                "original": r['original'],
                "resolved": r['resolved_date'].isoformat(),
                "confidence": r['confidence'],
                "type": r['type'],
                "granularity": r['granularity'],
            }
            for r in resolved_refs
        ],
        "earliest_date": earliest.isoformat(),
        "latest_date": latest.isoformat(),
        "time_scope": time_scope,
        "is_planning": is_planning,
        "is_narrative": is_narrative,
        "avg_confidence": round(avg_confidence, 2),
    }


# ───────────────────────────────────────────────────────────────────────────
# Message Augmentation (Main Entry Point)
# ───────────────────────────────────────────────────────────────────────────

def augment_message_with_temporal(message: dict, use_llm_fallback: bool = False) -> dict:
    """
    Augment a message dict with resolved temporal features.

    This is the main entry point for temporal v2 processing. Call during
    ingestion to add 'temporal_metadata' to each message.

    Args:
        message: Dict with 'content', 'timestamp', etc.
        use_llm_fallback: If True, use Qwen 7B for low-confidence cases

    Returns:
        Same dict with 'temporal_metadata' field added (JSON string)
    """
    if 'timestamp' not in message or not message['timestamp']:
        message['temporal_metadata'] = json.dumps({"has_temporal": False})
        return message

    session_date = datetime.fromisoformat(message['timestamp'])
    resolved_refs = resolve_temporal_expressions(message['content'], session_date)

    # Optional: LLM fallback for low-confidence cases
    if use_llm_fallback and _needs_llm_fallback(resolved_refs):
        llm_refs = extract_temporal_with_llm(message['content'], message['timestamp'])
        resolved_refs.extend(llm_refs)
        resolved_refs = _deduplicate_temporal_refs(resolved_refs)

    # Compute features
    metadata = compute_temporal_features(message, resolved_refs)
    message['temporal_metadata'] = json.dumps(metadata)

    return message


def _needs_llm_fallback(refs: list[dict]) -> bool:
    """Check if LLM fallback is needed (low confidence or no matches)."""
    if not refs:
        return True  # No matches at all
    avg_conf = sum(r['confidence'] for r in refs) / len(refs)
    return avg_conf < 0.6


# ───────────────────────────────────────────────────────────────────────────
# LLM Fallback (Optional, requires GPU box)
# ───────────────────────────────────────────────────────────────────────────

def extract_temporal_with_llm(message: str, session_date: str, timeout: int = 5) -> list[dict]:
    """
    Use local Qwen 7B for complex temporal extraction.

    Args:
        message: Message content
        session_date: Session date as ISO string
        timeout: Request timeout in seconds

    Returns:
        List of resolved temporal references (same format as resolve_temporal_expressions)
        Empty list if GPU box unavailable or request fails.
    """
    try:
        import requests

        OLLAMA_URL = "http://192.168.1.182:11434/api/generate"

        prompt = f"""Extract all temporal references from this message and resolve them to absolute dates.

Session date: {session_date}
Message: "{message[:500]}"

For each temporal reference, output ONE line:
ORIGINAL | RESOLVED_DATE | CONFIDENCE

Example:
"last summer" | 2025-07-01 | 0.8
"three months ago" | 2025-03-01 | 0.95

Output (one per line):"""

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": "qwen2.5:7b-instruct",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=timeout,
        )

        if response.status_code != 200:
            return []

        result = response.json()
        response_text = result.get("response", "")

        return _parse_llm_temporal_output(response_text)

    except Exception:
        return []  # Graceful degradation


def _parse_llm_temporal_output(text: str) -> list[dict]:
    """Parse LLM-generated temporal extraction."""
    results = []

    for line in text.strip().split('\n'):
        if '|' not in line:
            continue

        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3:
            continue

        original = parts[0].strip('"\'')
        resolved_str = parts[1]

        try:
            confidence = float(parts[2])
        except ValueError:
            confidence = 0.7

        # Parse resolved date
        try:
            resolved_dt = datetime.fromisoformat(resolved_str)
            results.append({
                'original': original,
                'resolved_date': resolved_dt,
                'confidence': confidence,
                'type': 'llm_extracted',
                'granularity': 'day',
                'span': (0, len(original)),  # Unknown span
            })
        except ValueError:
            pass  # Skip invalid dates

    return results


# ───────────────────────────────────────────────────────────────────────────
# SQLite Temporal Functions
# ───────────────────────────────────────────────────────────────────────────

def register_temporal_functions(conn: sqlite3.Connection):
    """
    Register custom temporal SQL functions for zero-cost query-time operations.

    Functions:
        - days_between(date1, date2) -> int
        - months_between(date1, date2) -> int
        - is_within_days(date, center, window) -> bool
        - extract_year(date) -> int
        - extract_month(date) -> int
        - extract_quarter(date) -> int
        - is_future(msg_date, ref_date) -> bool
        - is_past(msg_date, ref_date) -> bool
    """

    def safe_parse(date_str: str) -> datetime | None:
        """Safely parse ISO date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            return None

    conn.create_function("days_between", 2, lambda d1, d2: (
        (safe_parse(d2) - safe_parse(d1)).days if safe_parse(d1) and safe_parse(d2) else None
    ))

    conn.create_function("months_between", 2, lambda d1, d2: (
        (safe_parse(d2).year - safe_parse(d1).year) * 12 +
        (safe_parse(d2).month - safe_parse(d1).month)
        if safe_parse(d1) and safe_parse(d2) else None
    ))

    conn.create_function("is_within_days", 3, lambda date, center, window: (
        abs((safe_parse(date) - safe_parse(center)).days) <= window
        if safe_parse(date) and safe_parse(center) else False
    ))

    conn.create_function("extract_year", 1, lambda date: (
        safe_parse(date).year if safe_parse(date) else None
    ))

    conn.create_function("extract_month", 1, lambda date: (
        safe_parse(date).month if safe_parse(date) else None
    ))

    conn.create_function("extract_quarter", 1, lambda date: (
        (safe_parse(date).month - 1) // 3 + 1 if safe_parse(date) else None
    ))

    conn.create_function("is_future", 2, lambda msg_date, ref_date: (
        safe_parse(msg_date) > safe_parse(ref_date)
        if safe_parse(msg_date) and safe_parse(ref_date) else False
    ))

    conn.create_function("is_past", 2, lambda msg_date, ref_date: (
        safe_parse(msg_date) < safe_parse(ref_date)
        if safe_parse(msg_date) and safe_parse(ref_date) else False
    ))


# ───────────────────────────────────────────────────────────────────────────
# Helper Functions
# ───────────────────────────────────────────────────────────────────────────

def _infer_granularity_from_pattern(pattern: str) -> str:
    """Infer temporal granularity from regex pattern."""
    if 'year' in pattern:
        return 'year'
    elif 'month' in pattern:
        return 'month'
    elif 'week' in pattern:
        return 'week'
    elif 'morning' in pattern or 'afternoon' in pattern or 'evening' in pattern:
        return 'hour'
    else:
        return 'day'


def _infer_granularity_from_text(text: str) -> str:
    """Infer temporal granularity from text format."""
    if re.search(r'\d{1,2}:\d{2}', text):  # Has time component
        return 'hour'
    elif re.search(r'\d{1,2}', text):  # Has day number
        return 'day'
    elif any(m in text.lower() for m in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
        if re.search(r'\d{1,2}', text):
            return 'day'
        return 'month'
    elif re.search(r'\d{4}', text):  # Has year
        return 'year'
    return 'day'
