# Fair LoCoMo Benchmark — Final Results

## Run: fair-benchmark-20260318
**Started:** 2026-03-18 13:29 CT
**Completed:** 2026-03-18 15:07 CT
**Run Name:** fair-benchmark-20260318

## Final Results

| System | J-Score (mean +/- std) | Cat 1 (single_hop) | Cat 2 (multi_hop) | Cat 3 (temporal) | Cat 4 (open_domain) |
|--------|----------------------|---------------------|--------------------|--------------------|----------------------|
| No-Retrieval | **5.67% +/- 0.04%** | 2.1% (6/282) | 0.9% (3/321) | 13.5% (13/96) | 7.6% (64/841) |
| **Neuromem** | **72.34% +/- 0.06%** | 59.2% (167/282) | 72.9% (234/321) | 52.1% (50/96) | 79.0% (664/841) |
| **EverMemOS** | **92.77% +/- 0.10%** | 91.1% (257/282) | 89.4% (287/321) | 78.1% (75/96) | 96.2% (809/841) |

### Gap Analysis

| Category | EverMemOS | Neuromem | Gap | Notes |
|----------|-----------|----------|-----|-------|
| Overall | 92.77% | 72.34% | -20.43 pp | Significant gap |
| Cat 1 (single_hop) | 91.1% | 59.2% | -31.9 pp | Largest gap — basic fact retrieval |
| Cat 2 (multi_hop) | 89.4% | 72.9% | -16.5 pp | Multi-evidence reasoning |
| Cat 3 (temporal) | 78.1% | 52.1% | -26.0 pp | Temporal is hardest for both |
| Cat 4 (open_domain) | 96.2% | 79.0% | -17.2 pp | EverMemOS near-perfect |

### Per-Run Stability (3 independent judge runs, temp=0)

| System | Run 1 | Run 2 | Run 3 | Std |
|--------|-------|-------|-------|-----|
| No-Retrieval | 5.65% | 5.65% | 5.71% | 0.04% |
| Neuromem | 72.27% | 72.40% | 72.34% | 0.06% |
| EverMemOS | 92.86% | 92.66% | 92.79% | 0.10% |

### Runtime

| System | Total Time | Add | Search | Answer | Evaluate |
|--------|-----------|-----|--------|--------|----------|
| No-Retrieval | 374s (~6 min) | instant | instant | ~2 min | ~4 min |
| Neuromem | 515s (~9 min) | ~40s | ~51s | ~168s (9.2 qa/s) | ~255s |
| EverMemOS | 5879s (~98 min) | ~55 min | ~27 min | ~9 min | ~5 min |

## Configuration (Fairness Verification)

| Variable | EverMemOS | Neuromem | No-Retrieval |
|----------|-----------|----------|-------------|
| Answer model | openai/gpt-4.1-mini | openai/gpt-4.1-mini | openai/gpt-4.1-mini |
| Judge model | gpt-4o-mini | gpt-4o-mini | gpt-4o-mini |
| Judge runs | 3 | 3 | 3 |
| Judge temp | 0 | 0 | 0 |
| Dataset | LoCoMo 10 convs | LoCoMo 10 convs | LoCoMo 10 convs |
| Cat 5 filter | Yes (excluded) | Yes (excluded) | Yes (excluded) |
| Total Qs | 1540 | 1540 | 1540 |

## Observations

1. **EverMemOS reproduces its published score**: 92.77% vs published 92.3% — validates our setup is fair and correct.

2. **No-retrieval floor is extremely low (5.67%)**: Confirms LoCoMo questions genuinely require memory retrieval. No knowledge leakage concern.

3. **Neuromem has a significant 20-point gap** vs EverMemOS. The gap is largest on single-hop (32 pp) and temporal (26 pp) categories.

4. **Temporal reasoning (Cat 3) is hardest for both systems**: EverMemOS 78.1%, Neuromem 52.1%. This is the only category where EverMemOS drops below 89%.

5. **Neuromem's strengths**: Open-domain (79%) and multi-hop (72.9%) are its best categories, likely because episode extraction + agentic search helps gather broad context. But still ~17 pp behind EverMemOS.

