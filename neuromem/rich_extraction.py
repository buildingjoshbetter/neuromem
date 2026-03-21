"""
Rich Multi-Pass Extraction Pipeline
=====================================
Inspired by EverMemOS's 17-prompt extraction but designed for Neuromem's
architecture. Since accuracy > cost, we use multiple LLM passes to create
extremely rich searchable content.

Extraction Passes:
    1. Episode narratives (existing) — third-person summaries
    2. Atomic facts with entity attribution (existing, enhanced)
    3. Entity profile updates — per-person facts and preferences
    4. Temporal anchoring — normalize ALL dates to absolute ISO format
    5. Relationship extraction — who knows who, how they relate
    6. Topic/theme extraction — what subjects are discussed
    7. Question-answer pairs — predict what someone might ask about this

Each pass generates additional searchable documents that are indexed
alongside raw messages for retrieval.
"""

from __future__ import annotations

import re
import json
from typing import Callable
from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────────────────
# Pass 1+2: Enhanced Episode + Facts (replaces basic extraction)
# ─────────────────────────────────────────────────────────────────────────

ENHANCED_EPISODE_PROMPT = """You are a precise information extraction system analyzing a conversation between {speaker_a} and {speaker_b}.
Session date: {session_date}

Dialogue:
{dialogue}

Provide THREE outputs:

EPISODE:
Write a detailed third-person narrative summary (4-6 sentences). Include EVERY specific detail:
- All names of people, places, organizations mentioned
- All numbers (amounts, ages, distances, times)
- All dates (resolve "yesterday" to actual date using session date {session_date})
- All activities, events, plans discussed
- Emotional states and opinions (attributed to specific speakers)
- Any changes in status (new job, moved, relationship change, etc.)

FACTS:
Extract 8-15 atomic facts. Each fact must be:
- ONE sentence, third person, with the speaker's name
- Self-contained and specific
- Include resolved dates where applicable
- Cover: events, preferences, plans, relationships, emotions, locations, numbers
Prefix each with "- "

ENTITIES:
List every person, place, and organization mentioned, one per line:
- [Person] Name - key detail about them from this conversation
- [Place] Name - why it was mentioned
- [Organization] Name - context
Prefix each with "- "

Output:"""


# ─────────────────────────────────────────────────────────────────────────
# Pass 3: Predicted Questions (QA pairs)
# ─────────────────────────────────────────────────────────────────────────

QA_PREDICTION_PROMPT = """Given this conversation excerpt, predict 5-8 questions someone might ask about it later.
For each question, provide the answer based on the conversation.

Conversation between {speaker_a} and {speaker_b} on {session_date}:
{dialogue}

Generate questions that test:
1. Basic facts (who, what, where, when)
2. Temporal details (dates, durations, sequences)
3. Relationships between people
4. Plans and future actions
5. Opinions and preferences

Format each as:
Q: [question]
A: [concise answer]

Questions and answers:"""


# ─────────────────────────────────────────────────────────────────────────
# Pass 4: Temporal Normalization
# ─────────────────────────────────────────────────────────────────────────

TEMPORAL_PROMPT = """Extract ALL time references from this conversation and resolve them to absolute dates.

Session date: {session_date}

Dialogue:
{dialogue}

For each temporal reference, output:
- Original phrase: "[exact text from conversation]"
- Resolved date: [ISO format YYYY-MM-DD or YYYY-MM or YYYY]
- Context: [one sentence explaining what happened at this time]

Format each on its own line as: ORIGINAL | RESOLVED | CONTEXT

Temporal references:"""


# ─────────────────────────────────────────────────────────────────────────
# Pass 5: Relationship Extraction
# ─────────────────────────────────────────────────────────────────────────

RELATIONSHIP_PROMPT = """Analyze the relationships discussed in this conversation.

Conversation between {speaker_a} and {speaker_b} on {session_date}:
{dialogue}

For every relationship mentioned (including between the speakers), output:
- Person A: [name]
- Person B: [name or role like "their mom"]
- Relationship: [friend, family, colleague, partner, etc.]
- Key detail: [one sentence about this relationship from the conversation]

Format each relationship on its own line as: PERSON_A | PERSON_B | RELATIONSHIP | DETAIL

Relationships:"""


