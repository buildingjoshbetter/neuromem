"""
Neuromem Episode Extraction
============================

Converts raw conversation turns into searchable LLM-generated summaries.
This bridges the vocabulary gap between conversational language and question
phrasing — the single biggest retrieval failure mode on LoCoMo.

EverMemOS's key advantage is searching over LLM-extracted "episodes" (third-person
narratives) and "event logs" (atomic facts) rather than raw messages. Questions
like "What did Jordan research?" match poorly against raw text "I've been looking
into adoption agencies" but match well against an episode summary "Jordan discussed
their research on adoption agencies."

Architecture:
    1. Group messages by session (or by time gap)
    2. For each group, call LLM to generate:
       a) Episode summary (third-person narrative, 2-4 sentences)
       b) Atomic facts (one-sentence facts with resolved dates)
    3. Store these as additional searchable documents alongside raw messages

Design decisions:
    - Use cheap/fast model (Haiku) for generation — quality is good enough
    - Generate both episodes AND facts — episodes for semantic matching,
      facts for precise keyword matching
    - Include resolved dates in both outputs (critical for temporal QA)
    - Tag outputs with modality='episode' or 'fact' for filtering
"""

from __future__ import annotations

import re
from typing import Callable


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

EPISODE_PROMPT = """You are summarizing a conversation session between {speaker_a} and {speaker_b}.
Session date: {session_date}

Convert the following dialogue into a concise third-person narrative (2-4 sentences).

IMPORTANT RULES:
- Write in third person ("Jordan mentioned..." not "I mentioned...")
- Preserve ALL specific details: names, places, numbers, dates, activities
- Resolve relative time expressions to absolute dates:
  * "yesterday" → the actual date based on session date
  * "last week" → the approximate date
  * "next month" → the approximate month
- Include both the relative expression AND the resolved date, e.g.:
  "Jordan mentioned going camping yesterday (approximately {example_date})"
- Capture who said/did/felt/planned what — attribute everything to the correct speaker
- If opinions or preferences are expressed, note whose they are
- Keep the narrative factual and information-dense

Dialogue:
{dialogue}

Third-person narrative summary:"""

FACTS_PROMPT = """Extract atomic facts from this conversation between {speaker_a} and {speaker_b}.
Session date: {session_date}

Each fact should be:
- ONE sentence, third person
- Self-contained (understandable without other facts)
- Include the specific person's name (not "they" or "the speaker")
- Include resolved dates when temporal expressions are used
- Cover: events, preferences, plans, relationships, emotions, opinions, locations

Dialogue:
{dialogue}

Output each fact on its own line, prefixed with "- ". Output 3-8 facts depending on conversation length.

Facts:"""


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------

def extract_episodes(
    messages: list[dict],
    llm_fn: Callable[[str], str],
    speaker_a: str = "Speaker A",
    speaker_b: str = "Speaker B",
    group_by: str = "session",
    max_turns_per_group: int = 50,
) -> list[dict]:
    """
    Extract episode summaries and atomic facts from grouped messages.

    Args:
        messages: List of message dicts with 'content', 'sender', 'timestamp',
                  'category' (session), '_session_num' fields.
        llm_fn: Callable that takes a prompt string and returns LLM response.
        speaker_a: Name of first speaker.
        speaker_b: Name of second speaker.
        group_by: How to group messages — 'session' uses _session_num/category.
        max_turns_per_group: Skip groups larger than this (too expensive).

    Returns:
        List of dicts, each with:
        - content: The episode summary or fact text
        - sender: 'system' (these are synthetic)
        - timestamp: Same as the session timestamp
        - category: Same session category
        - modality: 'episode' or 'fact'
        - _source_session: Session identifier
    """
    # Group messages by session
    groups = {}
    for msg in messages:
        key = msg.get("category", msg.get("_session_num", "unknown"))
        if key not in groups:
            groups[key] = []
        groups[key].append(msg)

    extracted = []

    for session_key, session_msgs in sorted(groups.items()):
        if len(session_msgs) > max_turns_per_group:
            # Split large sessions into chunks
            chunks = [session_msgs[i:i+max_turns_per_group]
                      for i in range(0, len(session_msgs), max_turns_per_group)]
        else:
            chunks = [session_msgs]

        for chunk in chunks:
            if len(chunk) < 2:
                continue  # Skip single-turn sessions

            # Build dialogue string
            dialogue_lines = []
            for msg in chunk:
                sender = msg.get("sender", "?")
                content = msg.get("content", "")
                dialogue_lines.append(f"{sender}: {content}")
            dialogue = "\n".join(dialogue_lines)

            # Get session date from first message
            session_date = chunk[0].get("timestamp", "unknown date")
            session_cat = chunk[0].get("category", "")

            # Compute example resolved date for the prompt
            example_date = _compute_example_date(session_date)

            # --- Generate episode summary ---
            episode_prompt = EPISODE_PROMPT.format(
                speaker_a=speaker_a,
                speaker_b=speaker_b,
                session_date=session_date,
                example_date=example_date,
                dialogue=dialogue,
            )

            try:
                episode_text = llm_fn(episode_prompt)
                if episode_text and len(episode_text.strip()) > 20:
                    extracted.append({
                        "content": episode_text.strip(),
                        "sender": "system",
                        "recipient": "",
                        "timestamp": session_date,
                        "category": session_cat,
                        "modality": "episode",
                        "_source_session": session_key,
                    })
            except Exception as e:
                pass  # Skip on error, graceful degradation

            # --- Extract atomic facts ---
            facts_prompt = FACTS_PROMPT.format(
                speaker_a=speaker_a,
                speaker_b=speaker_b,
                session_date=session_date,
                dialogue=dialogue,
            )

            try:
                facts_text = llm_fn(facts_prompt)
                if facts_text:
                    facts = _parse_facts(facts_text)
                    for fact in facts:
                        extracted.append({
                            "content": fact,
                            "sender": "system",
                            "recipient": "",
                            "timestamp": session_date,
                            "category": session_cat,
                            "modality": "fact",
                            "_source_session": session_key,
                        })
            except Exception as e:
                pass  # Skip on error

    return extracted


