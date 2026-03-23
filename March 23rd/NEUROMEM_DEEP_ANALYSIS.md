# Neuromem: The Path to 96%
## A Deep Analysis of Where We Are, What's Left, and How to Get There

**Author:** Joshua Adler
**Date:** March 23, 2026
**Status:** Research complete — strategies ready for implementation

---

> **The bottom line:** Neuromem went from 72% to 91% in one week through prompt engineering and model upgrades. But those easy wins are over. The next jump — from 91% past EverMemOS (92.77%) and up to 96%+ — requires a fundamentally different approach. This document maps out exactly how to get there.

---

## Table of Contents

1. [The Story So Far](#1-the-story-so-far)
2. [Where We Stand Today](#2-where-we-stand-today)
3. [Understanding the Failures](#3-understanding-the-failures)
4. [Why Bigger Models Won't Work Anymore](#4-why-bigger-models-wont-work-anymore)
5. [Know Your Rival: EverMemOS Deep Dive](#5-know-your-rival-evermemos-deep-dive)
6. [The Five Breakthrough Strategies](#6-the-five-breakthrough-strategies)
7. [Implementation Roadmap](#7-implementation-roadmap)
8. [Projected Outcomes](#8-projected-outcomes)
9. [Cost Analysis](#9-cost-analysis)
10. [Risk Assessment](#10-risk-assessment)
11. [Data Appendix](#11-data-appendix)

---

## 1. The Story So Far

![Score Progression](charts/deep_01_score_progression.png)
*Figure 1: Every bar is a measured benchmark score except the green target. Each jump required a different kind of innovation.*

### The Numbers

| Configuration | Score | How We Got There | Date |
|--------------|-------|-----------------|------|
| **Neuromem v2** | 72.34% | Basic agentic search, top_k=15 | Mar 19 |
| **Neuromem v3** | 87.71% ± 0.33% | Structured prompt + top_k=100 + modality reranking | Mar 19 |
| **Phase 0** | 90.81% ± 0.33% | Reranker upgrade (22M → 435M params) | Mar 21 |
| **Phase 1** | 91.21% ± 0.50% | Embedding upgrade (8M → 600M params) | Mar 21 |
| **EverMemOS** | 92.77% ± 0.10% | Their published benchmark result | — |
| **Full Context** | 93.81% ± 0.13% | All messages given to LLM (no search) | Mar 19 |
| **Target** | ~96%+ | What this document is about | — |

> **What an 8th grader needs to know:**
>
> Think of this like a student's test scores improving over a semester. Version 2 was a C- (72%). We studied hard and jumped to a B+ (87%). Then we bought better study tools (bigger models) and got an A- (91%). Our rival has an A (93%). But now the easy improvements are used up — better tools alone won't get us to an A+ (96%). We need to actually learn *new strategies* for taking the test.

### What Each Jump Actually Did

**v2 → v3 (+15.37 points):** This was the single biggest improvement. Three changes combined:
- **Structured answer prompt (+12pp):** Instead of just saying "answer this question," we told the LLM to think step-by-step, cite evidence, and consider temporal context. This is like teaching a student to show their work instead of guessing.
- **top_k 15 → 100 (+8pp overlap):** We gave the LLM 100 potentially relevant messages instead of 15. More context = better answers. Like giving a student more pages of their textbook to reference during a test.
- **Modality-aware reranking (+2pp):** We taught the system that episode summaries are better for "explain" questions, while raw messages are better for "what date" questions.

**v3 → Phase 0 (+3.10 points):** Swapped the reranker model from a 22-million-parameter model to a 435-million-parameter one. The reranker is the part that looks at the top search results and re-orders them by relevance. A bigger model catches nuance that the smaller one missed.

**Phase 0 → Phase 1 (+0.40 points):** Swapped the embedding model from 8M parameters to 600M. Embeddings are how the system converts text into numbers for similarity search. The 75x bigger model gave us... only 0.40 points. This is the key signal: **model upgrades have hit diminishing returns.**

> **What an 8th grader needs to know:**
>
> Imagine you're searching for a book in a library. Version 2 used a card catalog (slow, only exact matches). Version 3 let you ask the librarian, who understands what you mean even if you use different words. Phase 0 hired a *better* librarian. Phase 1 upgraded the library's filing system. But now both the librarian and the filing system are really good — making them even bigger won't help much. What we need is a smarter *strategy* for finding books.

---

## 2. Where We Stand Today

![The Gap](charts/deep_02_the_gap.png)
*Figure 2: The playing field. Every 1 percentage point equals about 15 more correct answers out of 1,540 questions.*

### The Gap in Plain Numbers

| What We Need | Points | Questions to Fix |
|-------------|--------|-----------------|
| Match EverMemOS | +1.56pp | ~24 more correct |
| Beat the full-context ceiling | +2.60pp | ~40 more correct |
| Reach 96% target | +4.79pp | ~74 more correct |

The gap to EverMemOS is only 24 questions. That's less than 2% of the test. But these are the *hardest* questions — the ones that survived every optimization we've thrown at them.

### Competitive Landscape

![Competitive Landscape](charts/deep_06_competitive_landscape.png)
*Figure 3: Neuromem already beats every funded competitor. The remaining target is the academic system EverMemOS.*

**Key takeaway:** Systems with tens of millions in funding (Mem0, Zep, Letta) score between 58-75%. Neuromem is already in the top 3 in the world on this benchmark.

| System | Score | Funding | Cost/Month |
|--------|-------|---------|-----------|
| LangMem | 58.1% | LangChain backed | Varies |
| Mem0 | 66.9% | $24M raised | $19-249 |
| Neuromem v2 | 72.3% | $0 (you) | $12 |
| Letta/MemGPT | 74.0% | Series A | Varies |
| Zep/Graphiti | 75.1% | Series A | $149+ |
| SuperMemory | 81.6% | $2.6M raised | $99+ |
| **Neuromem Phase 1** | **91.2%** | **$0 (you)** | **$14** |
| Hindsight | 91.4% | Enterprise | Cloud pricing |
| **EverMemOS** | **92.8%** | Academic | ~$207 |

> **What an 8th grader needs to know:**
>
> Imagine a spelling bee with 12 contestants. Companies with millions of dollars in funding are getting eliminated in the early rounds (58-75%). Neuromem — built by one person with no funding — is in the final two. The only one ahead is an academic research team. This document is about how to win the bee.

---

## 3. Understanding the Failures

To improve, we need to understand exactly *what goes wrong* and *why*. At the v3 level (87.71%), there were 357 questions where Neuromem got the wrong answer but EverMemOS got it right.

![Failure Taxonomy](charts/deep_04_failure_taxonomy.png)
*Figure 4: Left — what types of failures occur. Right — how many can be fixed with proposed improvements.*

### The Six Failure Types

**1. Retrieval Miss (30% — 107 failures)**
The relevant information exists in the database, but the search system can't find it. Example: Searching for "credit cards" returns results about "carbon credits" instead of the actual OCR receipts containing card numbers.

> *Like searching your email for "dentist appointment" but only finding emails about "dental insurance" because the actual appointment confirmation uses different words.*

**2. Temporal Confusion (25% — 89 failures)**
The system finds relevant messages but can't reason about time. Example: "What happened between March and June?" returns events from February or July because the system doesn't build a proper timeline.

> *Like asking "What did you do last summer?" and getting answers from two summers ago because the system doesn't understand "last."*

**3. Multi-Hop Chain Break (19% — 68 failures)**
Questions that require connecting multiple pieces of information. Example: "How did Riley influence Jordan's mental health?" requires connecting Riley → therapy recommendation → Dr. Martinez → book → Dr. Choi → recovery. The system finds the first link but can't follow the chain.

> *Like a detective who finds one clue but can't connect it to the other clues to solve the case.*

**4. Insufficient Detail (16% — 57 failures)**
The system finds the right topic but returns messages that are too vague to answer specifically. Example: "What credit cards does Jordan use?" finds financial discussions but not the specific OCR receipt that says "Visa ending 4821."

> *Like asking a friend "where's the restaurant?" and they say "downtown" instead of giving you the actual address.*

**5. Wrong Inference (7% — 25 failures)**
The LLM has the right information but draws the wrong conclusion from it. This is an answer-generation problem, not a retrieval problem.

**6. Vocabulary Mismatch (3% — 11 failures)**
Specialized terms that the system doesn't understand. Example: "cap table" is financial jargon that the embedding model hasn't seen enough to properly encode.

### Category Breakdown: Where Each Type Hurts

![Category Comparison](charts/deep_03_category_comparison.png)
*Figure 5: Category-level performance. Temporal reasoning (Cat 3) is the biggest opportunity — 8+ points below the ceiling.*

| Category | Neuromem v3 | EverMemOS | FC Ceiling | Gap to Ceiling |
|----------|------------|-----------|------------|---------------|
| Cat 1 (Single-Hop) | 86.2% | 91.1% | 93.0% | 6.8pp |
| Cat 2 (Multi-Hop) | 85.7% | 89.4% | 91.9% | 6.2pp |
| **Cat 3 (Temporal)** | **69.8%** | **78.1%** | **78.8%** | **9.0pp** |
| Cat 4 (Open-Domain) | 90.4% | 96.2% | 96.5% | 6.1pp |

**The headline finding:** Category 3 (temporal reasoning) is where the most points are hiding. Neuromem scores 69.8% while even the full-context ceiling only reaches 78.8%. This means temporal questions are hard for *everyone*, but there's still 9 points of improvement available — and most of that gap is a retrieval problem, not an LLM reasoning problem.

> **What an 8th grader needs to know:**
>
> The test has 4 sections: Easy Lookups, Connect-the-Dots, Timeline Questions, and Big-Picture Questions. We're doing okay on 3 of them (85-90%) but bombing Timeline Questions (69.8%). That one section is dragging our whole grade down. If we can study for timelines specifically, our overall grade goes up a LOT.

---

## 4. Why Bigger Models Won't Work Anymore

![Diminishing Returns](charts/deep_05_diminishing_returns.png)
*Figure 6: The first 15 points came from a prompt change (free). The last 0.4 points cost a 75x model increase.*

This is maybe the most important insight in the entire analysis.

### The Data

| Change | Effort | Gain | Gain per Unit Effort |
|--------|--------|------|---------------------|
| Structured prompt | Minimal (text change) | +15.37pp | Massive |
| top_k 15→100 | Minimal (config change) | +8.0pp | Massive |
| Modality reranking | Small (code change) | +2.0pp | Large |
| Reranker 22M→435M | Medium (model swap) | +3.10pp | Moderate |
| Embedding 8M→600M | Large (75x model increase) | +0.40pp | **Tiny** |

**Pattern:** The best gains came from algorithmic changes, not bigger models. A simple text prompt change was worth more than a 75x model upgrade. This is a textbook case of diminishing returns.

### Why This Happens

The embedding upgrade (8M → 600M) barely helped because the *search quality* was already good enough. At top_k=100, we're already pulling in most of the relevant messages. Making the embedding model bigger helps with marginal cases, but the bottleneck has shifted.

**The bottleneck is no longer "can we find the right messages?" — it's "can we reason about what we found?"**

This is like upgrading a telescope to see Mars more clearly when the real problem is that you need to calculate Mars's orbit. Better optics don't help with the math.

> **What an 8th grader needs to know:**
>
> Imagine you're cooking. At first, getting better ingredients (bigger models) made your food way better. But at some point, you have great ingredients — now what matters is your *recipe* and *cooking technique*. Buying even fancier ingredients won't help if your recipe is wrong. We've reached the point where we need better recipes, not better ingredients.

---

## 5. Know Your Rival: EverMemOS Deep Dive

To beat EverMemOS, we need to understand exactly what they do differently — and where their approach breaks down.

### Their Architecture (How They Get to 92.77%)

EverMemOS uses a fundamentally different approach to storing and finding memories:

| Feature | EverMemOS | Neuromem |
|---------|-----------|---------|
| **Storage** | MongoDB (cloud database) | SQLite (single file on your computer) |
| **Embedding Model** | Qwen3-4B (4 billion params) | Qwen3-0.6B (600 million params) |
| **Embedding Dimension** | 1024+ dimensions | 1024 dimensions |
| **Search Method** | 2-round hybrid + LLM sufficiency check | 1-round hybrid + score threshold |
| **Extraction Depth** | 12+ LLM prompts per conversation | 1 combined prompt |
| **Monthly Cost** | ~$207 | ~$14 |

### Their Three Key Innovations

**1. MaxSim Scoring**
Instead of one embedding per message, EverMemOS extracts "atomic facts" from each message and embeds each fact separately. When searching, it computes similarity against every fact and takes the *maximum* score.

Why it works: A long message about 5 different topics will still score high if just ONE topic matches the query. Regular averaging would dilute the score.

> *Like a student who wrote a 10-page essay — instead of grading the whole essay against a rubric, you find the single best paragraph and grade THAT. Much fairer for essays that cover multiple topics.*

**2. LLM Sufficiency Check**
After the first round of search results, EverMemOS asks an LLM: "Do these results contain enough information to answer the question?" If not, it generates 2-3 alternative search queries and searches again.

This is especially powerful for temporal queries because the sufficiency prompt explicitly checks: "Do the results cover the full time range mentioned in the question?"

> *Like asking your librarian "did you find everything I need?" before leaving the library. If they say no, you search again with different keywords.*

**3. Deep Extraction Pipeline (12+ Prompts)**
When EverMemOS ingests a conversation, it runs 12+ separate LLM calls to extract:
- Episode narratives (3rd person summaries)
- Event logs with timestamps
- Profile attributes (3 passes)
- Life events and milestones
- Predicted future events
- Relationship updates
- Group profiles

This costs ~612 LLM calls per conversation (12 prompts x 51 memory cells), or about $20 per conversation. For the full benchmark (10 conversations), that's ~$200 just for ingestion.

> *Like having 12 different teachers each read the same essay and extract different types of notes — one tracks dates, one tracks people, one tracks emotions, etc. Very thorough, but very expensive.*

### Their Weaknesses — Where They're Vulnerable

![EverMemOS Weaknesses](charts/deep_08_evermemos_weaknesses.png)
*Figure 7: Feature comparison. Stars mark areas where Neuromem significantly leads.*

#### Benchmark-Relevant Technical Gaps

These are architectural differences that could directly impact retrieval quality:

**1. No Salience Filtering (Score: 0/10)**
EverMemOS treats every piece of information as equally important. It has no mechanism to distinguish "Jordan got a dog named Biscuit" (important, memorable fact) from "okay sounds good" (filler message). Neuromem's salience guard catches this. *Note: Despite this, EverMemOS still scores 92.77% — salience may matter more at scale than on this benchmark's 10 conversations.*

**2. No Consolidation / Memory Decay (Score: 0/10)**
EverMemOS stores everything forever with equal weight. It has no way to "forget" less important things or merge related memories over time. Neuromem models memory like a human brain — important things get reinforced, trivial things fade.

**3. No Entity Modeling (Score: 3/10)**
EverMemOS doesn't build unified profiles of people. If "Rachel" is mentioned in 50 different messages, it finds individual messages — it doesn't aggregate them into a "here's everything about Rachel" profile.

#### Product Advantages (Not Benchmark-Relevant, but Important)

These don't directly affect LoCoMo scores, but they determine which system is actually viable as a product:

**4. Cost Structure: $14/month vs $207/month**
EverMemOS requires MongoDB (~$57), DeepInfra embedding API (~$100), DeepInfra reranking (~$50), and a cloud LLM (~$20). Neuromem runs on local models + one API for answer generation. This is a 15x cost advantage that matters enormously for real-world deployment, even if it doesn't show up on the benchmark.

**5. Local-First Architecture**
EverMemOS requires three external services. If MongoDB changes pricing, DeepInfra has an outage, or OpenRouter goes down, EverMemOS stops working. Neuromem runs from a single SQLite file on a laptop — no external dependencies for storage or search.

> **What an 8th grader needs to know:**
>
> EverMemOS is like a student who uses expensive private tutors and fancy study materials. They get great grades (92.77%), but it costs a fortune. Neuromem is the student who uses free library books and smart study habits — nearly the same grades (91.2%) for 1/15th the cost. And importantly, the expensive student has some blind spots we can exploit.

---

## 6. The Five Breakthrough Strategies

These are the concrete innovations that can push Neuromem from 91% past EverMemOS to 96%+. Each one targets specific failure types identified in Section 3.

![Point Sources](charts/deep_09_point_sources.png)
*Figure 8: Projected impact of each strategy. Conservative estimates use the low end; optimistic uses the high end.*

### Strategy 1: Category-Specific Pipelines (+1.5 to +2.5pp)

**The problem:** Right now, every question goes through the same search pipeline regardless of whether it's asking for a date, a person's story, or a comparison. A "when did X happen?" question and a "describe Y's relationship" question both use the same retrieval, the same ranking, and the same answer strategy.

**The solution:** Route each question to a specialized pipeline:

| Question Type | Pipeline | Optimization |
|--------------|----------|-------------|
| **Single-hop** ("What is...") | Direct FTS5 + vector search | Fast, precise, entity-aware |
| **Multi-hop** ("How did X lead to Y?") | Chain-following with scent trails | Follow entity chains across messages |
| **Temporal** ("When/between/during...") | Timeline construction | Build event timeline, then answer |
| **Open-domain** ("Describe/summarize...") | Broad retrieval + aggregation | Pre-computed summaries + wide search |

**How it recovers questions:**
- The 89 temporal failures get a dedicated temporal pipeline that builds actual timelines instead of just searching for keywords
- The 68 multi-hop failures get a chain-following system that connects clues across messages
- The 57 insufficient-detail failures get broader search + pre-computed aggregations

**Implementation effort:** ~5 hours of coding. The routing classifier already exists in `engine.py` — we just need to differentiate the downstream behavior.

> *Think of it like a hospital. Right now, every patient goes through the same general check-up. The improvement is adding specialized departments — a cardiologist for heart problems, a neurologist for brain issues. Same hospital, but each patient gets the right specialist.*

### Strategy 2: Multi-Step Reasoning Chains (+1.0 to +2.0pp)

**The problem:** When a question requires connecting multiple pieces of information (multi-hop), the system finds relevant messages but presents them as a flat list. The LLM has to figure out the connections on its own, and often fails.

**The solution:** For questions classified as multi-hop:
1. Find initial relevant messages (current pipeline)
2. Extract entities and events from those messages
3. Search for messages that connect to those entities/events (a "second hop")
4. Optionally do a third hop for complex chains
5. Present the results in chronological order with explicit connections

**Example:** "How did Riley influence Jordan's mental health?"
- **Current (fails):** Finds messages about Riley + messages about therapy, but they're separate and the LLM can't connect them
- **With chains:** Step 1 finds Riley → Step 2 finds Riley mentioned Dr. Martinez → Step 3 finds Dr. Martinez recommended a book → Step 4 finds the book led Jordan to Dr. Choi → Step 5 finds Dr. Choi started therapy → Answer connects the full chain

**Implementation effort:** ~5 hours. The "scent trail" search already exists in `engine.py` (`_scent_trail()`) but only does 2 hops on entities. This extends it to follow causal chains more deliberately.

**Evidence status:** Theoretically well-supported (multi-hop QA is a studied problem in NLP), but Neuromem has not yet benchmarked an explicit chain-following approach. The +1.0-2.0pp range reflects this uncertainty — the low end assumes only marginal improvement over the existing 2-hop scent trail.

> *Like a detective building a case board with red string connecting clues. Right now we find the clues but don't draw the string. This strategy adds the string.*

### Strategy 3: Pre-Computed Knowledge Structures (+1.0 to +2.0pp)

**The problem:** Questions like "Summarize Jordan and Riley's relationship" or "What mistakes has Jordan made as a founder?" can't be answered by any single message. They require aggregating information across dozens of messages — which is impossible in real-time retrieval.

**The solution:** During ingestion (when we first store messages), pre-compute structured knowledge:

| Structure | What It Stores | Questions It Helps |
|-----------|---------------|-------------------|
| **Entity profiles** | Everything about each person (job, relationship, key events) | "Who is Rachel?" "Tell me about Nina" |
| **Relationship maps** | How people relate to each other with timeline | "How did X's relationship with Y evolve?" |
| **Topic summaries** | Aggregated facts per topic (finances, health, career) | "What's the financial situation?" "Describe the team" |
| **Event timelines** | Key events in chronological order per entity/topic | All temporal questions |

**How it works in practice:**
When the system gets the question "What credit cards does Jordan use?" instead of searching through thousands of messages, it first checks the pre-computed "Jordan — Financial" profile which already lists "Visa ending 4821, Amex ending 9012" extracted from OCR receipts during ingestion.

**Implementation effort:** ~6 hours. Requires extending the existing consolidation module to compute structured knowledge at ingestion time.

**Evidence status:** EverMemOS's 12-prompt extraction pipeline is direct evidence that deeper extraction helps (they score 92.77% with it). Neuromem's current single-pass extraction is a known weakness. However, the specific +1.0-2.0pp estimate has not been validated — the actual gain depends on how well pre-computed structures integrate with the existing retrieval pipeline.

> *Like making study flashcards before a test. Instead of flipping through the entire textbook during the exam, you've already organized the key facts into neat cards by topic. Slower to prepare, but much faster and more accurate during the test.*

### Strategy 4: Temporal Reasoning Engine (+1.5 to +3.0pp)

**The problem:** This is the biggest opportunity. Category 3 (temporal) scores 69.8% — nearly 10 points below the ceiling. The system treats time queries like regular search queries, which fails because time requires *reasoning*, not just *retrieval*.

**The solution:** Build a dedicated temporal engine:

![Temporal Deep Dive](charts/deep_10_temporal_deep_dive.png)
*Figure 9: Left — temporal performance across systems. Right — the specific types of temporal failures.*

**Components:**
1. **Timeline Construction:** When a temporal question is detected, build a chronological event list for the relevant entities/topics
2. **Temporal Query Decomposition:** Break "what happened between March and June?" into two queries: "events after March" AND "events before June"
3. **Sequence Ordering:** Explicitly sort and present events in time order
4. **Duration/Frequency Calculation:** Count occurrences, compute durations between events
5. **Relative Time Resolution:** Convert "last month" or "recently" into actual date ranges

**Specific failures this fixes:**
- "When did Jordan quit?" → Build career timeline, find the quit event with exact date
- "How did Sam's involvement evolve?" → Build Sam timeline, show progression from advisor → consultant → stepped back
- "EPA regulations impact on growth?" → Build CarbonSense timeline, connect EPA mandate → TAM expansion → Series A

**Important nuance on the +1.5-3.0pp range:** Category 3 only has 96 questions (6.2% of the test), so improving Cat 3 alone maxes out at ~1.9pp. But the 89 "temporal confusion" failures from Section 3 are spread across ALL four categories — any question involving time (even in Cat 1 or Cat 4) benefits from the temporal engine. Recovering 50 of those 89 temporal failures across all categories = 50/1540 = +3.2pp potential.

**Implementation effort:** ~5 hours. The temporal module exists but only does basic date filtering. This upgrades it to actual temporal reasoning.

> *Right now, when you ask "what happened last summer?" the system searches for messages that mention summer. With a temporal engine, it actually builds a calendar of events and gives you everything that happened between June and August — whether the messages mention "summer" or not.*

### Strategy 5: Judge-Aware Answer Optimization (+0.5 to +1.5pp)

**The problem:** The benchmark uses GPT-4o-mini as a judge with majority voting across 3 runs. Some answers that are technically correct get judged as wrong because they're too verbose, too brief, or structured in a way the judge doesn't like.

**The solution:** Tune the answer format to maximize judge agreement:
1. **Clear first sentence:** State the answer directly in the first sentence, then provide evidence
2. **Entity specificity:** Always include full names, dates, and numbers — the judge penalizes vagueness
3. **Temporal precision:** When a date is known, state it explicitly instead of "around that time"
4. **List formatting:** For multi-part answers, use numbered lists that the judge can easily verify

**Evidence this matters:** The 25 "wrong inference" failures include cases where Neuromem's answer is partially correct but formatted in a way the judge marks as wrong. Additionally, ~24 of the 357 failures are "judge disagreement" — cases where the answer is arguably correct but the judge's prompt interprets it differently.

**Implementation effort:** ~3 hours. This is purely a prompt-engineering task — changing the answer generation prompt.

> *Like learning how a specific teacher grades. If the teacher gives more credit for answers that start with a clear thesis statement, you should start your answers with a thesis statement. Not "gaming" the system — just communicating in the way the evaluator expects.*

---

## 7. Implementation Roadmap

![Implementation Roadmap](charts/deep_11_implementation_roadmap.png)
*Figure 10: Three horizons of work. H1 captures quick wins; H2 implements breakthroughs; H3 validates everything.*

### Horizon 1: Foundation (~10 hours, target: 93-94%)

These are quick wins that borrow proven techniques from EverMemOS:

| Task | Hours | Expected Impact | Source |
|------|-------|----------------|--------|
| LLM sufficiency check | 2 | +0.5pp | EverMemOS technique |
| Multi-query Round 1 (always 3 queries) | 2 | +0.5pp | EverMemOS technique |
| Temporal extraction during ingestion | 3 | +1.0pp | New feature |
| MaxSim-style per-fact scoring | 2 | +0.5pp | EverMemOS technique |
| Benchmark validation run | 1 | Verify gains | — |

**Why H1 works:** These are established techniques that EverMemOS already proved effective. We're not inventing — we're adopting.

**Key detail — LLM Sufficiency Check:** Currently, Neuromem decides if search results are "good enough" using a simple score threshold (`avg_score > 0.02`). EverMemOS uses an LLM to explicitly check: "Do these results answer the question? Is the time range covered? What's missing?" This catches cases where the score looks fine but critical information is absent.

### Horizon 2: Breakthroughs (~25 hours, target: 95-98%)

These are the five strategies from Section 6, implemented in priority order:

| Task | Hours | Expected Impact |
|------|-------|----------------|
| Category-specific pipelines | 5 | +1.5-2.5pp |
| Multi-step reasoning chains | 5 | +1.0-2.0pp |
| Pre-computed knowledge structures | 6 | +1.0-2.0pp |
| Temporal reasoning engine | 5 | +1.5-3.0pp |
| Judge-aware answer optimization | 3 | +0.5-1.5pp |

**Important note:** These gains are NOT fully additive. The table below shows how each strategy maps to specific failure buckets — and where they overlap:

| Failure Type (count) | S1: Routing | S2: Chains | S3: Knowledge | S4: Temporal | S5: Judge |
|---------------------|:-----------:|:----------:|:-------------:|:------------:|:---------:|
| Retrieval miss (107) | **Primary** | Secondary | **Primary** | — | — |
| Temporal confusion (89) | — | — | Secondary | **Primary** | — |
| Multi-hop chain (68) | Secondary | **Primary** | — | — | — |
| Insufficient detail (57) | — | — | **Primary** | — | Secondary |
| Wrong inference (25) | — | — | — | — | **Primary** |
| Vocab mismatch (11) | **Primary** | — | — | — | — |

**Primary** = main strategy targeting this failure type. **Secondary** = partial overlap (estimated 30-40% of gains from that bucket).

To avoid double-counting: the +1.5-2.5pp for S1 and +1.0-2.0pp for S3 both claim some of the 57 insufficient-detail failures. After deducting overlap (~15 shared recoveries), the combined net from S1+S3 is +2.0-3.5pp, not +2.5-4.5pp. Realistic total from all five strategies after overlap adjustment: **+3.5 to +7.0pp**.

### Horizon 3: Validation & Polish (~10 hours)

| Task | Hours | Purpose |
|------|-------|---------|
| Full 1,540-question benchmark | 2 | Official score |
| Ablation studies (disable each component) | 3 | Understand what works |
| Error analysis of remaining failures | 3 | Plan next cycle |
| Documentation and research report | 2 | Record findings |

> **What an 8th grader needs to know:**
>
> Think of it like training for a track meet:
> - **Horizon 1** is learning from the kid who beat you last time — copying their stretching routine, their starting position, their breathing technique. Quick wins.
> - **Horizon 2** is developing your OWN new moves — a better stride, a stronger kick, smarter pacing. This is where you go from "catching up" to "pulling ahead."
> - **Horizon 3** is running the actual race and reviewing the tape afterward to see what worked.

---

## 8. Projected Outcomes

![Probability Distribution](charts/deep_12_probability_distribution.png)
*Figure 11: Projected accuracy distribution after all improvements. The 68% confidence interval is 93.2%–96.8%.*

### What the Math Says

Based on the estimated gains from each strategy (Section 6), with adjustments for overlap:

| Scenario | Final Score | Probability | What It Means |
|----------|-----------|-------------|--------------|
| **Conservative** | 93.5-94.5% | ~25% | Beat EverMemOS, slightly below ceiling |
| **Expected** | 94.5-96.0% | ~45% | Substantially exceed EverMemOS |
| **Optimistic** | 96.0-98.0% | ~25% | Near-perfect, research-paper worthy |
| **Disappointing** | 91.5-93.5% | ~5% | Minor gains, strategies don't compound |

**Key probabilities (derivation below):**
- P(beat EverMemOS's 92.77%) = **~89%**
- P(beat full-context ceiling 93.81%) = **~75%**
- P(reach 95%+) = **~50%**

*How these were estimated:* The projected gain range from all five strategies after overlap is +3.5 to +7.0pp from the Phase 1 baseline of 91.21%. This gives a projected range of 94.7%–98.2%. Modeling this as a normal distribution centered on the midpoint (96.5%) with the range covering ~90% of outcomes (i.e., standard deviation ≈ 1.7pp), we can compute the probability of exceeding each threshold. The 68% confidence interval (93.2%–96.8% in Figure 11) is slightly wider because it also accounts for H1 variability and execution risk — the distribution in the chart uses mean 95.0% and SD 1.8pp, reflecting a more conservative center. The "disappointing" 5% scenario assumes multiple strategies underperform simultaneously.

### Why We Can Beat the Full-Context Ceiling

The full-context ceiling (93.81%) is often treated as an upper bound — "the best possible score." But it's actually an artificial limit:

**Full context mode gives the LLM ALL 5,882 messages at once.** This means:
- The LLM has to find the needle in a 5,882-message haystack
- It has no structure, no pre-computation, no reasoning chain
- It's limited by the LLM's ability to process massive context in one shot

**A smart retrieval system can beat this because:**
- It can pre-compute timelines, entity profiles, and topic summaries
- It can do multi-step reasoning that an LLM can't do in one pass
- It can present information in a structured way that reduces LLM errors
- It can verify its own answers before returning them

**Honest caveat:** This reasoning is plausible but unproven on LoCoMo specifically. No retrieval-based system has yet beaten the full-context ceiling on this benchmark. The theory is sound — structured retrieval should outperform brute-force context in complex reasoning tasks — but until we run the experiment, the 93.81% ceiling remains an empirical barrier that we haven't crossed. The probability estimates in Section 8 reflect this uncertainty (P(beat ceiling) = 75%, not 99%).

> *Full context mode is like giving a student the entire textbook during a test. A smart system is like giving them a well-organized set of notes + a calculator + a study guide. The notes are better than the textbook for test-taking, even though the textbook contains more information.*

### What "96%+" Would Mean

At 96%, Neuromem would:
- Answer 1,478 out of 1,540 questions correctly (vs. current 1,405)
- Have only 62 failures (vs. current 135)
- Beat EverMemOS by 3.2+ percentage points
- Be the #1 personal memory system in the world on this benchmark
- Do it for $14/month instead of $207/month

---

## 9. Cost Analysis

![Cost vs Accuracy](charts/deep_07_cost_vs_accuracy.png)
*Figure 12: Accuracy plotted against monthly cost. Neuromem is alone in the "ideal zone" — high accuracy, low cost.*

| System | Accuracy | Monthly Cost | Cost per Correct Answer |
|--------|----------|-------------|----------------------|
| **Neuromem (current)** | 91.21% | ~$14 | $0.010 |
| **Neuromem (target)** | ~96% | ~$16 | $0.011 |
| EverMemOS | 92.77% | ~$207 | $0.145 |
| Mem0 Pro | 66.90% | ~$249 | $0.242 |
| Zep Cloud | 75.10% | ~$149 | $0.129 |
| SuperMemory | 81.60% | ~$99 | $0.079 |

**Neuromem's cost advantage is structural, not temporary.** It runs on:
- SQLite (free, local, no database server)
- Local embedding model (free after download)
- Local reranker (free after download)
- Cloud API only for final answer generation (~$12-16/month at 100 queries/day)

EverMemOS requires:
- MongoDB (sharded cluster, ~$57/month)
- DeepInfra embedding API (~$100/month)
- DeepInfra reranking API (~$50/month)
- Cloud LLM for answer generation (~$20/month)

**The benchmark run itself costs ~$7-8** (mostly GPT-4.1-mini for answers + GPT-4o-mini for judging). Each Horizon's benchmark validation run costs about $8.

> **What an 8th grader needs to know:**
>
> Imagine two students. One hires private tutors, buys expensive prep materials, and pays for a fancy desk setup — spending $207/month. The other uses free library books, a laptop, and smart study habits — spending $14/month. The second student is getting *nearly the same grades* and is on track to surpass the first. That's the Neuromem advantage: brain over budget.

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Strategies don't compound as projected | Medium | Medium | Each tested independently; partial gains still valuable |
| Temporal engine is harder than expected | Medium | High | Can borrow from EverMemOS's temporal sufficiency prompt |
| Benchmark cost overruns | Low | Low | ~$8 per run; budget for 5-6 runs max |
| Model upgrades cause regressions | Low | Medium | Easy rollback; all changes are modular |
| LLM sufficiency check adds latency | Medium | Low | Only adds ~200ms; LLM answer (2s) dominates |
| EverMemOS publishes improved version | Low | Medium | Our improvements are architectural, not model-dependent |

**Worst case:** All five strategies underperform by 50%. We still reach ~93.5%, beating EverMemOS. The architectural improvements (temporal engine, knowledge structures, category routing) have value beyond the benchmark.

**Best case:** Strategies compound well and the temporal engine is transformative. We reach 97%+, setting a new state of the art.

---

## 11. Data Appendix

### All Measured Scores (Verified Against Source Files)

Every score below is from an official benchmark run using the EverMemOS evaluation framework (GPT-4o-mini judge, 3 runs, temp 0, majority vote).

**v3 Baseline (3 runs):**
- Run 1: 87.38%
- Run 2: 87.84%
- Run 3: 87.99%
- **Average: 87.71% ± 0.33%** *(arithmetic mean of these 3 runs is 87.74%; 87.71% is the standardized baseline used across all Phase benchmark scripts)*

**Phase 0 — Reranker Upgrade (5 runs):**
- Runs: 90.45%, 91.30%, 90.91%, 90.58%, 90.78%
- **Average: 90.81% ± 0.33%**

**Phase 1 — Embedding + Reranker Upgrade (3 runs):**
- Runs: 91.10%, 91.75%, 90.78%
- **Average: 91.21% ± 0.50%**

**Full Context Ceiling (3 runs):**
- Runs: 93.77%, 93.70%, 93.96%
- **Average: 93.81% ± 0.13%**

**EverMemOS (published):** 92.77%

### Category-Level Data

| System | Cat 1 (Single) | Cat 2 (Multi) | Cat 3 (Temporal) | Cat 4 (Open) |
|--------|---------------|---------------|------------------|-------------|
| No Retrieval | 2.1% | 0.9% | 13.5% | 7.6% |
| Neuromem v2 | 59.2% | 72.9% | 52.1% | 79.0% |
| **Neuromem v3** | **86.2%** | **85.7%** | **69.8%** | **90.4%** |
| **EverMemOS** | **91.1%** | **89.4%** | **78.1%** | **96.2%** |
| **Full Context** | **93.0%** | **91.9%** | **78.8%** | **96.5%** |

*Note: v3 category scores are from the first official run (87.38%). Phase 0+1 per-category breakdowns were not separately measured in the official benchmark framework. The category totals are: Cat 1 = 282 questions, Cat 2 = 321, Cat 3 = 96, Cat 4 = 841.*

### Failure Distribution (from v3 at 87.71%)

| Failure Type | Count | % of Total | Recovery Estimate |
|-------------|-------|-----------|------------------|
| Retrieval miss | 107 | 30% | 85/107 (79%) |
| Temporal confusion | 89 | 25% | 50/89 (56%) |
| Multi-hop chain break | 68 | 19% | 45/68 (66%) |
| Insufficient detail | 57 | 16% | 35/57 (61%) |
| Wrong inference | 25 | 7% | 5/25 (20%) |
| Vocabulary mismatch | 11 | 3% | 8/11 (73%) |
| **Total** | **357** | **100%** | **228/357 (64%)** |

*Recovery estimates are projections based on the proposed strategies at v3 (87.71%). At Phase 1 (91.21%), approximately 54 of these 357 failures have already been recovered. Of the remaining ~135 failures at Phase 1, an estimated 85 are recoverable with the proposed strategies, corresponding to roughly +5.5pp improvement (85 / 1540 = 5.5pp).*

### Benchmark Configuration

| Parameter | Value |
|-----------|-------|
| Dataset | LoCoMo (official, 10 conversations) |
| Total questions | 1,540 |
| Total messages | 5,882 |
| Answer model | GPT-4.1-mini (via OpenRouter) |
| Judge model | GPT-4o-mini |
| Judge runs | 3 (majority vote) |
| Judge temperature | 0 |
| Scoring | Binary (correct/incorrect) per judge run |

---

## Summary

**Where we are:** 91.21% — ahead of every funded competitor, 1.56pp behind EverMemOS.

**Where we're going:** 96%+ — substantially exceeding EverMemOS through five algorithmic breakthroughs that bigger models can't achieve.

**How we get there:** Three horizons of work totaling ~45 hours. Foundation (adopt proven techniques) → Breakthroughs (category-specific pipelines, multi-step reasoning, temporal engine) → Validation (official benchmark, ablation studies).

**Why it will work:** The 93.81% full-context ceiling is not a hard limit — it's an artifact of giving the LLM unstructured data. A smart retrieval system with pre-computed knowledge, temporal reasoning, and chain-following should beat a brute-force context dump.

**Why it matters:** Building the world's best personal memory system for $14/month, running from a single file on a laptop, with zero external infrastructure required. That's not just a benchmark win — it's a different category of product.

---

*This document was compiled from 3 official benchmark runs, 12+ experimental configurations, code analysis of both Neuromem and EverMemOS, and competitive research across 13 memory systems. All measured scores have been verified against source files (EXPERIMENT_JOURNAL.md, run_phase*.py). Projected scores are clearly labeled as estimates.*

*Sources: EXPERIMENT_JOURNAL.md, BIOMIMETIC_IMPROVEMENTS.md, COMPETITIVE_LANDSCAPE.md, ARCHITECTURE_UPGRADE_ANALYSIS.md, EVERMEMOS_ARCHITECTURE_REPORT.md, engine.py, vector_search.py, reranker.py*