# ─────────────────────────────────────────────────────────────────────────
# Main extraction function
# ─────────────────────────────────────────────────────────────────────────

def rich_extract(
    messages: list[dict],
    llm_fn: Callable[[str], str],
    speaker_a: str = "Speaker A",
    speaker_b: str = "Speaker B",
    passes: list[str] | None = None,
) -> list[dict]:
    """
    Run multi-pass extraction on grouped conversation messages.

    Args:
        messages: List of message dicts.
        llm_fn: LLM callable (prompt -> response).
        speaker_a: First speaker name.
        speaker_b: Second speaker name.
        passes: Which passes to run. Default: all.
                Options: 'episode', 'qa', 'temporal', 'relationship'

    Returns:
        List of extracted document dicts ready for insertion into messages table.
    """
    if passes is None:
        passes = ['episode', 'qa', 'temporal', 'relationship']

    # Group messages by session
    groups = {}
    for msg in messages:
        key = msg.get("category", msg.get("_session_num", "unknown"))
        if key not in groups:
            groups[key] = []
        groups[key].append(msg)

    extracted = []

    for session_key, session_msgs in sorted(groups.items()):
        if len(session_msgs) < 2:
            continue

        # Truncate very long sessions
        if len(session_msgs) > 60:
            session_msgs = session_msgs[:60]

        # Build dialogue string
        dialogue = _build_dialogue(session_msgs)
        session_date = session_msgs[0].get("timestamp", "unknown date")
        session_cat = session_msgs[0].get("category", "")

        # ── Pass 1+2: Enhanced episode + facts + entities ──
        if 'episode' in passes:
            try:
                prompt = ENHANCED_EPISODE_PROMPT.format(
                    speaker_a=speaker_a, speaker_b=speaker_b,
                    session_date=session_date, dialogue=dialogue,
                )
                response = llm_fn(prompt)
                if response:
                    docs = _parse_enhanced_episode(response, session_date, session_cat, session_key)
                    extracted.extend(docs)
            except Exception:
                pass

        # ── Pass 3: Predicted QA pairs ──
        if 'qa' in passes:
            try:
                prompt = QA_PREDICTION_PROMPT.format(
                    speaker_a=speaker_a, speaker_b=speaker_b,
                    session_date=session_date, dialogue=dialogue,
                )
                response = llm_fn(prompt)
                if response:
                    docs = _parse_qa_pairs(response, session_date, session_cat, session_key)
                    extracted.extend(docs)
            except Exception:
                pass

        # ── Pass 4: Temporal normalization ──
        if 'temporal' in passes:
            try:
                prompt = TEMPORAL_PROMPT.format(
                    session_date=session_date, dialogue=dialogue,
                )
                response = llm_fn(prompt)
                if response:
                    docs = _parse_temporal(response, session_date, session_cat, session_key)
                    extracted.extend(docs)
            except Exception:
                pass

        # ── Pass 5: Relationship extraction ──
        if 'relationship' in passes:
            try:
                prompt = RELATIONSHIP_PROMPT.format(
                    speaker_a=speaker_a, speaker_b=speaker_b,
                    session_date=session_date, dialogue=dialogue,
                )
                response = llm_fn(prompt)
                if response:
                    docs = _parse_relationships(response, session_date, session_cat, session_key)
                    extracted.extend(docs)
            except Exception:
                pass

    return extracted


# ─────────────────────────────────────────────────────────────────────────
# Parsers
# ─────────────────────────────────────────────────────────────────────────

def _build_dialogue(messages: list[dict]) -> str:
    """Build formatted dialogue string."""
    lines = []
    for msg in messages:
        sender = msg.get("sender", "?")
        content = msg.get("content", "")
        ts = msg.get("timestamp", "")
        if ts:
            lines.append(f"[{ts}] {sender}: {content}")
        else:
            lines.append(f"{sender}: {content}")
    return "\n".join(lines)