def extract_episodes_batch(
    messages: list[dict],
    llm_fn: Callable[[str], str],
    speaker_a: str = "Speaker A",
    speaker_b: str = "Speaker B",
    combined: bool = True,
) -> list[dict]:
    """
    Like extract_episodes but uses a single combined prompt per session to
    halve the number of LLM calls (episode + facts in one call).

    Args:
        messages: Message list.
        llm_fn: LLM callable.
        speaker_a: First speaker name.
        speaker_b: Second speaker name.
        combined: If True, use a single prompt for both episode and facts.

    Returns:
        List of episode and fact dicts.
    """
    if not combined:
        return extract_episodes(messages, llm_fn, speaker_a, speaker_b)

    # Group messages by session
    groups = {}
    for msg in messages:
        key = msg.get("category", msg.get("_session_num", "unknown"))
        if key not in groups:
            groups[key] = []
        groups[key].append(msg)

    extracted = []
    combined_prompt_template = """Summarize this conversation between {speaker_a} and {speaker_b}.
Session date: {session_date}

Dialogue:
{dialogue}

Provide TWO outputs:

EPISODE:
Write a third-person narrative summary (2-4 sentences). Preserve ALL specific details (names, places, numbers, dates). Resolve relative times to absolute dates using the session date. Attribute statements to the correct speaker.

FACTS:
Extract 3-8 atomic facts, one per line prefixed with "- ". Each fact should be one self-contained sentence in third person with the speaker's name (not "they").

Output format:
EPISODE:
[your narrative here]

FACTS:
- [fact 1]
- [fact 2]
..."""

    for session_key, session_msgs in sorted(groups.items()):
        if len(session_msgs) < 2:
            continue

        # Truncate very long sessions
        if len(session_msgs) > 50:
            session_msgs = session_msgs[:50]

        dialogue_lines = []
        for msg in session_msgs:
            sender = msg.get("sender", "?")
            content = msg.get("content", "")
            dialogue_lines.append(f"{sender}: {content}")
        dialogue = "\n".join(dialogue_lines)

        session_date = session_msgs[0].get("timestamp", "unknown date")
        session_cat = session_msgs[0].get("category", "")

        prompt = combined_prompt_template.format(
            speaker_a=speaker_a,
            speaker_b=speaker_b,
            session_date=session_date,
            dialogue=dialogue,
        )

        try:
            response = llm_fn(prompt)
            if not response:
                continue

            # Parse combined response
            episode_text, facts = _parse_combined_response(response)

            if episode_text and len(episode_text.strip()) > 20:
                extracted.append({
                    "content": episode_text.strip(),
                    "sender": "system",
                    "recipient": "",
                    "timestamp": session_date,
                    "category": session_cat,
                    "modality": "episode",
                    "_source_session": session_key,
                })

            for fact in facts:
                extracted.append({
                    "content": fact,
                    "sender": "system",
                    "recipient": "",
                    "timestamp": session_date,
                    "category": session_cat,
                    "modality": "fact",
                    "_source_session": session_key,
                })

        except Exception:
            pass  # Graceful degradation

    return extracted


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_facts(text: str) -> list[str]:
    """Parse fact lines from LLM output."""
    facts = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("- "):
            fact = line[2:].strip()
            if len(fact) > 10:  # Skip trivially short facts
                facts.append(fact)
        elif line.startswith("* "):
            fact = line[2:].strip()
            if len(fact) > 10:
                facts.append(fact)
    return facts


def _parse_combined_response(text: str) -> tuple[str, list[str]]:
    """Parse a combined EPISODE + FACTS response."""
    episode_text = ""
    facts = []

    # Split on FACTS: section
    parts = re.split(r'\n\s*FACTS\s*:\s*\n', text, maxsplit=1, flags=re.IGNORECASE)

    if len(parts) == 2:
        episode_part = parts[0]
        facts_part = parts[1]

        # Extract episode text (remove the EPISODE: header)
        episode_part = re.sub(r'^.*EPISODE\s*:\s*\n?', '', episode_part, flags=re.IGNORECASE)
        episode_text = episode_part.strip()

        # Parse facts
        facts = _parse_facts(facts_part)
    else:
        # Fallback: try to find EPISODE section
        ep_match = re.search(r'EPISODE\s*:\s*\n(.*?)(?=\nFACTS|\Z)', text,
                             flags=re.IGNORECASE | re.DOTALL)
        if ep_match:
            episode_text = ep_match.group(1).strip()

        # Try to find any bullet-point facts
        facts = _parse_facts(text)

    return episode_text, facts


def _compute_example_date(session_date: str) -> str:
    """Compute an example 'yesterday' date from a session date string."""
    from datetime import datetime, timedelta
    try:
        dt = datetime.strptime(session_date.strip(), "%I:%M %p on %d %B, %Y")
        yesterday = dt - timedelta(days=1)
        return yesterday.strftime("%B %d, %Y")
    except (ValueError, AttributeError):
        try:
            dt = datetime.strptime(session_date.strip(), "%I:%M %p on %d %B %Y")
            yesterday = dt - timedelta(days=1)
            return yesterday.strftime("%B %d, %Y")
        except (ValueError, AttributeError):
            return "the previous day"
