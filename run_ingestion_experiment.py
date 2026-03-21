#!/usr/bin/env python3
"""
Ingestion Experiment: Rich Multi-Pass Extraction
================================================
Rebuilds Neuromem DBs with the rich extraction pipeline, then tests
against the 357 failure questions.

This is the highest-impact experiment — EverMemOS's advantage comes
from rich extraction (17 LLM prompts per message). We're building
an equivalently rich pipeline for Neuromem.

Usage:
    python run_ingestion_experiment.py --passes episode,qa,temporal,relationship
    python run_ingestion_experiment.py --passes episode,qa  --max-q 50
    python run_ingestion_experiment.py --model claude-sonnet-4-5-20250929  # Use Sonnet for extraction
"""

import asyncio
import json
import os
import sys
import time
import sqlite3
import tempfile
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

from neuromem.engine import NeuromemEngine
from neuromem.rich_extraction import rich_extract
from test_harness import (
    run_experiment, load_failures, format_context, generate_answer,
    judge_answer, make_llm_fn, _append_journal,
    LLM_API_KEY, LLM_BASE_URL, ANSWER_MODEL, JOURNAL_PATH
)


# ── Paths ──
LOCOMO_DATA = Path("/Users/j/Desktop/neuromem/EverMemOS/evaluation/data/locomo/locomo10.json")
RESULTS_DIR = Path("/Users/j/Desktop/neuromem/EverMemOS/evaluation/results/locomo-neuromem-fair-benchmark-20260318")
EXPERIMENT_DB_DIR = Path("/tmp/nm_rich_extraction")


def load_locomo_conversations():
    """Load LoCoMo 10 conversations."""
    with open(LOCOMO_DATA) as f:
        data = json.load(f)
    return data


