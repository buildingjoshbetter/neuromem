#!/usr/bin/env python3
"""
Advanced Neuromem Experiments
==============================
Higher-impact experiments focused on maximizing accuracy.
Priority: Accuracy > Latency > Cost.
"""

import asyncio
import json
import os
import sys
import time
import sqlite3
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
    run_experiment, load_failures, format_context, make_llm_fn,
    LLM_API_KEY, LLM_BASE_URL, ANSWER_MODEL
)
import openai


# =============================================================================
# EXPERIMENT A: Full Context Dump (No Search — Perfect Retrieval Ceiling)
# =============================================================================

def full_context_search_fn(engine, query, top_k, llm_fn):
    """Return ALL messages from the database — no search, just dump everything."""
    if engine.conn is None:
        return []
    try:
        rows = engine.conn.execute(
            "SELECT rowid, content, sender, recipient, timestamp, category, modality FROM messages ORDER BY rowid"
        ).fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "content": row[1],
                "sender": row[2] or "",
                "recipient": row[3] or "",
                "timestamp": row[4] or "",
                "category": row[5] or "",
                "modality": row[6] or "",
                "score": 1.0,
            })
        return results
    except Exception as e:
        print(f"  Full context error: {e}")
        return []


def make_full_context_answer_fn(model="openai/gpt-4.1-mini"):
    """Answer with full conversation context — test ceiling with perfect retrieval."""
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def _answer(question: str, context: str) -> str:
        prompt = f"""You are answering a question about a conversation between two friends.
Below is the COMPLETE conversation transcript. The answer is definitely somewhere in this transcript.

INSTRUCTIONS:
1. Read the ENTIRE transcript carefully
2. Find ALL relevant information — it may be spread across multiple messages
3. Pay special attention to:
   - Specific names, dates, numbers, amounts
   - Who said what (speaker attribution)
   - Temporal references like "last year", "yesterday", "next week" — resolve them relative to the message date
   - Implied information (e.g., if someone says "I'm single" offhand)
4. Synthesize all evidence into a concise answer (1-2 sentences)
5. Be specific — include actual names, dates, numbers from the transcript

CONVERSATION TRANSCRIPT:
{context}

QUESTION: {question}

Think step by step, then give your final answer:"""

        resp = client.chat.completions.create(
            model=model,
            max_tokens=1000,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return _answer


# =============================================================================
# EXPERIMENT B: Full Context + Sonnet (strongest model + all context)
# =============================================================================

def make_full_context_sonnet_fn():
    """Full context + Sonnet 4.5 for answering."""
    return make_full_context_answer_fn(model="anthropic/claude-sonnet-4.5")


def make_full_context_opus_fn():
    """Full context + Opus 4.6 for answering."""
    return make_full_context_answer_fn(model="anthropic/claude-opus-4.6")


# =============================================================================
# EXPERIMENT C: Query Decomposition Search
# =============================================================================

def query_decomp_search_fn(engine, query, top_k, llm_fn):
    """Decompose query into sub-queries, search each, merge results."""
    # Generate sub-queries
    try:
        decomp_prompt = f"""Break this question into 2-3 simpler search queries that would help find the answer.
Return ONLY the queries, one per line.

Question: {query}

Search queries:"""
        sub_queries_text = llm_fn(decomp_prompt)
        sub_queries = [q.strip().lstrip("- ").lstrip("1234567890. ")
                       for q in sub_queries_text.strip().split("\n")
                       if q.strip() and len(q.strip()) > 5]
    except Exception:
        sub_queries = [query]

    # Add original query
    all_queries = [query] + sub_queries[:3]

    # Search each query and merge results
    all_results = {}
    for q in all_queries:
        try:
            results = engine.search_agentic(
                q, limit=top_k,
                llm_fn=llm_fn,
                use_hyde=True,
                use_reranker=True,
                use_clustering=True,
            )
            for r in results:
                rid = r.get("id", id(r))
                if rid not in all_results:
                    all_results[rid] = r
                else:
                    # Boost score for results found by multiple queries
                    all_results[rid]["score"] = max(
                        all_results[rid].get("score", 0),
                        r.get("score", 0)
                    ) * 1.1
        except Exception:
            pass

    # Sort by score and return
    results = sorted(all_results.values(), key=lambda d: -d.get("score", 0))
    return results[:top_k * 2]


# =============================================================================
# EXPERIMENT D: Entity-Aware Search
# =============================================================================

def entity_search_fn(engine, query, top_k, llm_fn):
    """Extract entities from query, then do targeted entity + keyword search."""
    # Standard agentic search
    base_results = engine.search_agentic(
        query, limit=top_k,
        llm_fn=llm_fn,
        use_hyde=True, use_reranker=True, use_clustering=True,
    )

    # Extract entities from question for targeted search
    try:
        entities_prompt = f"""Extract the key person names and specific topics from this question.
Return just the names/topics, one per line.

Question: {query}

Names/topics:"""
        entities_text = llm_fn(entities_prompt)
        entities = [e.strip() for e in entities_text.strip().split("\n") if e.strip()]
    except Exception:
        entities = []

    # Do targeted FTS search for each entity
    existing_ids = {r.get("id") for r in base_results if r.get("id")}
    for entity in entities[:3]:
        try:
            from neuromem.fts_search import search_fts
            fts_results = search_fts(engine.conn, entity, limit=10)
            for r in fts_results:
                if r.get("id") and r["id"] not in existing_ids:
                    r["score"] = r.get("score", 0) * 0.7
                    r["source"] = "entity_search"
                    base_results.append(r)
                    existing_ids.add(r["id"])
        except Exception:
            pass

    base_results.sort(key=lambda d: (-d.get("score", 0), d.get("id", 0)))
    return base_results[:top_k * 2]


# =============================================================================
# EXPERIMENT E: Structured Prompt + Sonnet via OpenRouter
# =============================================================================

def make_sonnet_structured_fn():
    """Sonnet 4.5 with structured prompt."""
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def _answer(question: str, context: str) -> str:
        prompt = f"""You are answering questions about personal conversations between friends.
You have been given retrieved conversation excerpts as context.

INSTRUCTIONS:
1. Read ALL context carefully — the answer may be spread across multiple excerpts
2. Look for specific names, dates, numbers, and details
3. Pay attention to who said what (speaker attribution matters)
4. For time questions, look for date mentions and temporal references
   - If someone says "last year" and the message is from 2023, that means 2022
   - If someone says "yesterday" on 2023-08-25, that means 2023-08-24
5. If multiple pieces of evidence exist, synthesize them
6. Give a concise, specific answer (1-2 sentences max)
7. If the context genuinely doesn't contain the answer, say "Not enough information"

Context:
{context}

Question: {question}

Think step by step, then give your final answer:"""

        resp = client.chat.completions.create(
            model="anthropic/claude-sonnet-4.5",
            max_tokens=800,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return _answer


# =============================================================================
# Main
# =============================================================================

EXPERIMENTS = {
    "A": ("full_context_gpt4mini", "Full conversation context + GPT-4.1-mini (ceiling test)",
          full_context_search_fn, make_full_context_answer_fn()),
    "B": ("full_context_sonnet", "Full conversation context + Sonnet 4.5 (strongest ceiling)",
          full_context_search_fn, make_full_context_sonnet_fn()),
    "C": ("query_decomposition", "Query decomposition into sub-queries + merge",
          query_decomp_search_fn, None),
    "D": ("entity_search", "Entity-aware targeted search",
          entity_search_fn, None),
    "E": ("sonnet_structured", "Sonnet 4.5 + structured prompt (best model + best prompt)",
          None, make_sonnet_structured_fn()),
    "F": ("full_context_opus", "Full conversation context + Opus 4.6 (max accuracy ceiling)",
          full_context_search_fn, make_full_context_opus_fn()),
}


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp", required=True, help="Experiment letter (A-F)")
    parser.add_argument("--max-q", type=int, default=50)
    parser.add_argument("--judge-runs", type=int, default=1)
    args = parser.parse_args()

    exp_key = args.exp.upper()
    if exp_key not in EXPERIMENTS:
        print(f"Unknown experiment: {exp_key}. Available: {list(EXPERIMENTS.keys())}")
        return

    name, desc, search_fn, answer_fn = EXPERIMENTS[exp_key]
    await run_experiment(
        name, desc,
        search_fn=search_fn,
        answer_fn=answer_fn,
        num_judge_runs=args.judge_runs,
        max_questions=args.max_q,
    )


if __name__ == "__main__":
    asyncio.run(main())
