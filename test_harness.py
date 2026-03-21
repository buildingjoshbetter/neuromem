#!/usr/bin/env python3
"""
Neuromem Experiment Test Harness
================================
Tests modifications against the 357 questions where Neuromem failed
but EverMemOS succeeded on the fair LoCoMo benchmark.

Usage:
    python test_harness.py --experiment "baseline_verify"
    python test_harness.py --experiment "experiment_name" --description "What changed"

The script:
1. Loads pre-built Neuromem DBs from the fair benchmark
2. Runs search on each failed question using the current engine code
3. Generates answers with GPT-4.1-mini
4. Judges with GPT-4o-mini (1 run for speed, 3 runs for final)
5. Logs results to EXPERIMENT_JOURNAL.md
"""

import asyncio
import json
import os
import sys
import time
import argparse
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv("/Users/j/Desktop/neuromem/EverMemOS/.env")
except ImportError:
    # Manual .env loading
    import re as _re
    for line in open("/Users/j/Desktop/neuromem/EverMemOS/.env"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

# Add neuromem to path
sys.path.insert(0, "/Users/j/Desktop/neuromem")

from neuromem.engine import NeuromemEngine

# --- Constants ---
FAILURES_PATH = "/tmp/nm_failures.json"
RESULTS_DIR = Path("/Users/j/Desktop/neuromem/EverMemOS/evaluation/results/locomo-neuromem-fair-benchmark-20260318")
DB_DIR = RESULTS_DIR  # DBs are in the results dir
JOURNAL_PATH = Path("/Users/j/Desktop/neuromem/EXPERIMENT_JOURNAL.md")

# API configuration
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANSWER_MODEL = "openai/gpt-4.1-mini"
JUDGE_MODEL = "gpt-4o-mini"


def load_failures():
    """Load the 357 failure questions."""
    with open(FAILURES_PATH) as f:
        return json.load(f)


def get_engine_for_conv(conv_id: str, copy_db: bool = False, suffix: str = "") -> NeuromemEngine:
    """
    Get a NeuromemEngine for a conversation.

    Args:
        conv_id: e.g. "locomo_exp_user_0"
        copy_db: If True, copy the DB so we can modify it without affecting original
        suffix: Suffix for the copied DB name
    """
    # Map conv_id to DB filename
    # locomo_exp_user_0 -> neuromem_locomo_0.db
    num = conv_id.split("_")[-1]
    db_name = f"neuromem_locomo_{num}.db"
    db_path = DB_DIR / db_name

    if not db_path.exists():
        raise FileNotFoundError(f"DB not found: {db_path}")

    if copy_db:
        copy_path = Path(f"/tmp/nm_experiment_{num}{suffix}.db")
        shutil.copy2(db_path, copy_path)
        return NeuromemEngine(db_path=copy_path).open()

    return NeuromemEngine(db_path=db_path).open()


def make_llm_fn():
    """Create LLM function for HyDE/query refinement."""
    import openai
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def _call(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=ANSWER_MODEL,
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return _call


def generate_answer(question: str, context: str, structured: bool = True) -> str:
    """Generate answer using GPT-4.1-mini."""
    import openai
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    if structured:
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
    else:
        prompt = f"""Answer the following question using ONLY the provided context.
If the context contains the answer, provide a concise response (under 2 sentences).
If the context does not contain enough information, say "Not enough information."

Context:
{context}

Question: {question}

Answer:"""

    resp = client.chat.completions.create(
        model=ANSWER_MODEL,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


async def judge_answer(question: str, gold: str, generated: str, num_runs: int = 1) -> dict:
    """Judge answer using GPT-4o-mini."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    system_prompt = "You are an expert grader that determines if answers to questions match a gold standard answer"
    user_prompt = f"""Your task is to label an answer to a question as 'CORRECT' or 'WRONG'. You will be given the following data:
    (1) a question (posed by one user to another user),
    (2) a 'gold' (ground truth) answer,
    (3) a generated answer
which you will score as CORRECT/WRONG.

The point of the question is to ask about something one user should know about the other user based on their prior conversations.
The gold answer will usually be a concise and short answer that includes the referenced topic, for example:
Question: Do you remember what I got the last time I went to Hawaii?
Gold answer: A shell necklace
The generated answer might be much longer, but you should be generous with your grading - as long as it touches on the same topic as the gold answer, it should be counted as CORRECT.

For time related questions, the gold answer will be a specific date, month, year, etc. The generated answer might be much longer or use relative time references (like "last Tuesday" or "next month"), but you should be generous with your grading - as long as it refers to the same date or time period as the gold answer, it should be counted as CORRECT. Even if the format differs (e.g., "May 7th" vs "7 May"), consider it CORRECT if it's the same date.

Now it's time for the real question:
Question: {question}
Gold answer: {gold}
Generated answer: {generated}

First, provide a short (one sentence) explanation of your reasoning, then finish with CORRECT or WRONG.
Do NOT include both CORRECT and WRONG in your response, or it will break the evaluation script.

Just return the label CORRECT or WRONG in a json format with the key as "label"."""

    judgments = []
    for _ in range(num_runs):
        try:
            resp = await client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
            content = resp.choices[0].message.content
            import re
            json_match = re.search(r'\{[^{}]*"label"\s*:\s*"[^"]*"[^{}]*\}', content)
            if json_match:
                result = json.loads(json_match.group(0))
                judgments.append(result.get("label", "").strip().upper() == "CORRECT")
            else:
                judgments.append(False)
        except Exception as e:
            print(f"  Judge error: {e}")
            judgments.append(False)

    return {"judgments": judgments, "correct": any(judgments) if num_runs == 1 else sum(judgments) > len(judgments) / 2}


def format_context(results: list) -> str:
    """Format search results into context string."""
    parts = []
    for r in results:
        sender = r.get("sender", "?")
        ts = r.get("timestamp", "")
        cat = r.get("category", "")
        modality = r.get("modality", "")
        meta = f"[{sender}"
        if ts:
            meta += f" | {ts}"
        if cat:
            meta += f" | {cat}"
        if modality and modality != "conversation":
            meta += f" | {modality}"
        meta += "]"
        parts.append(f"{meta} {r['content']}")
    return "\n\n".join(parts)


async def run_experiment(
    experiment_name: str,
    description: str,
    search_fn=None,
    answer_fn=None,
    pre_search_fn=None,
    num_judge_runs: int = 1,
    top_k: int = 15,
    copy_dbs: bool = False,
    max_questions: int = 0,
):
    """
    Run an experiment against the 357 failures.

    Args:
        experiment_name: Name for logging
        description: What changed
        search_fn: Custom search function (engine, query, top_k) -> results
                   If None, uses default search_agentic
        answer_fn: Custom answer function (question, context) -> answer
                   If None, uses default generate_answer
        pre_search_fn: Function called before search (engine, conv_id) -> None
                       For modifying engine state (e.g., adding indexes)
        num_judge_runs: Number of judge runs (1 for fast, 3 for final)
        top_k: Number of results to retrieve
        copy_dbs: Whether to copy DBs (needed if modifying them)
        max_questions: Limit questions for quick testing (0 = all 357)
    """
    failures = load_failures()
    if max_questions > 0:
        failures = failures[:max_questions]

    llm_fn = make_llm_fn()

    print(f"\n{'='*70}")
    print(f"EXPERIMENT: {experiment_name}")
    print(f"Description: {description}")
    print(f"Questions: {len(failures)}")
    print(f"Judge runs: {num_judge_runs}")
    print(f"Top-k: {top_k}")
    print(f"{'='*70}\n")

    t_start = time.time()

    # Cache engines per conversation
    engines = {}
    results_log = []
    correct_count = 0
    category_correct = defaultdict(int)
    category_total = defaultdict(int)

    for i, failure in enumerate(failures):
        question = failure["question"]
        gold = failure["gold"]
        conv_id = failure["conv_id"]
        category = failure["category"]

        category_total[category] += 1

        # Get or create engine
        if conv_id not in engines:
            try:
                engine = get_engine_for_conv(conv_id, copy_db=copy_dbs, suffix=f"_{experiment_name}")
                if pre_search_fn:
                    pre_search_fn(engine, conv_id)
                engines[conv_id] = engine
            except Exception as e:
                print(f"  Error loading engine for {conv_id}: {e}")
                results_log.append({
                    "question": question, "gold": gold, "conv_id": conv_id,
                    "category": category, "answer": "ERROR", "correct": False,
                    "error": str(e),
                })
                continue

        engine = engines[conv_id]

        # Search
        try:
            if search_fn:
                search_results = search_fn(engine, question, top_k, llm_fn)
            else:
                search_results = engine.search_agentic(
                    question, limit=top_k, llm_fn=llm_fn,
                    use_hyde=True, use_reranker=True, use_clustering=True,
                )
        except Exception as e:
            print(f"  Search error on q{i}: {e}")
            search_results = []

        # Format context and generate answer
        context = format_context(search_results)

        try:
            if answer_fn:
                answer = answer_fn(question, context)
            else:
                answer = generate_answer(question, context)
        except Exception as e:
            print(f"  Answer error on q{i}: {e}")
            answer = "Error generating answer"

        # Judge
        try:
            judgment = await judge_answer(question, gold, answer, num_runs=num_judge_runs)
            is_correct = judgment["correct"]
        except Exception as e:
            print(f"  Judge error on q{i}: {e}")
            is_correct = False

        if is_correct:
            correct_count += 1
            category_correct[category] += 1

        results_log.append({
            "question": question,
            "gold": gold,
            "conv_id": conv_id,
            "category": category,
            "answer": answer,
            "correct": is_correct,
            "context_preview": context[:200] if context else "",
            "num_results": len(search_results),
        })

        # Progress
        if (i + 1) % 25 == 0 or i == len(failures) - 1:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed
            print(f"  [{i+1}/{len(failures)}] {correct_count}/{i+1} correct "
                  f"({100*correct_count/(i+1):.1f}%) | {rate:.1f} q/s | {elapsed:.0f}s elapsed")

    t_total = time.time() - t_start

    # Compute final stats
    recovery_rate = correct_count / len(failures) * 100 if failures else 0

    # Estimated new LoCoMo score
    # Original: 1115 correct out of 1540 (72.34%)
    # If we recover X of the 357 failures: (1115 + X) / 1540
    estimated_total_correct = 1115 + correct_count
    estimated_score = estimated_total_correct / 1540 * 100

    print(f"\n{'='*70}")
    print(f"RESULTS: {experiment_name}")
    print(f"{'='*70}")
    print(f"Recovered: {correct_count}/{len(failures)} ({recovery_rate:.1f}%)")
    print(f"Estimated LoCoMo score: {estimated_score:.1f}% (was 72.3%)")
    print(f"EverMemOS target: 92.8%")
    print(f"Total time: {t_total:.0f}s ({t_total/60:.1f} min)")

    # Per-category breakdown
    print(f"\nPer-category recovery:")
    for cat in sorted(category_total.keys()):
        c = category_correct.get(cat, 0)
        t = category_total[cat]
        print(f"  Cat {cat}: {c}/{t} ({100*c/t:.1f}%)")

    # Save detailed results
    output_path = Path(f"/Users/j/Desktop/neuromem/experiment_results/{experiment_name}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "experiment": experiment_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "total_questions": len(failures),
            "correct": correct_count,
            "recovery_rate": recovery_rate,
            "estimated_locomo_score": estimated_score,
            "time_seconds": t_total,
            "category_breakdown": {
                cat: {"correct": category_correct.get(cat, 0), "total": category_total[cat]}
                for cat in sorted(category_total.keys())
            },
            "results": results_log,
        }, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")

    # Append to journal
    _append_journal(experiment_name, description, correct_count, len(failures),
                    recovery_rate, estimated_score, t_total, category_correct, category_total)

    # Clean up copied DBs
    if copy_dbs:
        for conv_id, engine in engines.items():
            try:
                engine.close()
            except:
                pass

    return {
        "correct": correct_count,
        "total": len(failures),
        "recovery_rate": recovery_rate,
        "estimated_score": estimated_score,
        "time": t_total,
        "category_correct": dict(category_correct),
        "category_total": dict(category_total),
    }


def _append_journal(name, desc, correct, total, rate, est_score, time_s, cat_correct, cat_total):
    """Append experiment results to the journal markdown."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M CT")

    entry = f"""
### Experiment: {name}
**Time**: {now}
**Duration**: {time_s:.0f}s ({time_s/60:.1f} min)
**Description**: {desc}

**Results**: {correct}/{total} recovered ({rate:.1f}%)
**Estimated LoCoMo**: {est_score:.1f}% (baseline 72.3%, target 92.8%)

| Category | Recovered | Total | Rate |
|----------|-----------|-------|------|
"""
    for cat in sorted(cat_total.keys()):
        c = cat_correct.get(cat, 0)
        t = cat_total[cat]
        entry += f"| Cat {cat} | {c} | {t} | {100*c/t:.1f}% |\n"

    entry += "\n---\n"

    with open(JOURNAL_PATH, "a") as f:
        f.write(entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Neuromem Experiment Harness")
    parser.add_argument("--experiment", required=True, help="Experiment name")
    parser.add_argument("--description", default="", help="What changed")
    parser.add_argument("--judge-runs", type=int, default=1, help="Number of judge runs")
    parser.add_argument("--top-k", type=int, default=15, help="Search top-k")
    parser.add_argument("--max-questions", type=int, default=0, help="Limit questions (0=all)")
    args = parser.parse_args()

    result = asyncio.run(run_experiment(
        experiment_name=args.experiment,
        description=args.description or args.experiment,
        num_judge_runs=args.judge_runs,
        top_k=args.top_k,
        max_questions=args.max_questions,
    ))
