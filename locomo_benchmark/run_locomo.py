#!/usr/bin/env python3
"""
LoCoMo Benchmark Runner for Neuromem v2
========================================

Runs the standard LoCoMo benchmark (10 conversations, ~1540 scored QA pairs)
against Neuromem and computes both retrieval metrics (no LLM needed) and
J-score (LLM-as-judge, needs API key).

Search modes:
    standard  — Original 6-layer pipeline (FTS5+vector+temporal+salience)
    agentic   — Multi-round retrieval with HyDE + reranking + sufficiency check

Usage:
    # Retrieval-only with standard search:
    python run_locomo.py --retrieval-only

    # Retrieval-only with agentic search:
    python run_locomo.py --retrieval-only --search-mode agentic

    # Full benchmark with agentic search + Opus 4.6:
    python run_locomo.py --search-mode agentic --llm-backend anthropic --model claude-opus-4-6

    # Quick smoke test (1 conversation):
    python run_locomo.py --retrieval-only --conv-ids 0

Published J-Scores for comparison:
    EverMemOS:    92.3%
    MemMachine:   84.9%
    Zep/Graphiti: 75.1%
    Letta:        74.0%
    Full-Context: 72.9%
    Mem0:         66.9%
    LangMem:      58.1%
"""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path

# Add neuromem to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from neuromem.engine import NeuromemEngine
from neuromem.storage import load_messages
from neuromem.episodes import extract_episodes_batch

LOCOMO_DATA = PROJECT_ROOT / "locomo_data" / "data" / "locomo10.json"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# LLM helpers — used for HyDE generation and query refinement
# ---------------------------------------------------------------------------

def make_llm_fn(backend: str, model: str, max_tokens: int = 300):
    """
    Create a simple LLM callable for HyDE / query refinement / episode extraction.

    Args:
        backend: "anthropic", "openai", or "ollama".
        model: Model name string.
        max_tokens: Maximum tokens for response (300 for HyDE, 800+ for episodes).

    Returns a function: ``fn(prompt: str) -> str``
    """
    if backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic()

        def _call(prompt: str) -> str:
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text

        return _call

    elif backend == "openai":
        import openai
        client = openai.OpenAI()

        def _call(prompt: str) -> str:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content

        return _call

    elif backend == "ollama":
        import requests

        def _call(prompt: str) -> str:
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            return resp.json()["response"]

        return _call

    else:
        return None


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_locomo():
    """Load LoCoMo dataset."""
    with open(LOCOMO_DATA) as f:
        return json.load(f)


def _parse_locomo_datetime(dt_str: str):
    """Parse LoCoMo datetime format like '1:56 pm on 8 May, 2023' to datetime."""
    from datetime import datetime
    dt_str = dt_str.strip()
    try:
        return datetime.strptime(dt_str, "%I:%M %p on %d %B, %Y")
    except ValueError:
        try:
            return datetime.strptime(dt_str, "%I:%M %p on %d %B %Y")
        except ValueError:
            return None


