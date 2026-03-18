"""
Two-phase scorer for v3 benchmark.

Phase A: Raw Retrieval Scoring
  - Does the retrieved context contain the facts needed to answer?
  - Scored by Claude API: HIT (2) / PARTIAL (1) / MISS (0)

Phase B: Retrieval + LLM Synthesis
  - Feed retrieved context + query to Claude Sonnet 4.5
  - Score the LLM's answer against expected answer
  - Same HIT/PARTIAL/MISS rubric

Usage:
    python scorer.py results/chromadb_raw.json
    python scorer.py results/chromadb_raw.json --phase-a-only
    python scorer.py --all  # Score all raw results in results/
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: pip install anthropic")
    sys.exit(1)

V3_DIR = Path(__file__).parent
RESULTS_DIR = V3_DIR / "results"

# Scoring model — fixed for all systems
SCORING_MODEL = "claude-sonnet-4-5-20250929"
SYNTHESIS_MODEL = "claude-sonnet-4-5-20250929"


def get_client() -> anthropic.Anthropic:
    """Get Anthropic client."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY environment variable")
    return anthropic.Anthropic(api_key=api_key)


def score_phase_a(client: anthropic.Anthropic, query: dict, retrieved: list[dict]) -> dict:
    """
    Phase A: Score raw retrieval quality.
    Does the retrieved context contain enough information to answer the query?
    """
    context_text = "\n\n".join(
        f"[Result {i+1}] (score: {r.get('score', 'N/A')})\n{r['content']}"
        for i, r in enumerate(retrieved[:10])
    )

    if not context_text.strip():
        return {"score": 0, "label": "MISS", "reason": "No results retrieved"}

    prompt = f"""You are scoring a memory system's retrieval quality.

QUERY: {query['query']}

EXPECTED ANSWER: {query['expected']}

SCORING CRITERIA: {query['scoring_notes']}
{f"HIT CRITERIA: {query['hit_criteria']}" if query.get('hit_criteria') else ""}
{f"PARTIAL CRITERIA: {query['partial_criteria']}" if query.get('partial_criteria') else ""}

RETRIEVED CONTEXT:
{context_text}

Does the retrieved context contain enough information to answer the query correctly?

Score as:
- HIT (2 points): The retrieved context contains all or nearly all the key facts needed.
- PARTIAL (1 point): The retrieved context contains some relevant facts but is incomplete.
- MISS (0 points): The retrieved context is irrelevant or contains none of the needed facts.

Respond with EXACTLY this JSON format:
{{"score": 0|1|2, "label": "MISS"|"PARTIAL"|"HIT", "reason": "brief explanation"}}"""

    try:
        response = client.messages.create(
            model=SCORING_MODEL,
            max_tokens=200,
            temperature=0.0,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Parse JSON from response
        if "{" in text:
            json_str = text[text.index("{"):text.rindex("}") + 1]
            result = json.loads(json_str)
            return {
                "score": int(result["score"]),
                "label": result["label"],
                "reason": result.get("reason", ""),
            }
    except Exception as e:
        return {"score": 0, "label": "ERROR", "reason": str(e)}

    return {"score": 0, "label": "ERROR", "reason": "Could not parse scoring response"}


def score_phase_b(client: anthropic.Anthropic, query: dict, retrieved: list[dict]) -> dict:
    """
    Phase B: Score retrieval + LLM synthesis.
    Feed context to Claude, get an answer, then score the answer.
    """
    context_text = "\n\n".join(
        f"[Memory {i+1}]\n{r['content']}"
        for i, r in enumerate(retrieved[:10])
    )

    if not context_text.strip():
        return {
            "score": 0,
            "label": "MISS",
            "reason": "No context to synthesize from",
            "llm_answer": "",
        }

    # Step 1: Get LLM answer from context
    synthesis_prompt = f"""You are an AI assistant with access to stored memories about a user named Jordan Chen.
Use ONLY the retrieved memories below to answer the question. If the memories don't contain enough information, say so.

RETRIEVED MEMORIES:
{context_text}

QUESTION: {query['query']}

Answer concisely based only on the memories above."""

    try:
        synth_response = client.messages.create(
            model=SYNTHESIS_MODEL,
            max_tokens=500,
            temperature=0.0,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        llm_answer = synth_response.content[0].text.strip()
    except Exception as e:
        return {
            "score": 0,
            "label": "ERROR",
            "reason": f"Synthesis failed: {e}",
            "llm_answer": "",
        }

    # Step 2: Score the answer
    scoring_prompt = f"""You are scoring an AI's answer about a user named Jordan Chen.

QUERY: {query['query']}

EXPECTED ANSWER: {query['expected']}

SCORING CRITERIA: {query['scoring_notes']}
{f"HIT CRITERIA: {query['hit_criteria']}" if query.get('hit_criteria') else ""}
{f"PARTIAL CRITERIA: {query['partial_criteria']}" if query.get('partial_criteria') else ""}

AI'S ANSWER: {llm_answer}

Score the AI's answer:
- HIT (2 points): Answer contains all or nearly all key facts from the expected answer.
- PARTIAL (1 point): Answer contains some correct facts but misses important details.
- MISS (0 points): Answer is wrong, irrelevant, or says it can't answer when it should be able to.

Respond with EXACTLY this JSON format:
{{"score": 0|1|2, "label": "MISS"|"PARTIAL"|"HIT", "reason": "brief explanation"}}"""

    try:
        score_response = client.messages.create(
            model=SCORING_MODEL,
            max_tokens=200,
            temperature=0.0,
            messages=[{"role": "user", "content": scoring_prompt}],
        )
        text = score_response.content[0].text.strip()
        if "{" in text:
            json_str = text[text.index("{"):text.rindex("}") + 1]
            result = json.loads(json_str)
            return {
                "score": int(result["score"]),
                "label": result["label"],
                "reason": result.get("reason", ""),
                "llm_answer": llm_answer,
            }
    except Exception as e:
        return {
            "score": 0,
            "label": "ERROR",
            "reason": str(e),
            "llm_answer": llm_answer,
        }

    return {
        "score": 0,
        "label": "ERROR",
        "reason": "Could not parse scoring response",
        "llm_answer": llm_answer,
    }


def score_results_file(raw_path: Path, phase_a_only: bool = False) -> dict:
    """Score all results in a raw results file."""
    with open(raw_path) as f:
        raw = json.load(f)

    if raw.get("status") != "COMPLETED":
        print(f"  Skipping {raw_path.name} — status: {raw.get('status', 'unknown')}")
        return raw

    system_name = raw["system"]
    results = raw["results"]

    print(f"\n{'=' * 60}")
    print(f"SCORING: {system_name} ({len(results)} queries)")
    print(f"{'=' * 60}")

    client = get_client()

    scored_results = []
    phase_a_total = 0
    phase_b_total = 0
    phase_a_by_cat = {}
    phase_b_by_cat = {}

    for i, q in enumerate(results):
        cat = q["category"]
        retrieved = q.get("results", [])

        # Phase A
        print(f"  Q{q['query_id']:2d} [{cat:25s}] ", end="", flush=True)
        phase_a = score_phase_a(client, q, retrieved)
        phase_a_total += phase_a["score"]

        if cat not in phase_a_by_cat:
            phase_a_by_cat[cat] = {"total": 0, "max": 0, "hits": 0, "partials": 0, "misses": 0}
        phase_a_by_cat[cat]["total"] += phase_a["score"]
        phase_a_by_cat[cat]["max"] += 2
        if phase_a["label"] == "HIT":
            phase_a_by_cat[cat]["hits"] += 1
        elif phase_a["label"] == "PARTIAL":
            phase_a_by_cat[cat]["partials"] += 1
        else:
            phase_a_by_cat[cat]["misses"] += 1

        scored_q = {**q, "phase_a": phase_a}
        print(f"A:{phase_a['label']:7s}", end="", flush=True)

        # Phase B
        if not phase_a_only:
            phase_b = score_phase_b(client, q, retrieved)
            phase_b_total += phase_b["score"]

            if cat not in phase_b_by_cat:
                phase_b_by_cat[cat] = {"total": 0, "max": 0, "hits": 0, "partials": 0, "misses": 0}
            phase_b_by_cat[cat]["total"] += phase_b["score"]
            phase_b_by_cat[cat]["max"] += 2
            if phase_b["label"] == "HIT":
                phase_b_by_cat[cat]["hits"] += 1
            elif phase_b["label"] == "PARTIAL":
                phase_b_by_cat[cat]["partials"] += 1
            else:
                phase_b_by_cat[cat]["misses"] += 1

            scored_q["phase_b"] = phase_b
            print(f" | B:{phase_b['label']:7s}", end="")

        scored_results.append(scored_q)
        print()

        # Rate limit: ~0.5s between API calls
        time.sleep(0.3)

    # Compute overall scores
    max_score = len(results) * 2
    phase_a_pct = (phase_a_total / max_score * 100) if max_score > 0 else 0
    phase_b_pct = (phase_b_total / max_score * 100) if max_score > 0 else 0

    scored_output = {
        **raw,
        "scoring": {
            "scoring_model": SCORING_MODEL,
            "synthesis_model": SYNTHESIS_MODEL,
            "phase_a": {
                "total_score": phase_a_total,
                "max_score": max_score,
                "percentage": round(phase_a_pct, 1),
                "by_category": phase_a_by_cat,
            },
        },
        "results": scored_results,
    }

    if not phase_a_only:
        scored_output["scoring"]["phase_b"] = {
            "total_score": phase_b_total,
            "max_score": max_score,
            "percentage": round(phase_b_pct, 1),
            "by_category": phase_b_by_cat,
        }

    # Save scored results
    scored_path = raw_path.parent / raw_path.name.replace("_raw", "_scored")
    with open(scored_path, "w") as f:
        json.dump(scored_output, f, indent=2)

    # Print summary
    print(f"\n{'=' * 60}")
    print(f"SCORES: {system_name}")
    print(f"{'=' * 60}")
    print(f"  Phase A (Raw Retrieval): {phase_a_total}/{max_score} ({phase_a_pct:.1f}%)")
    if not phase_a_only:
        print(f"  Phase B (LLM Synthesis): {phase_b_total}/{max_score} ({phase_b_pct:.1f}%)")

    print(f"\n  Phase A by category:")
    for cat in sorted(phase_a_by_cat.keys()):
        c = phase_a_by_cat[cat]
        pct = (c["total"] / c["max"] * 100) if c["max"] > 0 else 0
        print(f"    {cat:30s} {c['total']:2d}/{c['max']:2d} ({pct:5.1f}%) "
              f"H:{c['hits']} P:{c['partials']} M:{c['misses']}")

    if not phase_a_only:
        print(f"\n  Phase B by category:")
        for cat in sorted(phase_b_by_cat.keys()):
            c = phase_b_by_cat[cat]
            pct = (c["total"] / c["max"] * 100) if c["max"] > 0 else 0
            print(f"    {cat:30s} {c['total']:2d}/{c['max']:2d} ({pct:5.1f}%) "
                  f"H:{c['hits']} P:{c['partials']} M:{c['misses']}")

    print(f"\n  Saved to: {scored_path}")
    return scored_output


def generate_scorecard(results_dir: Path = RESULTS_DIR) -> str:
    """Generate a markdown scorecard from all scored results."""
    scored_files = sorted(results_dir.glob("*_scored*.json"))
    if not scored_files:
        return "No scored results found."

    systems = []
    for f in scored_files:
        with open(f) as fh:
            data = json.load(fh)
        if "scoring" not in data:
            continue
        systems.append(data)

    # Sort by Phase B score if available, else Phase A
    systems.sort(
        key=lambda s: s["scoring"].get("phase_b", s["scoring"]["phase_a"])["percentage"],
        reverse=True,
    )

    lines = [
        "# V3 Benchmark Results",
        "",
        f"**Systems tested:** {len(systems)}",
        "",
        "## Overall Scores",
        "",
        "| Rank | System | Phase A (Retrieval) | Phase B (Synthesis) | Avg Query (ms) |",
        "|------|--------|-------------------|-------------------|----------------|",
    ]

    for i, s in enumerate(systems):
        pa = s["scoring"]["phase_a"]
        pb = s["scoring"].get("phase_b", {"percentage": "N/A"})
        avg_ms = s.get("timing", {}).get("avg_query_ms", "N/A")
        pa_str = f"{pa['percentage']:.1f}%"
        pb_str = f"{pb['percentage']:.1f}%" if isinstance(pb.get("percentage"), (int, float)) else "N/A"
        lines.append(f"| {i+1} | **{s['system']}** | {pa_str} | {pb_str} | {avg_ms} |")

    # Category breakdown
    all_categories = set()
    for s in systems:
        cats = s["scoring"]["phase_a"].get("by_category", {})
        all_categories.update(cats.keys())

    if all_categories:
        lines.extend([
            "",
            "## Phase A — By Category",
            "",
        ])
        header = "| Category |" + "|".join(f" {s['system']} " for s in systems) + "|"
        sep = "|----------|" + "|".join("---" for _ in systems) + "|"
        lines.extend([header, sep])

        for cat in sorted(all_categories):
            row = f"| {cat} |"
            for s in systems:
                cats = s["scoring"]["phase_a"].get("by_category", {})
                if cat in cats:
                    c = cats[cat]
                    pct = (c["total"] / c["max"] * 100) if c["max"] > 0 else 0
                    row += f" {pct:.0f}% |"
                else:
                    row += " — |"
            lines.append(row)

    scorecard = "\n".join(lines)

    scorecard_path = results_dir.parent / "BENCHMARK_RESULTS.md"
    with open(scorecard_path, "w") as f:
        f.write(scorecard)
    print(f"\nScorecard saved to: {scorecard_path}")

    return scorecard


def main():
    parser = argparse.ArgumentParser(description="V3 Benchmark Scorer")
    parser.add_argument("results_file", nargs="?", help="Path to raw results JSON")
    parser.add_argument("--phase-a-only", action="store_true", help="Only run Phase A scoring")
    parser.add_argument("--all", action="store_true", help="Score all raw results in results/")
    parser.add_argument("--scorecard", action="store_true", help="Generate scorecard from scored results")
    args = parser.parse_args()

    if args.scorecard:
        scorecard = generate_scorecard()
        print(scorecard)
        return

    if args.all:
        raw_files = sorted(RESULTS_DIR.glob("*_raw*.json"))
        if not raw_files:
            print("No raw results found in results/")
            return
        for raw_path in raw_files:
            # Skip if already scored
            scored_path = raw_path.parent / raw_path.name.replace("_raw", "_scored")
            if scored_path.exists():
                print(f"  Already scored: {raw_path.name} → {scored_path.name}")
                continue
            score_results_file(raw_path, phase_a_only=args.phase_a_only)
        generate_scorecard()
        return

    if args.results_file:
        raw_path = Path(args.results_file)
        if not raw_path.exists():
            print(f"File not found: {raw_path}")
            sys.exit(1)
        score_results_file(raw_path, phase_a_only=args.phase_a_only)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