def _parse_enhanced_episode(text: str, session_date: str, category: str, session_key: str) -> list[dict]:
    """Parse enhanced episode + facts + entities from LLM response."""
    docs = []

    # Split into sections
    episode_text = ""
    facts = []
    entities = []

    # Try to split on section headers
    sections = re.split(r'\n\s*(?:FACTS|ENTITIES)\s*:\s*\n', text, flags=re.IGNORECASE)

    if len(sections) >= 1:
        # First section is episode
        ep_text = sections[0]
        ep_text = re.sub(r'^.*?EPISODE\s*:\s*\n?', '', ep_text, flags=re.IGNORECASE).strip()
        if len(ep_text) > 20:
            episode_text = ep_text

    if len(sections) >= 2:
        # Second section is facts
        facts = _parse_bullet_list(sections[1])

    if len(sections) >= 3:
        # Third section is entities
        entities = _parse_bullet_list(sections[2])

    # Add episode
    if episode_text:
        docs.append({
            "content": episode_text,
            "sender": "system",
            "recipient": "",
            "timestamp": session_date,
            "category": category,
            "modality": "episode",
            "_source_session": session_key,
        })

    # Add facts
    for fact in facts:
        docs.append({
            "content": fact,
            "sender": "system",
            "recipient": "",
            "timestamp": session_date,
            "category": category,
            "modality": "fact",
            "_source_session": session_key,
        })

    # Add entities as searchable documents
    for entity in entities:
        docs.append({
            "content": entity,
            "sender": "system",
            "recipient": "",
            "timestamp": session_date,
            "category": category,
            "modality": "entity",
            "_source_session": session_key,
        })

    return docs


def _parse_qa_pairs(text: str, session_date: str, category: str, session_key: str) -> list[dict]:
    """Parse Q&A pairs into searchable documents."""
    docs = []

    # Split into Q/A pairs
    pairs = re.findall(
        r'Q:\s*(.+?)\nA:\s*(.+?)(?=\nQ:|\Z)',
        text, flags=re.DOTALL
    )

    for question, answer in pairs:
        q = question.strip()
        a = answer.strip()
        if len(q) > 10 and len(a) > 5:
            # Store as searchable document: "Q: ... A: ..."
            # This creates synthetic content that matches question-phrasing
            docs.append({
                "content": f"Question: {q}\nAnswer: {a}",
                "sender": "system",
                "recipient": "",
                "timestamp": session_date,
                "category": category,
                "modality": "qa_pair",
                "_source_session": session_key,
            })

    return docs


def _parse_temporal(text: str, session_date: str, category: str, session_key: str) -> list[dict]:
    """Parse temporal references into searchable documents."""
    docs = []

    for line in text.strip().split("\n"):
        line = line.strip()
        if "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) >= 3:
            original = parts[0].strip().strip('"').strip("'")
            resolved = parts[1].strip()
            context = parts[2].strip()

            if len(context) > 10:
                # Create a temporal fact document
                doc_content = f"On {resolved}: {context}"
                if original and original.lower() != resolved.lower():
                    doc_content += f" (originally referenced as \"{original}\")"

                docs.append({
                    "content": doc_content,
                    "sender": "system",
                    "recipient": "",
                    "timestamp": resolved if _looks_like_date(resolved) else session_date,
                    "category": category,
                    "modality": "temporal_fact",
                    "_source_session": session_key,
                })

    return docs


def _parse_relationships(text: str, session_date: str, category: str, session_key: str) -> list[dict]:
    """Parse relationship info into searchable documents."""
    docs = []

    for line in text.strip().split("\n"):
        line = line.strip()
        if "|" not in line:
            continue

        parts = line.split("|")
        if len(parts) >= 4:
            person_a = parts[0].strip()
            person_b = parts[1].strip()
            rel_type = parts[2].strip()
            detail = parts[3].strip()

            if len(detail) > 10:
                doc_content = f"{person_a} and {person_b} ({rel_type}): {detail}"
                docs.append({
                    "content": doc_content,
                    "sender": "system",
                    "recipient": "",
                    "timestamp": session_date,
                    "category": category,
                    "modality": "relationship",
                    "_source_session": session_key,
                })

    return docs


def _parse_bullet_list(text: str) -> list[str]:
    """Parse bullet-point list from text."""
    items = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            item = line[2:].strip()
            if len(item) > 10:
                items.append(item)
    return items


def _looks_like_date(s: str) -> bool:
    """Check if string looks like a date."""
    return bool(re.match(r'\d{4}[-/]\d{1,2}(?:[-/]\d{1,2})?', s.strip()))