def _resolve_relative_times(text: str, session_dt_str: str) -> str:
    """
    Resolve relative time expressions in message text using the session datetime.

    Converts phrases like 'yesterday', 'last week', 'last Saturday' by appending
    the approximate absolute date.  This is critical for temporal question answering
    where the LLM needs to resolve 'yesterday' to an actual date.

    Example:
        Input:  "I went camping yesterday" (session: "1:56 pm on 8 May, 2023")
        Output: "I went camping yesterday (approximately May 7, 2023)"
    """
    import re
    from datetime import timedelta

    session_dt = _parse_locomo_datetime(session_dt_str)
    if not session_dt:
        return text

    # Mapping of relative expressions to approximate timedelta offsets
    RELATIVE_PATTERNS = [
        (r'\byesterday\b', timedelta(days=1), "yesterday"),
        (r'\blast night\b', timedelta(days=1), "last night"),
        (r'\blast week\b', timedelta(weeks=1), "last week"),
        (r'\btwo weeks ago\b', timedelta(weeks=2), "two weeks ago"),
        (r'\bthree weeks ago\b', timedelta(weeks=3), "three weeks ago"),
        (r'\blast month\b', timedelta(days=30), "last month"),
        (r'\btwo months ago\b', timedelta(days=60), "two months ago"),
        (r'\bthree months ago\b', timedelta(days=90), "three months ago"),
        (r'\blast year\b', timedelta(days=365), "last year"),
        (r'\btwo years ago\b', timedelta(days=730), "two years ago"),
        (r'\bthree years ago\b', timedelta(days=1095), "three years ago"),
        (r'\bfour years ago\b', timedelta(days=1460), "four years ago"),
        (r'\bfive years ago\b', timedelta(days=1825), "five years ago"),
        (r'\bten years ago\b', timedelta(days=3650), "ten years ago"),
        (r'\ba few years ago\b', timedelta(days=1095), "a few years ago"),
        (r'\ba year ago\b', timedelta(days=365), "a year ago"),
        (r'\ba month ago\b', timedelta(days=30), "a month ago"),
        (r'\ba week ago\b', timedelta(weeks=1), "a week ago"),
        (r'\blast weekend\b', timedelta(days=5), "last weekend"),
        (r'\blast Saturday\b', timedelta(days=7), "last Saturday"),
        (r'\blast Sunday\b', timedelta(days=7), "last Sunday"),
        (r'\blast Friday\b', timedelta(days=7), "last Friday"),
        (r'\bnext week\b', timedelta(weeks=-1), "next week"),
        (r'\bnext month\b', timedelta(days=-30), "next month"),
        (r'\bthis weekend\b', timedelta(days=0), "this weekend"),
        (r'\bthis morning\b', timedelta(days=0), "this morning"),
        (r'\bthe other day\b', timedelta(days=3), "the other day"),
        (r'\brecently\b', timedelta(days=7), "recently"),
    ]

    resolved = text
    for pattern, delta, label in RELATIVE_PATTERNS:
        match = re.search(pattern, resolved, re.IGNORECASE)
        if match:
            # Compute approximate absolute date
            if delta.days >= 0:
                approx_date = session_dt - delta
            else:
                approx_date = session_dt - delta  # negative delta = future
            date_str = approx_date.strftime("%B %d, %Y")

            # Append resolution in parentheses after the first match
            original_text = match.group(0)
            replacement = f"{original_text} (approximately {date_str})"
            resolved = resolved[:match.start()] + replacement + resolved[match.end():]

    return resolved


def parse_conversations(conv_data: dict, resolve_times: bool = True) -> list[dict]:
    """
    Convert a LoCoMo conversation into flat messages for Neuromem.

    Each turn becomes a message with:
    - content: the text (with resolved temporal expressions if resolve_times=True)
    - sender: speaker name
    - timestamp: session datetime
    - category: session number

    Args:
        conv_data: LoCoMo conversation data dict.
        resolve_times: If True, resolve relative time expressions ('yesterday',
                      'last week') to approximate absolute dates using session
                      timestamps.  This is critical for temporal question answering.
    """
    messages = []
    conversation = conv_data["conversation"]
    speaker_a = conversation["speaker_a"]
    speaker_b = conversation["speaker_b"]

    # Find all sessions
    session_keys = sorted(
        [k for k in conversation if k.startswith("session_") and not k.endswith("_date_time")],
        key=lambda k: int(k.split("_")[1]),
    )

    for session_key in session_keys:
        session_num = session_key.split("_")[1]
        datetime_key = f"{session_key}_date_time"
        session_dt = conversation.get(datetime_key, "")
        turns = conversation[session_key]

        for i, turn in enumerate(turns):
            speaker = turn["speaker"]
            recipient = speaker_b if speaker == speaker_a else speaker_a
            dia_id = turn.get("dia_id", f"D{session_num}:{i+1}")

            content = turn["text"]
            if resolve_times and session_dt:
                content = _resolve_relative_times(content, session_dt)

            messages.append({
                "content": content,
                "sender": speaker,
                "recipient": recipient,
                "timestamp": session_dt,
                "category": f"session_{session_num}",
                "modality": "conversation",
                "_dia_id": dia_id,  # Keep for evidence matching
                "_session_num": int(session_num),
            })

    return messages


# ---------------------------------------------------------------------------
# Retrieval metrics
# ---------------------------------------------------------------------------

