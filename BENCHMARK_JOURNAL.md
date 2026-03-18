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