def make_extraction_llm_fn(model: str = "claude-haiku-4-5-20251001", provider: str = "anthropic"):
    """Create LLM function for extraction."""
    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic()

        def _call(prompt: str) -> str:
            resp = client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.content[0].text
        return _call
    else:
        import openai
        client = openai.OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

        def _call(prompt: str) -> str:
            resp = client.chat.completions.create(
                model=model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content
        return _call


def rebuild_db_with_rich_extraction(
    conv_id: str,
    conv_data: dict,
    extraction_llm_fn,
    passes: list[str],
    db_dir: Path,
) -> Path:
    """
    Rebuild a Neuromem DB with rich extraction for a single conversation.

    Steps:
    1. Load raw messages from LoCoMo data
    2. Create engine and ingest raw messages
    3. Run rich extraction passes
    4. Insert extracted documents
    5. Rebuild vectors

    Returns path to the new DB.
    """
    # Convert LoCoMo messages to Neuromem format
    # LoCoMo format: conversation dict with session_1..session_N keys,
    # each session is a list of {speaker, dia_id, text} dicts
    # Plus session_N_date_time keys for timestamps
    messages = []
    conv = conv_data.get("conversation", {})
    speaker_a = conv.get("speaker_a", "Speaker A")
    speaker_b = conv.get("speaker_b", "Speaker B")

    # Collect all sessions
    session_keys = sorted(
        [k for k in conv.keys() if k.startswith("session_") and not k.endswith("_date_time")],
        key=lambda x: int(x.split("_")[1])
    )

    for session_key in session_keys:
        session_msgs = conv.get(session_key, [])
        if not isinstance(session_msgs, list):
            continue
        session_date = conv.get(f"{session_key}_date_time", "")

        for msg in session_msgs:
            sender = msg.get("speaker", "")
            text = msg.get("text", "")
            if not text:
                continue

            recipient = speaker_b if sender == speaker_a else speaker_a
            messages.append({
                "content": text,
                "sender": sender,
                "recipient": recipient,
                "timestamp": session_date,
                "category": session_key,
                "modality": "conversation",
            })

    # Create engine and ingest
    db_path = db_dir / f"neuromem_{conv_id}.db"
    if db_path.exists():
        db_path.unlink()

    # Write messages to temp JSON
    tmp_json = Path(tempfile.mktemp(suffix=".json"))
    with open(tmp_json, "w") as f:
        json.dump(messages, f)

    engine = NeuromemEngine(db_path=db_path)
    engine.ingest(tmp_json)
    tmp_json.unlink(missing_ok=True)

    # Run rich extraction
    t0 = time.time()
    extracted = rich_extract(
        messages=messages,
        llm_fn=extraction_llm_fn,
        speaker_a=speaker_a,
        speaker_b=speaker_b,
        passes=passes,
    )
    extract_time = time.time() - t0

    # Insert extracted documents
    if extracted and engine.conn:
        for doc in extracted:
            engine.conn.execute(
                """INSERT INTO messages
                   (content, sender, recipient, timestamp, category, modality)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    doc["content"],
                    doc.get("sender", "system"),
                    doc.get("recipient", ""),
                    doc.get("timestamp", ""),
                    doc.get("category", ""),
                    doc.get("modality", "extracted"),
                ),
            )
        engine.conn.commit()

        # Rebuild vectors to include new documents
        try:
            from neuromem.vector_search import init_vec_table, build_vectors
            init_vec_table(engine.conn)
            build_vectors(engine.conn)
        except Exception as e:
            print(f"    Warning: Vector rebuild failed: {e}")

    episode_count = sum(1 for d in extracted if d.get("modality") == "episode")
    fact_count = sum(1 for d in extracted if d.get("modality") == "fact")
    qa_count = sum(1 for d in extracted if d.get("modality") == "qa_pair")
    temporal_count = sum(1 for d in extracted if d.get("modality") == "temporal_fact")
    rel_count = sum(1 for d in extracted if d.get("modality") == "relationship")
    entity_count = sum(1 for d in extracted if d.get("modality") == "entity")

    total_msgs = engine.conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0] if engine.conn else 0
    print(f"    {conv_id}: {len(messages)} raw + {len(extracted)} extracted = {total_msgs} total "
          f"({episode_count} episodes, {fact_count} facts, {qa_count} QA, "
          f"{temporal_count} temporal, {rel_count} relationships, {entity_count} entities) "
          f"in {extract_time:.1f}s")

    engine.close()
    return db_path


async def run_rich_extraction_experiment(
    experiment_name: str,
    passes: list[str],
    extraction_model: str = "claude-haiku-4-5-20251001",
    extraction_provider: str = "anthropic",
    answer_model: str = None,
    answer_fn=None,
    search_fn=None,
    max_questions: int = 0,
    num_judge_runs: int = 1,
    top_k: int = 15,
    rebuild_dbs: bool = True,
):
    """
    Full ingestion experiment:
    1. Rebuild DBs with rich extraction (if rebuild_dbs)
    2. Test against 357 failures
    """
    print(f"\n{'='*70}")
    print(f"INGESTION EXPERIMENT: {experiment_name}")
    print(f"Extraction passes: {passes}")
    print(f"Extraction model: {extraction_provider}/{extraction_model}")
    print(f"{'='*70}\n")

    db_dir = EXPERIMENT_DB_DIR / experiment_name
    db_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Rebuild DBs
    if rebuild_dbs:
        print("Step 1: Rebuilding DBs with rich extraction...")
        t_start = time.time()

        # Load LoCoMo data
        locomo_data = load_locomo_conversations()
        extraction_llm_fn = make_extraction_llm_fn(extraction_model, extraction_provider)

        for i, conv_data in enumerate(locomo_data):
            conv_id = f"locomo_{i}"
            try:
                rebuild_db_with_rich_extraction(
                    conv_id=conv_id,
                    conv_data=conv_data,
                    extraction_llm_fn=extraction_llm_fn,
                    passes=passes,
                    db_dir=db_dir,
                )
            except Exception as e:
                print(f"    ERROR rebuilding {conv_id}: {e}")

        rebuild_time = time.time() - t_start
        print(f"\nDB rebuild complete in {rebuild_time:.0f}s ({rebuild_time/60:.1f} min)")

    # Step 2: Test against failures
    print("\nStep 2: Testing against failure questions...")

    failures = load_failures()
    if max_questions > 0:
        failures = failures[:max_questions]

    llm_fn = make_llm_fn()
    t_start = time.time()

    engines = {}
    correct_count = 0
    category_correct = defaultdict(int)
    category_total = defaultdict(int)
    results_log = []

    for i, failure in enumerate(failures):
        question = failure["question"]
        gold = failure["gold"]
        conv_id = failure["conv_id"]
        category = failure["category"]
        category_total[category] += 1

        # Get engine (map conv_id to db)
        if conv_id not in engines:
            try:
                num = conv_id.split("_")[-1]
                db_path = db_dir / f"neuromem_locomo_{num}.db"
                if not db_path.exists():
                    # Fall back to original DB
                    db_path = RESULTS_DIR / f"neuromem_locomo_{num}.db"
                engine = NeuromemEngine(db_path=db_path).open()
                engines[conv_id] = engine
            except Exception as e:
                print(f"  Error loading engine for {conv_id}: {e}")
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
            search_results = []

        # Answer
        context = format_context(search_results)
        try:
            if answer_fn:
                answer = answer_fn(question, context)
            else:
                answer = generate_answer(question, context)
        except Exception as e:
            answer = "Error"

        # Judge
        try:
            judgment = await judge_answer(question, gold, answer, num_runs=num_judge_runs)
            is_correct = judgment["correct"]
        except Exception:
            is_correct = False

        if is_correct:
            correct_count += 1
            category_correct[category] += 1

        results_log.append({
            "question": question, "gold": gold, "conv_id": conv_id,
            "category": category, "answer": answer, "correct": is_correct,
            "num_results": len(search_results),
        })

        if (i + 1) % 25 == 0 or i == len(failures) - 1:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  [{i+1}/{len(failures)}] {correct_count}/{i+1} correct "
                  f"({100*correct_count/(i+1):.1f}%) | {rate:.1f} q/s | {elapsed:.0f}s")

    t_total = time.time() - t_start
    recovery_rate = correct_count / len(failures) * 100 if failures else 0
    estimated_score = (1115 + correct_count) / 1540 * 100

    print(f"\n{'='*70}")
    print(f"RESULTS: {experiment_name}")
    print(f"{'='*70}")
    print(f"Recovered: {correct_count}/{len(failures)} ({recovery_rate:.1f}%)")
    print(f"Estimated LoCoMo: {estimated_score:.1f}%")
    print(f"Time: {t_total:.0f}s")

    for cat in sorted(category_total.keys()):
        c = category_correct.get(cat, 0)
        t = category_total[cat]
        print(f"  Cat {cat}: {c}/{t} ({100*c/t:.1f}%)")

    # Save results
    output_path = Path(f"/Users/j/Desktop/neuromem/experiment_results/{experiment_name}.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({
            "experiment": experiment_name,
            "passes": passes,
            "extraction_model": extraction_model,
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

    _append_journal(experiment_name, f"Rich extraction [{','.join(passes)}] with {extraction_model}",
                    correct_count, len(failures), recovery_rate, estimated_score, t_total,
                    category_correct, category_total)

    return {
        "correct": correct_count,
        "total": len(failures),
        "recovery_rate": recovery_rate,
        "estimated_score": estimated_score,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--passes", default="episode,qa,temporal,relationship",
                        help="Comma-separated extraction passes")
    parser.add_argument("--extraction-model", default="claude-haiku-4-5-20251001")
    parser.add_argument("--extraction-provider", default="anthropic")
    parser.add_argument("--max-q", type=int, default=0, help="Max questions (0=all 357)")
    parser.add_argument("--judge-runs", type=int, default=1)
    parser.add_argument("--top-k", type=int, default=15)
    parser.add_argument("--name", default=None, help="Experiment name override")
    parser.add_argument("--no-rebuild", action="store_true", help="Skip DB rebuild")
    args = parser.parse_args()

    passes = [p.strip() for p in args.passes.split(",")]
    name = args.name or f"rich_{'+'.join(passes)}_{args.extraction_model.split('/')[-1]}"

    asyncio.run(run_rich_extraction_experiment(
        experiment_name=name,
        passes=passes,
        extraction_model=args.extraction_model,
        extraction_provider=args.extraction_provider,
        max_questions=args.max_q,
        num_judge_runs=args.judge_runs,
        top_k=args.top_k,
        rebuild_dbs=not args.no_rebuild,
    ))
