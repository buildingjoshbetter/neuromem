"""
M1 Test Queries: 20 queries across 5 categories.

Each query has:
- query: the search question
- category: what type of retrieval this tests
- expected: what a GOOD system should return (human-judged gold standard)
- notes: why this query is interesting/tricky
"""

TEST_QUERIES = [
    # ============================================
    # Category 1: EXACT RECALL (specific facts)
    # A good memory system should find specific details
    # ============================================
    {
        "id": 1,
        "query": "What is the name of Josh's dog?",
        "category": "exact_recall",
        "expected": "Luna, a 2-year-old golden retriever mix adopted from Austin Pets Alive",
        "notes": "Requires finding specific named entity across multiple messages"
    },
    {
        "id": 2,
        "query": "What embedding model is being used for the memory system?",
        "category": "exact_recall",
        "expected": "Model2Vec potion-base-8M, 256 dimensions, 30MB, CPU-only",
        "notes": "Technical fact retrieval -- specific model name and specs"
    },
    {
        "id": 3,
        "query": "How much did Mem0 raise in funding?",
        "category": "exact_recall",
        "expected": "$24M",
        "notes": "Simple factual lookup"
    },
    {
        "id": 4,
        "query": "What is Josh's running pace?",
        "category": "exact_recall",
        "expected": "7:12 per mile average on a 10-mile run, new PR by 4 minutes",
        "notes": "Specific numerical detail from a personal message"
    },

    # ============================================
    # Category 2: SEMANTIC SEARCH (meaning-based)
    # System should find relevant results by meaning, not just keywords
    # ============================================
    {
        "id": 5,
        "query": "What has Josh been doing to stay healthy?",
        "category": "semantic",
        "expected": "Running (10-mile PR, half marathon signup, evening runs), gym (leg day, upper body), Whoop tracking, creatine supplementation, morning meditation",
        "notes": "No message contains 'stay healthy' -- requires understanding semantic meaning across many messages"
    },
    {
        "id": 6,
        "query": "What is the competitive landscape for the memory system product?",
        "category": "semantic",
        "expected": "Mem0 ($24M raised), SuperMemory ($2.6M raised, simpler product), Rewind AI (acquired by Meta), Screenpipe (OSS, basic)",
        "notes": "Requires connecting messages about different competitors into a coherent picture"
    },
    {
        "id": 7,
        "query": "How does Josh feel about Austin as a city?",
        "category": "semantic",
        "expected": "Lives there, enjoys food scene (ramen, breakfast tacos, Veracruz), active lifestyle (running, gym, Zilker), frustrated with ERCOT/power outages, considering moving within Austin (east side)",
        "notes": "Requires inferring sentiment from multiple indirect references"
    },
    {
        "id": 8,
        "query": "What are the key technical innovations in the neuromem architecture?",
        "category": "semantic",
        "expected": "6-layer architecture, predictive coding filter (stores only 7%), dual-rate learning, EWC identity drift protection, per-entity salience, RRF hybrid search, MCP integration",
        "notes": "Requires synthesizing technical details scattered across many messages"
    },

    # ============================================
    # Category 3: TEMPORAL (time-based queries)
    # System should understand recency and time context
    # ============================================
    {
        "id": 9,
        "query": "What happened this week?",
        "category": "temporal",
        "expected": "Messages from the last 7 days: GitHub hit 500 stars, 10K Twitter followers, east Austin apartment listing, MCP server working, filed trademark, HRV/meditation insight",
        "notes": "Requires understanding 'this week' relative to the dataset's timeline"
    },
    {
        "id": 10,
        "query": "What was Josh working on last month?",
        "category": "temporal",
        "expected": "Older messages: testing Pinecone vs sqlite-vec, benchmarking embedding models, chunk size experiments, early business model discussions",
        "notes": "Requires filtering to a time window AND understanding what 'working on' means"
    },
    {
        "id": 11,
        "query": "When is Josh's parents' visit planned for?",
        "category": "temporal",
        "expected": "May (originally April but pushed back due to dad's doctor appointment)",
        "notes": "Tests contradiction handling -- the answer CHANGED over time. Should return the LATEST information"
    },
    {
        "id": 12,
        "query": "What are Josh's upcoming events?",
        "category": "temporal",
        "expected": "Coffee with Priya (Tuesday at Epoch Coffee), COTA F1 race in October, half marathon in November, lease renewal by April 15, YC deadline in 6 weeks",
        "notes": "Requires understanding which scheduled events are in the future vs past"
    },

    # ============================================
    # Category 4: ENTITY-SPECIFIC (person/context filtering)
    # System should differentiate between people and contexts
    # ============================================
    {
        "id": 13,
        "query": "What does Josh talk about with Marcus?",
        "category": "entity",
        "expected": "Cars (Ferrari, Rivian), fitness (running, gym, Whoop), F1 (COTA paddock passes), dog (Luna chewing shoes), creatine",
        "notes": "Should isolate Marcus-specific conversations from all others"
    },
    {
        "id": 14,
        "query": "What does Josh discuss with Alex vs Sarah?",
        "category": "entity",
        "expected": "Alex: business strategy, technical architecture, fundraising, hiring. Sarah: personal life, book, dog adoption, birthday, sister's engagement, podcast idea",
        "notes": "Should show distinct topic patterns per relationship"
    },
    {
        "id": 15,
        "query": "Who is Priya?",
        "category": "entity",
        "expected": "ML engineer met at Austin AI meetup, worked at OpenAI, potential advisor, coffee scheduled at Epoch Coffee",
        "notes": "Entity that appears in only a few messages -- tests ability to construct a profile from sparse data"
    },
    {
        "id": 16,
        "query": "What is Alex's role in the company?",
        "category": "entity",
        "expected": "Co-founder/partner -- handles paperwork (LLC filing), reviews API docs, manages support emails, discusses strategy and technical decisions with Josh",
        "notes": "Requires inferring role from behavior across messages, not from explicit statement"
    },

    # ============================================
    # Category 5: CONSOLIDATION / CONTRADICTION
    # System should handle conflicting information correctly
    # ============================================
    {
        "id": 17,
        "query": "What vector database is the project using?",
        "category": "consolidation",
        "expected": "sqlite-vec (originally considered Pinecone but switched after benchmarking showed it was overkill)",
        "notes": "Contradiction: early message says Pinecone, later message says sqlite-vec. Should return CURRENT answer"
    },
    {
        "id": 18,
        "query": "What is the pricing strategy for neuromem?",
        "category": "consolidation",
        "expected": "Open source core with managed cloud offering at $97/mo (MongoDB model). Originally considered $50/mo flat pricing",
        "notes": "Contradiction: pricing changed from $50 to open-source + $97 cloud. Should prefer latest"
    },
    {
        "id": 19,
        "query": "When does Josh run?",
        "category": "consolidation",
        "expected": "Evenings (switched from morning runs to keep mornings for deep work)",
        "notes": "Contradiction: first said 6am morning runs, later switched to evenings. Should return current habit"
    },
    {
        "id": 20,
        "query": "Does Josh need to hire anyone?",
        "category": "consolidation",
        "expected": "Yes -- met Priya (ML engineer, ex-OpenAI) at meetup, scheduling coffee, considering as advisor or more. Originally said no hiring needed",
        "notes": "Contradiction: first said no hiring, later found Priya. Tests whether system captures the evolution of thinking"
    },
]

if __name__ == "__main__":
    print(f"Total queries: {len(TEST_QUERIES)}")
    print(f"\nBy category:")
    cats = {}
    for q in TEST_QUERIES:
        cat = q["category"]
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    print(f"\n{'='*60}")
    for q in TEST_QUERIES:
        print(f"\nQ{q['id']} [{q['category']}]: {q['query']}")
        print(f"  Expected: {q['expected'][:100]}...")