def compute_retrieval_metrics(
    engine,
    qa_pairs: list[dict],
    messages: list[dict],
    top_k: int = 10,
    search_mode: str = "standard",
    llm_fn=None,
) -> dict:
    """
    Compute retrieval metrics: recall@k, MRR, etc.
    No LLM needed for generation/judging — just checks if evidence turns
    are in top-k results.

    For agentic mode, llm_fn is used for HyDE and query refinement only
    (not for answer generation).
    """
    # Build dia_id -> content map for evidence matching
    dia_id_to_content = {}
    for msg in messages:
        did = msg.get("_dia_id", "")
        if did:
            dia_id_to_content[did] = msg["content"]

    results_by_category = {1: [], 2: [], 3: [], 4: []}
    all_results = []
    query_details = []

    for qa in qa_pairs:
        cat = qa["category"]
        if cat == 5:  # Skip adversarial
            continue

        question = qa["question"]
        evidence_ids = qa.get("evidence", [])
        gold_answer = qa.get("answer", "")

        # Query Neuromem
        # For retrieval metrics, disable reranker (hurts recall on conversational data)
        t0 = time.time()
        if search_mode == "agentic":
            search_results = engine.search_agentic(
                question, limit=top_k, llm_fn=llm_fn,
                use_reranker=False,
            )
        else:
            search_results = engine.search(question, limit=top_k)
        elapsed = time.time() - t0

        # Check if any evidence turn content is in retrieved results
        retrieved_contents = [r["content"] for r in search_results]

        # Evidence recall: what fraction of evidence turns are retrieved?
        evidence_found = 0
        evidence_details = []
        for eid in evidence_ids:
            evidence_text = dia_id_to_content.get(eid, "")
            if evidence_text:
                found = any(evidence_text in rc or rc in evidence_text
                           for rc in retrieved_contents)
                if found:
                    evidence_found += 1
                evidence_details.append({"dia_id": eid, "found": found})

        recall = evidence_found / len(evidence_ids) if evidence_ids else 0.0

        # Content overlap: does any retrieved result contain key answer terms?
        answer_terms = set(str(gold_answer).lower().split())
        content_overlap = 0.0
        if answer_terms and search_results:
            best_overlap = 0
            for r in search_results:
                rc_terms = set(r["content"].lower().split())
                overlap = len(answer_terms & rc_terms) / len(answer_terms)
                best_overlap = max(best_overlap, overlap)
            content_overlap = best_overlap

        result = {
            "recall_at_k": recall,
            "content_overlap": content_overlap,
            "num_results": len(search_results),
            "elapsed_ms": round(elapsed * 1000, 1),
        }

        results_by_category[cat].append(result)
        all_results.append(result)

        query_details.append({
            "question": question,
            "category": cat,
            "gold_answer": gold_answer,
            "evidence_ids": evidence_ids,
            "evidence_recall": recall,
            "content_overlap": content_overlap,
            "top_result": search_results[0]["content"][:200] if search_results else "",
            "elapsed_ms": round(elapsed * 1000, 1),
        })

    # Aggregate
    cat_names = {1: "single_hop", 2: "multi_hop", 3: "temporal", 4: "open_domain"}
    summary = {}
    for cat_id, cat_name in cat_names.items():
        cat_results = results_by_category[cat_id]
        if cat_results:
            avg_recall = sum(r["recall_at_k"] for r in cat_results) / len(cat_results)
            avg_overlap = sum(r["content_overlap"] for r in cat_results) / len(cat_results)
            avg_time = sum(r["elapsed_ms"] for r in cat_results) / len(cat_results)
            summary[cat_name] = {
                "count": len(cat_results),
                "avg_recall_at_k": round(avg_recall, 4),
                "avg_content_overlap": round(avg_overlap, 4),
                "avg_query_ms": round(avg_time, 1),
            }

    overall_recall = sum(r["recall_at_k"] for r in all_results) / len(all_results) if all_results else 0
    overall_overlap = sum(r["content_overlap"] for r in all_results) / len(all_results) if all_results else 0

    return {
        "overall_recall_at_k": round(overall_recall, 4),
        "overall_content_overlap": round(overall_overlap, 4),
        "total_questions": len(all_results),
        "top_k": top_k,
        "by_category": summary,
        "details": query_details,
    }


# ---------------------------------------------------------------------------
# Answer generation (improved prompt)
# ---------------------------------------------------------------------------

ANSWER_PROMPT = """You are answering a question about past conversations between two people.
The context below contains relevant conversation excerpts and memory summaries.
Metadata in brackets: [Speaker | Session Date | Session Number] or [system | Date | Session] for summaries.

TEMPORAL REASONING:
- Each excerpt has a session date (e.g., "1:56 pm on 8 May, 2023")
- Resolve relative times: "yesterday" on May 8 → May 7, 2023; "last week" on May 25 → ~May 18; "five years ago" in 2023 → ~2018
- ALWAYS give absolute dates, never relative ones
- Phrases like "approximately [date]" in the text are pre-resolved dates — use them directly

CRITICAL — LIST COMPLETENESS:
- Questions like "What X does Y do?", "Where has Y been?", "What books/movies/hobbies?" expect EVERY instance
- Scan ALL excerpts carefully — items may be mentioned just once, in passing, across different sessions
- Include EVERY distinct item found anywhere in the context, even if mentioned briefly
- Missing even one item is wrong — be exhaustive
- Format lists with commas: "item1, item2, item3"

ANSWERING RULES:
- Answer based on what IS in the context, even if partial
- Combine information from ALL excerpts — a fact in excerpt 3 is just as valid as one in excerpt 1
- Pay attention to WHO said WHAT — attribute correctly based on speaker labels
- Use specific details: names, dates, numbers, places
- Answer concisely in 1-3 sentences
- ONLY say "Not mentioned" if you have ZERO relevant information
- Memory summaries (from [system]) contain condensed facts — treat them as reliable context
- For counterfactual/hypothetical questions ("Would X be...?", "If X hadn't..."), reason about what the conversation implies

Context:
{context}

Question: {question}

Answer:"""


