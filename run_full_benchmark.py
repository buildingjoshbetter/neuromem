#!/usr/bin/env python3
"""
Full LoCoMo Benchmark Runner for Neuromem
==========================================

Runs the complete 1,540-question LoCoMo benchmark using the same methodology
as the v3 baseline (87.71% ± 0.33%).

Methodology:
    - Same 10 conversations, same 1,540 questions
    - Same search config: search_agentic(limit=100, use_hyde=True,
      use_reranker=True, use_clustering=True)
    - Same answer model: gpt-4.1-mini via OpenRouter (temperature=0)
    - Same judge model: gpt-4o-mini via OpenRouter (temperature=0)
    - Same answer prompt and judge prompt as test_harness.py
    - 3 judge runs per question (majority vote)
    - 3 independent full-pipeline runs for variance measurement

The ONLY change vs v3 baseline: the cross-encoder reranker model.
    v3 baseline: cross-encoder/ms-marco-MiniLM-L6-v2 (22M params)
    This run:    mixedbread-ai/mxbai-rerank-large-v1 (435M params)

Usage:
    python run_full_benchmark.py --run 1
    python run_full_benchmark.py --run 2
    python run_full_benchmark.py --run 3

Author: building_josh
Date: March 21, 2026
"""

import asyncio
import json
import os
import sys
import time
import argparse
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ── Environment setup ──────────────────────────────────────────────────────
# Load API keys from EverMemOS .env (same source as v3 baseline)
_env_path = Path("/Users/j/Desktop/neuromem/EverMemOS/.env")
if _env_path.exists():
    for line in open(_env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())

sys.path.insert(0, "/Users/j/Desktop/neuromem")

from neuromem.engine import NeuromemEngine

# ── Constants (identical to v3 baseline) ───────────────────────────────────
DB_DIR = Path("/Users/j/Desktop/neuromem/EverMemOS/evaluation/results/"
              "locomo-neuromem-fair-benchmark-20260318")
EVAL_RESULTS_PATH = DB_DIR / "eval_results.json"
OUTPUT_DIR = Path("/Users/j/Desktop/neuromem/experiment_results")

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://openrouter.ai/api/v1")
ANSWER_MODEL = "openai/gpt-4.1-mini"
JUDGE_MODEL = "openai/gpt-4o-mini"

# Search config (identical to v3 baseline)
TOP_K = 100
USE_HYDE = True
USE_RERANKER = True
USE_CLUSTERING = True
MAX_ROUNDS = 2

# Judge config
NUM_JUDGE_RUNS = 3  # Majority vote, same as v3 baseline


# ── LLM helpers (identical prompts to test_harness.py) ─────────────────────

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


def generate_answer(question: str, context: str) -> str:
    """Generate answer using structured prompt (identical to v3 baseline)."""
    import openai
    client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

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
        model=ANSWER_MODEL,
        max_tokens=500,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content


async def judge_answer(question: str, gold: str, generated: str) -> dict:
    """Judge answer using GPT-4o-mini with 3 runs (majority vote)."""
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    system_prompt = ("You are an expert grader that determines if answers "
                     "to questions match a gold standard answer")

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
    for _ in range(NUM_JUDGE_RUNS):
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
            json_match = re.search(
                r'\{[^{}]*"label"\s*:\s*"[^"]*"[^{}]*\}', content
            )
            if json_match:
                result = json.loads(json_match.group(0))
                judgments.append(
                    result.get("label", "").strip().upper() == "CORRECT"
                )
            else:
                judgments.append(False)
        except Exception as e:
            print(f"    Judge error: {e}")
            judgments.append(False)

    # Majority vote
    correct = sum(judgments) > len(judgments) / 2
    return {
        "judgments": judgments,
        "correct": correct,
        "votes": f"{sum(judgments)}/{len(judgments)}",
    }


def format_context(results: list) -> str:
    """Format search results into context string (identical to test_harness)."""
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


# ── Data loading ───────────────────────────────────────────────────────────

def load_all_questions() -> list[dict]:
    """Load all 1,540 questions from the eval results (same question set as v3)."""
    with open(EVAL_RESULTS_PATH) as f:
        eval_data = json.load(f)

    questions = []
    for conv_id, qa_list in eval_data["detailed_results"].items():
        for qa in qa_list:
            questions.append({
                "question_id": qa.get("question_id", ""),
                "question": qa["question"],
                "gold": str(qa["golden_answer"]),
                "category": str(qa["category"]),
                "conv_id": conv_id,
            })

    return questions