6. **Neuromem is 10x faster**: Total runtime 515s vs 5879s. Most of EverMemOS's time is spent on MemCell extraction (17 LLM prompts per message).

7. **Both systems are highly consistent**: All std deviations < 0.10%, showing the GPT-4o-mini judge at temp=0 is extremely deterministic.

## Possible Neuromem Improvement Areas

1. **Single-hop retrieval (Cat 1: 59.2%)**: Basic fact lookup is failing 41% of the time. EverMemOS's 17-prompt extraction (scene detection, sentiment, themes, event logs) creates much richer searchable content. Neuromem's episode extraction only generates narrative summaries — may miss specific details.

2. **Temporal reasoning (Cat 3: 52.1%)**: Both systems struggle here, but Neuromem more so. The episode extraction includes timestamps, but the search may not be resolving temporal queries well (e.g., "what happened before X" or "in which month did Y").

3. **Context formatting**: EverMemOS uses structured MemCells with rich metadata (subjects, participants, timestamps, event logs). Neuromem sends raw messages + episode narratives. The answer LLM may find MemCells easier to work with.

4. **Retrieval depth**: EverMemOS's agentic retrieval does BM25+embedding hybrid → sufficiency check → multi-query refinement → reranking. Neuromem does HyDE + hybrid search + reranking. EverMemOS's approach may be more thorough at finding relevant evidence.

## Results Directories

- No-Retrieval: `evaluation/results/locomo-no_retrieval-fair-benchmark-20260318/`
- Neuromem: `evaluation/results/locomo-neuromem-fair-benchmark-20260318/`
- EverMemOS: `evaluation/results/locomo-evermemos-fair-benchmark-20260318/`

---

## Prompt Fairness Audit (2026-03-18, evening)

### Why We Did This

After the main benchmark, we discovered the two systems used very different answer prompts. EverMemOS had a 380-word, 7-step Chain-of-Thought prompt with 16K token budget. Neuromem had an 80-word "answer in 1-2 sentences" prompt with 200 token budget. We needed to verify the 20-point gap came from retrieval quality, not prompt engineering.

### What We Tested

Three experiments, all using the same search results (retrieval held constant):

1. **Original prompts** — each system's own prompt (already measured)
2. **EverMemOS CoT prompt on Neuromem** — give Neuromem the exact same 7-step CoT prompt
3. **Neutral prompt on both** — identical simple prompt: "Answer using ONLY the provided context"

### Results

| Experiment | Neuromem | EverMemOS | Gap |
|---|---|---|---|
| Original (own prompts) | 72.34% | 92.77% | 20.4 pp |
| CoT prompt on Neuromem | 36.71% | n/a | n/a |
| Neutral identical prompt | 66.10% | 86.88% | 20.8 pp |

### Per-Category: Neutral Prompt

| Category | EverMemOS | Neuromem | Gap |
|----------|-----------|----------|-----|
| Cat 1 (single_hop) | 85.5% | 54.6% | -30.9 pp |
| Cat 2 (multi_hop) | 81.1% | 66.3% | -14.8 pp |
| Cat 3 (temporal) | 52.4% | 28.1% | -24.3 pp |
| Cat 4 (open_domain) | 93.5% | 74.2% | -19.3 pp |

### Key Findings

1. **CoT prompt destroyed Neuromem (36.71%).** The 7-step reasoning process caused the LLM to hallucinate — fabricating dates, topics, and facts that weren't in the retrieved context. The CoT prompt was designed for EverMemOS's structured MemCell format. When applied to Neuromem's raw speaker-tagged messages, it caused massive confabulation.

2. **Each system's own prompt helped by ~6 points.** EverMemOS dropped from 92.77% → 86.88% (−5.89 pp). Neuromem dropped from 72.34% → 66.10% (−6.24 pp). The prompt engineering benefit was roughly equal.

3. **The gap is unchanged (~20 pp).** With identical prompts: 20.8 pp gap. With original prompts: 20.4 pp gap. The prompt asymmetry was a wash.

### Conclusion

**The 20-point gap is real and comes from retrieval quality, not prompt engineering.** The original benchmark was honest.

### Results Directories

