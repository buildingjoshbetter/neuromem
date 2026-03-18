"""
Generalist Benchmark Queries v2 — 60 queries across 12 categories.
Designed to be UNBIASED — each category tests capabilities that
different architectures excel at. Not optimized for any one system.

Scoring: Each query has 'expected' and 'scoring_notes'.
Queries are rated: HIT (correct answer), PARTIAL (some correct info),
MISS (wrong/irrelevant), ERROR (system failed to respond).

Character: Jordan Chen, 28yo founder of CarbonSense (climate-tech startup)
Timeline: July 2024 — April 2026
"""

TEST_QUERIES_V2 = [
    # ================================================================
    # CATEGORY 1: EXACT RECALL (5 queries)
    # Can the system find specific facts verbatim?
    # Favors: Vector search, keyword search
    # ================================================================
    {
        "id": 1,
        "query": "What is the name of Jordan's dog?",
        "category": "exact_recall",
        "expected": "Biscuit, a Pembroke Welsh Corgi, born March 15, 2023",
        "scoring_notes": "HIT requires breed and name. PARTIAL if only name.",
    },
    {
        "id": 2,
        "query": "How much funding did CarbonSense raise in the seed round?",
        "category": "exact_recall",
        "expected": "$1.5M from Elevation Ventures at $10M post-money valuation",
        "scoring_notes": "HIT requires amount and source. PARTIAL if only amount.",
    },
    {
        "id": 3,
        "query": "What was the scope 1 accuracy on the Meridian Steel pilot?",
        "category": "exact_recall",
        "expected": "96.1% (initially projected 90%, exceeded expectations)",
        "scoring_notes": "HIT requires 96.1%. PARTIAL if close but wrong number.",
    },
    {
        "id": 4,
        "query": "What is Jordan's half marathon finish time?",
        "category": "exact_recall",
        "expected": "1:52:34 at the Austin Half Marathon on April 6, 2025",
        "scoring_notes": "HIT requires exact time. PARTIAL if event is correct but time is wrong.",
    },
    {
        "id": 5,
        "query": "What is the address of Jordan's new house?",
        "category": "exact_recall",
        "expected": "2847 Chicon St, Austin TX 78702. 4 bed/2 bath, $495,000, closed October 15, 2025",
        "scoring_notes": "HIT requires address. PARTIAL if any detail is correct.",
    },

    # ================================================================
    # CATEGORY 2: SEMANTIC SEARCH (5 queries)
    # Can the system understand meaning, not just keywords?
    # Favors: LLM extraction, embedding quality
    # ================================================================
    {
        "id": 6,
        "query": "What has Jordan been doing to manage stress?",
        "category": "semantic",
        "expected": "Therapy with Dr. Linda Choi (CBT, biweekly), meditation (Headspace then Insight Timer), 7pm work hard stop, running, yoga on Sundays",
        "scoring_notes": "HIT requires therapy + at least 2 other methods. PARTIAL if only one method.",
    },
    {
        "id": 7,
        "query": "What is CarbonSense's competitive advantage over EcoTrace?",
        "category": "semantic",
        "expected": "Higher accuracy (96% vs 89%), real-time capability vs batch, scope 3 capability (EcoTrace doesn't have it), 0% churn vs high churn. Nina: 'EcoTrace is a faster horse, you're building a car'",
        "scoring_notes": "HIT requires accuracy difference + scope 3. PARTIAL if only one advantage.",
    },
    {
        "id": 8,
        "query": "How does Jordan feel about Austin?",
        "category": "semantic",
        "expected": "Loves it — food (ramen, Veracruz tacos, Uchi), outdoor life (Zilker, Lady Bird Lake, Barton Springs), F1 at COTA. Complaints: extreme heat (106 degrees), ERCOT grid failures, cedar allergies, traffic on I-35. Bought a house in East Austin.",
        "scoring_notes": "HIT requires both positive and negative. PARTIAL if only one side.",
    },
    {
        "id": 9,
        "query": "What is the CarbonSense tech stack?",
        "category": "semantic",
        "expected": "Go API layer (rewritten from Python May 2025) + Python ML pipelines, gRPC communication. PostgreSQL + ClickHouse (migrated from Postgres). React 18 + TypeScript + Vite + Tailwind. AWS (ECS, S3, CloudFront). Scope 3 uses Graph Attention Networks.",
        "scoring_notes": "HIT requires Go + Python + ClickHouse. PARTIAL if some components correct.",
    },
    {
        "id": 10,
        "query": "What books has Jordan read or been recommended?",
        "category": "semantic",
        "expected": "Read: The Hard Thing About Hard Things (5 stars), Zero to One, Measure What Matters, The Lean Startup, Thinking Fast and Slow, The Body Keeps the Score (therapist rec), Atomic Habits, Drawdown. Recommended: The Mom Test (by Dev), High Growth Handbook (by Dev), Burnout by Emily Nagoski (Riley's professor)",
        "scoring_notes": "HIT requires 4+ books with any context. PARTIAL if 2-3 books.",
    },

    # ================================================================
    # CATEGORY 3: TEMPORAL REASONING (5 queries)
    # Can the system understand time, recency, sequences?
    # Favors: Temporal knowledge graphs (Zep/Graphiti)
    # ================================================================
    {
        "id": 11,
        "query": "What happened in the month after Demo Day (June 15, 2025)?",
        "category": "temporal",
        "expected": "14 investor follow-ups, 3 firms wanted to lead Series A (Sequoia, a16z, Khosla). Missed anniversary dinner (July 3). Health scare — chest tightness, started therapy. EcoTrace raised $40M and pivoted into their space.",
        "scoring_notes": "HIT requires 3+ events from June 15 - July 15 2025. PARTIAL if 1-2.",
    },
    {
        "id": 12,
        "query": "How did CarbonSense's MRR grow over time?",
        "category": "temporal",
        "expected": "$8,000 (Dec 2024) → $43,000 (May 2025) → $67,000 (July 2025) → $82,000 (Sep 2025) → ~$100,000 (Dec 2025, implied by $1.2M ARR)",
        "scoring_notes": "HIT requires at least 3 data points in correct order. PARTIAL if trend is correct but numbers wrong.",
    },
    {
        "id": 13,
        "query": "When did Jordan quit his job and what happened in the first month?",
        "category": "temporal",
        "expected": "Quit Dataflux July 29, 2024 (submitted notice July 16). First month: incorporated CarbonSense (July 25), set up infrastructure with Dev, started Meridian Steel pilot deployment, anxiety about money (only $45K savings + $47K 401k rollover).",
        "scoring_notes": "HIT requires quit date + 2 first-month events. PARTIAL if date only.",
    },
    {
        "id": 14,
        "query": "What are Jordan's upcoming events as of January 2026?",
        "category": "temporal",
        "expected": "Board meeting (Jan 15, 2026), Lily's birthday dinner at Uchi (Feb 8), Austin Marathon (Feb 16), Parents visiting (Feb 15-22), Riley's graduation (May 17), ACL Festival (Oct 10-12), Portland reunion (Aug 15), proposal (after Riley's graduation)",
        "scoring_notes": "HIT requires 4+ upcoming events. PARTIAL if 2-3.",
    },
    {
        "id": 15,
        "query": "What was Jordan's health trajectory from early 2025 to late 2025?",
        "category": "temporal",
        "expected": "Jan: Healthy (RHR 64, 7.2hr sleep, 8500 steps). Deteriorated through spring/summer. July: Crisis (RHR 72, 5.8hr sleep, 4200 steps, chest tightness, stress). Started therapy July 22. By Dec: Recovery (RHR 66, 7.0hr sleep, 7200 steps, VO2 Max 44).",
        "scoring_notes": "HIT requires decline + recovery arc with data. PARTIAL if trend without numbers.",
    },

    # ================================================================
    # CATEGORY 4: ENTITY DISAMBIGUATION (5 queries)
    # Can the system distinguish between different people/things?
    # Favors: Knowledge graphs, entity resolution
    # ================================================================
    {
        "id": 16,
        "query": "Who is Marcus? Be specific — there may be more than one.",
        "category": "entity",
        "expected": "Two Marcus: (1) Marcus Johnson — Jordan's gym buddy, does Olympic lifts (225 clean and jerk), met through Jake. (2) Lily's ex-boyfriend Marcus — met at Thanksgiving 2024, did CrossFit, they broke up August 2025 when he wanted to move to Seattle.",
        "scoring_notes": "HIT requires identifying BOTH Marcus. PARTIAL if only one.",
    },
    {
        "id": 17,
        "query": "What does Jordan discuss with Dev vs Sam?",
        "category": "entity",
        "expected": "Dev: Technical (architecture, databases, ML models, hiring engineers, infrastructure, security). Sam: Personal (life advice, relationships, career, F1, ACL, proposal plans, running). Some overlap on business strategy.",
        "scoring_notes": "HIT requires clear distinction with examples. PARTIAL if vaguely correct.",
    },
    {
        "id": 18,
        "query": "Who is Aisha Rahman and why is she important?",
        "category": "entity",
        "expected": "ML engineer, PhD in industrial emissions modeling, hired March 2025 at $135K + 0.75% equity. Built scope 3 model (84.7% → 88.9% accuracy). Got Google offer ($280K), was retained with raise to $160K + 1.25% + $30K student loan coverage. Collaborated with Chen Wei (Dr. Woo's PhD student) on ICML paper.",
        "scoring_notes": "HIT requires hire + scope 3 work + retention. PARTIAL if only basic facts.",
    },
    {
        "id": 19,
        "query": "Who is Rachel? Be specific — there may be more than one.",
        "category": "entity",
        "expected": "Two Rachel: (1) Rachel Torres — VP Sales at CarbonSense, hired August 2025, 12 years enterprise SaaS, $180K + 1% equity. Built TCO calculator, opened Houston office. (2) Rachel Kim — Riley's college friend from University of Oregon, now a doctor in Seattle.",
        "scoring_notes": "HIT requires both Rachels. PARTIAL if only one.",
    },
    {
        "id": 20,
        "query": "What is Nina Vasquez's relationship with CarbonSense?",
        "category": "entity",
        "expected": "Partner at Elevation Ventures, led their $1.5M seed investment. Met Jordan at Epoch Coffee Nov 20, 2024 (wore orange scarf). Has a board seat. Advises on strategy, pricing, fundraising. Mentioned EcoTrace as portfolio company/competitor. Pushed pricing higher. Connected Jordan to Rachel Torres. Recommended Series B in Q2 2026.",
        "scoring_notes": "HIT requires investor + specific interactions. PARTIAL if only role.",
    },

    # ================================================================
    # CATEGORY 5: CONTRADICTION RESOLUTION (5 queries)
    # Does the system return current/correct info when facts changed?
    # Favors: Temporal KGs, bi-temporal models (Zep)
    # ================================================================
    {
        "id": 21,
        "query": "What database does CarbonSense use for time series data?",
        "category": "contradiction",
        "expected": "ClickHouse (migrated from PostgreSQL via TimescaleDB consideration in May 2025. Postgres had 2.3s query times, TimescaleDB wasn't fast enough, ClickHouse got it to 47ms. Postgres still used for users/auth/billing.)",
        "scoring_notes": "HIT requires ClickHouse as current + migration context. MISS if says PostgreSQL or TimescaleDB as current.",
    },
    {
        "id": 22,
        "query": "What is CarbonSense's pricing?",
        "category": "contradiction",
        "expected": "$5,000/facility base, $12,000/facility enterprise (changed from original $2,000/$5,000 in March 2025 per Nina's advice). Meridian grandfathered at $2K for year 1.",
        "scoring_notes": "HIT requires current pricing ($5K). MISS if says $2K as current.",
    },
    {
        "id": 23,
        "query": "Where is CarbonSense's office?",
        "category": "contradiction",
        "expected": "WeWork Austin (switched October 2025 from leased office at 2847 E Cesar Chavez. Originally considered Domain and Springdale locations but chose WeWork for flexibility. Also has WeWork Houston satellite for Rachel's sales team.)",
        "scoring_notes": "HIT requires WeWork. MISS if says E Cesar Chavez or Domain.",
    },
    {
        "id": 24,
        "query": "When does Jordan go to the gym?",
        "category": "contradiction",
        "expected": "Mornings again (as of October 2025). Originally mornings at 6am, switched to evenings in June 2025 (couldn't sync with Jake who coaches little league). Back to mornings after the 7pm work boundary started working.",
        "scoring_notes": "HIT requires morning as current + evolution. PARTIAL if just 'mornings' without context.",
    },
    {
        "id": 25,
        "query": "What veterinarian does Biscuit go to?",
        "category": "contradiction",
        "expected": "Thrive Veterinary on Burnet Road (switched from Heart of Texas on South Lamar after a billing issue). Also had emergency visit at Veterinary Emergency Clinic of Austin in Dec 2024 for chicken bone ingestion.",
        "scoring_notes": "HIT requires Thrive. MISS if says Heart of Texas.",
    },

    # ================================================================
    # CATEGORY 6: MULTI-HOP REASONING (5 queries)
    # Answer requires connecting facts from different messages
    # Favors: Graph traversal, LLM reasoning
    # ================================================================
    {
        "id": 26,
        "query": "How did Dr. Woo's lab contribute to CarbonSense's product improvement?",
        "category": "multi_hop",
        "expected": "Dr. Woo (UT Austin professor, advisor) sponsored PhD student Chen Wei → Chen Wei developed synthetic data augmentation technique (VAE) → Generated 50K training samples from 2K real data points → This improved scope 3 accuracy from 84.7% to 88.9% → Chen Wei published this at ICML 2026. Also, Dr. Woo recommended hiring Aisha Rahman (former postdoc), who built the scope 3 model.",
        "scoring_notes": "HIT requires Dr. Woo → Chen Wei → accuracy improvement chain. PARTIAL if only one link.",
    },
    {
        "id": 27,
        "query": "How did Riley influence Jordan's mental health recovery?",
        "category": "multi_hop",
        "expected": "Riley's professor (Dr. Martinez) recommended the book 'Burnout'. Later Riley recommended Dr. Linda Choi (from Dr. Martinez) → Jordan started therapy July 22, 2025 → Therapy led to 7pm work boundary → Better sleep and health metrics → Saved the relationship → Jordan planning to propose.",
        "scoring_notes": "HIT requires Riley → Dr. Choi recommendation → therapy → improvement chain. PARTIAL if 2 links.",
    },
    {
        "id": 28,
        "query": "Trace the path from Jordan's birthday to the Series A term sheet.",
        "category": "multi_hop",
        "expected": "Sept 14, 2024 birthday → Sam gifted COTA F1 paddock passes → At some point met Nina Vasquez (Nov 15) → Coffee at Epoch (Nov 20) → Applied to Elevation cohort (Jan 15 deadline) → Accepted (Feb 10) → Cohort + Demo Day (June 15) → 14 investor meetings → Khosla term sheet (Aug 10) → Series A signed (Aug 25)",
        "scoring_notes": "HIT requires at least 4 links in the chain. PARTIAL if 2-3 links.",
    },
    {
        "id": 29,
        "query": "How did Sam's involvement with CarbonSense evolve?",
        "category": "multi_hop",
        "expected": "Started as advisor/sounding board → Helped mock pitch for Elevation interview → Did moonlighting sales consulting (part-time) → Helped close Lone Star negotiation → CarbonSense hired Rachel Torres as real VP Sales (Aug 2025) → Sam stepped back → Now considering his own fintech startup idea inspired by CarbonSense experience",
        "scoring_notes": "HIT requires progression from advisor → sales → stepped back → own idea. PARTIAL if 2 stages.",
    },
    {
        "id": 30,
        "query": "What is the connection between the EPA regulations and CarbonSense's growth?",
        "category": "multi_hop",
        "expected": "EPA released new scope 3 reporting requirements for manufacturers >$100M revenue → This expanded CarbonSense TAM from $2B to $8B → Made product essentially mandatory → Drove massive inbound demand → Nina used this in fundraise positioning → Directly led to Series A success. Similarly, EU CSRD mandate drives European expansion via KlimaSync partnership.",
        "scoring_notes": "HIT requires EPA → TAM expansion → growth connection. PARTIAL if only mentions regulations.",
    },

    # ================================================================
    # CATEGORY 7: CROSS-MODAL RETRIEVAL (5 queries)
    # Can the system find info across different data types?
    # Favors: Unified storage, metadata-aware search
    # ================================================================
    {
        "id": 31,
        "query": "How much does Jordan spend at restaurants per month?",
        "category": "cross_modal",
        "expected": "Various OCR receipts show: Uchi Valentine's $452, Epoch Coffee $13, Torchy's $20, Thai-Kun $16, Veracruz $8, Uchiko anniversary $48, MT Supermarket $32 (groceries). Plus mentions of Dai Due, Odd Duck, Pie Society. Moderate restaurant spending, mix of casual and special occasion.",
        "scoring_notes": "HIT requires data from OCR receipts + text mentions. PARTIAL if only one source.",
    },
    {
        "id": 32,
        "query": "What is Biscuit's complete medical history?",
        "category": "cross_modal",
        "expected": "From vet records (OCR): DOB March 15, 2023, Corgi, weight issues (28.4 lbs Mar 2025, 30.1 lbs Sep 2025). Vaccinations updated March 2025 at Thrive. Emergency visit Dec 2024 for chicken bone ingestion ($795). Bee sting Sept 2024 (Benadryl). From texts: puking from farmer's market treats, overweight from neighbor treats, rolled in something dead.",
        "scoring_notes": "HIT requires OCR health records + text anecdotes. PARTIAL if only one source.",
    },
    {
        "id": 33,
        "query": "What is CarbonSense's financial position as of late 2025?",
        "category": "cross_modal",
        "expected": "From email (investor update): $1.2M ARR, 15 customers, 42 facilities. From OCR (Mercury bank): $10.8M checking, $95K monthly burn, 24 months runway. From OCR (cap table): Post-Series A, Jordan 33.1%, Dev 26.5%, Khosla 18%, Elevation 11.7%. From text: discussing Series B at $200-300M valuation for Q2 2026.",
        "scoring_notes": "HIT requires financial data from 3+ modalities. PARTIAL if 1-2 modalities.",
    },
    {
        "id": 34,
        "query": "What do calendar events reveal about Jordan's priorities?",
        "category": "cross_modal",
        "expected": "Mix of personal and professional: board meetings, therapy, vet appointments, partner's graduation, marathon, family visits, housewarming, F1 race, ACL festival, anniversary (which he missed per text). Shows attempt to balance work and personal life. Calendar note for anniversary says 'DO NOT SCHEDULE CALLS AFTER 5PM'.",
        "scoring_notes": "HIT requires calendar + text cross-reference. PARTIAL if calendar only.",
    },
    {
        "id": 35,
        "query": "What products has Jordan purchased for the new house?",
        "category": "cross_modal",
        "expected": "From OCR: Weber Spirit II grill ($449), propane, grill tools, paint supplies ($410 at Sherwin-Williams — ExtraWhite + Roycroft Bottle Green). From texts: mentioned Google Fiber 2 gig internet. From notes: plans for standing desk, raised garden beds, dog run, KIVIK couch recommendation to Lily (but that was Lily's apt). From calendar: house closing costs $12,847.",
        "scoring_notes": "HIT requires purchase details from OCR + text. PARTIAL if only one source.",
    },

    # ================================================================
    # CATEGORY 8: PERSONALITY & PREFERENCE INFERENCE (5 queries)
    # Can the system build a profile from scattered data?
    # Favors: LLM synthesis, pattern recognition
    # ================================================================
    {
        "id": 36,
        "query": "What kind of person is Jordan?",
        "category": "personality",
        "expected": "Driven, ambitious founder who struggles with work-life balance. Cares deeply about people (Riley, family, team). Tends to overcommit and prioritize work. Self-aware enough to seek therapy. Values authenticity and impact over money. Nerdy (Pi Day restaurant, Severance, tech discussions). Active but inconsistent (gym, running, yoga). Loyal friend. Anxious about failure.",
        "scoring_notes": "HIT requires 4+ personality traits with evidence. PARTIAL if 2-3 traits.",
    },
    {
        "id": 37,
        "query": "What does Jordan eat and drink?",
        "category": "personality",
        "expected": "Coffee: oat milk lattes (Epoch Coffee favorite). Food: breakfast tacos (Veracruz), ramen, sushi (Uchi/Uchiko), Thai (pad kra pao), mom's dumplings, mapo tofu. Cooks: lemon garlic salmon. Supplements: creatine, protein powder. Tried weekday vegetarian but quit after 2 weeks. Overnight oats or eggs for breakfast. Beer (Asahi at dinners).",
        "scoring_notes": "HIT requires 5+ specific food/drink preferences. PARTIAL if 2-4.",
    },
    {
        "id": 38,
        "query": "How does Jordan communicate differently with different people?",
        "category": "personality",
        "expected": "With Dev: technical, direct, tactical. With Sam: casual, emotional, vulnerable. With Riley: loving, sometimes apologetic (re: work). With Mom: reassuring, filters bad news. With Jake: bro-ish, gym talk. With Nina: professional but warm. With Lily: protective big brother. Emails are formal, texts are casual.",
        "scoring_notes": "HIT requires 4+ distinct communication patterns. PARTIAL if 2-3.",
    },
    {
        "id": 39,
        "query": "What are Jordan's biggest fears and insecurities?",
        "category": "personality",
        "expected": "Fear of failure (multiple notes about 'what if we fail'), running out of money (tracked savings obsessively early on), losing Riley due to work obsession, not being present enough for family, tying self-worth to company performance (explored in therapy — connected to immigrant parent upbringing), health deterioration from stress.",
        "scoring_notes": "HIT requires 3+ fears with supporting evidence. PARTIAL if 1-2.",
    },
    {
        "id": 40,
        "query": "What is Jordan's morning routine?",
        "category": "personality",
        "expected": "Wake 6am, meditate 10 min (switched from Headspace to Insight Timer Aug 2025), gym or run, shower, breakfast (overnight oats or eggs), work by 8:30. This routine has been inconsistent — disrupted during intense work periods (fundraising, Demo Day prep).",
        "scoring_notes": "HIT requires routine + app change + inconsistency. PARTIAL if just routine.",
    },

    # ================================================================
    # CATEGORY 9: NEGATION & FALSE PREMISES (5 queries)
    # System should NOT return false information
    # Favors: Precise systems, low hallucination
    # ================================================================
    {
        "id": 41,
        "query": "Did CarbonSense acquire EcoTrace?",
        "category": "negation",
        "expected": "No. Jordan asked Nina about it (July 2025) and she said 'absolutely not' — EcoTrace raised $40M and wouldn't sell for less than $100M. CarbonSense's strategy is to compete on accuracy, not acquire.",
        "scoring_notes": "HIT requires clear 'no' with context. MISS if suggests acquisition happened.",
    },
    {
        "id": 42,
        "query": "Does CarbonSense use Kubernetes?",
        "category": "negation",
        "expected": "No. Dev asked about it and Jordan said 'definitely not, k8s is overkill for our stage. ECS is fine.' They use AWS ECS for container orchestration.",
        "scoring_notes": "HIT requires clear 'no' with ECS alternative. MISS if suggests they use K8s.",
    },
    {
        "id": 43,
        "query": "Is Sam an employee of CarbonSense?",
        "category": "negation",
        "expected": "No. Sam did part-time sales consulting/moonlighting but was never a full-time employee. Jordan explicitly said 'no i'm not hiring sam as a full time employee.' Sam has his own job and is now considering his own fintech startup.",
        "scoring_notes": "HIT requires clear 'no' with context. MISS if says Sam is an employee.",
    },
    {
        "id": 44,
        "query": "Did Jordan get a second dog?",
        "category": "negation",
        "expected": "No. Jordan wanted to (saw a golden retriever puppy at the shelter in Dec 2025) but Riley said no — Biscuit needs to lose weight first. Riley said 'ask me again in spring, MAYBE.'",
        "scoring_notes": "HIT requires clear 'no' with the discussion details. MISS if suggests they got one.",
    },
    {
        "id": 45,
        "query": "Did Jordan propose to Riley?",
        "category": "negation",
        "expected": "Not yet as of December 2025. He bought a vintage art deco ring ($4,200 from Fredericksburg estate sale, on layaway). Plan is to propose after Riley's graduation (May 17, 2026) at Lady Bird Lake at sunset. Sam and Lily know. Parents don't.",
        "scoring_notes": "HIT requires 'not yet' + plan details. MISS if says he proposed.",
    },

    # ================================================================
    # CATEGORY 10: SUMMARIZATION & CONSOLIDATION (5 queries)
    # Can the system synthesize large amounts of info?
    # Favors: LLM reasoning, hierarchical memory
    # ================================================================
    {
        "id": 46,
        "query": "Summarize the CarbonSense journey from founding to Series A.",
        "category": "consolidation",
        "expected": "Side project (pre-July 2024) → Jordan quits Dataflux (July 29) → Delaware C-Corp incorporation (July 25) → Meridian Steel pilot (Aug-Oct, 96.1% accuracy) → 3 pilots total → Met Nina at Epoch Coffee (Nov 20) → Applied to Elevation (Jan 15) → Accepted, $1.5M seed at $10M (Feb 10) → Hired Aisha (Mar) → 7 customers, $43K MRR (May) → Demo Day (June 15) → 14 investors → Khosla term sheet $10M at $55M pre (Aug 10) → Series A closed (Aug 25) → $65M company, 14 employees, $1.2M ARR by Dec 2025.",
        "scoring_notes": "HIT requires 6+ milestones in chronological order. PARTIAL if 3-5.",
    },
    {
        "id": 47,
        "query": "Summarize Jordan and Riley's relationship over this period.",
        "category": "consolidation",
        "expected": "Supportive but strained. Riley supported the startup decision. Fredericksburg weekend (Jan 2025). Valentine's at Uchi. But Jordan increasingly absent — missed anniversary (July 3). Riley pushed therapy recommendation. Things improved after 7pm boundary. Bought house together (Oct 2025). Jordan planning to propose after Riley's graduation (May 2026). Riley finishing Master's in counseling psych at UT.",
        "scoring_notes": "HIT requires arc (support → strain → recovery) with milestones. PARTIAL if flat summary.",
    },
    {
        "id": 48,
        "query": "What is the full team at CarbonSense as of December 2025?",
        "category": "consolidation",
        "expected": "14 people: CEO Jordan Chen, CTO Dev Patel, ML Engineer Aisha Rahman, Backend: Luis Moreno + Preet Kaur, Frontend: Danny Okafor, VP Sales: Rachel Torres, AEs: Mike Chen + Sarah Lindquist, SDR: Jamie Walsh, Customer Success: Tanya Reed, Product Manager: Omar Hassan, Office Admin: Becky Tran. Plus sponsored PhD student Chen Wei at UT Austin.",
        "scoring_notes": "HIT requires 8+ names with roles. PARTIAL if 4-7.",
    },
    {
        "id": 49,
        "query": "What are all the places Jordan frequents in Austin?",
        "category": "consolidation",
        "expected": "Restaurants: Uchi, Uchiko, Veracruz All Natural, Torchy's, Thai-Kun, Dai Due, Odd Duck, Pie Society, el primo (Lily's rec). Coffee: Epoch Coffee. Grocery: HEB Mueller, MT Supermarket, Whole Foods, Costco. Gym: Gold's South Lamar → Lifetime on Burnet. Outdoors: Zilker Park, Lady Bird Lake, Barton Springs. Shopping: REI, Home Depot, Apple Store Domain. Events: COTA, ACL at Zilker. Vet: Thrive on Burnet. Therapy: 4301 W William Cannon.",
        "scoring_notes": "HIT requires 10+ locations across categories. PARTIAL if 5-9.",
    },
    {
        "id": 50,
        "query": "What were the key turning points in CarbonSense's trajectory?",
        "category": "consolidation",
        "expected": "1. Meridian pilot exceeding targets (Oct 2024). 2. Meeting Nina Vasquez (Nov 2024). 3. EPA scope 3 mandate expanding TAM to $8B (Jan 2025). 4. Elevation seed acceptance (Feb 2025). 5. Hiring Aisha (Mar 2025, scope 3 capability). 6. Go rewrite for performance (May 2025). 7. Demo Day (June 2025). 8. Khosla Series A (Aug 2025). 9. TechCrunch feature (Sep 2025). 10. KlimaSync European partnership (Nov 2025).",
        "scoring_notes": "HIT requires 5+ turning points. PARTIAL if 3-4.",
    },

    # ================================================================
    # CATEGORY 11: OCR-SPECIFIC RETRIEVAL (5 queries)
    # Can the system search OCR/document data effectively?
    # Favors: Full-text search (FTS5), metadata filtering
    # ================================================================
    {
        "id": 51,
        "query": "What credit cards does Jordan use?",
        "category": "ocr_retrieval",
        "expected": "Visa ending 4821 (personal — groceries, gas, restaurants). Amex ending 9012 (higher-end purchases — Uchi, REI, running gear). CarbonSense has a company Amex (MacBook purchase). Mercury checking for company expenses.",
        "scoring_notes": "HIT requires both card numbers with usage patterns. PARTIAL if just card numbers.",
    },
    {
        "id": 52,
        "query": "What is Jordan's old apartment address?",
        "category": "ocr_retrieval",
        "expected": "1847 E Riverside Dr, Apt 4A, Austin TX 78741 (from Amazon delivery OCR). Rent was $2,100, raised to $2,350 at renewal. Moved to 2847 Chicon St in October 2025.",
        "scoring_notes": "HIT requires address. PARTIAL if approximate location only.",
    },
    {
        "id": 53,
        "query": "What are Jordan's fitness stats from Strava?",
        "category": "ocr_retrieval",
        "expected": "2025 year summary: 127 runs, 482 miles, 8:18 avg pace, best 5K 22:48 (Oct PR), half marathon 1:52:34. March 2025: 14 runs, 52.3 miles, 8:24 pace, 5K PR 23:12. Trained 18 weeks for Austin Marathon (Feb 2026 goal: sub 4 hours).",
        "scoring_notes": "HIT requires yearly stats + half marathon time. PARTIAL if only one data point.",
    },
    {
        "id": 54,
        "query": "What does the cap table look like after Series A?",
        "category": "ocr_retrieval",
        "expected": "Jordan 33.1% (4,250,000), Dev 26.5% (3,400,000), Khosla 18.0% (2,307,692), Elevation 11.7% (1,500,000), Option pool 10.8%. Key employee equity: Aisha 0.97%, Rachel 1.0%, Luis/Preet/Danny 0.3% each. Total shares: 12,850,000. 409A: $5.06/share.",
        "scoring_notes": "HIT requires 3+ shareholders with percentages. PARTIAL if just founder splits.",
    },
    {
        "id": 55,
        "query": "What did the home inspection reveal?",
        "category": "ocr_retrieval",
        "expected": "Passed. Inspector Mike Reeves. Roof: good, ~5 years remaining. Foundation: minor cosmetic crack. HVAC: 3-year-old Trane. Plumbing: copper, good pressure. Electrical: 200 amp, up to code. Minor issues: kitchen faucet drip, 2 windows need resealing, fence gate latch broken.",
        "scoring_notes": "HIT requires pass + 3 specific findings. PARTIAL if just pass/fail.",
    },

    # ================================================================
    # CATEGORY 12: COMPLEX / ANALYTICAL (5 queries)
    # Requires deeper reasoning beyond simple retrieval
    # Favors: LLM reasoning, comprehensive memory
    # ================================================================
    {
        "id": 56,
        "query": "What mistakes has Jordan made as a founder?",
        "category": "analytical",
        "expected": "1. Underpriced initially ($2K when should have been $5K — Nina corrected). 2. Tried to do everything himself (no delegation). 3. Neglected personal health and relationships. 4. Missed anniversary dinner for investor call. 5. Didn't hire sales early enough (Sam moonlighting wasn't enough). 6. Unit conversion bug in pilot (metric vs short tons). 7. Chose PostgreSQL initially when needed ClickHouse.",
        "scoring_notes": "HIT requires 4+ mistakes. PARTIAL if 2-3.",
    },
    {
        "id": 57,
        "query": "What role does each person play in Jordan's support system?",
        "category": "analytical",
        "expected": "Riley: emotional anchor, pushes self-care. Dev: reliable co-founder, technical partner. Sam: honest friend, sounding board, life perspective. Mom: unconditional love, worrier. Lily: sibling bond, new Austin companion. Jake: fitness accountability, ground-level friendship. Nina: professional mentor, strategic guide. Dr. Choi: mental health, self-awareness. Dr. Woo: academic credibility, talent pipeline (Aisha).",
        "scoring_notes": "HIT requires 5+ people with distinct roles. PARTIAL if 3-4.",
    },
    {
        "id": 58,
        "query": "How has Jordan's relationship with money changed over the period?",
        "category": "analytical",
        "expected": "Initially anxious: tracked savings obsessively ($45K savings, $47K 401k), worried about $4,200/month burn. After seed: more comfortable but still frugal ($120K salary when could take more). After Series A: bought house ($495K), Rivian R1S, nicer dinners. But still thoughtful: grandfathered Meridian pricing, chose WeWork over lease for flexibility, engagement ring on layaway ($4,200).",
        "scoring_notes": "HIT requires evolution from anxious → comfortable with examples. PARTIAL if just one phase.",
    },
    {
        "id": 59,
        "query": "What are the risks facing CarbonSense going into 2026?",
        "category": "analytical",
        "expected": "1. EcoTrace competition ($40M, undercutting on price by 40%). 2. Jordan's burnout risk (partially managed now with therapy). 3. Key person risk (Aisha almost left for Google). 4. European expansion complexity (GDPR, different emission factors). 5. Need to hit $5M ARR for Series B. 6. Engineering team still needs 2 more hires. 7. fastembed/huggingface dependency — kidding, that's our problem not Jordan's 😄",
        "scoring_notes": "HIT requires 4+ real risks. PARTIAL if 2-3.",
    },
    {
        "id": 60,
        "query": "If you were advising Jordan, what would you tell him to focus on in 2026?",
        "category": "analytical",
        "expected": "Based on all data: 1. Propose to Riley (has ring, she's ready, don't wait). 2. Win European customers via KlimaSync (CSRD mandate). 3. Get scope 3 above 92% (Chen Wei's research). 4. Retain Aisha at all costs. 5. Keep therapy going. 6. Run the marathon (has been training). 7. Start Series B conversations Q2-Q3. 8. Don't compete with EcoTrace on price — compete on accuracy. 9. Call mom more often.",
        "scoring_notes": "HIT requires advice grounded in data from 4+ areas. PARTIAL if generic advice.",
    },
]

if __name__ == "__main__":
    print(f"Total queries: {len(TEST_QUERIES_V2)}")
    print(f"\nBy category:")
    cats = {}
    for q in TEST_QUERIES_V2:
        cat = q["category"]
        cats[cat] = cats.get(cat, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count}")

    print(f"\n{'='*60}")
    for q in TEST_QUERIES_V2:
        print(f"\nQ{q['id']} [{q['category']}]: {q['query']}")
        print(f"  Expected: {q['expected'][:100]}...")