def get_engine(conv_id: str, engines_cache: dict) -> NeuromemEngine:
    """Get engine for a conversation (cached)."""
    if conv_id not in engines_cache:
        num = conv_id.split("_")[-1]
        db_name = f"neuromem_locomo_{num}.db"
        db_path = DB_DIR / db_name
        if not db_path.exists():
            raise FileNotFoundError(f"DB not found: {db_path}")
        engines_cache[conv_id] = NeuromemEngine(db_path=db_path).open()
    return engines_cache[conv_id]


# ── Main benchmark ─────────────────────────────────────────────────────────

async def run_benchmark(run_number: int):
    """Run the full 1,540-question benchmark."""
    experiment_name = f"phase0_reranker_mxbai_run{run_number}"
    checkpoint_path = OUTPUT_DIR / f"{experiment_name}_checkpoint.json"
    output_path = OUTPUT_DIR / f"{experiment_name}.json"

    print(f"\n{'='*70}")
    print(f"FULL LOCOMO BENCHMARK — Run {run_number}/3")
    print(f"{'='*70}")
    print(f"Reranker: mixedbread-ai/mxbai-rerank-large-v1 (435M params)")
    print(f"Search:   search_agentic(limit={TOP_K}, hyde={USE_HYDE}, "
          f"reranker={USE_RERANKER}, clustering={USE_CLUSTERING})")
    print(f"Answer:   {ANSWER_MODEL} (temperature=0, structured prompt)")
    print(f"Judge:    {JUDGE_MODEL} ({NUM_JUDGE_RUNS} runs, majority vote)")
    print(f"Questions: 1,540")
    print(f"Start:    {datetime.now().isoformat()}")
    print(f"{'='*70}\n")

    # Load questions
    all_questions = load_all_questions()
    print(f"Loaded {len(all_questions)} questions")

    # Resume from checkpoint if exists
    completed = {}
    if checkpoint_path.exists():
        with open(checkpoint_path) as f:
            checkpoint = json.load(f)
        completed = {r["question_id"]: r for r in checkpoint.get("results", [])}
        print(f"Resuming from checkpoint: {len(completed)} already done")

    # Initialize
    llm_fn = make_llm_fn()
    engines_cache = {}
    results_log = list(completed.values())
    correct_count = sum(1 for r in results_log if r.get("correct", False))

    t_start = time.time()
    api_errors = 0

    for i, q in enumerate(all_questions):
        qid = q["question_id"]

        # Skip if already done
        if qid in completed:
            continue

        question = q["question"]
        gold = q["gold"]
        conv_id = q["conv_id"]
        category = q["category"]

        # Get engine
        try:
            engine = get_engine(conv_id, engines_cache)
        except Exception as e:
            print(f"  ERROR loading DB for {conv_id}: {e}")
            results_log.append({
                "question_id": qid, "question": question, "gold": gold,
                "conv_id": conv_id, "category": category,
                "answer": "ERROR", "correct": False, "error": str(e),
            })
            continue

        # Search (same config as v3)
        try:
            search_results = engine.search_agentic(
                question, limit=TOP_K, llm_fn=llm_fn,
                use_hyde=USE_HYDE, use_reranker=USE_RERANKER,
                use_clustering=USE_CLUSTERING,
            )
        except Exception as e:
            print(f"  Search error on {qid}: {e}")
            search_results = []

        # Generate answer
        context = format_context(search_results)
        try:
            answer = generate_answer(question, context)
        except Exception as e:
            print(f"  Answer error on {qid}: {e}")
            answer = "Error generating answer"
            api_errors += 1

        # Judge (3 runs, majority vote)
        try:
            judgment = await judge_answer(question, gold, answer)
            is_correct = judgment["correct"]
            votes = judgment["votes"]
        except Exception as e:
            print(f"  Judge error on {qid}: {e}")
            is_correct = False
            votes = "0/0"
            api_errors += 1

        if is_correct:
            correct_count += 1

        result = {
            "question_id": qid,
            "question": question,
            "gold": gold,
            "conv_id": conv_id,
            "category": category,
            "answer": answer,
            "correct": is_correct,
            "judge_votes": votes,
            "num_results": len(search_results),
            "context_preview": context[:300] if context else "",
        }
        results_log.append(result)
        completed[qid] = result

        # Progress report every 50 questions
        done = len(completed)
        if done % 50 == 0 or done == len(all_questions):
            elapsed = time.time() - t_start
            rate = max(1, done - (len(completed) - (done - i))) / max(1, elapsed)
            accuracy = correct_count / done * 100
            remaining = len(all_questions) - done
            eta = remaining / rate / 60 if rate > 0 else 0
            print(f"  [{done}/{len(all_questions)}] "
                  f"{correct_count}/{done} correct ({accuracy:.1f}%) | "
                  f"{rate:.2f} q/s | ETA: {eta:.0f} min | "
                  f"errors: {api_errors}")

        # Checkpoint every 100 questions
        if done % 100 == 0:
            with open(checkpoint_path, "w") as f:
                json.dump({"results": results_log, "timestamp": time.time()}, f)

    # ── Final results ──────────────────────────────────────────────────────
    t_total = time.time() - t_start
    total = len(results_log)
    accuracy = correct_count / total * 100 if total else 0

    # Per-category breakdown
    cat_correct = defaultdict(int)
    cat_total = defaultdict(int)
    for r in results_log:
        cat = r["category"]
        cat_total[cat] += 1
        if r.get("correct"):
            cat_correct[cat] += 1

    print(f"\n{'='*70}")
    print(f"RESULTS — Run {run_number}")
    print(f"{'='*70}")
    print(f"Overall: {correct_count}/{total} ({accuracy:.2f}%)")
    print(f"Time: {t_total:.0f}s ({t_total/60:.1f} min)")
    print(f"API errors: {api_errors}")
    print()
    print(f"Per-category:")
    for cat in sorted(cat_total.keys()):
        c = cat_correct[cat]
        t = cat_total[cat]
        pct = c / t * 100 if t else 0
        print(f"  Cat {cat}: {c}/{t} ({pct:.1f}%)")
    print()
    print(f"Comparison:")
    print(f"  v3 baseline:  87.71% ± 0.33%")
    print(f"  This run:     {accuracy:.2f}%")
    print(f"  Delta:        {accuracy - 87.71:+.2f}pp")
    print(f"  EverMemOS:    92.77%")
    print(f"{'='*70}")

    # Save final results
    final = {
        "experiment": experiment_name,
        "run_number": run_number,
        "reranker_model": "mixedbread-ai/mxbai-rerank-large-v1",
        "reranker_params": "435M",
        "baseline_reranker": "cross-encoder/ms-marco-MiniLM-L6-v2",
        "baseline_params": "22M",
        "search_config": {
            "top_k": TOP_K,
            "use_hyde": USE_HYDE,
            "use_reranker": USE_RERANKER,
            "use_clustering": USE_CLUSTERING,
            "max_rounds": MAX_ROUNDS,
        },
        "answer_model": ANSWER_MODEL,
        "judge_model": JUDGE_MODEL,
        "num_judge_runs": NUM_JUDGE_RUNS,
        "total_questions": total,
        "correct": correct_count,
        "accuracy": accuracy,
        "category_results": {
            cat: {"correct": cat_correct[cat], "total": cat_total[cat],
                  "accuracy": cat_correct[cat] / cat_total[cat] * 100}
            for cat in sorted(cat_total.keys())
        },
        "v3_baseline": {
            "accuracy": 87.71,
            "std": 0.33,
            "runs": [87.38, 87.84, 87.99],
        },
        "evermemos": {"accuracy": 92.77},
        "delta_vs_v3": accuracy - 87.71,
        "delta_vs_evermemos": accuracy - 92.77,
        "elapsed_seconds": t_total,
        "api_errors": api_errors,
        "timestamp": datetime.now().isoformat(),
        "detailed_results": results_log,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(final, f, indent=2)

    print(f"\nResults saved to: {output_path}")

    # Clean up checkpoint
    if checkpoint_path.exists():
        checkpoint_path.unlink()

    return final


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Full LoCoMo benchmark for Neuromem reranker upgrade"
    )
    parser.add_argument(
        "--run", type=int, required=True, choices=[1, 2, 3],
        help="Run number (1, 2, or 3)"
    )
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.run))
