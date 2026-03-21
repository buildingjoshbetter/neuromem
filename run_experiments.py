#!/usr/bin/env python3
"""
Neuromem Experiment Runner
===========================
Implements and tests specific improvements against the 357 failures.

Each experiment modifies either search behavior, answer generation, or both,
then runs through the test harness.

Priority: Accuracy > Latency > Cost
"""

import asyncio
import json
import os
import sys
import time
import sqlite3
import shutil
from pathlib import Path
from collections import defaultdict

# Load environment
for line in open("/Users/j/Desktop/neuromem/EverMemOS/.env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip())

sys.path.insert(0, "/Users/j/Desktop/neuromem")

from test_harness import (
    run_experiment, load_failures, get_engine_for_conv,
    make_llm_fn, generate_answer, format_context,
    LLM_API_KEY, LLM_BASE_URL, ANSWER_MODEL
)


# =============================================================================
# EXPERIMENT 1: Better Answer Prompt (Structured Reasoning)
# =============================================================================

def make_structured_answer_fn():
    """Answer with structured reasoning — helps wrong inference & insufficient detail."""
    import openai
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def _answer(question: str, context: str) -> str:
        prompt = f"""You are answering questions about personal conversations between friends.
You have been given retrieved conversation excerpts as context.

INSTRUCTIONS:
1. Read ALL context carefully — the answer may be spread across multiple excerpts
2. Look for specific names, dates, numbers, and details
3. Pay attention to who said what (speaker attribution matters)
4. For time questions, look for date mentions and temporal references
5. If multiple pieces of evidence exist, synthesize them
6. Give a concise, specific answer (1-2 sentences max)
7. If the context genuinely doesn't contain the answer, say "Not enough information"

Context:
{context}

Question: {question}

Think step by step, then give your final answer:"""

        resp = client.chat.completions.create(
            model=ANSWER_MODEL,
            max_tokens=800,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return _answer


# =============================================================================
# EXPERIMENT 2: Aggressive Search (more rounds, more candidates)
# =============================================================================

def aggressive_search_fn(engine, query, top_k, llm_fn):
    """More aggressive search: higher top_k, always use HyDE, LLM reranker."""
    return engine.search_agentic(
        query,
        limit=top_k * 2,  # Double the candidates
        max_rounds=2,
        llm_fn=llm_fn,
        use_hyde=True,
        use_reranker=True,
        use_clustering=True,
        use_llm_reranker=True,  # Enable LLM reranking
    )


# =============================================================================
# EXPERIMENT 3: Multi-HyDE (multiple hypothetical documents)
# =============================================================================

def multi_hyde_search_fn(engine, query, top_k, llm_fn):
    """Generate multiple HyDE documents and fuse results."""
    # First, try the standard agentic search
    primary = engine.search_agentic(
        query, limit=top_k,
        llm_fn=llm_fn, use_hyde=True,
        use_reranker=True, use_clustering=True,
    )

    # Also generate additional hypothetical docs and search
    try:
        from neuromem.hyde import hyde_multi_search
        extra = hyde_multi_search(
            engine.conn, query, llm_fn=llm_fn, limit=top_k, n=3,
        )
        # Merge unique results
        existing_ids = {r.get("id") for r in primary if r.get("id")}
        for r in extra:
            if r.get("id") and r["id"] not in existing_ids:
                r["score"] = r.get("score", 0) * 0.8  # Slight discount
                r["source"] = r.get("source", "") + "+multi_hyde"
                primary.append(r)
                existing_ids.add(r["id"])
    except Exception:
        pass

    # Re-sort and trim
    primary.sort(key=lambda d: (-d.get("score", 0), d.get("id", 0)))
    return primary[:top_k * 2]


# =============================================================================
# EXPERIMENT 4: Enhanced Context Formatting
# =============================================================================

def make_enhanced_context_answer_fn():
    """Better context formatting + structured reasoning."""
    import openai
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def _format_enhanced(results):
        """Format with clear structure, grouping by relevance and time."""
        parts = []
        for i, r in enumerate(results):
            sender = r.get("sender", "?")
            ts = r.get("timestamp", "")
            modality = r.get("modality", "")
            content = r.get("content", "")

            label = f"[Message {i+1}]"
            if modality and modality != "conversation":
                label = f"[{modality.title()} {i+1}]"

            meta = f"Speaker: {sender}"
            if ts:
                meta += f" | Date: {ts}"

            parts.append(f"{label}\n{meta}\n{content}")

        return "\n\n---\n\n".join(parts)

    def _answer(question: str, context: str) -> str:
        # Re-parse isn't needed since we receive pre-formatted context
        # But we can add structured reasoning
        prompt = f"""You are a memory retrieval system answering questions about personal conversations.

RETRIEVED MEMORY EXCERPTS:
{context}

QUESTION: {question}

INSTRUCTIONS:
- Carefully read every excerpt above
- The answer is often in the exact words of a message — look for direct quotes
- Pay attention to speaker names and dates
- For "when" questions, look for dates in format YYYY-MM-DD or natural date mentions
- For "what" questions, look for specific details, names, numbers
- For "who" questions, identify the person from speaker tags
- Synthesize information from multiple excerpts if needed
- Be concise (1-2 sentences) and specific

ANSWER:"""

        resp = client.chat.completions.create(
            model=ANSWER_MODEL,
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return _answer


# =============================================================================
# EXPERIMENT 5: Top-k 30 (double the context window)
# =============================================================================

def topk30_search_fn(engine, query, top_k, llm_fn):
    """Search with top_k=30 to give the LLM more context."""
    return engine.search_agentic(
        query, limit=30,
        llm_fn=llm_fn, use_hyde=True,
        use_reranker=True, use_clustering=True,
    )


# =============================================================================
# EXPERIMENT 6: Powerful Answer Model (use Opus for answering)
# =============================================================================

def make_opus_answer_fn():
    """Use Claude Opus 4.6 for answer generation — accuracy over cost."""
    import anthropic
    client = anthropic.Anthropic()

    def _answer(question: str, context: str) -> str:
        prompt = f"""You are answering questions about personal conversations between friends.
You have been given retrieved conversation excerpts as context.

INSTRUCTIONS:
1. Read ALL context carefully — the answer may be spread across multiple excerpts
2. Look for specific names, dates, numbers, and details
3. Pay attention to who said what (speaker attribution matters)
4. For time questions, look for date mentions and temporal references
5. If multiple pieces of evidence exist, synthesize them
6. Give a concise, specific answer (1-2 sentences max)
7. If the context genuinely doesn't contain the answer, say "Not enough information"

Context:
{context}

Question: {question}

Answer:"""

        resp = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    return _answer


# =============================================================================
# EXPERIMENT 7: Sonnet for Answer (good accuracy, faster than Opus)
# =============================================================================

def make_sonnet_answer_fn():
    """Use Claude Sonnet 4.5 for answer generation."""
    import anthropic
    client = anthropic.Anthropic()

    def _answer(question: str, context: str) -> str:
        prompt = f"""You are answering questions about personal conversations between friends.
You have been given retrieved conversation excerpts as context.

Read ALL context carefully. The answer may be in the exact words of a message.
Pay attention to speaker names and dates. Be concise (1-2 sentences).
If the context doesn't contain the answer, say "Not enough information."

Context:
{context}

Question: {question}

Answer:"""

        resp = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=500,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    return _answer


# =============================================================================
# EXPERIMENT 8: Combined Best - Aggressive Search + Structured Prompt + Top-k 30
# =============================================================================

def combined_search_fn(engine, query, top_k, llm_fn):
    """Aggressive search with top-k 30, LLM reranking, multi-HyDE."""
    results = engine.search_agentic(
        query, limit=30,
        max_rounds=2,
        llm_fn=llm_fn, use_hyde=True,
        use_reranker=True, use_clustering=True,
        use_llm_reranker=True,
    )

    # Also try multi-HyDE
    try:
        from neuromem.hyde import hyde_multi_search
        extra = hyde_multi_search(
            engine.conn, query, llm_fn=llm_fn, limit=20, n=3,
        )
        existing_ids = {r.get("id") for r in results if r.get("id")}
        for r in extra:
            if r.get("id") and r["id"] not in existing_ids:
                r["source"] = r.get("source", "") + "+multi_hyde"
                results.append(r)
                existing_ids.add(r["id"])
    except Exception:
        pass

    results.sort(key=lambda d: (-d.get("score", 0), d.get("id", 0)))
    return results[:30]


# =============================================================================
# Main: Run all experiments
# =============================================================================

async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", type=int, default=0, help="Experiment number (0=all)")
    parser.add_argument("--max-q", type=int, default=50, help="Max questions per experiment")
    parser.add_argument("--judge-runs", type=int, default=1, help="Judge runs")
    args = parser.parse_args()

    experiments = {
        1: ("exp1_structured_prompt", "Better answer prompt with step-by-step reasoning",
            None, make_structured_answer_fn()),
        2: ("exp2_aggressive_search", "Aggressive search: LLM reranker + double candidates",
            aggressive_search_fn, None),
        3: ("exp3_multi_hyde", "Multiple HyDE hypothetical documents (n=3)",
            multi_hyde_search_fn, None),
        4: ("exp4_enhanced_context", "Enhanced context formatting + structured prompt",
            None, make_enhanced_context_answer_fn()),
        5: ("exp5_topk30", "Double context window: top_k=30",
            topk30_search_fn, None),
        6: ("exp6_opus_answer", "Claude Opus 4.6 for answer generation",
            None, make_opus_answer_fn()),
        7: ("exp7_sonnet_answer", "Claude Sonnet 4.5 for answer generation",
            None, make_sonnet_answer_fn()),
        8: ("exp8_combined", "Combined: aggressive search + top-k 30 + structured prompt",
            combined_search_fn, make_structured_answer_fn()),
    }

    if args.exp > 0:
        if args.exp in experiments:
            name, desc, search_fn, answer_fn = experiments[args.exp]
            await run_experiment(
                name, desc,
                search_fn=search_fn,
                answer_fn=answer_fn,
                num_judge_runs=args.judge_runs,
                max_questions=args.max_q,
            )
        else:
            print(f"Unknown experiment: {args.exp}")
    else:
        # Run all sequentially
        for exp_num in sorted(experiments.keys()):
            name, desc, search_fn, answer_fn = experiments[exp_num]
            print(f"\n{'#'*70}")
            print(f"# Running experiment {exp_num}: {name}")
            print(f"{'#'*70}")
            await run_experiment(
                name, desc,
                search_fn=search_fn,
                answer_fn=answer_fn,
                num_judge_runs=args.judge_runs,
                max_questions=args.max_q,
            )


if __name__ == "__main__":
    asyncio.run(main())
