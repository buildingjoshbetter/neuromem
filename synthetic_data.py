"""
Synthetic dataset for Neuromem M1: The Baseline Test

200 messages simulating real conversations across categories:
- Personal/casual conversations
- Business/strategy discussions
- Technical discussions
- Scheduling/temporal events
- Relationship-specific context (different people, different topics)
- Contradictions (old facts superseded by new facts)
- Repetitive/routine messages (noise that a smart system should handle)

Each message has: content, timestamp, sender, category
"""

from datetime import datetime, timedelta
import json

BASE_DATE = datetime(2026, 3, 1)

def ts(days_ago, hour=12):
    """Generate timestamp N days ago at given hour."""
    dt = BASE_DATE - timedelta(days=days_ago, hours=24-hour)
    return dt.isoformat()

MESSAGES = [
    # ============================================
    # PERSONAL / CASUAL (messages with friends, family)
    # ============================================
    {"content": "hey mom just landed in austin, flight was smooth", "sender": "josh", "recipient": "mom", "timestamp": ts(30, 14), "category": "personal"},
    {"content": "so glad you're safe! dad says hi. we're thinking about visiting in april", "sender": "mom", "recipient": "josh", "timestamp": ts(30, 14), "category": "personal"},
    {"content": "that would be amazing, april works. i'll have the guest room ready", "sender": "josh", "recipient": "mom", "timestamp": ts(30, 15), "category": "personal"},
    {"content": "actually we might push to may, your dad has a doctors appointment mid april", "sender": "mom", "recipient": "josh", "timestamp": ts(22, 10), "category": "personal"},
    {"content": "no worries may works too. is dad doing ok?", "sender": "josh", "recipient": "mom", "timestamp": ts(22, 10), "category": "personal"},
    {"content": "he's fine just a routine checkup. nothing to worry about", "sender": "mom", "recipient": "josh", "timestamp": ts(22, 11), "category": "personal"},

    {"content": "dude the new ferrari sf-24 is insane. did you see the lap times?", "sender": "marcus", "recipient": "josh", "timestamp": ts(25, 20), "category": "personal"},
    {"content": "yeah the downforce numbers are crazy. reminds me of the red bull rb19 era", "sender": "josh", "recipient": "marcus", "timestamp": ts(25, 20), "category": "personal"},
    {"content": "we should go to cota for the race in october. i can get paddock passes", "sender": "marcus", "recipient": "josh", "timestamp": ts(25, 21), "category": "personal"},
    {"content": "100% down. lock it in", "sender": "josh", "recipient": "marcus", "timestamp": ts(25, 21), "category": "personal"},

    {"content": "happy birthday bro! 27 looks good on you", "sender": "sarah", "recipient": "josh", "timestamp": ts(45, 9), "category": "personal"},
    {"content": "haha thanks sarah. still feel 22 tbh", "sender": "josh", "recipient": "sarah", "timestamp": ts(45, 10), "category": "personal"},

    {"content": "yo did you try that new ramen spot on south congress?", "sender": "tyler", "recipient": "josh", "timestamp": ts(15, 19), "category": "personal"},
    {"content": "not yet but its on my list. is it actually good or just hyped?", "sender": "josh", "recipient": "tyler", "timestamp": ts(15, 19), "category": "personal"},
    {"content": "legit the best tonkotsu ive had in austin. go on a tuesday, no line", "sender": "tyler", "recipient": "josh", "timestamp": ts(15, 19), "category": "personal"},

    {"content": "just finished a 10 mile run. new PR by 4 minutes", "sender": "josh", "recipient": "marcus", "timestamp": ts(10, 8), "category": "personal"},
    {"content": "beast mode. what was your pace?", "sender": "marcus", "recipient": "josh", "timestamp": ts(10, 8), "category": "personal"},
    {"content": "7:12 per mile average. whoop says my strain was 18.4", "sender": "josh", "recipient": "marcus", "timestamp": ts(10, 9), "category": "personal"},

    {"content": "thinking about getting a dog. maybe a golden retriever", "sender": "josh", "recipient": "sarah", "timestamp": ts(18, 16), "category": "personal"},
    {"content": "omg yes! you should adopt not shop though. austin pets alive has goldens sometimes", "sender": "sarah", "recipient": "josh", "timestamp": ts(18, 16), "category": "personal"},
    {"content": "good call. gonna check their site this weekend", "sender": "josh", "recipient": "sarah", "timestamp": ts(18, 17), "category": "personal"},

    # ============================================
    # BUSINESS / STRATEGY
    # ============================================
    {"content": "had a great call with the investor today. they're interested in the memory system angle", "sender": "josh", "recipient": "alex", "timestamp": ts(20, 16), "category": "business"},
    {"content": "nice. what did they say about the market size?", "sender": "alex", "recipient": "josh", "timestamp": ts(20, 16), "category": "business"},
    {"content": "they think personal AI memory is a $2B market by 2028. mem0 raising 24M validates the space", "sender": "josh", "recipient": "alex", "timestamp": ts(20, 17), "category": "business"},
    {"content": "agree. our differentiation is the 6-layer architecture. nobody else is doing predictive coding for memory filtering", "sender": "josh", "recipient": "alex", "timestamp": ts(20, 17), "category": "business"},

    {"content": "i think we should target developers first, not consumers. B2D motion like stripe did", "sender": "josh", "recipient": "alex", "timestamp": ts(14, 11), "category": "business"},
    {"content": "makes sense. the api-first approach lets us skip the consumer UX problem entirely", "sender": "alex", "recipient": "josh", "timestamp": ts(14, 11), "category": "business"},
    {"content": "exactly. ship an npm package and a python sdk. let other people build the UX", "sender": "josh", "recipient": "alex", "timestamp": ts(14, 12), "category": "business"},

    {"content": "just looked at mem0's pricing. they charge $97/mo for their pro tier. we can undercut that easily since our compute is local", "sender": "josh", "recipient": "alex", "timestamp": ts(8, 15), "category": "business"},
    {"content": "or we go open source core with a managed cloud offering. the mongodb model", "sender": "alex", "recipient": "josh", "timestamp": ts(8, 15), "category": "business"},
    {"content": "i like that. open source builds trust and community. cloud offering captures enterprise revenue", "sender": "josh", "recipient": "alex", "timestamp": ts(8, 16), "category": "business"},

    {"content": "the book is selling about 200 copies a month now. not bad for zero marketing", "sender": "josh", "recipient": "sarah", "timestamp": ts(12, 14), "category": "business"},
    {"content": "thats actually amazing for a self-published book josh. have you thought about a second edition?", "sender": "sarah", "recipient": "josh", "timestamp": ts(12, 14), "category": "business"},

    {"content": "we need to file the LLC by end of march. i've been procrastinating on this", "sender": "josh", "recipient": "alex", "timestamp": ts(5, 10), "category": "business"},
    {"content": "i can handle the paperwork. texas or delaware?", "sender": "alex", "recipient": "josh", "timestamp": ts(5, 10), "category": "business"},
    {"content": "delaware for the corp structure. we'll want that for fundraising later", "sender": "josh", "recipient": "alex", "timestamp": ts(5, 11), "category": "business"},

    {"content": "revenue update: skippy generated $1,200 in consulting revenue this month", "sender": "josh", "recipient": "alex", "timestamp": ts(3, 9), "category": "business"},
    {"content": "solid. that covers our server costs with margin. when do we start charging for the api?", "sender": "alex", "recipient": "josh", "timestamp": ts(3, 9), "category": "business"},

    {"content": "met a great ML engineer at the austin AI meetup. her name is priya. she's worked at openai", "sender": "josh", "recipient": "alex", "timestamp": ts(7, 22), "category": "business"},
    {"content": "sick. we should bring her on as an advisor at minimum", "sender": "alex", "recipient": "josh", "timestamp": ts(7, 22), "category": "business"},
    {"content": "already on it. coffee scheduled for next tuesday", "sender": "josh", "recipient": "alex", "timestamp": ts(7, 22), "category": "business"},

    # ============================================
    # TECHNICAL DISCUSSIONS
    # ============================================
    {"content": "been testing model2vec potion-base-8M. 256 dimensions, 30MB, runs on CPU. insanely fast", "sender": "josh", "recipient": "alex", "timestamp": ts(16, 14), "category": "technical"},
    {"content": "how does it compare to openai ada-002 on quality?", "sender": "alex", "recipient": "josh", "timestamp": ts(16, 14), "category": "technical"},
    {"content": "honestly for our use case its 90% as good at 500x the speed. we dont need 1536 dimensions for personal memory", "sender": "josh", "recipient": "alex", "timestamp": ts(16, 15), "category": "technical"},

    {"content": "the sqlite-vec benchmarks are back. 50K vectors, cosine similarity, 23ms average query time on m3 macbook", "sender": "josh", "recipient": "alex", "timestamp": ts(13, 11), "category": "technical"},
    {"content": "thats more than fast enough. we dont need pinecone or qdrant for this scale", "sender": "alex", "recipient": "josh", "timestamp": ts(13, 11), "category": "technical"},
    {"content": "exactly. single file database, no network calls, no api costs. sqlite + fts5 + sqlite-vec is the whole stack", "sender": "josh", "recipient": "alex", "timestamp": ts(13, 12), "category": "technical"},

    {"content": "RRF with k=60 is outperforming learned fusion on our test set. simpler is better here", "sender": "josh", "recipient": "alex", "timestamp": ts(11, 16), "category": "technical"},
    {"content": "yeah the cormack 2009 paper was right. RRF is surprisingly hard to beat", "sender": "alex", "recipient": "josh", "timestamp": ts(11, 16), "category": "technical"},

    {"content": "the predictive coding filter is working. out of 1000 test inputs, it only stored 73. thats 7.3%", "sender": "josh", "recipient": "alex", "timestamp": ts(6, 18), "category": "technical"},
    {"content": "and retrieval quality went UP? storing less data gives better results?", "sender": "alex", "recipient": "josh", "timestamp": ts(6, 18), "category": "technical"},
    {"content": "yep. because we're only storing the surprising stuff. all the noise is gone. cosine similarity actually finds relevant matches now instead of drowning in routine messages", "sender": "josh", "recipient": "alex", "timestamp": ts(6, 19), "category": "technical"},

    {"content": "just discovered that ollama's qwen2.5 7b is good enough for consolidation. dont need claude for that layer", "sender": "josh", "recipient": "alex", "timestamp": ts(4, 15), "category": "technical"},
    {"content": "wait really? the quality is acceptable?", "sender": "alex", "recipient": "josh", "timestamp": ts(4, 15), "category": "technical"},
    {"content": "for SKIP/LIGHT/FULL triage yes. it correctly identifies duplicates and near-duplicates. FULL consolidation might need a bigger model but thats only 20% of inputs", "sender": "josh", "recipient": "alex", "timestamp": ts(4, 16), "category": "technical"},

    {"content": "bug report: the temporal decay is too aggressive. messages from 3 days ago are already at 0.2 relevance", "sender": "josh", "recipient": "alex", "timestamp": ts(9, 10), "category": "technical"},
    {"content": "we need different decay rates per entity. mom messages should decay slower than work standup notes", "sender": "alex", "recipient": "josh", "timestamp": ts(9, 10), "category": "technical"},
    {"content": "thats literally what L4 salience guard is for. per-entity decay thresholds", "sender": "josh", "recipient": "alex", "timestamp": ts(9, 11), "category": "technical"},

    {"content": "tried chunk sizes of 128, 256, and 512 tokens. 256 is the sweet spot for messages", "sender": "josh", "recipient": "alex", "timestamp": ts(17, 13), "category": "technical"},
    {"content": "what about overlap?", "sender": "alex", "recipient": "josh", "timestamp": ts(17, 13), "category": "technical"},
    {"content": "15% overlap. without it we lose context at chunk boundaries. a message referencing 'the project' in chunk 2 has no meaning without chunk 1 mentioning which project", "sender": "josh", "recipient": "alex", "timestamp": ts(17, 14), "category": "technical"},

    {"content": "the EWC-inspired identity drift protection is preventing the personality engram from shifting when processing angry messages. exactly what we wanted", "sender": "josh", "recipient": "alex", "timestamp": ts(2, 17), "category": "technical"},

    {"content": "openrouter just added deepseek v3 for $0.14 per million tokens. insanely cheap", "sender": "josh", "recipient": "alex", "timestamp": ts(19, 9), "category": "technical"},
    {"content": "thats cheaper than running qwen locally when you factor in GPU electricity costs", "sender": "alex", "recipient": "josh", "timestamp": ts(19, 9), "category": "technical"},

    # ============================================
    # SCHEDULING / TEMPORAL EVENTS
    # ============================================
    {"content": "dentist appointment tomorrow at 2pm. south austin dental on lamar", "sender": "josh", "recipient": "josh", "timestamp": ts(28, 20), "category": "scheduling"},
    {"content": "reminder: investor call thursday at 3pm CST. zoom link in email", "sender": "alex", "recipient": "josh", "timestamp": ts(21, 8), "category": "scheduling"},
    {"content": "austin AI meetup this friday at capital factory. 6pm. gonna give a lightning talk on memory systems", "sender": "josh", "recipient": "marcus", "timestamp": ts(8, 12), "category": "scheduling"},
    {"content": "can we push our 1:1 from monday to wednesday? got a conflict", "sender": "alex", "recipient": "josh", "timestamp": ts(6, 9), "category": "scheduling"},
    {"content": "yeah wednesday works. same time?", "sender": "josh", "recipient": "alex", "timestamp": ts(6, 9), "category": "scheduling"},
    {"content": "yep 11am. talk then", "sender": "alex", "recipient": "josh", "timestamp": ts(6, 9), "category": "scheduling"},
    {"content": "gym at 6am tomorrow. leg day. dont let me skip", "sender": "josh", "recipient": "marcus", "timestamp": ts(3, 22), "category": "scheduling"},
    {"content": "i'll text you at 5:45. no excuses", "sender": "marcus", "recipient": "josh", "timestamp": ts(3, 22), "category": "scheduling"},
    {"content": "coffee with priya next tuesday at 10am. epoch coffee on north loop", "sender": "josh", "recipient": "josh", "timestamp": ts(7, 22), "category": "scheduling"},
    {"content": "book club is cancelled this month. sarah has covid", "sender": "tyler", "recipient": "josh", "timestamp": ts(11, 15), "category": "scheduling"},

    # ============================================
    # CONTRADICTIONS (old info superseded by new info)
    # ============================================
    # Contradiction 1: Parents visiting
    # (already handled above: april -> changed to may)

    # Contradiction 2: Tech stack choice
    {"content": "i think we should use pinecone for vector search. its the industry standard", "sender": "josh", "recipient": "alex", "timestamp": ts(26, 14), "category": "technical"},
    {"content": "actually after benchmarking, sqlite-vec is better for our scale. pinecone is overkill and adds network latency", "sender": "josh", "recipient": "alex", "timestamp": ts(13, 12), "category": "technical"},

    # Contradiction 3: Business model
    {"content": "we should charge $50/month for the api. thats the sweet spot", "sender": "josh", "recipient": "alex", "timestamp": ts(20, 18), "category": "business"},
    {"content": "changing my mind on pricing. open source core, free tier, then $97/mo for managed cloud. the mongodb model is smarter", "sender": "josh", "recipient": "alex", "timestamp": ts(8, 16), "category": "business"},

    # Contradiction 4: Hiring
    {"content": "we dont need to hire anyone yet. just me and you can ship the MVP", "sender": "josh", "recipient": "alex", "timestamp": ts(24, 10), "category": "business"},
    {"content": "actually met priya at the meetup. we should bring her on as advisor. maybe more", "sender": "josh", "recipient": "alex", "timestamp": ts(7, 22), "category": "business"},

    # Contradiction 5: Running habit
    {"content": "im going to start running every morning at 6am. new habit", "sender": "josh", "recipient": "marcus", "timestamp": ts(20, 21), "category": "personal"},
    {"content": "switched to evening runs. mornings are for deep work now", "sender": "josh", "recipient": "marcus", "timestamp": ts(10, 19), "category": "personal"},

    # ============================================
    # REPETITIVE / ROUTINE (noise a smart system should handle)
    # ============================================
    {"content": "good morning!", "sender": "josh", "recipient": "alex", "timestamp": ts(29, 8), "category": "routine"},
    {"content": "morning!", "sender": "alex", "recipient": "josh", "timestamp": ts(29, 8), "category": "routine"},
    {"content": "good morning", "sender": "josh", "recipient": "alex", "timestamp": ts(28, 8), "category": "routine"},
    {"content": "gm!", "sender": "alex", "recipient": "josh", "timestamp": ts(28, 8), "category": "routine"},
    {"content": "good morning!", "sender": "josh", "recipient": "alex", "timestamp": ts(27, 8), "category": "routine"},
    {"content": "morning bro", "sender": "alex", "recipient": "josh", "timestamp": ts(27, 8), "category": "routine"},
    {"content": "good morning!", "sender": "josh", "recipient": "alex", "timestamp": ts(26, 8), "category": "routine"},
    {"content": "gm", "sender": "alex", "recipient": "josh", "timestamp": ts(26, 8), "category": "routine"},
    {"content": "good morning!", "sender": "josh", "recipient": "alex", "timestamp": ts(25, 8), "category": "routine"},
    {"content": "morning!", "sender": "alex", "recipient": "josh", "timestamp": ts(25, 8), "category": "routine"},
    {"content": "good morning", "sender": "josh", "recipient": "alex", "timestamp": ts(24, 8), "category": "routine"},
    {"content": "gm!", "sender": "alex", "recipient": "josh", "timestamp": ts(24, 8), "category": "routine"},
    {"content": "good morning!", "sender": "josh", "recipient": "alex", "timestamp": ts(23, 8), "category": "routine"},
    {"content": "morning", "sender": "alex", "recipient": "josh", "timestamp": ts(23, 8), "category": "routine"},

    {"content": "sounds good", "sender": "josh", "recipient": "alex", "timestamp": ts(27, 15), "category": "routine"},
    {"content": "sounds good", "sender": "josh", "recipient": "alex", "timestamp": ts(22, 14), "category": "routine"},
    {"content": "sounds good", "sender": "josh", "recipient": "sarah", "timestamp": ts(18, 12), "category": "routine"},
    {"content": "sounds good", "sender": "josh", "recipient": "tyler", "timestamp": ts(14, 16), "category": "routine"},
    {"content": "lol", "sender": "josh", "recipient": "marcus", "timestamp": ts(25, 21), "category": "routine"},
    {"content": "lol", "sender": "josh", "recipient": "sarah", "timestamp": ts(20, 15), "category": "routine"},
    {"content": "lol", "sender": "josh", "recipient": "tyler", "timestamp": ts(15, 20), "category": "routine"},
    {"content": "haha", "sender": "josh", "recipient": "marcus", "timestamp": ts(12, 18), "category": "routine"},
    {"content": "ok cool", "sender": "josh", "recipient": "alex", "timestamp": ts(9, 11), "category": "routine"},
    {"content": "ok cool", "sender": "josh", "recipient": "alex", "timestamp": ts(6, 10), "category": "routine"},
    {"content": "bet", "sender": "josh", "recipient": "marcus", "timestamp": ts(10, 9), "category": "routine"},
    {"content": "bet", "sender": "josh", "recipient": "tyler", "timestamp": ts(8, 14), "category": "routine"},

    # ============================================
    # MORE PERSONAL DEPTH (for richer entity testing)
    # ============================================
    {"content": "sarah recommended this book called atomic habits. have you read it?", "sender": "josh", "recipient": "tyler", "timestamp": ts(16, 20), "category": "personal"},
    {"content": "yeah its solid. the identity-based habits chapter changed how i think about goals", "sender": "tyler", "recipient": "josh", "timestamp": ts(16, 20), "category": "personal"},

    {"content": "im thinking about selling the tesla and getting a rivian", "sender": "josh", "recipient": "marcus", "timestamp": ts(14, 18), "category": "personal"},
    {"content": "the R1T? those things are sick but expensive", "sender": "marcus", "recipient": "josh", "timestamp": ts(14, 18), "category": "personal"},
    {"content": "yeah but the adventure gear options are insane. and i want something for camping trips", "sender": "josh", "recipient": "marcus", "timestamp": ts(14, 19), "category": "personal"},

    {"content": "just signed up for a half marathon in november. the austin half", "sender": "josh", "recipient": "marcus", "timestamp": ts(5, 20), "category": "personal"},
    {"content": "lets gooo. im signing up too. training partners", "sender": "marcus", "recipient": "josh", "timestamp": ts(5, 20), "category": "personal"},

    {"content": "my sister just got engaged! matt proposed at big bend", "sender": "sarah", "recipient": "josh", "timestamp": ts(9, 19), "category": "personal"},
    {"content": "no way!! tell her congrats from me. matt is a great dude", "sender": "josh", "recipient": "sarah", "timestamp": ts(9, 19), "category": "personal"},

    # ============================================
    # MORE BUSINESS DEPTH
    # ============================================
    {"content": "competitor alert: rewind AI just got acquired by meta. they're dead as a standalone product", "sender": "alex", "recipient": "josh", "timestamp": ts(23, 14), "category": "business"},
    {"content": "good for us. one less player. their tech was mediocre anyway -- screen recording + basic OCR", "sender": "josh", "recipient": "alex", "timestamp": ts(23, 14), "category": "business"},

    {"content": "the HYPERAWARE audiobook version is done. launching on audible next month", "sender": "josh", "recipient": "sarah", "timestamp": ts(4, 11), "category": "business"},
    {"content": "josh thats huge!! who did the narration?", "sender": "sarah", "recipient": "josh", "timestamp": ts(4, 11), "category": "business"},
    {"content": "i did it myself. took 3 days in a studio downtown", "sender": "josh", "recipient": "sarah", "timestamp": ts(4, 12), "category": "business"},

    {"content": "github stars hit 500 today on the trainer repo. organic growth only", "sender": "josh", "recipient": "alex", "timestamp": ts(1, 16), "category": "business"},
    {"content": "🔥 thats faster than mem0 grew in their first month", "sender": "alex", "recipient": "josh", "timestamp": ts(1, 16), "category": "business"},

    {"content": "legal update: trademark application for 'neuromem' filed yesterday", "sender": "josh", "recipient": "alex", "timestamp": ts(2, 9), "category": "business"},

    {"content": "YC deadline is in 6 weeks. we should apply with the neuromem pitch", "sender": "alex", "recipient": "josh", "timestamp": ts(3, 14), "category": "business"},
    {"content": "agree. the pitch is: open source memory infrastructure for AI. the six layer architecture is the moat", "sender": "josh", "recipient": "alex", "timestamp": ts(3, 14), "category": "business"},

    # ============================================
    # MORE TECHNICAL DEPTH
    # ============================================
    {"content": "the dual-rate learning is working. fast alpha 0.15 for new contacts, slow alpha 0.03 for established patterns", "sender": "josh", "recipient": "alex", "timestamp": ts(5, 14), "category": "technical"},
    {"content": "how does it handle someone you havent talked to in months then suddenly they message?", "sender": "alex", "recipient": "josh", "timestamp": ts(5, 14), "category": "technical"},
    {"content": "it ramps the fast rate back up because the prediction error is high. the system is surprised", "sender": "josh", "recipient": "alex", "timestamp": ts(5, 15), "category": "technical"},

    {"content": "MCP server is working. six tools: add_memory, search, get_context, get_entity_profile, consolidate, get_timeline", "sender": "josh", "recipient": "alex", "timestamp": ts(1, 13), "category": "technical"},
    {"content": "does claude actually call them correctly?", "sender": "alex", "recipient": "josh", "timestamp": ts(1, 13), "category": "technical"},
    {"content": "yes because the tool descriptions are carefully written. the description IS the prompt. badly written descriptions = tools that never get used", "sender": "josh", "recipient": "alex", "timestamp": ts(1, 14), "category": "technical"},

    {"content": "WAL mode on sqlite is a game changer. we can write captures and run searches simultaneously with zero locking", "sender": "josh", "recipient": "alex", "timestamp": ts(15, 11), "category": "technical"},

    {"content": "found a bug in the consolidation layer. its merging messages from different people into the same summary", "sender": "josh", "recipient": "alex", "timestamp": ts(3, 20), "category": "technical"},
    {"content": "thats a per-entity boundary issue. consolidation should NEVER cross entity boundaries", "sender": "alex", "recipient": "josh", "timestamp": ts(3, 20), "category": "technical"},

    {"content": "anthropic just released claude 4.5 sonnet. the context window is 200K tokens now", "sender": "josh", "recipient": "alex", "timestamp": ts(7, 10), "category": "technical"},
    {"content": "bigger context windows actually make our memory system MORE valuable not less. without smart retrieval you just dump everything in and pray", "sender": "josh", "recipient": "alex", "timestamp": ts(7, 10), "category": "technical"},

    # ============================================
    # HEALTH / FITNESS
    # ============================================
    {"content": "whoop recovery score is 87% today. green day. going hard at the gym", "sender": "josh", "recipient": "marcus", "timestamp": ts(7, 7), "category": "personal"},
    {"content": "nice. what strain you targeting?", "sender": "marcus", "recipient": "josh", "timestamp": ts(7, 7), "category": "personal"},
    {"content": "aiming for 15+. upper body and a 5k after", "sender": "josh", "recipient": "marcus", "timestamp": ts(7, 7), "category": "personal"},

    {"content": "sleep was garbage last night. 4.5 hours. whoop is red", "sender": "josh", "recipient": "marcus", "timestamp": ts(4, 8), "category": "personal"},
    {"content": "take a rest day bro. dont push it", "sender": "marcus", "recipient": "josh", "timestamp": ts(4, 8), "category": "personal"},

    {"content": "started taking creatine again. 5g daily", "sender": "josh", "recipient": "marcus", "timestamp": ts(12, 12), "category": "personal"},
    {"content": "good call. it helps with focus too not just strength. theres research on it", "sender": "marcus", "recipient": "josh", "timestamp": ts(12, 12), "category": "personal"},

    # ============================================
    # FOOD / AUSTIN LIFE
    # ============================================
    {"content": "found the best breakfast taco in austin. veracruz all natural on east cesar chavez", "sender": "josh", "recipient": "tyler", "timestamp": ts(21, 10), "category": "personal"},
    {"content": "bro everyone knows veracruz. try valentinas for brisket tacos. next level", "sender": "tyler", "recipient": "josh", "timestamp": ts(21, 10), "category": "personal"},

    {"content": "power went out on my block again. third time this month. ERCOT is a joke", "sender": "josh", "recipient": "alex", "timestamp": ts(18, 14), "category": "personal"},
    {"content": "get a battery backup for your setup. cant afford downtime during a demo", "sender": "alex", "recipient": "josh", "timestamp": ts(18, 14), "category": "personal"},

    # ============================================
    # ADDITIONAL MESSAGES FOR VOLUME (200 total)
    # ============================================
    {"content": "reading 'the mom test' by rob fitzpatrick. every founder should read this", "sender": "josh", "recipient": "alex", "timestamp": ts(19, 21), "category": "business"},
    {"content": "its basically about how to do customer interviews without leading the witness", "sender": "josh", "recipient": "alex", "timestamp": ts(19, 21), "category": "business"},

    {"content": "just saw supermemory raised 2.6M. their product is way simpler than ours", "sender": "alex", "recipient": "josh", "timestamp": ts(15, 13), "category": "business"},
    {"content": "good validation for the space. their approach is too basic though -- no consolidation, no entity filtering, no temporal awareness", "sender": "josh", "recipient": "alex", "timestamp": ts(15, 13), "category": "business"},

    {"content": "the GPU box is running hot. 82C on the 5090 during training", "sender": "josh", "recipient": "alex", "timestamp": ts(11, 22), "category": "technical"},
    {"content": "might need better cooling. or throttle the workload", "sender": "alex", "recipient": "josh", "timestamp": ts(11, 22), "category": "technical"},
    {"content": "ordered a noctua fan setup. should bring it down to 70C", "sender": "josh", "recipient": "alex", "timestamp": ts(10, 10), "category": "technical"},

    {"content": "the RTX PRO 6000 blackwell has 98GB vram. we can run a 70B model on a single card", "sender": "josh", "recipient": "alex", "timestamp": ts(16, 10), "category": "technical"},

    {"content": "thinking about doing a podcast. AI memory systems, building in public, ADHD founder stuff", "sender": "josh", "recipient": "sarah", "timestamp": ts(6, 20), "category": "business"},
    {"content": "yes! you should absolutely do that. your voice is already good from the audiobook recording", "sender": "sarah", "recipient": "josh", "timestamp": ts(6, 20), "category": "business"},

    {"content": "update on the dog situation: found a golden retriever mix at austin pets alive. going to meet her saturday", "sender": "josh", "recipient": "sarah", "timestamp": ts(11, 17), "category": "personal"},
    {"content": "OMG send pics immediately", "sender": "sarah", "recipient": "josh", "timestamp": ts(11, 17), "category": "personal"},
    {"content": "her name is luna. shes 2 years old. the most gentle dog ive ever met", "sender": "josh", "recipient": "sarah", "timestamp": ts(10, 14), "category": "personal"},
    {"content": "we adopted luna!! she's home and already claimed the couch", "sender": "josh", "recipient": "sarah", "timestamp": ts(9, 16), "category": "personal"},
    {"content": "I KNEW IT. best decision youll ever make", "sender": "sarah", "recipient": "josh", "timestamp": ts(9, 16), "category": "personal"},

    {"content": "luna destroyed my running shoes last night. classic puppy move", "sender": "josh", "recipient": "marcus", "timestamp": ts(7, 8), "category": "personal"},
    {"content": "haha welcome to dog ownership. get her some chew toys asap", "sender": "marcus", "recipient": "josh", "timestamp": ts(7, 8), "category": "personal"},

    {"content": "taking luna to zilker park this weekend. she needs to burn off energy", "sender": "josh", "recipient": "tyler", "timestamp": ts(5, 18), "category": "personal"},

    {"content": "can you review the API docs before i publish them? want a second set of eyes", "sender": "josh", "recipient": "alex", "timestamp": ts(2, 11), "category": "technical"},
    {"content": "sure send them over. ill review tonight", "sender": "alex", "recipient": "josh", "timestamp": ts(2, 11), "category": "technical"},

    {"content": "the cloudflare tunnel is solid. gpu box accessible from anywhere now. gpu.gpubox.net", "sender": "josh", "recipient": "alex", "timestamp": ts(8, 17), "category": "technical"},

    {"content": "thanksgiving at my place this year. tyler sarah marcus you're all invited", "sender": "josh", "recipient": "tyler", "timestamp": ts(27, 12), "category": "personal"},
    {"content": "ill bring the mac and cheese. the good kind with the breadcrumb top", "sender": "tyler", "recipient": "josh", "timestamp": ts(27, 12), "category": "personal"},

    {"content": "just hit 10K followers on twitter/X. the AI content is resonating", "sender": "josh", "recipient": "alex", "timestamp": ts(1, 20), "category": "business"},
    {"content": "your thread about the 6-layer memory architecture got 400 retweets. people want this", "sender": "alex", "recipient": "josh", "timestamp": ts(1, 20), "category": "business"},

    {"content": "weekly standup: shipped hybrid search, fixed the temporal decay bug, started work on consolidation", "sender": "josh", "recipient": "alex", "timestamp": ts(4, 10), "category": "business"},
    {"content": "solid week. consolidation is the big one. thats where we really differentiate", "sender": "alex", "recipient": "josh", "timestamp": ts(4, 10), "category": "business"},

    {"content": "need to renew my lease by april 15th. landlord wants to raise rent by $200", "sender": "josh", "recipient": "sarah", "timestamp": ts(6, 14), "category": "personal"},
    {"content": "ugh austin rents are insane right now. have you looked at buying?", "sender": "sarah", "recipient": "josh", "timestamp": ts(6, 14), "category": "personal"},
    {"content": "not yet. want to wait until the company has more traction before taking on a mortgage", "sender": "josh", "recipient": "sarah", "timestamp": ts(6, 15), "category": "personal"},

    {"content": "finally got the interrogation mode working over cloudflare tunnel. can demo it from anywhere", "sender": "josh", "recipient": "alex", "timestamp": ts(13, 20), "category": "technical"},

    {"content": "reminder to self: refill adderall prescription on friday", "sender": "josh", "recipient": "josh", "timestamp": ts(8, 9), "category": "personal"},

    {"content": "alex can you handle the support emails this week? im deep in the consolidation code", "sender": "josh", "recipient": "alex", "timestamp": ts(3, 8), "category": "business"},
    {"content": "got it covered. focus on shipping", "sender": "alex", "recipient": "josh", "timestamp": ts(3, 8), "category": "business"},

    {"content": "the whoop data shows my HRV spikes on days i do morning meditation. 15 min is all it takes", "sender": "josh", "recipient": "marcus", "timestamp": ts(2, 7), "category": "personal"},

    {"content": "saw an apartment listing in east austin. 2br, dog friendly, $2100/mo. might move", "sender": "josh", "recipient": "sarah", "timestamp": ts(1, 12), "category": "personal"},
    {"content": "east austin is perfect for you. close to everything", "sender": "sarah", "recipient": "josh", "timestamp": ts(1, 12), "category": "personal"},

    {"content": "note to self: the key insight from building neuromem is that memory is not a database problem, its a cognitive problem. the competitors treat it like a database.", "sender": "josh", "recipient": "josh", "timestamp": ts(1, 23), "category": "technical"},
]

# Verify count
print(f"Total messages: {len(MESSAGES)}")
print(f"\nBy category:")
categories = {}
for m in MESSAGES:
    cat = m["category"]
    categories[cat] = categories.get(cat, 0) + 1
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

print(f"\nBy sender:")
senders = {}
for m in MESSAGES:
    s = m["sender"]
    senders[s] = senders.get(s, 0) + 1
for s, count in sorted(senders.items()):
    print(f"  {s}: {count}")

# Export
with open("/Users/j/Desktop/neuromem/synthetic_messages.json", "w") as f:
    json.dump(MESSAGES, f, indent=2)
print(f"\nExported to synthetic_messages.json")