def generate_answers(
    engine,
    qa_pairs: list[dict],
    top_k: int = 15,
    llm_backend: str = "anthropic",
    model: str = "claude-opus-4-6",
    search_mode: str = "standard",
    llm_fn=None,
    max_per_session: int = 0,
    use_llm_reranker: bool = False,
) -> list[dict]:
    """
    Generate answers for each QA pair using retrieved context + LLM.
    """
    if llm_backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
    elif llm_backend == "openai":
        import openai
        client = openai.OpenAI()
    else:
        raise ValueError(f"Unknown LLM backend: {llm_backend}")

    results = []
    scored_pairs = [qa for qa in qa_pairs if qa["category"] != 5]

    for i, qa in enumerate(scored_pairs):
        question = qa["question"]

        # Adaptive k: explicit list/collection questions get more results
        # to capture items scattered across different sessions.
        # Only trigger for clear enumeration questions, NOT broad "what does X think?"
        q_lower = question.lower()
        is_list_q = any(p in q_lower for p in [
            "what books", "what movies", "what hobbies", "what activities",
            "what items", "what places", "what foods", "what sports",
            "what songs", "what bands", "what artists", "what authors",
            "where has ", "what collect", "what musical",
            "which cities", "which countries", "which locations",
            "what exercises", "what pets", "what games",
        ])
        effective_k = min(top_k + 5, 20) if is_list_q else top_k

        # Retrieve context using selected search mode
        # For answer generation, enable reranker for better precision
        if search_mode == "agentic":
            search_results = engine.search_agentic(
                question, limit=effective_k, llm_fn=llm_fn,
                use_reranker=True,
                max_per_session=max_per_session,
                use_llm_reranker=use_llm_reranker,
            )
        else:
            search_results = engine.search(question, limit=effective_k)

        # Build context grouped by session, chronological within each
        # This helps the LLM follow conversation flow and temporal sequence
        from collections import defaultdict
        sessions = defaultdict(list)
        for r in search_results:
            sess_key = r.get("category", "unknown")
            sessions[sess_key].append(r)

        context_parts = []
        for sess_key in sorted(sessions.keys()):
            sess_results = sessions[sess_key]
            # Sort by message ID within session (chronological)
            sess_results.sort(key=lambda r: r.get("id", 0))
            for r in sess_results:
                sender = r.get("sender", "?")
                timestamp = r.get("timestamp", "")
                content = r["content"]
                meta = f"[{sender}"
                if timestamp:
                    meta += f" | {timestamp}"
                meta += f" | {sess_key}]"
                context_parts.append(f"{meta} {content}")

        context = "\n\n".join(context_parts)

        # Generate answer with improved prompt
        prompt = ANSWER_PROMPT.format(context=context, question=question)

        try:
            if llm_backend == "anthropic":
                resp = client.messages.create(
                    model=model,
                    max_tokens=200,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}],
                )
                answer = resp.content[0].text
            elif llm_backend == "openai":
                resp = client.chat.completions.create(
                    model=model,
                    max_tokens=200,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}],
                )
                answer = resp.choices[0].message.content
        except Exception as e:
            answer = f"ERROR: {e}"

        results.append({
            "question": question,
            "category": qa["category"],
            "gold_answer": qa["answer"],
            "generated_answer": answer,
            "evidence": qa.get("evidence", []),
            "num_retrieved": len(search_results),
        })

        if (i + 1) % 50 == 0:
            print(f"  Generated {i+1}/{len(scored_pairs)} answers...")

    return results


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def score_answers(generated: list[dict], llm_backend: str = "anthropic",
                  model: str = "claude-sonnet-4-5-20250929") -> dict:
    """
    Score generated answers using LLM-as-judge (J-score).
    Binary CORRECT/WRONG per answer.
    """
    if llm_backend == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
    elif llm_backend == "openai":
        import openai
        client = openai.OpenAI()
    else:
        raise ValueError(f"Unknown LLM backend: {llm_backend}")

    cat_names = {1: "single_hop", 2: "multi_hop", 3: "temporal", 4: "open_domain"}
    scored = []

    for i, item in enumerate(generated):
        judge_prompt = f"""You are evaluating an AI memory system's answer to a question about a conversation.

Gold answer: {item['gold_answer']}
System answer: {item['generated_answer']}

Is the system's answer CORRECT? Be generous — if the answer touches on the same topic and contains the key information from the gold answer, it should be CORRECT. Minor phrasing differences, extra details, or varied date formats are acceptable.

Respond with exactly one word: CORRECT or WRONG"""

        try:
            if llm_backend == "anthropic":
                resp = client.messages.create(
                    model=model,
                    max_tokens=10,
                    temperature=0.1,
                    messages=[{"role": "user", "content": judge_prompt}],
                )
                verdict = resp.content[0].text.strip().upper()
            elif llm_backend == "openai":
                resp = client.chat.completions.create(
                    model=model,
                    max_tokens=10,
                    temperature=0.1,
                    messages=[{"role": "user", "content": judge_prompt}],
                )
                verdict = resp.choices[0].message.content.strip().upper()
        except Exception as e:
            verdict = f"ERROR: {e}"

        is_correct = "CORRECT" in verdict
        scored.append({
            **item,
            "verdict": verdict,
            "correct": is_correct,
        })

        if (i + 1) % 50 == 0:
            correct_so_far = sum(1 for s in scored if s["correct"])
            print(f"  Scored {i+1}/{len(generated)}: {correct_so_far}/{i+1} correct ({correct_so_far/(i+1)*100:.1f}%)")

    # Aggregate J-score
    by_cat = {}
    for cat_id, cat_name in cat_names.items():
        cat_items = [s for s in scored if s["category"] == cat_id]
        if cat_items:
            correct = sum(1 for s in cat_items if s["correct"])
            by_cat[cat_name] = {
                "correct": correct,
                "total": len(cat_items),
                "accuracy": round(correct / len(cat_items) * 100, 1),
            }

    total_correct = sum(1 for s in scored if s["correct"])
    j_score = total_correct / len(scored) * 100 if scored else 0

    return {
        "j_score": round(j_score, 1),
        "total_correct": total_correct,
        "total_questions": len(scored),
        "by_category": by_cat,
        "details": scored,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="LoCoMo Benchmark for Neuromem")
    parser.add_argument("--retrieval-only", action="store_true",
                        help="Only compute retrieval metrics (no LLM needed for generation)")
    parser.add_argument("--search-mode", default="standard",
                        choices=["standard", "agentic"],
                        help="Search mode: standard (6-layer) or agentic (multi-round + HyDE + reranking)")
    parser.add_argument("--llm-backend", default="anthropic",
                        choices=["anthropic", "openai", "ollama"],
                        help="LLM backend for answer generation + scoring")
    parser.add_argument("--model", default="claude-opus-4-6",
                        help="Model name for generation and scoring")
    parser.add_argument("--hyde-model", default=None,
                        help="Model for HyDE generation (defaults to --model; use 'ollama:qwen2.5:7b-instruct' for local)")
    parser.add_argument("--judge-model", default=None,
                        help="Model for judging (defaults to --model)")
    parser.add_argument("--top-k", type=int, default=15,
                        help="Number of results to retrieve per query (default 15)")
    parser.add_argument("--conv-ids", default=None,
                        help="Comma-separated conversation indices to run (default: all)")
    parser.add_argument("--enable-hyde", action="store_true",
                        help="Enable HyDE even in retrieval-only mode (requires LLM calls)")
    parser.add_argument("--embedding-model", default="model2vec",
                        choices=["model2vec", "minilm", "bge-small"],
                        help="Embedding model: model2vec (256d, fast), minilm (384d, better), bge-small (384d, best)")
    parser.add_argument("--llm-rerank", action="store_true",
                        help="Use LLM (Haiku) as reranker after cross-encoder (more accurate, slower)")
    parser.add_argument("--no-resolve-times", action="store_true",
                        help="Disable temporal resolution in message content (for A/B testing)")
    parser.add_argument("--enable-episodes", action="store_true",
                        help="Generate LLM episode summaries + atomic facts per session (requires LLM calls during ingestion)")
    parser.add_argument("--episode-model", default=None,
                        help="Model for episode extraction (defaults to --hyde-model)")
    parser.add_argument("--max-per-session", type=int, default=0,
                        help="Max results per session for diversity (0=unlimited)")
    parser.add_argument("--output-suffix", default="",
                        help="Suffix for output filenames (for A/B comparisons)")
    parser.add_argument("--rejudge", default=None,
                        help="Path to existing full results JSON to re-score (skips retrieval + generation)")
    parser.add_argument("--judge-backend", default=None,
                        choices=["anthropic", "openai", "ollama"],
                        help="LLM backend for judging (defaults to --llm-backend)")
    parser.add_argument("--judge-api-key", default=None,
                        help="API key for judge backend (overrides env)")
    args = parser.parse_args()

    if args.judge_model is None:
        args.judge_model = args.model
    if args.hyde_model is None:
        args.hyde_model = args.model
    if args.episode_model is None:
        args.episode_model = args.hyde_model
    if args.judge_backend is None:
        args.judge_backend = args.llm_backend

    # Set judge API key if provided
    if args.judge_api_key:
        if args.judge_backend == "openai":
            os.environ["OPENAI_API_KEY"] = args.judge_api_key
        elif args.judge_backend == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = args.judge_api_key

    # --- Re-judge mode: load existing results and re-score ---
    if args.rejudge:
        rejudge_path = Path(args.rejudge)
        if not rejudge_path.exists():
            print(f"ERROR: File not found: {rejudge_path}")
            sys.exit(1)

        print(f"\n{'='*70}")
        print(f"RE-JUDGE MODE — Scoring existing answers")
        print(f"{'='*70}")
        print(f"  Input: {rejudge_path}")
        print(f"  Judge: {args.judge_backend}/{args.judge_model}")

        with open(rejudge_path) as f:
            existing = json.load(f)

        # Extract the answer details (skip ERRORs in generated_answer)
        details = existing.get("details", [])
        valid = [d for d in details if not str(d.get("generated_answer", "")).startswith("ERROR")]
        errored = [d for d in details if str(d.get("generated_answer", "")).startswith("ERROR")]
        print(f"  Total answers: {len(details)}")
        print(f"  Valid answers: {len(valid)}")
        print(f"  Errored (skipped): {len(errored)}")

        print(f"\n  Scoring {len(valid)} answers with {args.judge_backend}/{args.judge_model}...")
        score_result = score_answers(valid, llm_backend=args.judge_backend,
                                      model=args.judge_model)

        print(f"\n{'='*70}")
        print("J-SCORE RESULTS (RE-JUDGED)")
        print(f"{'='*70}")
        print(f"  J-Score: {score_result['j_score']}%")
        print(f"  Correct: {score_result['total_correct']}/{score_result['total_questions']}")
        for cat_name, cat_data in score_result["by_category"].items():
            print(f"    {cat_name:15s}: {cat_data['accuracy']}% ({cat_data['correct']}/{cat_data['total']})")

        if errored:
            print(f"\n  NOTE: {len(errored)} questions excluded (answer generation failed)")
            total_with_errors = score_result['total_questions'] + len(errored)
            adj_score = score_result['total_correct'] / total_with_errors * 100
            print(f"  Adjusted J-Score (counting errors as wrong): {adj_score:.1f}% ({score_result['total_correct']}/{total_with_errors})")

        print("\n  Published scores for comparison:")
        print("    EverMemOS:    92.3%")
        print("    MemMachine:   84.9%")
        print("    Zep/Graphiti: 75.1%")
        print("    Letta:        74.0%")
        print("    Full-Context: 72.9%")
        print("    Mem0:         66.9%")
        print("    LangMem:      58.1%")

        # Save re-judged results
        suffix = f"_rejudged_{args.judge_backend}_{args.judge_model.replace('/', '_')}"
        if args.output_suffix:
            suffix += f"_{args.output_suffix}"
        out_path = RESULTS_DIR / f"neuromem_locomo_full{suffix}.json"
        with open(out_path, "w") as f:
            json.dump({
                "system": "Neuromem",
                "version": "2.0.0",
                "benchmark": "LoCoMo",
                "search_mode": existing.get("search_mode", "unknown"),
                "j_score": score_result["j_score"],
                "original_generation_model": existing.get("generation_model", "unknown"),
                "judge_backend": args.judge_backend,
                "judge_model": args.judge_model,
                "source_file": str(rejudge_path),
                **score_result,
            }, f, indent=2)
        print(f"\n  Re-judged results saved to: {out_path}")
        return

    # Set embedding model before any engine creation
    if args.embedding_model != "model2vec":
        from neuromem.vector_search import set_embedding_model
        set_embedding_model(args.embedding_model)
        print(f"  Embedding model: {args.embedding_model}")

    # Set up LLM function for agentic search (HyDE + query refinement)
    # With --enable-hyde, HyDE works even in retrieval-only mode
    llm_fn = None
    need_llm = (args.search_mode == "agentic" and
                (not args.retrieval_only or args.enable_hyde))
    if need_llm:
        # Parse hyde-model which may be in format "backend:model"
        if ":" in args.hyde_model and args.hyde_model.split(":")[0] in ("ollama",):
            hyde_backend = args.hyde_model.split(":")[0]
            hyde_model = ":".join(args.hyde_model.split(":")[1:])
        else:
            hyde_backend = args.llm_backend
            hyde_model = args.hyde_model

        try:
            llm_fn = make_llm_fn(hyde_backend, hyde_model)
            if llm_fn:
                print(f"  HyDE/query refinement: {hyde_backend}/{hyde_model}")
        except ImportError:
            print(f"  Warning: {hyde_backend} SDK not installed, HyDE/refinement disabled")
    elif args.search_mode == "agentic":
        print("  Agentic mode (retrieval-only): clustering enabled, HyDE disabled")

    print("=" * 70)
    print(f"LoCoMo BENCHMARK — Neuromem v2 ({args.search_mode} search)")
    print("=" * 70)

    # Load dataset
    print("\n[1/5] Loading LoCoMo dataset...")
    data = load_locomo()
    print(f"  Loaded {len(data)} conversations")

    conv_indices = list(range(len(data)))
    if args.conv_ids:
        conv_indices = [int(x) for x in args.conv_ids.split(",")]
        print(f"  Running on conversations: {conv_indices}")

    all_retrieval_metrics = []
    all_generated = []
    total_qa = 0
    total_turns = 0

    for ci in conv_indices:
        conv = data[ci]
        sample_id = conv["sample_id"]
        qa_pairs = conv["qa"]
        scored_qa = [q for q in qa_pairs if q["category"] != 5]
        total_qa += len(scored_qa)

        print(f"\n--- Conversation {ci}: {sample_id} ({len(scored_qa)} scored QA) ---")

        # Parse and ingest
        messages = parse_conversations(conv, resolve_times=not args.no_resolve_times)
        total_turns += len(messages)
        print(f"  Parsed {len(messages)} turns")

        # Create engine for this conversation
        tmp_db = Path(tempfile.mktemp(suffix=".db", prefix=f"locomo_{sample_id}_"))
        engine = NeuromemEngine(db_path=tmp_db)

        # --- Episode extraction (optional, requires LLM calls) ---
        episode_messages = []
        if args.enable_episodes:
            # Set up episode LLM function
            if ":" in args.episode_model and args.episode_model.split(":")[0] in ("ollama",):
                ep_backend = args.episode_model.split(":")[0]
                ep_model = ":".join(args.episode_model.split(":")[1:])
            else:
                ep_backend = args.llm_backend
                ep_model = args.episode_model

            episode_llm_fn = make_llm_fn(ep_backend, ep_model, max_tokens=800)
            if episode_llm_fn:
                # Get speaker names
                conversation_data = conv["conversation"]
                sp_a = conversation_data.get("speaker_a", "Speaker A")
                sp_b = conversation_data.get("speaker_b", "Speaker B")

                print(f"  [1.5/5] Extracting episodes with {ep_backend}/{ep_model}...")
                t0_ep = time.time()
                episode_messages = extract_episodes_batch(
                    messages, episode_llm_fn,
                    speaker_a=sp_a, speaker_b=sp_b,
                    combined=True,
                )
                ep_time = time.time() - t0_ep
                n_episodes = sum(1 for m in episode_messages if m.get("modality") == "episode")
                n_facts = sum(1 for m in episode_messages if m.get("modality") == "fact")
                print(f"  Extracted {n_episodes} episodes + {n_facts} facts in {ep_time:.1f}s")

        # Combine raw messages + episodes for ingestion
        all_messages = messages + episode_messages

        # Write messages to temp JSON and ingest
        tmp_json = Path(tempfile.mktemp(suffix=".json", prefix="locomo_msgs_"))
        # Strip internal fields before saving
        clean_messages = [{k: v for k, v in m.items() if not k.startswith("_")} for m in all_messages]
        with open(tmp_json, "w") as f:
            json.dump(clean_messages, f)

        print(f"  [2/5] Ingesting into Neuromem...")
        t0 = time.time()
        ingest_stats = engine.ingest(tmp_json)
        ingest_time = time.time() - t0
        print(f"  Ingested in {ingest_time:.2f}s")
        for k, v in ingest_stats.items():
            if "ERROR" in str(v):
                print(f"    {k}: {v}")
            elif k in ("build_clusters", "build_vectors"):
                print(f"    {k}: {v}")

        # Retrieval metrics
        print(f"  [3/5] Computing retrieval metrics (top_k={args.top_k}, mode={args.search_mode})...")
        metrics = compute_retrieval_metrics(
            engine, qa_pairs, messages,
            top_k=args.top_k,
            search_mode=args.search_mode,
            llm_fn=llm_fn,
        )
        all_retrieval_metrics.append({
            "conversation": sample_id,
            **{k: v for k, v in metrics.items() if k != "details"},
        })

        print(f"  Recall@{args.top_k}: {metrics['overall_recall_at_k']:.4f}")
        print(f"  Content overlap: {metrics['overall_content_overlap']:.4f}")
        for cat_name, cat_data in metrics["by_category"].items():
            print(f"    {cat_name:15s}: recall={cat_data['avg_recall_at_k']:.3f}  overlap={cat_data['avg_content_overlap']:.3f}  ({cat_data['count']} Q)")

        # Full LLM pipeline
        if not args.retrieval_only:
            print(f"  [4/5] Generating answers with {args.model}...")
            gen = generate_answers(
                engine, qa_pairs, top_k=args.top_k,
                llm_backend=args.llm_backend, model=args.model,
                search_mode=args.search_mode, llm_fn=llm_fn,
                max_per_session=args.max_per_session,
                use_llm_reranker=args.llm_rerank,
            )
            all_generated.extend(gen)

        # Cleanup
        engine.close()
        tmp_db.unlink(missing_ok=True)
        for suffix in ["-wal", "-shm"]:
            Path(str(tmp_db) + suffix).unlink(missing_ok=True)
        tmp_json.unlink(missing_ok=True)

    # Overall retrieval summary
    print("\n" + "=" * 70)
    print("RETRIEVAL RESULTS SUMMARY")
    print("=" * 70)
    avg_recall = 0
    avg_overlap = 0
    if all_retrieval_metrics:
        avg_recall = sum(m["overall_recall_at_k"] for m in all_retrieval_metrics) / len(all_retrieval_metrics)
        avg_overlap = sum(m["overall_content_overlap"] for m in all_retrieval_metrics) / len(all_retrieval_metrics)
        print(f"  Search mode: {args.search_mode}")
        print(f"  Conversations tested: {len(all_retrieval_metrics)}")
        print(f"  Total scored QA pairs: {total_qa}")
        print(f"  Total turns ingested: {total_turns}")
        print(f"  Average Recall@{args.top_k}: {avg_recall:.4f} ({avg_recall*100:.1f}%)")
        print(f"  Average Content Overlap: {avg_overlap:.4f} ({avg_overlap*100:.1f}%)")

    # Save retrieval results
    suffix = f"_{args.search_mode}"
    if args.output_suffix:
        suffix += f"_{args.output_suffix}"
    retrieval_path = RESULTS_DIR / f"neuromem_locomo_retrieval{suffix}.json"
    with open(retrieval_path, "w") as f:
        json.dump({
            "system": "Neuromem",
            "version": "2.0.0",
            "benchmark": "LoCoMo",
            "search_mode": args.search_mode,
            "top_k": args.top_k,
            "conversations_tested": len(all_retrieval_metrics),
            "total_qa_pairs": total_qa,
            "total_turns": total_turns,
            "avg_recall_at_k": round(avg_recall, 4) if all_retrieval_metrics else 0,
            "avg_content_overlap": round(avg_overlap, 4) if all_retrieval_metrics else 0,
            "per_conversation": all_retrieval_metrics,
        }, f, indent=2)
    print(f"\n  Retrieval results saved to: {retrieval_path}")

    # Score if full pipeline
    if not args.retrieval_only and all_generated:
        print(f"\n  [5/5] Scoring with LLM judge ({args.judge_backend}/{args.judge_model})...")
        score_result = score_answers(all_generated, llm_backend=args.judge_backend,
                                      model=args.judge_model)

        print("\n" + "=" * 70)
        print("J-SCORE RESULTS")
        print("=" * 70)
        print(f"  J-Score: {score_result['j_score']}%")
        print(f"  Correct: {score_result['total_correct']}/{score_result['total_questions']}")
        for cat_name, cat_data in score_result["by_category"].items():
            print(f"    {cat_name:15s}: {cat_data['accuracy']}% ({cat_data['correct']}/{cat_data['total']})")

        print("\n  Published scores for comparison:")
        print("    EverMemOS:    92.3%")
        print("    MemMachine:   84.9%")
        print("    Zep/Graphiti: 75.1%")
        print("    Letta:        74.0%")
        print("    Full-Context: 72.9%")
        print("    Mem0:         66.9%")
        print("    LangMem:      58.1%")

        # Save full results
        full_path = RESULTS_DIR / f"neuromem_locomo_full{suffix}.json"
        with open(full_path, "w") as f:
            json.dump({
                "system": "Neuromem",
                "version": "2.0.0",
                "benchmark": "LoCoMo",
                "search_mode": args.search_mode,
                "j_score": score_result["j_score"],
                "llm_backend": args.llm_backend,
                "generation_model": args.model,
                "judge_model": args.judge_model,
                **score_result,
            }, f, indent=2)
        print(f"\n  Full results saved to: {full_path}")


if __name__ == "__main__":
    main()