- Neuromem CoT prompt: `evaluation/results/locomo-neuromem-cot-prompt-test/`
- Neuromem neutral: `evaluation/results/locomo-neuromem-neutral-prompt/`
- EverMemOS neutral: `evaluation/results/locomo-evermemos-neutral-prompt/`

---

## Failure Analysis (2026-03-18, late evening)

### Why We Did This

We know the gap is 20 points (357 questions where Neuromem failed but EverMemOS succeeded). But to close the gap efficiently, we need to know WHY each question failed. Instead of running many benchmarks with different extraction passes, we analyzed the existing failures to predict which fixes would help most.

### Method

1. Extracted all 357 questions where Neuromem was wrong but EverMemOS was right
2. Took a stratified sample of 100 (25 per category)
3. Classified each failure into one of 7 root cause categories
4. Extrapolated counts to estimate points recoverable from each fix

### Failure Breakdown

| Failure Reason | Count (of 100) | % | Est. Recoverable (of 357) | What It Means |
|---|---|---|---|---|
| **Retrieval miss** | 30 | 30% | ~107 questions | Search didn't find the message at all |
| **Temporal** | 25 | 25% | ~89 questions | Time questions — "when", "how long ago" |
| **Multi-hop** | 19 | 19% | ~68 questions | Needed to connect 2+ messages together |
| **Insufficient detail** | 16 | 16% | ~57 questions | Found right area, missed specific names/numbers |
| **Wrong inference** | 7 | 7% | ~25 questions | Found right context, drew wrong conclusion |
| **Vocab mismatch** | 3 | 3% | ~11 questions | Question used different words than message |

### By Category

| Failure Reason | Cat 1 (single_hop) | Cat 2 (multi_hop) | Cat 3 (temporal) | Cat 4 (open_domain) |
|---|---|---|---|---|
| Retrieval miss | Common | Moderate | Rare | Very common |
| Temporal | Rare | Rare | **Dominant** | Rare |
| Multi-hop | Rare | **Dominant** | Rare | Common |
| Insufficient detail | Common | Moderate | Rare | Common |

### Surprises

1. **Vocabulary mismatch is only 3%.** We initially thought this was the main problem (questions using different words than messages). It's barely a factor — episode extraction + HyDE already handle most vocabulary gaps.

2. **Retrieval miss is #1 at 30%.** The search pipeline simply fails to find the relevant message in nearly a third of failures. The information is there, the search just doesn't surface it.

3. **Temporal is #2 at 25%.** Time-related questions are a huge weakness. Resolving "three years ago" or "the week before November 16" is very hard without explicit date extraction.

### Estimated Impact of Each Fix

Based on the failure analysis, here's what each extraction pass would be worth:

| Fix | Addresses | Est. Points Gained | New Score |
|---|---|---|---|
| Baseline (current) | — | — | 72.3% |
| + Better retrieval (more passes, query expansion) | Retrieval miss (30%) | +7.0 | ~79% |
| + Temporal date extraction | Temporal (25%) | +5.8 | ~85% |
| + Entity linking / chain search | Multi-hop (19%) | +4.4 | ~89% |
| + Atomic fact extraction | Insufficient detail (16%) | +3.7 | ~93% |
| + Better answer prompts | Wrong inference (7%) | +1.6 | ~94% |

**Note:** These are estimates based on 100-sample extrapolation. Real gains will be lower (not all failures are fully fixable). A realistic ceiling is ~87-90% with the top 3 fixes.

### Priority Order for Development

1. **Retrieval improvement** — highest impact, addresses 30% of failures. More search rounds, lower thresholds, better query expansion.
2. **Temporal normalization** — second highest, addresses 25%. Convert all relative dates to absolute at ingest time.
3. **Entity linking + multi-hop search** — third, addresses 19%. Pre-compute entity connections so chain-following queries work.
4. **Atomic fact extraction** — fourth, addresses 16%. Extract every name, number, and detail as searchable atoms.

Items 2-4 are all forms of "extraction passes" — the answer to "how many passes do we need?" is approximately 3 focused passes (temporal, entity linking, atomic facts), which collectively address 60% of all failures.
