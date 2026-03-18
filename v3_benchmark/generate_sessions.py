#!/usr/bin/env python3
"""
Generate v3 benchmark sessions.json from v2 messages + new hand-crafted sessions.

Reads synthetic_v2_messages.json (797 messages about Jordan Chen) and:
1. Creates ~35 hand-crafted conversation sessions from the v2 message themes
   (Jordan talking to an AI assistant about his life)
2. Adds ~15 new sessions targeting v3-specific categories:
   - Belief/opinion evolution
   - Cross-session continuity
   - Temporal markers
   - Fact updates
3. Outputs sessions.json with ~50 sessions, ~500 turns total

Deterministic — no API calls needed.
"""

import json
from pathlib import Path

V2_PATH = Path(__file__).parent.parent / "synthetic_v2_messages.json"
OUT_PATH = Path(__file__).parent / "sessions.json"


def build_v2_sessions():
    """Build ~35 sessions from v2 message themes as Jordan<->AI conversations."""
    sessions = []

    # Session 1: Startup brainstorm
    sessions.append({
        "session_id": 1,
        "timestamp": "2024-07-01T09:00:00",
        "turns": [
            {"role": "user", "content": "hey i need to think through some startup ideas. been brainstorming with dev. we have: carbon tracking for manufacturers, AI-powered energy audit tool, supply chain transparency platform, and climate risk scoring for real estate"},
            {"role": "assistant", "content": "Those are all in the climate-tech space, which has strong regulatory tailwinds right now. What's your background that connects to these?"},
            {"role": "user", "content": "i work at dataflux right now, data engineering. dev is at oracle. we've been building a carbon tracking prototype nights and weekends for 6 months"},
            {"role": "assistant", "content": "Six months of building already puts you way ahead. The carbon tracking idea seems most viable since you have a working prototype. What does it actually do?"},
            {"role": "user", "content": "it's like a fitbit for factories. monitors scope 1 and scope 2 emissions in near real-time. dev says carbon tracking has the most clear regulatory tailwind. we already have three companies interested in piloting it"},
            {"role": "assistant", "content": "Three pilot commitments before you've even launched is a strong signal. That's rare. What companies?"},
            {"role": "user", "content": "meridian steel, lone star cement, and gulf coast plastics. all texas manufacturers. met them through dev's oracle contacts and a manufacturing conference"},
            {"role": "assistant", "content": "Texas manufacturers make sense as an initial market. What's the business model?"},
            {"role": "user", "content": "SaaS, per-facility pricing. dev's lawyer said we should incorporate as a delaware c-corp for VC fundraising later even though we're based in austin. standard playbook"},
            {"role": "assistant", "content": "Are you and Dev aligned on equity and roles?"},
            {"role": "user", "content": "we talked about it. i'm CEO doing customer-facing and product vision. dev is CTO doing all the engineering. he just wants to build — doesn't care about pitching investors or sales calls. perfect complement"},
        ],
        "facts_introduced": [
            "Jordan works at Dataflux (data engineering)",
            "Dev works at Oracle",
            "They've been building carbon tracking prototype for 6 months",
            "Product concept: real-time emissions monitoring for factories",
            "Three pilot companies: Meridian Steel, Lone Star Cement, Gulf Coast Plastics",
            "Planning Delaware C-Corp incorporation",
            "Jordan CEO, Dev CTO"
        ],
        "facts_updated": []
    })

    # Session 2: Quitting decision
    sessions.append({
        "session_id": 2,
        "timestamp": "2024-07-05T19:00:00",
        "turns": [
            {"role": "user", "content": "ok so i told my sister lily about potentially quitting dataflux. she's worried but supportive. mom is gonna freak"},
            {"role": "assistant", "content": "How's Riley feeling about the idea? That's usually the most important conversation."},
            {"role": "user", "content": "riley is supportive. she's starting her masters in counseling psych at UT this fall so she gets the whole 'follow your passion' thing. i just worry about money"},
            {"role": "assistant", "content": "What's your financial cushion look like?"},
            {"role": "user", "content": "about $45k in savings plus $47k in my 401k that i can roll over. our rent is $2,100/month at 1847 E Riverside Dr. dev quit oracle last week so it's getting real"},
            {"role": "assistant", "content": "Dev quitting Oracle is a big commitment signal. With your savings you have roughly 18-20 months of runway if you're careful. What about Riley's income?"},
            {"role": "user", "content": "she'll have a stipend from UT, about $28k/year. not much but it helps. also we have biscuit — he's our corgi, pembroke welsh corgi, born march 15 2023. gotta factor in vet bills and blue buffalo food lol"},
            {"role": "assistant", "content": "Any concerns about the relationship pressure of a startup plus her grad school?"},
            {"role": "user", "content": "honestly yes. we've been together 4 years, mostly stable. but riley said 'i support you but you have to still be present.' fair. she doesn't want to be a startup widow. i promised no more than 12 hour days"},
            {"role": "assistant", "content": "That's a good boundary to set early."},
            {"role": "user", "content": "sam thinks i won't keep it. he's probably right. but i'm going to try. also my buddy jake from the gym said 'just don't skip leg day for investor meetings' which is very jake advice"},
        ],
        "facts_introduced": [
            "Lily is Jordan's sister",
            "Riley is Jordan's partner, starting masters in counseling psych at UT",
            "Jordan has $45K savings + $47K 401k",
            "Apartment: 1847 E Riverside Dr, rent $2,100/month",
            "Dev quit Oracle",
            "Biscuit is a Pembroke Welsh Corgi, born March 15, 2023",
            "Riley's stipend: ~$28K/year"
        ],
        "facts_updated": []
    })

    # Session 3: Resignation and first days
    sessions.append({
        "session_id": 3,
        "timestamp": "2024-07-16T20:00:00",
        "turns": [
            {"role": "user", "content": "submitted my two weeks notice at dataflux today. last day will be july 29. told my boss david morrison. three years at that company"},
            {"role": "assistant", "content": "That takes courage. How are you feeling?"},
            {"role": "user", "content": "terrifying and exciting. sam — he's my best friend — said the terror keeps you sharp. he's right. also dev and i already confirmed three paid pilot customers before we even incorporated"},
            {"role": "assistant", "content": "Three paid pilots before incorporation is exceptional. What are you calling the company?"},
            {"role": "user", "content": "CarbonSense. actually it was riley's idea. we almost called it EmissionIQ but she said 'it should sound like common sense for carbon.' brilliant. we're incorporating july 25 as a delaware c-corp"},
            {"role": "assistant", "content": "Great name. What's the plan for the first month after you leave Dataflux?"},
            {"role": "user", "content": "set up infrastructure with dev, start the meridian steel pilot deployment, get the carbonsense.io domain running. dev already has github actions CI/CD, terraform for AWS, react 18 with typescript and vite frontend. we're using ECS on AWS"},
            {"role": "assistant", "content": "Solid tech stack. How did David Morrison take the resignation?"},
            {"role": "user", "content": "better than expected. he said 'you'll be back in 6 months' which was kind of insulting but also motivating. sam said 'prove him wrong' and i intend to. three years at dataflux taught me a lot about data engineering but i need to build something that matters"},
            {"role": "assistant", "content": "What's Riley's reaction now that it's officially happening?"},
            {"role": "user", "content": "she opened a bottle of wine and toasted 'to the scariest best decision you'll ever make.' she's incredible. also she designed our first logo on canva — it's temporary but surprisingly good. a leaf with a data wave through it"},
        ],
        "facts_introduced": [
            "Jordan submitted notice July 16, last day July 29",
            "David Morrison is his boss at Dataflux",
            "3 years at Dataflux",
            "Sam is Jordan's best friend",
            "Company name: CarbonSense (Riley's idea)",
            "Incorporation date: July 25, 2024",
            "Tech stack: React 18, TypeScript, Vite, AWS ECS, GitHub Actions",
            "David Morrison: 'You'll be back in 6 months'",
            "Riley designed first logo on Canva"
        ],
        "facts_updated": []
    })

    # Session 4: Early startup life
    sessions.append({
        "session_id": 4,
        "timestamp": "2024-08-05T21:00:00",
        "turns": [
            {"role": "user", "content": "first week as founders. working out of dev's apartment. my morning routine is wake 6am, meditate 10 min with headspace, gym or run, breakfast (usually overnight oats or eggs), work by 8:30"},
            {"role": "assistant", "content": "Good that you're establishing routines early. How's the pilot deployment going?"},
            {"role": "user", "content": "meridian pilot is deployed on ECS with RDS postgres. dev set up VPC with private subnets, encryption at rest AES-256, TLS 1.3, IAM roles with least privilege. security is solid"},
            {"role": "assistant", "content": "That's a mature security setup for a two-person startup. What about the actual data accuracy?"},
            {"role": "user", "content": "scope 1 accuracy was 94.2% initially but the prototype is running against meridian's production data now. scope 2 is at 87.6% — dev thinks we can get above 90 if we integrate the EPA eGRID dataset"},
            {"role": "assistant", "content": "The eGRID integration could be a differentiator. What about scope 3?"},
            {"role": "user", "content": "scope 3 is way harder. supply chain data is messy — different vendors report differently, some don't report at all. not tackling that yet. need to nail scope 1 and 2 first"},
            {"role": "assistant", "content": "Smart to stay focused. What's the burn rate looking like?"},
            {"role": "user", "content": "about $4,200/month total — $2,400 for dev's apartment we use as office, $1,200 AWS, $600 misc tools and food. lean operation. at this rate our savings last well over a year"},
            {"role": "assistant", "content": "How's working from Dev's apartment going?"},
            {"role": "user", "content": "cramped but functional. two desks, whiteboards on the wall, biscuit visits sometimes when riley drops him off. dev's cat and biscuit have an uneasy truce. we work well together though — 10 hours a day, minimal meetings, just building"},
        ],
        "facts_introduced": [
            "Morning routine: 6am wake, meditate (Headspace), gym/run, breakfast, work by 8:30",
            "Working from Dev's apartment",
            "Pilot on AWS ECS with RDS Postgres",
            "Initial scope 1: 94.2%, scope 2: 87.6%",
            "Planning EPA eGRID integration for scope 2",
            "Burn rate: $4,200/month",
            "Dev has a cat",
            "Two desks, whiteboards, 10-hour days"
        ],
        "facts_updated": []
    })

    # Session 5: Personal life / fitness
    sessions.append({
        "session_id": 5,
        "timestamp": "2024-08-20T19:00:00",
        "turns": [
            {"role": "user", "content": "i go to gold's gym on south lamar with my buddy jake. $35/month. jake got me into creatine monohydrate — 5g/day. he takes whey protein, fish oil, vitamin D, magnesium before bed"},
            {"role": "assistant", "content": "Creatine is well-supported by research. How are your lifts going?"},
            {"role": "user", "content": "working on getting back to squatting 315 by end of summer. bench was stuck at 225 for months but i just broke through to 235 using pause reps and close-grip sets. creatine is definitely helping"},
            {"role": "assistant", "content": "Nice progress. How's the stress level with the startup?"},
            {"role": "user", "content": "honestly i'm sleeping 5-6 hours and freaking out about money. no revenue yet, $3k in unexpected legal fees. riley is supportive but i can tell she's worried. sam keeps telling me to breathe and that first 6 months of any startup is pure grind"},
            {"role": "assistant", "content": "Sleep deprivation will catch up to you. Try to protect that."},
            {"role": "user", "content": "yeah jake also called out my deadlift form — rounding my lower back. dropped the weight to fix it. also marcus johnson from the gym does olympic lifts, 225 clean and jerk. he's a beast. jake introduced us"},
            {"role": "assistant", "content": "Having gym community helps with the startup isolation. What's your weekly split?"},
            {"role": "user", "content": "3 days lifting with jake (push/pull/legs), 3 days running (easy/tempo/long), sundays rest or yoga. jake convinced me to try yoga for mobility — i was skeptical but my squat depth improved immediately"},
            {"role": "assistant", "content": "What about nutrition? Startups and good eating don't always mix."},
            {"role": "user", "content": "trying. riley meal preps on sundays — chicken, rice, broccoli. i supplement with whey protein post-workout and creatine daily. jake takes fish oil, vitamin D, magnesium before bed. he's basically a walking supplement store"},
        ],
        "facts_introduced": [
            "Gold's Gym on South Lamar, $35/month",
            "Jake is gym buddy",
            "Takes creatine 5g/day",
            "Squat goal: 315, bench broke through 225 to 235",
            "Marcus Johnson: gym buddy, 225 clean and jerk, met through Jake",
            "Sleeping 5-6 hours, stressed about money",
            "Weekly split: 3 lift, 3 run, 1 rest/yoga",
            "Riley meal preps on Sundays"
        ],
        "facts_updated": []
    })

    # Session 6: Meridian pilot results + pricing
    sessions.append({
        "session_id": 6,
        "timestamp": "2024-10-29T12:00:00",
        "turns": [
            {"role": "user", "content": "HUGE news. meridian steel pilot results are in. 96.1% accuracy on scope 1, 91.3% on scope 2. they want to convert to annual contract. maria gonzalez their VP sustainability said it saved them 40 hours/month vs manual reporting"},
            {"role": "assistant", "content": "96.1% on scope 1 blows past your 90% target. That's a strong case study. What about pricing?"},
            {"role": "user", "content": "thinking $2,000/month per facility base tier, $5,000 enterprise with API access. meridian has 4 facilities so $8k/mo. also lone star cement is at 93.8% scope 1 but struggling with scope 3 upstream — cement supply chains are a nightmare"},
            {"role": "assistant", "content": "Those prices seem low for enterprise software. Enterprise carbon reporting tools typically charge $10-15K per facility."},
            {"role": "user", "content": "interesting. i'll keep that in mind. for now i want to get the first customers locked in. also we had a fun bug — unit conversion error. meridian reports in short tons but we assumed metric tons. 10% difference. classic"},
            {"role": "assistant", "content": "Unit conversion bugs are a rite of passage in industrial software. Did you build a normalization layer?"},
            {"role": "user", "content": "dev added a configurable unit mapping per facility in the admin panel. every customer reports differently so we needed it"},
            {"role": "assistant", "content": "Those kinds of edge cases are gold for building a moat. What's next for Lone Star and Gulf Coast?"},
            {"role": "user", "content": "lone star is at 93.8% scope 1 but struggling with scope 3 upstream. cement supply chains are a nightmare — limestone from multiple quarries, each reporting differently. gulf coast is simpler, plastics has a more linear supply chain. they should sign annual contracts by January"},
        ],
        "facts_introduced": [
            "Meridian pilot: 96.1% scope 1, 91.3% scope 2",
            "Maria Gonzalez: VP Sustainability at Meridian Steel",
            "Saves 40 hours/month vs manual reporting",
            "Initial pricing: $2K/facility base, $5K enterprise",
            "Lone Star Cement: 93.8% scope 1",
            "Unit conversion bug: metric vs short tons"
        ],
        "facts_updated": []
    })

    # Session 7: F1 and birthday
    sessions.append({
        "session_id": 7,
        "timestamp": "2024-10-28T18:00:00",
        "turns": [
            {"role": "user", "content": "just got back from the F1 race at COTA! sam got me paddock passes as a birthday gift — i turned 28 on september 14. me, sam, and jake went. max verstappen walked right past us"},
            {"role": "assistant", "content": "Happy belated birthday! Paddock passes at COTA are incredible. How was the rest of the birthday?"},
            {"role": "user", "content": "riley made a red velvet cake, dinner at home. she's amazing. also we just finished watching shogun — best show ever. riley's recommendation"},
            {"role": "assistant", "content": "Sounds like things with Riley are good despite the startup stress?"},
            {"role": "user", "content": "yeah we're solid. she started her masters program sept 1. her professor dr martinez recommended a book called 'burnout' by emily nagoski. says founders are especially prone to burnout"},
            {"role": "assistant", "content": "Dr. Martinez sounds wise. Are you reading it?"},
            {"role": "user", "content": "added it to the list. just finished 'the lean startup' — basic but useful. sam recommended 'the hard thing about hard things' by ben horowitz next. sam reads a lot of business books for someone who works in finance"},
            {"role": "assistant", "content": "Sam seems like a good sounding board."},
            {"role": "user", "content": "he's the best. known him since high school in portland. he works at a bank but he's always been entrepreneurial. helps me think through pricing, strategy, customer conversations. honestly i don't know what i'd do without him and riley and jake in my corner"},
            {"role": "assistant", "content": "Strong support system. That matters more than most founders realize."},
            {"role": "user", "content": "dev said the same thing. he said his last startup failed partly because the founder was isolated. no friends, no partner, just 'the mission.' he told me 'don't sacrifice your people for the company, sacrifice sleep instead.' which is terrible health advice but the sentiment is right"},
            {"role": "assistant", "content": "Any birthday resolutions for 28?"},
            {"role": "user", "content": "get carbonsense to $50k MRR, keep my relationship strong, squat 315, and maybe learn to cook something other than eggs. riley keeps hinting she wants me to learn pad thai. her favorite is from thai-kun on south congress"},
        ],
        "facts_introduced": [
            "Jordan turned 28 on September 14, 2024",
            "F1 at COTA with Sam and Jake, paddock passes (Sam's gift)",
            "Riley made red velvet birthday cake",
            "Watching Shogun together",
            "Riley started masters Sept 1",
            "Dr. Martinez recommended 'Burnout' by Emily Nagoski",
            "Read 'The Lean Startup', Sam recommended 'Hard Thing About Hard Things'",
            "Sam and Jordan known since high school in Portland",
            "Sam works in finance/banking",
            "Dev's previous startup failed"
        ],
        "facts_updated": []
    })

    # Session 8: Meeting Nina Vasquez
    sessions.append({
        "session_id": 8,
        "timestamp": "2024-11-20T21:00:00",
        "turns": [
            {"role": "user", "content": "had an incredible meeting today. met nina vasquez from elevation ventures at epoch coffee on north loop. she was wearing an orange scarf. she's interested in our seed round"},
            {"role": "assistant", "content": "Elevation Ventures is a strong climate-tech fund. How did the meeting go?"},
            {"role": "user", "content": "she said our pricing is way too low. enterprise carbon tools charge $10-15k per facility. she thinks we should be at $5k base, $12k enterprise. we're leaving so much money on the table"},
            {"role": "assistant", "content": "That's a significant price increase. Did she say anything about the competition?"},
            {"role": "user", "content": "ecotrace is our main competitor — they just raised $40M series B. 89% scope 1, no scope 3, batch processing only. she said 'ecotrace is a faster horse, you're building a car'"},
            {"role": "assistant", "content": "That's a powerful metaphor. What about the accelerator program?"},
            {"role": "user", "content": "she wants us to apply for their accelerator cohort. deadline january 15. 400 applications for 12 spots. the cohort gets $1.5M seed, office space, and nina's personal mentorship for 4 months"},
            {"role": "assistant", "content": "What's the regulatory landscape looking like?"},
            {"role": "user", "content": "this is the huge news — EPA just released new scope 3 reporting requirements for all manufacturers over $100M revenue. our total addressable market just went from $2B to $8B overnight. nina literally clapped when i told her about our scope 3 prototype"},
            {"role": "assistant", "content": "TAM quadrupling on regulation is the climate-tech thesis. How are you feeling about the meeting?"},
            {"role": "user", "content": "best meeting of my life. called dev immediately after. he said 'we need to apply.' even sam was excited — he came to epoch to see the end of it and nina told him 'your friend is building something important.' sam was beaming"},
        ],
        "facts_introduced": [
            "Nina Vasquez: partner at Elevation Ventures",
            "Met at Epoch Coffee, Nov 20, orange scarf",
            "Elevation accelerator cohort deadline: January 15",
            "Nina's pricing advice: $5K base, $12K enterprise",
            "EcoTrace: competitor, $40M raised, 89% scope 1, no scope 3",
            "Nina quote: 'EcoTrace is a faster horse, you're building a car'",
            "EPA scope 3 mandate expands TAM from $2B to $8B",
            "Elevation cohort: $1.5M seed + office + mentorship"
        ],
        "facts_updated": []
    })

    # Session 9: Thanksgiving and family
    sessions.append({
        "session_id": 9,
        "timestamp": "2024-11-29T14:00:00",
        "turns": [
            {"role": "user", "content": "thanksgiving in portland with the family. riley and biscuit came with me. mom made her famous dumplings — recipe from grandma. dad's knee is better after physical therapy, he's doing morning walks again"},
            {"role": "assistant", "content": "Glad about your dad's recovery. Did you tell your parents about CarbonSense?"},
            {"role": "user", "content": "tried to. mom sent me an article about startup failure rates the DAY BEFORE thanksgiving. classic helen chen move. 'just want you to be informed, baobei.' she's coming around now that we have revenue though"},
            {"role": "assistant", "content": "What's the revenue picture?"},
            {"role": "user", "content": "$8k MRR by december. meridian annual contract plus lone star starting. mom understands revenue. she ran the family restaurant for 20 years so she respects actual money coming in, not 'projections'"},
            {"role": "assistant", "content": "How about Lily?"},
            {"role": "user", "content": "lily brought her new boyfriend marcus to thanksgiving. different marcus from my gym buddy marcus johnson — lily's marcus does crossfit, which jake says doesn't count as real lifting lol"},
            {"role": "assistant", "content": "How's Lily doing career-wise?"},
            {"role": "user", "content": "she changed her major from pre-med to marketing. mom absolutely freaked. 'two chen children not being doctors!' but lily's happy and that's what matters. she got an internship at a portland agency"},
            {"role": "assistant", "content": "How was the family dynamic overall?"},
            {"role": "user", "content": "good actually. riley and lily bonded — stayed up late talking while i fell asleep on the couch with biscuit. dad pulled me aside and said he's proud even if mom doesn't know how to show it. also biscuit ate a dinner roll off aunt linda's plate which was mortifying but very on-brand"},
        ],
        "facts_introduced": [
            "Mom's name: Helen Chen, from Portland",
            "Dad doing physical therapy for knee",
            "$8K MRR by December 2024",
            "Lily's boyfriend Marcus (different from gym Marcus Johnson)",
            "Lily's Marcus does CrossFit",
            "Mom ran family restaurant for 20 years",
            "Lily interning at Portland agency"
        ],
        "facts_updated": []
    })

    # Session 10: Year-end tech decisions
    sessions.append({
        "session_id": 10,
        "timestamp": "2024-12-01T20:00:00",
        "turns": [
            {"role": "user", "content": "year end planning with dev. python fastapi is struggling above 200 concurrent connections. response times spiking to 340ms. customers are going to notice soon"},
            {"role": "assistant", "content": "200 concurrent is low for enterprise. What's the plan?"},
            {"role": "user", "content": "dev wants to rewrite the API layer in go. he's been prototyping on weekends and getting 10x improvement in concurrency"},
            {"role": "assistant", "content": "Go makes sense for a high-concurrency API layer. What about Rust?"},
            {"role": "user", "content": "dev says go is pragmatic, rust is overkill for an API. we're not building a database. go gives us 10x concurrency with a language most backend devs already know. python stays for ML inference and data pipelines — aisha would revolt if we tried to port her models"},
            {"role": "assistant", "content": "Fair point. What about compliance?"},
            {"role": "user", "content": "SOC 2 Type 1 just passed — all 47 controls green. maria at meridian required it before signing the annual contract. our security setup from day one is paying off. AES-256, TLS 1.3, IAM least privilege — enterprise customers love it"},
            {"role": "assistant", "content": "How's the personal side going?"},
            {"role": "user", "content": "riley wants a weekend away for christmas. planning fredericksburg wine country in january. no laptops, no slack. she says she hasn't really seen me since i started the company. she's right — i need this too"},
            {"role": "assistant", "content": "When did you last take a day off?"},
            {"role": "user", "content": "i honestly can't remember. maybe thanksgiving? and even then i was on my laptop after dinner. dev said 'take the trip, i'll hold the fort.' he's been great about boundaries — he takes sundays completely off and is more productive than me. i should learn from that"},
            {"role": "assistant", "content": "Dev has the right idea."},
            {"role": "user", "content": "sam said the same thing: 'you can't pour from an empty cup bro.' very fortune-cookie of him but he's not wrong. ok fredericksburg in january. hye meadow winery has a cottage. biscuit-friendly. no excuses"},
        ],
        "facts_introduced": [
            "FastAPI struggling above 200 concurrent connections, 340ms",
            "Dev proposing Go rewrite for API layer, 10x improvement",
            "SOC 2 Type 1 passed, 47 controls",
            "Fredericksburg weekend planned for January 2025",
            "Riley feeling neglected",
            "Maria at Meridian required SOC 2 for annual contract"
        ],
        "facts_updated": []
    })

    # Session 11: Fredericksburg + Elevation application
    sessions.append({
        "session_id": 11,
        "timestamp": "2025-01-08T22:00:00",
        "turns": [
            {"role": "user", "content": "just got back from fredericksburg with riley. stayed at hye meadow winery cottage. no cell service, just vineyards and biscuit chasing butterflies. first time i put the laptop away in months"},
            {"role": "assistant", "content": "That sounds restorative. How's Riley feeling now?"},
            {"role": "user", "content": "much better. she said it reminded her why we work — the vineyard sunset, biscuit napping on the porch. we talked about our future for the first time in months without me checking my phone"},
            {"role": "assistant", "content": "That's important. What did you talk about?"},
            {"role": "user", "content": "buying a house eventually, getting another dog, whether she wants to stay in austin after her masters. she loves austin now. also i tried a tempranillo there that changed my mind about texas wine"},
            {"role": "assistant", "content": "Now you're back in startup mode though?"},
            {"role": "user", "content": "yeah back to reality — dev and i are finalizing the elevation ventures deck. deadline january 15. the EPA scope 3 mandate basically makes our product mandatory for thousands of companies"},
            {"role": "assistant", "content": "How's the deck looking?"},
            {"role": "user", "content": "strong. 96.1% scope 1, $8k MRR growing, 3 paid customers, huge TAM with EPA mandate. nina told us 400 applications for 12 spots. dev's slides are clean — he learned figma for the pitch deck"},
            {"role": "assistant", "content": "Dev learning Figma is commitment."},
            {"role": "user", "content": "he said 'i refuse to let our pitch lose because of ugly slides.' he's right. first impressions matter. sam reviewed the financial projections and said they're conservative which is actually a good thing — nina hates hockey stick projections"},
            {"role": "assistant", "content": "How's Riley's first semester going?"},
            {"role": "user", "content": "she's loving it. her cohort does study groups at epoch coffee which is funny since that's where i met nina. she comes home glowing after practicum sessions. she's going to be an amazing therapist — she already is, honestly. been my unofficial one for years"},
        ],
        "facts_introduced": [
            "Fredericksburg trip: Hye Meadow Winery Cottage, Jan 3-5 2025",
            "Elevation application: deadline Jan 15",
            "Riley loves Austin, considering staying long-term",
            "400 applications for 12 spots at Elevation"
        ],
        "facts_updated": []
    })

    # Session 12: Elevation acceptance + hiring
    sessions.append({
        "session_id": 12,
        "timestamp": "2025-02-15T20:00:00",
        "turns": [
            {"role": "user", "content": "WE GOT IN. elevation ventures accepted us february 10. $1.5M seed at $10M post-money valuation. nina led the deal. 12 companies from 400 applications and we're one of them"},
            {"role": "assistant", "content": "Congratulations! That's incredible after all the work on the application. How does the cap table look?"},
            {"role": "user", "content": "me 42.5%, dev 34%, elevation 15%, option pool 8.5%. nina said our cap table is 'founder-friendly' which matters for series A leverage later"},
            {"role": "assistant", "content": "Smart to protect founder ownership early. How did you celebrate?"},
            {"role": "user", "content": "valentine's day was the day after we heard, so double celebration. took riley to uchi for omakase. $452 total with sake flight. she deserved it — she proofread our entire application twice"},
            {"role": "assistant", "content": "Uchi omakase is a proper celebration. What's the hiring plan now with funding?"},
            {"role": "user", "content": "need 1 backend engineer, 1 ML engineer, 1 sales person. most important is ML — dr woo from UT suggested her former postdoc aisha rahman. phd in industrial emissions modeling, published 6 papers. perfect fit"},
            {"role": "assistant", "content": "What about Sam for the sales role?"},
            {"role": "user", "content": "sam is doing part-time sales consulting which is great but i explicitly told him 'no i'm not hiring sam as a full time employee.' he's my best friend and mixing that with employment is a recipe for disaster. he agrees actually — he'd rather be a freelance contributor than report to me"},
        ],
        "facts_introduced": [
            "Elevation accepted Feb 10, $1.5M seed at $10M post-money",
            "Cap table: Jordan 42.5%, Dev 34%, Elevation 15%, pool 8.5%",
            "Valentine's at Uchi: omakase, $452 total",
            "Dr. Woo suggested Aisha Rahman (PhD in emissions modeling, 6 papers)",
            "Sam doing part-time sales, NOT full-time employee"
        ],
        "facts_updated": []
    })

    # Session 13: Hiring Aisha + pricing change
    sessions.append({
        "session_id": 13,
        "timestamp": "2025-03-15T18:00:00",
        "turns": [
            {"role": "user", "content": "hired aisha rahman! $135k + 0.75% equity. she published 6 papers and already built a transformer model for scope 3 emissions estimation. dev said 'hire her, that scope 3 model alone is worth the equity'"},
            {"role": "assistant", "content": "That's a strong hire. When does she start?"},
            {"role": "user", "content": "started this week. she's already refactoring our scope 2 pipeline and asking smart questions about data normalization. the team energy changed immediately — dev is coding until midnight again which is both good and concerning"},
            {"role": "assistant", "content": "What about the pricing change Nina recommended back in November?"},
            {"role": "user", "content": "done. changed from $2k/$5k to $5k/$12k per facility. nina helped us rehearse the conversation with existing customers. grandfathered meridian at $2k for year 1 since they were our first believer"},
            {"role": "assistant", "content": "How did Lone Star and Gulf Coast react?"},
            {"role": "user", "content": "both signed at $5k without pushback. turns out nina was right — we were leaving money on the table. also random thing — switched biscuit's vet from heart of texas on south lamar to thrive on burnet road after they double-billed us $340"},
            {"role": "assistant", "content": "Good to get ahead of pricing now. How's Riley?"},
            {"role": "user", "content": "she called me out last night. said since the fundraise i've been even MORE absent, not less. 'you said funding would mean less stress, but you're just stressed about bigger numbers now.' she's right"},
            {"role": "assistant", "content": "What are you going to do about it?"},
            {"role": "user", "content": "dinner tonight, phone in the drawer. not as a one-time thing but as a new rule. also dr woo's phd student chen wei is starting research on supply chain emissions — potential collaboration with aisha on scope 3. but that's tomorrow's problem. tonight is riley's"},
        ],
        "facts_introduced": [
            "Aisha Rahman hired: $135K + 0.75% equity",
            "Pricing changed: $2K/$5K -> $5K/$12K per facility",
            "Meridian grandfathered at $2K for year 1",
            "Chen Wei: Dr. Woo's PhD student",
            "Vet switched from Heart of Texas to Thrive on Burnet Road",
            "Heart of Texas double-billed $340"
        ],
        "facts_updated": [
            "Pricing changed from $2K/$5K to $5K/$12K"
        ]
    })

    # Session 14: Growing fast
    sessions.append({
        "session_id": 14,
        "timestamp": "2025-05-01T20:00:00",
        "turns": [
            {"role": "user", "content": "7 paying customers, 14 facilities, $43k MRR. the go API rewrite is done — 3,200 concurrent connections, 12ms avg response. python version was 200 connections with 340ms"},
            {"role": "assistant", "content": "12ms is excellent. That's a massive improvement. How's the architecture split?"},
            {"role": "user", "content": "go handles API/auth/billing/webhooks. python handles ML inference and data processing. grpc between them. clean separation"},
            {"role": "assistant", "content": "Smart to keep Python for ML. Any new hires?"},
            {"role": "user", "content": "danny okafor applied from stripe for frontend — great take-home project. we're hiring him. $130k + 0.3%. he built their merchant dashboard"},
            {"role": "assistant", "content": "What happened with Sam's sales consulting role?"},
            {"role": "user", "content": "told sam his moonlighting is done — hiring a real VP sales. he learned a ton and wants to do his own thing eventually. he handled the lone star negotiation beautifully though. got them from $3k to $5k/facility"},
            {"role": "assistant", "content": "How's he taking it?"},
            {"role": "user", "content": "totally fine. sam's been reading 'venture deals' by brad feld and asking me about SAFEs. i think he's plotting his own startup. good for him honestly. also dev wants to implement feature flags with launchdarkly — i said just use environment variables for now, don't over-engineer"},
        ],
        "facts_introduced": [
            "7 customers, 14 facilities, $43K MRR (May 2025)",
            "Go API: 3,200 concurrent, 12ms response",
            "Go + Python via gRPC",
            "Danny Okafor: frontend hire from Stripe",
            "Sam stepping back, wants to start own thing",
            "Sam reading 'Venture Deals' by Brad Feld"
        ],
        "facts_updated": [
            "MRR grew from $8K (Dec 2024) to $43K (May 2025)"
        ]
    })

    # Session 15: Database migration + security
    sessions.append({
        "session_id": 15,
        "timestamp": "2025-05-15T22:00:00",
        "turns": [
            {"role": "user", "content": "postgres is struggling. query latency up to 2.3 seconds on the emissions time series. tried timescaledb — not fast enough. dev tested clickhouse and got queries down to 47ms"},
            {"role": "assistant", "content": "50x improvement is hard to ignore. Are you migrating everything?"},
            {"role": "user", "content": "no, clickhouse for time series / sensor / emissions data. postgres stays for users, auth, billing. clean separation. migration plan is 2 weeks, dual-write first then cutover"},
            {"role": "assistant", "content": "Smart approach. What about the security posture?"},
            {"role": "user", "content": "funny you mention that. had a security scare last thursday — port scanning, 45,000 requests in an hour targeting our API endpoints. WAF blocked most of it. added cloudflare, fail2ban, rate limiting"},
            {"role": "assistant", "content": "Any data exposure?"},
            {"role": "user", "content": "no, nothing got through. SOC 2 controls held. dev did a full audit — all 47 controls still passing. but it scared us. also dev asked about moving to kubernetes. i said 'definitely not, k8s is overkill for our stage. ECS is fine'"},
            {"role": "assistant", "content": "ECS with the right auto-scaling should cover you for a while."},
            {"role": "user", "content": "exactly. we're at 7 customers not 700. also added redis for caching frequently-accessed dashboard queries. reduced average page load from 1.2s to 200ms"},
            {"role": "assistant", "content": "How's Dev handling all these infrastructure changes?"},
            {"role": "user", "content": "he thrives on it honestly. said 'clickhouse migration is the most fun since building the prototype.' his dual-write approach means zero customer-facing downtime. aisha is helping validate that query results match between the two databases"},
        ],
        "facts_introduced": [
            "Migrated time series from PostgreSQL to ClickHouse (47ms vs 2.3s)",
            "TimescaleDB tested but not fast enough",
            "Security incident: port scanning, 45K requests",
            "Rejected Kubernetes: 'overkill, ECS is fine'",
            "Added Redis for dashboard caching",
            "SOC 2 all 47 controls passing"
        ],
        "facts_updated": [
            "Database: PostgreSQL -> ClickHouse for time series"
        ]
    })

    # Session 16: Scope 3 breakthrough
    sessions.append({
        "session_id": 16,
        "timestamp": "2025-05-25T19:00:00",
        "turns": [
            {"role": "user", "content": "aisha's scope 3 model v2: 88.9% accuracy on meridian, 91.2% on lone star, 86.4% on gulf coast. weighted avg 89.1%. graph attention networks on partial supply chain graphs"},
            {"role": "assistant", "content": "89.1% on scope 3 is impressive. EcoTrace doesn't even have scope 3. What drove the improvement?"},
            {"role": "user", "content": "chen wei's synthetic data augmentation using VAEs — generated 50k training samples from 2k real supply chain records. he's writing it up for ICML"},
            {"role": "assistant", "content": "Academic credibility is a nice side effect. How's demo day prep?"},
            {"role": "user", "content": "demo day is june 15. working on the pitch. nina says focus on the scope 3 breakthrough — that's our moat. also the EPA just moved the scope 3 reporting deadline up by 6 months. perfect timing"},
            {"role": "assistant", "content": "Any fun stuff coming up?"},
            {"role": "user", "content": "sam got ACL tickets for october — khruangbin headlining weekend 2. me, sam, riley, jake. also dev said he'd go this year. first time. he's more of a classical music guy honestly"},
            {"role": "assistant", "content": "Dev at a music festival should be entertaining."},
            {"role": "user", "content": "right? sam said he'll 'culturally educate' dev. aisha wants to come too — she's actually a huge khruangbin fan. her favorite album is mordechai. might be a whole company outing lol"},
        ],
        "facts_introduced": [
            "Scope 3: 89.1% avg via Graph Attention Networks",
            "Chen Wei: VAE synthetic data, 50K from 2K samples",
            "Chen Wei ICML paper",
            "Demo Day: June 15",
            "ACL tickets: Khruangbin, Weekend 2",
            "EPA moved scope 3 deadline up 6 months"
        ],
        "facts_updated": [
            "Scope 3: 84.7% -> 89.1%"
        ]
    })

    # Session 17: Demo Day
    sessions.append({
        "session_id": 17,
        "timestamp": "2025-06-16T10:00:00",
        "turns": [
            {"role": "user", "content": "demo day was yesterday. nina said best pitch of the cohort. 14 investors want follow-ups. three want to lead series A — sequoia, a16z, khosla"},
            {"role": "assistant", "content": "Three firms wanting to lead gives you leverage. Who are you leaning toward?"},
            {"role": "user", "content": "khosla. vinod actually understands the science. he asked about our graph attention network approach to scope 3. a16z kept asking about 'AI agents' which isn't what we do"},
            {"role": "assistant", "content": "What did Nina recommend?"},
            {"role": "user", "content": "nina agrees on khosla. she said vinod's rolodex in energy and manufacturing is unmatched. currently $67k MRR — two new customers signed this month"},
            {"role": "assistant", "content": "What about your personal state? You've been grinding hard on this pitch."},
            {"role": "user", "content": "sam says i look exhausted. honestly i cried in the bathroom after the pitch. relief crying. like a year of stress just came out. called mom from the parking lot. dad said 'i always knew you could do it'"},
            {"role": "assistant", "content": "That's a real moment. How's Riley?"},
            {"role": "user", "content": "she came to the pitch. front row. she said my hands were shaking the first 30 seconds but then i found my groove. she's proud. we're doing dinner at dai due tonight to celebrate"},
        ],
        "facts_introduced": [
            "Demo Day June 15: best pitch, 14 investor follow-ups",
            "Three want to lead: Sequoia, a16z, Khosla",
            "Leaning Khosla — Vinod understands science",
            "MRR: $67K (June 2025)",
            "Riley attended the pitch"
        ],
        "facts_updated": [
            "MRR: $43K (May) -> $67K (June)"
        ]
    })

    # Session 18: Anniversary disaster + therapy
    sessions.append({
        "session_id": 18,
        "timestamp": "2025-07-04T11:00:00",
        "turns": [
            {"role": "user", "content": "i messed up bad. missed our 5th anniversary dinner july 3. had uchiko reservation at 7:30. a sequoia call ran over and i just... didn't leave"},
            {"role": "assistant", "content": "What happened with Riley?"},
            {"role": "user", "content": "she waited at the restaurant for 45 minutes. called me twice, i didn't pick up. when i got home she said 'it's not just tonight. it's every night. i eat dinner alone with biscuit more than with you'"},
            {"role": "assistant", "content": "That's a serious wake-up call. What are you going to do?"},
            {"role": "user", "content": "starting therapy. for real this time. riley's professor dr martinez recommended dr linda choi — CBT specialist who works with entrepreneurs. i'm calling monday. also implementing a hard stop at 7pm every day, no exceptions"},
            {"role": "assistant", "content": "That's a good step. How are your health metrics looking?"},
            {"role": "user", "content": "terrible. resting heart rate 72 (was 64 in october). sleeping 5.8 hours. only 4200 steps daily. chest tightness that comes and goes. i've been ignoring it"},
            {"role": "assistant", "content": "Chest tightness at 28 is concerning. Have you seen a doctor?"},
            {"role": "user", "content": "riley is making me go. probably stress related. also switched gym to evenings because i can't wake up early anymore on 5 hours of sleep. but jake can't do evenings — he coaches little league at 6:30. so i'm going alone which means i skip more often"},
            {"role": "assistant", "content": "The accountability partner loss compounds it. Sam?"},
            {"role": "user", "content": "sam noticed too. he said 'bro you look like shit, eat something.' he's right. i've been living on coffee and whatever's in the office. riley left a note on the fridge that said 'i miss the jordan who took care of himself.' that one hit hard"},
            {"role": "assistant", "content": "That note from Riley is painful but it shows she cares enough to be honest."},
            {"role": "user", "content": "she's not wrong about any of it. i used to cook dinner, we'd watch shows together, walk biscuit at sunset, actually be present. now i'm physically home but mentally still at work. the 7pm stop starts now. non-negotiable. if sequoia can't do a call before 7 they can wait until tomorrow"},
        ],
        "facts_introduced": [
            "Missed 5th anniversary July 3 for Sequoia call",
            "Uchiko reservation at 7:30",
            "Committed to 7pm hard stop",
            "Starting therapy with Dr. Linda Choi (CBT)",
            "Health crisis: RHR 72, sleep 5.8hr, 4200 steps, chest tightness",
            "Gym switched to evenings, Jake coaches little league"
        ],
        "facts_updated": [
            "Gym: mornings -> evenings (June 2025)",
            "Health metrics declined significantly"
        ]
    })

    # Session 19: Series A + Aisha retention
    sessions.append({
        "session_id": 19,
        "timestamp": "2025-08-25T20:00:00",
        "turns": [
            {"role": "user", "content": "series A closed. $10M from khosla at $55M pre-money. $65M company. vinod khosla personally joined the board call"},
            {"role": "assistant", "content": "Congratulations. That's a huge milestone from where you started. How's the cap table?"},
            {"role": "user", "content": "diluted but still good. me 33.1%, dev 26.5%, khosla 18%, elevation 11.7%, option pool 10.8%. also had to deal with aisha — google offered her $280k"},
            {"role": "assistant", "content": "That's double her current comp. How'd you keep her?"},
            {"role": "user", "content": "raised her to $160k + 1.25% equity + $30k student loan coverage. the student loan thing was riley's suggestion. riley said 'what would make YOU stay somewhere? the thing that reduces your anxiety the most.' brilliant"},
            {"role": "assistant", "content": "Riley has good instincts. What about the VP Sales hire?"},
            {"role": "user", "content": "rachel torres — 12 years enterprise SaaS at salesforce and hubspot. $180k + 1%. nina connected us. she's already mapping 40 target accounts in the first week"},
            {"role": "assistant", "content": "How's the business looking overall?"},
            {"role": "user", "content": "MRR hit $82k in september, 13 customers, 36 facilities. 0% churn. not a single customer has left. rachel says the churn number is what sells — enterprise buyers are terrified of switching costs"},
            {"role": "assistant", "content": "How did you celebrate the Series A?"},
            {"role": "user", "content": "took the whole team to uchiko. dev made a toast: 'to building something that matters.' riley surprised me with a framed photo of our first whiteboard sketch from dev's apartment — the original CarbonSense architecture diagram. i may have gotten emotional"},
        ],
        "facts_introduced": [
            "Series A: $10M from Khosla, $55M pre ($65M post), Aug 25",
            "Aisha retention: $160K + 1.25% + $30K student loan (Riley's idea)",
            "Google offered Aisha $280K",
            "Rachel Torres: VP Sales, $180K + 1%, via Nina",
            "MRR: $82K (Sep), 13 customers, 36 facilities, 0% churn",
            "Rachel from Salesforce and HubSpot"
        ],
        "facts_updated": [
            "Aisha comp: $135K/0.75% -> $160K/1.25% + $30K student loan"
        ]
    })

    # Session 20: House hunting
    sessions.append({
        "session_id": 20,
        "timestamp": "2025-09-01T19:00:00",
        "turns": [
            {"role": "user", "content": "mortgage pre-approved! up to $550k, 5.875% 30-year fixed. credit scores: me 782, riley 768"},
            {"role": "assistant", "content": "Great scores. Are you finding anything in budget?"},
            {"role": "user", "content": "found a listing we love — 2847 chicon st, 4 bed 2 bath, $495k, east austin. it's perfect. big backyard for biscuit"},
            {"role": "assistant", "content": "Four bedrooms gives you a home office. What's the neighborhood like?"},
            {"role": "user", "content": "walk score 82, bike score 91. built 1962 but renovated 2021. 1,850 sqft. we put in an offer and it got accepted! closing october 15"},
            {"role": "assistant", "content": "How are the numbers?"},
            {"role": "user", "content": "20% down is $99k, closing costs $12,847. monthly will be $3,254 including taxes and insurance. more than our $2,100 rent but we're building equity. riley is already planning a garden"},
            {"role": "assistant", "content": "Where's the down payment coming from?"},
            {"role": "user", "content": "combination of savings and my salary. also dev lent me $15k which i'll pay back after the series A money hits. don't tell nina lol. biscuit is going to lose his mind with a real yard after apartment life"},
            {"role": "assistant", "content": "What's the plan for the extra bedrooms?"},
            {"role": "user", "content": "main bedroom for us, one for riley's study, one for a home office, one for guests — mom and dad will visit in february. the home office means i can work from home some days which helps with the 7pm boundary. no commute means more time with riley and biscuit"},
        ],
        "facts_introduced": [
            "House: 2847 Chicon St, 4bed/2bath, $495K",
            "Mortgage: 5.875%, 30-year, credit 782/768",
            "Closing: October 15, down $99K, closing costs $12,847",
            "Monthly mortgage: $3,254",
            "Dev lent $15K for down payment"
        ],
        "facts_updated": []
    })

    # Session 21: Office move + competition
    sessions.append({
        "session_id": 21,
        "timestamp": "2025-10-01T20:00:00",
        "turns": [
            {"role": "user", "content": "big changes. moving out of our office on E Cesar Chavez to wework. $450/desk, flexible, and they have locations in austin AND houston which matters for rachel's sales team"},
            {"role": "assistant", "content": "Houston is a smart expansion for energy sector clients. Any downsides?"},
            {"role": "user", "content": "less ownership of the space, but we're growing too fast for that office anyway. 14 people. also — bad news. lost boeing to ecotrace. they undercut us at $2k vs our $5k"},
            {"role": "assistant", "content": "That hurts. How are you responding to the price competition?"},
            {"role": "user", "content": "building a TCO calculator with rachel and omar hassan (product manager we hired). our 96% vs their 89% accuracy means millions in carbon credit miscalculations. the 7% gap costs a 10-facility manufacturer roughly $2M annually in bad data"},
            {"role": "assistant", "content": "What does Nina think?"},
            {"role": "user", "content": "nina says 'don't compete on price, compete on accuracy and scope 3.' she's right. we have scope 3 at 89.1%. ecotrace has zero scope 3. also our 0% churn vs their high churn rate tells the whole story"},
            {"role": "assistant", "content": "Win on value, not cost. Smart."},
            {"role": "user", "content": "exactly. rachel's houston satellite is working already — 3 in-person meetings first week. pipeline $380k qualified. going after refining and petrochemical companies"},
        ],
        "facts_introduced": [
            "Moved to WeWork Austin + WeWork Houston",
            "Lost Boeing to EcoTrace on price",
            "Omar Hassan: Product Manager",
            "TCO calculator being built",
            "7% accuracy gap = ~$2M annually for 10-facility manufacturer",
            "Houston pipeline: $380K qualified"
        ],
        "facts_updated": [
            "Office: E Cesar Chavez -> WeWork"
        ]
    })

    # Session 22: House closing + therapy progress
    sessions.append({
        "session_id": 22,
        "timestamp": "2025-10-16T20:00:00",
        "turns": [
            {"role": "user", "content": "closed on the house yesterday! we're homeowners. inspector mike reeves went through everything — roof has about 5 years left, minor cosmetic foundation crack, 3-year trane HVAC, copper plumbing, 200 amp electrical"},
            {"role": "assistant", "content": "Copper plumbing and 200 amp are good signs. Any issues?"},
            {"role": "user", "content": "minor stuff — kitchen faucet drip, 2 windows need re-sealing, fence gate latch broken. asked for $3k credit and got it. riley is already on pinterest looking at paint colors"},
            {"role": "assistant", "content": "How's therapy going? You started in July right?"},
            {"role": "user", "content": "july 22 was my first session. biweekly CBT with dr choi. working on boundaries, perfectionism, and the big one — self-worth tied to company performance. she traced it to immigrant parent upbringing, especially mom's anxiety about stability"},
            {"role": "assistant", "content": "How's that affecting your day-to-day?"},
            {"role": "user", "content": "night and day. switched meditation from headspace to insight timer in august — more flexibility, better sleep meditations. back to morning gym since the 7pm boundary means i actually sleep enough. RHR down to 66 from 72, sleeping 7 hours, weight 175. chest tightness is gone"},
            {"role": "assistant", "content": "That's a complete reversal from three months ago."},
            {"role": "user", "content": "dr choi says the chest tightness was psychosomatic — anxiety manifesting physically. once we addressed the root cause it went away. riley noticed before i did honestly. she said 'you're laughing again'"},
        ],
        "facts_introduced": [
            "House closed Oct 15, inspector Mike Reeves",
            "Therapy started July 22, biweekly CBT",
            "Switched Headspace -> Insight Timer (Aug 2025)",
            "Health recovering: RHR 66, sleep 7hr, weight 175",
            "Got $3K credit for repairs",
            "Chest tightness psychosomatic per Dr. Choi"
        ],
        "facts_updated": [
            "Meditation: Headspace -> Insight Timer",
            "Gym: back to mornings (Oct 2025)"
        ]
    })

    # Session 23: Team growth
    sessions.append({
        "session_id": 23,
        "timestamp": "2025-10-12T14:00:00",
        "turns": [
            {"role": "user", "content": "team is growing fast. just hired: luis moreno (ex-stripe, go), preet kaur (ex-datadog, monitoring), danny okafor (frontend from stripe). $130k + 0.3% each on the eng side"},
            {"role": "assistant", "content": "That's solid engineering talent. What about go-to-market?"},
            {"role": "user", "content": "rachel hired mike chen (AE), sarah lindquist (AE), and jamie walsh (SDR). she knows how to build a sales team. mike chen is crushing it — closed two deals his first month"},
            {"role": "assistant", "content": "That's 14 people now counting everyone?"},
            {"role": "user", "content": "yeah let me count: me, dev, aisha, danny, luis, preet — that's eng. rachel, mike chen, sarah, jamie — sales. tanya reed (customer success), omar hassan (product), becky tran (office admin). plus chen wei as sponsored phd. 14 full-time"},
            {"role": "assistant", "content": "Quite a team from two guys in an apartment."},
            {"role": "user", "content": "right? also funny thing — our AE mike chen has the same name as my cousin mike chen who works at anthropic in SF. totally different person. dev keeps mixing up their slack messages when i mention 'mike chen said...'"},
            {"role": "assistant", "content": "How's the culture with all these new people?"},
            {"role": "user", "content": "good. dev started 'demo fridays' where anyone shows what they built that week. aisha demoed scope 3 model improvements last friday and everyone clapped. weekly all-hands, monthly team lunch. feels like a real company now. rachel even started a sales leaderboard which is both motivating and terrifying"},
        ],
        "facts_introduced": [
            "Luis Moreno, Preet Kaur, Danny Okafor: engineering hires",
            "Mike Chen (AE), Sarah Lindquist (AE), Jamie Walsh (SDR)",
            "Tanya Reed (CS), Omar Hassan (PM), Becky Tran (admin)",
            "Team: 14 people",
            "Cousin Mike Chen at Anthropic",
            "Demo Fridays, weekly all-hands, monthly team lunch"
        ],
        "facts_updated": []
    })

    # Session 24: ACL + Lily moves
    sessions.append({
        "session_id": 24,
        "timestamp": "2025-10-06T13:00:00",
        "turns": [
            {"role": "user", "content": "ACL was amazing. khruangbin destroyed it. weekend 2 was perfect weather. me, riley, sam, jake, and lily all went together"},
            {"role": "assistant", "content": "Full crew! Did Sam bring Maya?"},
            {"role": "user", "content": "yes! riley and maya are now best friends. they disappeared for like 2 hours at the food stalls. maya is a nurse at dell seton, met sam on bumble back in march. she's great for him — keeps him grounded"},
            {"role": "assistant", "content": "What about Lily? I thought she was in Portland."},
            {"role": "user", "content": "she moved to austin! works at indeed now, got promoted to marketing manager. campaign analytics team. broke up with marcus in august — he moved to seattle for amazon. she's better off honestly"},
            {"role": "assistant", "content": "Is she seeing anyone new?"},
            {"role": "user", "content": "she has a crush on this guy ben, UX designer at indeed. they keep 'accidentally' running into each other at the coffee machine. i told her 'just ask him out, the chen family doesn't do subtle' and she threw a pillow at me"},
            {"role": "assistant", "content": "Protective big brother mode activated. What else is going on?"},
            {"role": "user", "content": "lily found this taco truck el primo on east 12th — she claims it's better than veracruz. fighting words in this household. riley agrees with lily which means i'm outnumbered"},
            {"role": "assistant", "content": "How's it feel having Lily close by?"},
            {"role": "user", "content": "honestly amazing. she comes over for dinner twice a week. her and riley do wine nights. biscuit loves her. having family nearby makes austin feel like home in a way it didn't before. mom is jealous — both her kids left portland"},
        ],
        "facts_introduced": [
            "Sam's girlfriend Maya: nurse at Dell Seton, met on Bumble",
            "Riley and Maya became close friends",
            "Lily moved to Austin, Indeed, Marketing Manager",
            "Lily broke up with Marcus (Aug, he moved to Seattle)",
            "Lily crushing on Ben (UX designer at Indeed)",
            "El primo taco truck on East 12th (Lily's rec)"
        ],
        "facts_updated": [
            "Lily's Marcus: broke up August 2025"
        ]
    })

    # Session 25: European expansion
    sessions.append({
        "session_id": 25,
        "timestamp": "2025-11-15T21:00:00",
        "turns": [
            {"role": "user", "content": "spoke at climate tech summit SF. 500 people in the audience. biggest stage of my life. and the best part — ecotrace demo crashed twice during their presentation"},
            {"role": "assistant", "content": "That's unfortunate for them. How did yours go?"},
            {"role": "user", "content": "flawless. live demo of scope 3 tracking. crowd gasped when i showed 89.1% accuracy on partial supply chain data. got a standing ovation from the sustainability directors section"},
            {"role": "assistant", "content": "What about the European expansion you've been planning?"},
            {"role": "user", "content": "partnering with klimasync for europe. EU CSRD mandate requires emissions monitoring by 2027 so there's massive demand. we're setting up AWS eu-west-1 for data residency compliance"},
            {"role": "assistant", "content": "How's the European model performing?"},
            {"role": "user", "content": "aisha trained a european-specific scope 3 model at 87.3%. different supply chains than US so needed separate training. also chen wei's ICML paper got accepted — 91.2% scope 3 accuracy in the paper. reviewer called it 'a significant contribution'"},
            {"role": "assistant", "content": "Academic validation plus commercial traction. Anything else from the summit?"},
            {"role": "user", "content": "a bloomberg journalist wants to feature us in a climate tech piece. and i got drinks with the CEO of a german steel company who wants to be our first EU customer. rachel is following up"},
        ],
        "facts_introduced": [
            "Climate Tech Summit SF: 500 people",
            "KlimaSync partnership for Europe",
            "EU CSRD mandate by 2027",
            "European scope 3: 87.3%",
            "Chen Wei ICML accepted: 91.2% scope 3",
            "Bloomberg feature incoming",
            "German steel company interested as first EU customer"
        ],
        "facts_updated": []
    })

    # Session 26: End of year reflection
    sessions.append({
        "session_id": 26,
        "timestamp": "2025-12-15T20:00:00",
        "turns": [
            {"role": "user", "content": "board meeting today. numbers: $1.2M ARR, 15 customers, 42 facilities, 14 employees, 0% churn, NRR 135%. nina is thrilled"},
            {"role": "assistant", "content": "135% NRR means existing customers are spending 35% more. That's expansion revenue working. What's Nina's vision for next year?"},
            {"role": "user", "content": "series B in Q2 2026 — she's targeting $25-40M at $200-300M valuation. milestones: $5M ARR by dec 2026, 3 EU customers via klimasync, 50 total customers, scope 3 above 92%"},
            {"role": "assistant", "content": "Aggressive but achievable given the trajectory. How are you feeling about all of it?"},
            {"role": "user", "content": "honestly? grateful. 18 months ago i was checking my savings every morning wondering if we'd make it. now we have 24 months runway and product-market fit. dr choi would be proud of that perspective shift"},
            {"role": "assistant", "content": "Speaking of personal life — how are things with Riley?"},
            {"role": "user", "content": "amazing. i'm planning to propose. found a vintage art deco ring at a fredericksburg estate sale — $4,200, it's on layaway. plan is after riley's graduation may 17, walk to lady bird lake at sunset. sam and lily know. dev knows. nobody else"},
            {"role": "assistant", "content": "That sounds perfect. The fredericksburg connection makes it meaningful."},
            {"role": "user", "content": "right? that's where we reconnected. she said that trip saved us. the ring has this intricate geometric pattern — very her. she's not a big diamond person. she once told lily 'if jordan proposes with a boring solitaire i'll say no just on principle'"},
        ],
        "facts_introduced": [
            "$1.2M ARR, 15 customers, 42 facilities (Dec 2025)",
            "Series B target: $25-40M at $200-300M, Q2 2026",
            "Engagement ring: vintage art deco, $4,200, layaway",
            "Proposal: after graduation May 17, Lady Bird Lake, sunset",
            "NRR 135%",
            "24 months runway"
        ],
        "facts_updated": []
    })

    # Session 27: Biscuit + dog life
    sessions.append({
        "session_id": 27,
        "timestamp": "2025-12-11T14:00:00",
        "turns": [
            {"role": "user", "content": "saw a golden retriever puppy at the shelter today. 4 months old, wearing a little bandana. i want another dog so bad"},
            {"role": "assistant", "content": "How does Riley feel about that?"},
            {"role": "user", "content": "she said absolutely not. biscuit needs to lose 2 lbs first. he was 28.4 lbs in march, now he's 30.1 in september. the neighbor carol keeps giving him treats over the fence"},
            {"role": "assistant", "content": "Has Biscuit had any health issues with the weight gain?"},
            {"role": "user", "content": "not from weight but he's had adventures. emergency vet december 2024 — ate an entire rotisserie chicken off the counter. $795 at the emergency clinic on christmas eve. riley was NOT amused. and a bee sting september 2024, just gave him benadryl for that one"},
            {"role": "assistant", "content": "Rotisserie chicken on Christmas Eve is peak corgi behavior. When can you revisit the puppy idea?"},
            {"role": "user", "content": "riley said 'ask me again in spring. MAYBE.' she's not wrong though — we just moved, the yard needs fencing work, and biscuit is an only-child dog. he might not even like a sibling"},
            {"role": "assistant", "content": "Does Biscuit get along with other dogs?"},
            {"role": "user", "content": "yes actually. he made a friend named maple, a golden retriever, at zilker park. they do zoomies together. also he's already dug 3 holes in the new yard. riley put up a sign that says 'biscuit's excavation zone' which is passive aggressive and hilarious"},
        ],
        "facts_introduced": [
            "Wants second dog, Riley says no (Biscuit overweight)",
            "Biscuit: 28.4 lbs (Mar) -> 30.1 lbs (Sep)",
            "Emergency vet Dec 2024: rotisserie chicken, $795",
            "Bee sting Sept 2024",
            "Riley: 'ask again in spring, MAYBE'",
            "Biscuit's friend Maple (golden retriever) at Zilker",
            "Dug 3 holes in new yard"
        ],
        "facts_updated": []
    })

    # Session 28: Sam's fintech + year-end
    sessions.append({
        "session_id": 28,
        "timestamp": "2025-12-28T21:00:00",
        "turns": [
            {"role": "user", "content": "sam is getting serious about his fintech idea. carbon credit marketplace for corporate banking. think stripe for carbon credits"},
            {"role": "assistant", "content": "Interesting. Didn't Nina ask CarbonSense to build something similar?"},
            {"role": "user", "content": "she did. but dev said scope creep — and he's right. as a separate company though, our monitoring + sam's marketplace is a powerful combo. nina thinks so too. she might even invest in sam"},
            {"role": "assistant", "content": "From moonlighting sales consultant to founder. How's your fitness and personal life holding up with everything?"},
            {"role": "user", "content": "actually great. half marathon april 6: 1:52:34. strava 2025 year-end: 127 runs, 482 miles, best 5K 22:48. training for the austin full marathon feb 16, goal sub-4 hours"},
            {"role": "assistant", "content": "That's a big jump from half to full. Reading anything good?"},
            {"role": "user", "content": "read 10 books this year: hard thing about hard things (5 stars — sam was right), zero to one, measure what matters, lean startup, thinking fast and slow, body keeps the score (dr choi recommended), atomic habits, drawdown (5 stars), burnout by nagoski, and shoe dog"},
            {"role": "assistant", "content": "Body Keeps the Score makes sense with your therapy journey. Good year of reading."},
            {"role": "user", "content": "yeah dr choi assigns 'homework reading' which i actually enjoy. the body keeps the score explained so much about why stress was showing up as chest tightness. anyway — 2025 was the year of my life. scary, painful, but incredible"},
        ],
        "facts_introduced": [
            "Sam's fintech: carbon credit marketplace",
            "Half marathon April 6: 1:52:34",
            "Strava 2025: 127 runs, 482 miles, 5K PR 22:48",
            "Austin Marathon Feb 16, goal sub-4",
            "Books read (10 listed)",
            "Dr. Choi assigns homework reading"
        ],
        "facts_updated": []
    })

    # Session 29: Upcoming events
    sessions.append({
        "session_id": 29,
        "timestamp": "2026-01-05T18:00:00",
        "turns": [
            {"role": "user", "content": "new year planning. board meeting jan 15 — david kim from khosla will be there for first time as board observer. lily's birthday dinner at uchi feb 8 — turning 25, i'm covering, she wants omakase"},
            {"role": "assistant", "content": "Uchi omakase for Lily's birthday is nice. What else is on the calendar?"},
            {"role": "user", "content": "marathon feb 16, bib 4821. been doing 40 mile weeks. jake is pacing me for the first 13 miles then peeling off — he's not doing the full"},
            {"role": "assistant", "content": "Smart to have a pacer for the first half. Parents visiting too?"},
            {"role": "user", "content": "feb 15-22. alaska airlines arriving 2:15pm. staying at our house — finally have a guest room. mom hasn't seen the house yet. she's going to cry"},
            {"role": "assistant", "content": "And later in the year?"},
            {"role": "user", "content": "riley's graduation may 17 at frank erwin center — the big one. then the proposal. portland reunion aug 15 at mcmenamins kennedy school — class of 2016 ten-year reunion. and ACL oct 10-12. stacking up to be an even bigger year than 2025"},
            {"role": "assistant", "content": "That's a full calendar. The graduation-to-proposal sequence will be emotional."},
            {"role": "user", "content": "i've been rehearsing what i'll say in the shower and biscuit judges me. sam offered to be 'on standby with champagne.' lily is organizing the post-proposal dinner at uchiko. dev said 'just don't fumble the ring into the lake'"},
        ],
        "facts_introduced": [
            "Board meeting Jan 15, David Kim (Khosla designee)",
            "Lily's birthday Feb 8 at Uchi, turning 25",
            "Marathon Feb 16, bib 4821",
            "Parents visiting Feb 15-22, Alaska Airlines 2:15pm",
            "Riley graduation May 17, Frank Erwin Center",
            "Portland reunion Aug 15, Class of 2016",
            "ACL Oct 10-12",
            "Jake pacing first 13 miles of marathon"
        ],
        "facts_updated": []
    })

    # Session 30: Financial overview
    sessions.append({
        "session_id": 30,
        "timestamp": "2025-12-31T14:00:00",
        "turns": [
            {"role": "user", "content": "year-end financial review. personal: salary $120k, mortgage $3,254/mo, rivian R1S $892/mo. sam said 'climate CEO can't drive a gas truck' and he was right"},
            {"role": "assistant", "content": "How are your investments?"},
            {"role": "user", "content": "robinhood $12,847 in VOO, QCLN, and TSLA. IRA at $52,419 rolled over from my dataflux 401k. not bad for someone who had $45k in savings 18 months ago"},
            {"role": "assistant", "content": "What about company finances?"},
            {"role": "user", "content": "mercury bank: $10.8M, monthly burn $95k, 24 months runway. burn includes all salaries, AWS, wework, tools. rachel says we need to hire 3 more by Q2"},
            {"role": "assistant", "content": "Cap table?"},
            {"role": "user", "content": "me 33.1% at 4,250,000 shares. dev 26.5% at 3,400,000. khosla 18%, elevation 11.7%, option pool 10.8%. 409A valuation $5.06/share on 12,850,000 total shares"},
            {"role": "assistant", "content": "At $5.06 your shares are worth about $21.5M on paper."},
            {"role": "user", "content": "i try not to think about that. it's all paper until series B or exit. visa ending 4821 for personal stuff, amex ending 9012 for higher-end, plus company amex for business expenses. riley manages the personal finances — she's way more organized than me"},
        ],
        "facts_introduced": [
            "Salary $120K, Rivian R1S $892/mo",
            "Mercury $10.8M, burn $95K/mo, 24mo runway",
            "Cap table: Jordan 33.1%, Dev 26.5%, Khosla 18%, Elevation 11.7%",
            "409A: $5.06/share, 12.85M shares",
            "Visa 4821, Amex 9012, company Amex",
            "Jordan's shares worth ~$21.5M on paper"
        ],
        "facts_updated": []
    })

    # Session 31: Competitive analysis
    sessions.append({
        "session_id": 31,
        "timestamp": "2025-10-20T11:00:00",
        "turns": [
            {"role": "user", "content": "i asked nina about potentially acquiring ecotrace. thought it might be cheaper than competing"},
            {"role": "assistant", "content": "Bold idea. What did she say?"},
            {"role": "user", "content": "absolutely not. they raised $40M, wouldn't sell for less than $100M. and why would we want their 89% accuracy code? our strategy: compete on quality. 96% vs 89% scope 1, real-time vs batch, scope 3 vs nothing, 0% churn vs their revolving door"},
            {"role": "assistant", "content": "Rachel's TCO calculator should help quantify that for prospects."},
            {"role": "user", "content": "she's building it with omar. interactive web tool where prospects enter their facility count and see the 5-year cost of bad data from lower accuracy. it's brutal math — 7% accuracy gap at scale costs millions in carbon credit miscalculations"},
            {"role": "assistant", "content": "How's the Houston expansion going?"},
            {"role": "user", "content": "great. wework satellite is working — 3 in-person meetings rachel's first week there. pipeline $380k qualified. going after refining and petrochemical which is big in houston obviously. ecotrace undercuts by 40% but we're earning growth, not buying it"},
            {"role": "assistant", "content": "Organic growth with 0% churn is the best story for Series B."},
            {"role": "user", "content": "exactly what nina says. she wants the NRR number front and center in the deck. 135% means customers keep buying more after they start. that's the real moat — not just winning deals but expanding them"},
            {"role": "assistant", "content": "What's driving the expansion revenue?"},
            {"role": "user", "content": "customers add more facilities after seeing ROI on the first ones. meridian started with 1 facility, now has 4. lone star went from 2 to 5. the scope 3 upsell is the next big expansion lever — every customer wants it after seeing our demo"},
        ],
        "facts_introduced": [
            "Nina rejected EcoTrace acquisition — would cost $100M+",
            "CarbonSense vs EcoTrace comparison",
            "Houston pipeline: $380K qualified",
            "TCO calculator: interactive web tool",
            "Meridian: 1->4 facilities, Lone Star: 2->5"
        ],
        "facts_updated": []
    })

    # Session 32: Communication + Austin places
    sessions.append({
        "session_id": 32,
        "timestamp": "2025-09-20T15:00:00",
        "turns": [
            {"role": "user", "content": "thinking about how i communicate differently with everyone. dev: technical, terse, lots of code links. sam: personal, emotional, deeper stuff. riley: loving but apologetic lately. mom: reassuring, filter out bad news. jake: bro-ish gym talk. nina: professional. lily: protective big brother mode"},
            {"role": "assistant", "content": "Being aware of those patterns is healthy. The 'apologetic' note with Riley is interesting — therapy insight?"},
            {"role": "user", "content": "dr choi pointed it out. i default to 'sorry' with riley because of guilt. working on replacing apologies with actions. also she noticed i text mom very differently — never mention stress, always positive. classic first-gen kid thing"},
            {"role": "assistant", "content": "What's your Austin routine look like now that you're settled?"},
            {"role": "user", "content": "restaurants: uchi and uchiko for special occasions, veracruz for tacos, torchys for late night, thai-kun, dai due for brunch, odd duck, pie society for pi day with riley — that's our tradition"},
            {"role": "assistant", "content": "Pi day at Pie Society is charming. Where else?"},
            {"role": "user", "content": "coffee at epoch on north loop — that's where i met nina actually. grocery rotation: HEB mueller for weekly, MT supermarket for asian ingredients (mom's recipes), whole foods for specialty stuff, costco monthly for bulk. gym moved from gold's south lamar to lifetime on burnet — closer to the new house"},
            {"role": "assistant", "content": "You've really built a life here. What's your typical weekend look like?"},
            {"role": "user", "content": "saturdays: morning gym with jake (even though different gyms now we meet up), farmers market with riley, afternoon work or errands, dinner out or cook together. sundays: sleep in, yoga, biscuit at zilker, meal prep, read. it's the first time in my life i've had a real routine and it makes everything else work better"},
        ],
        "facts_introduced": [
            "Communication styles vary by person",
            "Austin restaurants listed",
            "Pi day tradition at Pie Society with Riley",
            "Epoch Coffee on North Loop",
            "Grocery: HEB Mueller, MT Supermarket, Whole Foods, Costco",
            "Gym: Gold's South Lamar -> Lifetime on Burnet",
            "Weekend routine: gym, farmers market, zilker, yoga"
        ],
        "facts_updated": [
            "Gym changed: Gold's -> Lifetime on Burnet"
        ]
    })

    # Session 33: Housewarming
    sessions.append({
        "session_id": 33,
        "timestamp": "2025-11-23T12:00:00",
        "turns": [
            {"role": "user", "content": "housewarming party last night was amazing. sam brought brisket from terry blacks — 14 hour smoke. i bought a weber spirit II grill ($449) for the backyard. google fiber 2 gig is installed. this house is everything"},
            {"role": "assistant", "content": "Who came?"},
            {"role": "user", "content": "sam and maya, jake, lily, dev, aisha, rachel. even my neighbor dropped by — retired teacher named carol. she keeps giving biscuit treats which is why he's gaining weight. maya and riley made cocktails. jake broke the fence gate again playing cornhole"},
            {"role": "assistant", "content": "Sounds like a proper housewarming. Everyone settling in?"},
            {"role": "user", "content": "love it. riley is planning raised garden beds in the back and a proper dog run along the fence line. sam says he's working from MY house now since his apartment has 100mbps vs our 2 gig. lily and riley do girls nights at a wine bar on east 6th"},
            {"role": "assistant", "content": "Riley and Lily getting close is nice."},
            {"role": "user", "content": "they went from 'jordan's sister' and 'jordan's girlfriend' to actual friends. riley helps lily with her marketing presentations and lily helps riley decompress from her practicum clients"},
            {"role": "assistant", "content": "How's Biscuit adjusting to the house?"},
            {"role": "user", "content": "he's in heaven. at the party he greeted everyone individually with his stuffed hedgehog toy. brought it to each person like a gift. then dug another hole in the backyard. carol from next door came over with homemade cookies for us and treats for biscuit. she's going to be a great neighbor"},
        ],
        "facts_introduced": [
            "Housewarming Nov 22",
            "Weber Spirit II grill $449",
            "Google Fiber 2 gig",
            "Riley planning garden beds and dog run",
            "Neighbor Carol (retired teacher) gives Biscuit treats",
            "Riley and Lily became genuine friends"
        ],
        "facts_updated": []
    })

    # Session 34: Austin life
    sessions.append({
        "session_id": 34,
        "timestamp": "2025-08-21T11:00:00",
        "turns": [
            {"role": "user", "content": "therapy today at 4301 W William Cannon with dr choi. good session. CBT exercises on 'cognitive distortions in high-achievers.' she nailed some stuff about my patterns"},
            {"role": "assistant", "content": "What came up?"},
            {"role": "user", "content": "black-and-white thinking about success. if a quarter isn't record-breaking i feel like a failure. she called it 'CEO catastrophizing.' also power went out during our session — ERCOT at 95% capacity, third time this summer. 106 degrees outside"},
            {"role": "assistant", "content": "ERCOT and Austin summers. What do you love about Austin despite the complaints?"},
            {"role": "user", "content": "honestly so much. the food — ramen tatsu-ya, veracruz tacos, uchi sushi. outdoor life — zilker, lady bird lake, barton springs when it's 100 degrees. F1 at COTA every october. the people. the startup energy"},
            {"role": "assistant", "content": "Cedar allergies and I-35 traffic are the usual downsides I hear."},
            {"role": "user", "content": "both terrible. cedar season december through february destroys me. and I-35 from downtown to south lamar at 5pm is an existential crisis. but we bought a house in east austin. can't imagine living anywhere else"},
            {"role": "assistant", "content": "Would you ever leave Austin?"},
            {"role": "user", "content": "riley and i talked about it. answer is no. her program is here, my company is here, lily moved here, our friends are here. biscuit has his favorite spots — he knows the route to zilker by heart. this is home now. even mom admitted austin is nicer than portland weather-wise"},
        ],
        "facts_introduced": [
            "Therapy: 4301 W William Cannon, CBT",
            "Dr. Choi term: 'CEO catastrophizing'",
            "Austin: ERCOT failures, 106 degrees, cedar allergies, I-35 traffic",
            "Austin loves: food, outdoors, COTA, people"
        ],
        "facts_updated": []
    })

    # Session 35: Old apartment + Lily settling in
    sessions.append({
        "session_id": 35,
        "timestamp": "2025-08-06T19:00:00",
        "turns": [
            {"role": "user", "content": "not renewing the lease at 1847 E Riverside Dr Apt 4A. landlord wants to raise rent from $2,100 to $2,350. buying instead now that series A closed"},
            {"role": "assistant", "content": "Makes sense to build equity. How's the move timeline?"},
            {"role": "user", "content": "closing oct 15 so we have a couple months. riley is already decluttering. i have way too many monitors and cables. dev said 'just throw everything in a box labeled misc — you'll never open it but you'll feel better'"},
            {"role": "assistant", "content": "How's Lily settling into Austin?"},
            {"role": "user", "content": "great. she got a KIVIK couch in dark gray and a bookshelf from marketplace for $40. her apartment is near campus. she's on campaign analytics at indeed now — marketing manager title"},
            {"role": "assistant", "content": "Has she made friends outside of your circle?"},
            {"role": "user", "content": "introduced her to riley's friend jessica who also works at indeed. they hit it off immediately. lily turns 25 in february — already told me she wants uchi omakase for her birthday. she's learning my expensive taste"},
            {"role": "assistant", "content": "When does the current apartment lease end?"},
            {"role": "user", "content": "lease at 1847 E Riverside Dr ends october 31. perfect timing for the house closing on october 15. two weeks overlap to move gradually instead of one frantic weekend. riley already has a color-coded moving spreadsheet. she's terrifyingly organized"},
        ],
        "facts_introduced": [
            "Old apartment: 1847 E Riverside Dr Apt 4A, $2,100->$2,350",
            "Lily's KIVIK couch, campaign analytics at Indeed",
            "Lily turns 25 in February",
            "Jessica: Riley's friend at Indeed, connected with Lily"
        ],
        "facts_updated": []
    })

    return sessions


def build_v3_sessions():
    """Build ~15 new sessions targeting v3-specific memory categories."""
    sessions = []
    base_id = 36

    # V3-1: Belief evolution — anti-VC
    sessions.append({
        "session_id": base_id,
        "timestamp": "2024-09-15T20:00:00",
        "turns": [
            {"role": "user", "content": "i don't think we'll ever take VC money. read too many horror stories about founders losing control. board seats, liquidation preferences, growth-at-all-costs mentality"},
            {"role": "assistant", "content": "Those are legitimate concerns. What specifically worries you?"},
            {"role": "user", "content": "a friend from dataflux joined a VC-backed startup. they had to pivot from their mission to chase ARR metrics the board wanted. CEO got replaced after 18 months. i'd rather grow slower and keep control"},
            {"role": "assistant", "content": "Bootstrapping is harder but you keep full ownership. Are there circumstances that would change your mind?"},
            {"role": "user", "content": "maybe if we found someone who truly understood climate tech and didn't push growth-at-all-costs. but that's rare. sam says all VCs are the same. dev agrees — bootstrapping for now. we have 3 pilot customers paying us, that's real revenue"},
            {"role": "assistant", "content": "Revenue-funded growth is the cleanest model."},
            {"role": "user", "content": "exactly. if we can get to $50k MRR without VC we'll have all the leverage. my nightmare is some partner in a patagonia vest telling me to 'move fast and break things' with carbon data that companies depend on for EPA compliance"},
            {"role": "assistant", "content": "Fair enough. How's the bootstrapping math look?"},
            {"role": "user", "content": "3 pilot customers at $2k/facility = roughly $6k MRR once they all sign. with our $4.2k burn rate we'd be cash-flow positive almost immediately. dev says we don't need a dime of outside money to prove the product. i agree with him"},
            {"role": "assistant", "content": "That's a strong position to be in."},
            {"role": "user", "content": "and if we DO eventually raise, we raise from a position of strength, not desperation. sam said 'never raise money when you need it, raise when you don't.' pretty good advice from a banker"},
        ],
        "facts_introduced": ["Jordan initially anti-VC, wants to bootstrap", "Sam says all VCs are the same", "Goal: $50K MRR without VC for leverage"],
        "facts_updated": []
    })

    # V3-2: Belief evolution — softening on VCs
    sessions.append({
        "session_id": base_id + 1,
        "timestamp": "2024-11-25T19:00:00",
        "turns": [
            {"role": "user", "content": "remember when i said i'd never take VC money? i think i was wrong. or at least... not entirely right"},
            {"role": "assistant", "content": "What changed? A few weeks ago you were firmly anti-VC."},
            {"role": "user", "content": "nina vasquez from elevation is different. when we met at epoch coffee she asked about accuracy methodology and the science behind our scope 2 approach. not growth hacking. not 'how fast can you 10x'"},
            {"role": "assistant", "content": "One good investor doesn't mean VCs are good generally."},
            {"role": "user", "content": "true. but she said something that stuck: 'i invest in companies that make money by making the world better.' dev came around too after seeing elevation's portfolio. their companies have 90% founder retention after 5 years. that's unheard of"},
            {"role": "assistant", "content": "What does Sam think?"},
            {"role": "user", "content": "sam still thinks all VCs are sharks. but sam also hasn't met nina. i told him 'you'll change your mind when you meet her.' she actually understands carbon accounting regulations. most investors hear 'carbon' and think 'ESG marketing'"},
            {"role": "assistant", "content": "Are you going to apply to their accelerator then?"},
            {"role": "user", "content": "dev and i talked until 2am. we're applying. deadline january 15. worst case we keep bootstrapping. best case we get nina as a mentor and $1.5M in the bank. the EPA scope 3 mandate makes our pitch even stronger now"},
        ],
        "facts_introduced": ["Jordan changed mind about VCs after meeting Nina", "Elevation has 90% founder retention", "Sam still skeptical of VCs", "Decided to apply to Elevation"],
        "facts_updated": ["Jordan's VC stance: anti-VC -> open to right investor"]
    })

    # V3-3: Belief evolution — fully pro-VC (selectively)
    sessions.append({
        "session_id": base_id + 2,
        "timestamp": "2025-09-01T11:00:00",
        "turns": [
            {"role": "user", "content": "funny — remember when i said i'd rather bootstrap forever? i literally said 'my nightmare is some partner in a patagonia vest telling me to move fast.' just closed $10M series A from khosla at $55M pre lol"},
            {"role": "assistant", "content": "Quite the evolution from 'all VCs are the same.' How do you feel now?"},
            {"role": "user", "content": "i was wrong about ALL VCs being bad. right about bad VCs being bad. nina and vinod have been incredible — opened doors we never could alone. vinod personally introduced us to 3 fortune 500 companies"},
            {"role": "assistant", "content": "What would you tell past-you?"},
            {"role": "user", "content": "be picky. do backchannel references. only take money from someone who's built something themselves. vinod built sun microsystems. nina ran a factory before going into VC. they GET it. even sam came around after meeting vinod"},
            {"role": "assistant", "content": "Sam changed his mind too?"},
            {"role": "user", "content": "yeah sam said 'ok i was wrong about VCs. i was right about BAD VCs.' which is basically what i just said. he's actually asking nina for advice on his own fintech idea now. full circle"},
            {"role": "assistant", "content": "Any regrets about the dilution?"},
            {"role": "user", "content": "went from 42.5% to 33.1%. but 33% of a $65M company is better than 100% of a $2M company. nina told me early: 'would you rather have a big slice of a small pie or a smaller slice of an enormous pie?' the math is obvious"},
        ],
        "facts_introduced": ["Vinod introduced 3 Fortune 500 companies", "Sam came around on VCs too", "Nina pie analogy on dilution"],
        "facts_updated": ["Jordan now selectively pro-VC", "Sam's VC stance also evolved"]
    })

    # V3-4: Cross-session continuity — post-quitting update
    sessions.append({
        "session_id": base_id + 3,
        "timestamp": "2024-09-01T10:00:00",
        "turns": [
            {"role": "user", "content": "been about a month since i left dataflux. wanted to give you an update on how everything is going"},
            {"role": "assistant", "content": "I remember you submitted your notice July 16th and your last day was July 29th. How's the transition been?"},
            {"role": "user", "content": "harder than expected. first week was pure freedom — slept in, worked on my own terms, no more stand-ups with david morrison. then the anxiety hit"},
            {"role": "assistant", "content": "What kind of anxiety?"},
            {"role": "user", "content": "checking savings every morning. $45K felt like a lot with a salary coming in, now it feels like nothing. i wake up at 4am doing mental math on burn rate. dev says i need to chill"},
            {"role": "assistant", "content": "How's the Meridian pilot going though? That's your proof point."},
            {"role": "user", "content": "that's the good news. deployed and running. scope 1 at 94.8% and climbing — dev optimized the data ingestion pipeline. maria gonzalez at meridian sent an email saying 'this is already better than our manual process'"},
            {"role": "assistant", "content": "How's Riley adjusting?"},
            {"role": "user", "content": "riley started her masters program yesterday — nervous but excited. first day orientation, already likes her cohort. her first practicum client is in october. she's going to be an amazing therapist. she's already basically mine lol"},
            {"role": "assistant", "content": "Both of you starting new chapters at the same time."},
            {"role": "user", "content": "exactly. we're both terrified and excited. she said 'we're doing the scary thing together.' biscuit doesn't care — he just wants his morning walk and dinner at 5:30. dogs keep you grounded"},
        ],
        "facts_introduced": ["Meridian pilot deployed, scope 1 at 94.8%", "Riley started masters", "Maria Gonzalez positive feedback on pilot", "Riley's first practicum client in October"],
        "facts_updated": ["Scope 1: 94.2% -> 94.8%"]
    })

    # V3-5: Cross-session continuity — half marathon callback
    sessions.append({
        "session_id": base_id + 4,
        "timestamp": "2025-04-10T14:00:00",
        "turns": [
            {"role": "user", "content": "austin half marathon was sunday april 6! my time was 1:52:34. i'm so happy"},
            {"role": "assistant", "content": "That's great! Last time we talked about fitness you were doing 3 days lifting, 3 running, 1 rest plus yoga Sundays with Jake. Did you keep that split?"},
            {"role": "user", "content": "mostly. had to cut back lifting during peak training weeks — went to 2 days lifting, 4 running. yoga helped with recovery so much. jake was right about that"},
            {"role": "assistant", "content": "What shoes did you end up running in?"},
            {"role": "user", "content": "hoka clifton 9s from REI, $140. game changer. my knees thank me. also got a garmin forerunner for training — the heart rate zones made a huge difference in pacing"},
            {"role": "assistant", "content": "Who else ran?"},
            {"role": "user", "content": "sam ran it too — beat me by 2 minutes, the bastard. jake finished 5 minutes behind me. classic sam, barely trained and still faster. he went out too fast, bonked at mile 10, then somehow found another gear"},
            {"role": "assistant", "content": "Supporters at the finish?"},
            {"role": "user", "content": "maya was at the finish line with handmade signs. riley had biscuit in a 'go dad' bandana which was embarrassing and perfect. dev stayed home and tracked us on the garmin app — sent a text at mile 8 saying 'your pace dropped, push it.' very dev"},
        ],
        "facts_introduced": ["Half marathon April 6: 1:52:34", "Sam ran (2min faster), Jake (5min slower)", "Hoka Clifton 9s from REI $140", "Maya at finish line, Biscuit in 'go dad' bandana"],
        "facts_updated": []
    })

    # V3-6: Temporal markers — first therapy session
    sessions.append({
        "session_id": base_id + 5,
        "timestamp": "2025-07-22T20:00:00",
        "turns": [
            {"role": "user", "content": "had my first therapy session today with dr linda choi. intense. CBT approach. we talked for 50 minutes about my work patterns"},
            {"role": "assistant", "content": "What prompted you to finally start? You've been resistant to the idea."},
            {"role": "user", "content": "three weeks ago i missed our anniversary dinner for a sequoia call. last week chest tightness got worse and my RHR jumped to 72 from 64. six months ago i would have laughed at therapy. now i actually need it"},
            {"role": "assistant", "content": "What did Dr. Choi focus on in the first session?"},
            {"role": "user", "content": "childhood. immigrant parents, high expectations, tying self-worth to achievement. she asked 'when was the first time you felt like your worth depended on your output?' and i was like... kindergarten report cards"},
            {"role": "assistant", "content": "That's deep for a first session."},
            {"role": "user", "content": "she's good. riley recommended her via dr martinez from UT. the 'burnout' book riley gave me last september makes so much more sense now. dr choi said burnout isn't just being tired — it's the gap between effort and meaning"},
            {"role": "assistant", "content": "That's a powerful definition."},
            {"role": "user", "content": "my effort was going to the company, not to the people i love. i told her about the anniversary and she didn't judge — she said 'the fact that you're here means you want to change.' that was the first time i felt hope in weeks"},
            {"role": "assistant", "content": "When's your next session?"},
            {"role": "user", "content": "two weeks. biweekly schedule. she gave me homework — track when i feel the urge to check slack after 7pm and write down what i'm avoiding by doing it. spoiler: it's usually sitting with uncomfortable feelings about whether i'm doing enough"},
            {"role": "assistant", "content": "That's a powerful exercise. How does Riley feel about you starting?"},
            {"role": "user", "content": "relieved. she said 'i've been asking you to do this for three months.' she's right. the anniversary miss was the final straw but the signs were there all along. she said she could see me disappearing into the company piece by piece. i owe it to her to get better"},
        ],
        "facts_introduced": ["First therapy session July 22", "CBT with Dr. Choi", "Connected patterns to immigrant parent upbringing", "Biweekly sessions", "Homework: track urge to check Slack after 7pm", "Riley had been asking for therapy for 3 months"],
        "facts_updated": []
    })

    # V3-7: Fact update — database narrated real-time
    sessions.append({
        "session_id": base_id + 6,
        "timestamp": "2025-05-20T22:00:00",
        "turns": [
            {"role": "user", "content": "we need to talk about our database situation. postgres query times are at 2.3 seconds for our main emissions dashboard query. customers are noticing"},
            {"role": "assistant", "content": "2.3 seconds is rough for a dashboard. What have you tried?"},
            {"role": "user", "content": "tried timescaledb first since it's postgres-compatible. better but not fast enough — still 800ms. dev tested clickhouse over the weekend"},
            {"role": "assistant", "content": "ClickHouse is purpose-built for time series analytics. How did it perform?"},
            {"role": "user", "content": "47 milliseconds. same exact queries. i literally made dev run it three times because i didn't believe it. going with clickhouse for sensor data and emissions time series, keeping postgres for users, auth, billing"},
            {"role": "assistant", "content": "Dual database is more operational complexity but the performance gap justifies it."},
            {"role": "user", "content": "exactly. also adding redis for caching the dashboard's most frequently accessed queries. page load went from 1.2 seconds to 200ms with redis in front. dev's doing a 2-week dual-write migration — no downtime cutover"},
            {"role": "assistant", "content": "Customers will notice the speed improvement immediately."},
            {"role": "user", "content": "maria at meridian already asked 'did you guys upgrade something? the dashboard is flying.' that's the best kind of feedback — they noticed without being told. aisha wants to use clickhouse for the ML pipeline too but one thing at a time"},
        ],
        "facts_introduced": ["ClickHouse: 47ms vs 2.3s", "TimescaleDB tested: 800ms", "Redis for caching: 1.2s to 200ms", "2-week dual-write migration plan", "Maria noticed speed improvement"],
        "facts_updated": ["Time series DB: PostgreSQL -> ClickHouse"]
    })

    # V3-8: Belief evolution — work-life balance
    sessions.append({
        "session_id": base_id + 7,
        "timestamp": "2025-10-15T21:00:00",
        "turns": [
            {"role": "user", "content": "six months ago i thought 16 hour days were necessary. 'real founder' stuff. if you're not grinding you're not serious. now i know that's ego and bad time management"},
            {"role": "assistant", "content": "That's a big shift. What specifically changed your perspective?"},
            {"role": "user", "content": "almost losing riley. chest tightness that turned out to be psychosomatic. three months of therapy. dr choi helped me see that my productivity INCREASED after the 7pm boundary. 10 focused hours beats 16 scattered ones"},
            {"role": "assistant", "content": "The data backs that up for knowledge work generally."},
            {"role": "user", "content": "and the team has more ownership now. dev, aisha, rachel — they don't need me hovering. i was a bottleneck disguised as a hard worker. aisha actually ships faster when i'm not in every code review"},
            {"role": "assistant", "content": "Delegation as a byproduct of boundaries. That's powerful."},
            {"role": "user", "content": "dr choi called it 'productive constraint.' limiting hours forced prioritization. also sleeping 7 hours instead of 5.8 makes me literally smarter — i make better decisions, catch bugs faster, write clearer emails"},
            {"role": "assistant", "content": "How does this connect to the company values?"},
            {"role": "user", "content": "we added 'sustainable pace' to our team principles. no one should be doing what i did. rachel pushed back on a customer request to work over thanksgiving and i backed her 100%. six months ago i would have said 'whatever the customer needs.' growth at any cost was my religion. not anymore"},
        ],
        "facts_introduced": ["Dr. Choi term: 'productive constraint'", "7pm boundary increased productivity", "Added 'sustainable pace' to team principles", "Jordan was a bottleneck disguised as hard worker"],
        "facts_updated": ["Jordan: hustle culture -> boundaries + delegation"]
    })

    # V3-9: Cross-session — pricing evolution
    sessions.append({
        "session_id": base_id + 8,
        "timestamp": "2025-06-01T10:00:00",
        "turns": [
            {"role": "user", "content": "remember our pricing conversation? started at $2k base, $5k enterprise. nina was right to push us higher. changed to $5k/$12k in march. barely slowed sales at all"},
            {"role": "assistant", "content": "What's the customer's alternative cost?"},
            {"role": "user", "content": "hiring consultants at $60/hr for about 40 hours/month. that's $28,800/year versus our $60K for base or $144K for enterprise. but we're real-time, automated, and more accurate. no comparison really"},
            {"role": "assistant", "content": "What about Meridian at the old pricing?"},
            {"role": "user", "content": "grandfathered at $2k per facility for year 1 as a loyalty thing. they were our first believer. new customers all at $5k+. lone star and gulf coast both signed at $5k"},
            {"role": "assistant", "content": "Nina mentioned going even higher. What's stopping you?"},
            {"role": "user", "content": "i don't want to price out smaller manufacturers. the whole point of CarbonSense is making carbon tracking accessible. nina says 'you can always add a tier' which is probably the right answer. maybe $5k small, $12k mid, $20k enterprise"},
            {"role": "assistant", "content": "Three tiers would let you serve both markets."},
            {"role": "user", "content": "exactly. rachel loves it too — she said 'give me three price points and i'll close anyone.' she's scary effective. also the pricing conversation reminded me of something nina said early on: 'the biggest mistake startups make is undercharging, not overcharging.' i was making that exact mistake at $2k"},
        ],
        "facts_introduced": ["Alternative cost: $60/hr consultants, ~$28,800/year", "Potential third tier at $20K discussed", "Nina quote on startup undercharging"],
        "facts_updated": ["Considering 3-tier pricing: $5K/$12K/$20K"]
    })

    # V3-10: Temporal — birthday with time references
    sessions.append({
        "session_id": base_id + 9,
        "timestamp": "2025-09-14T19:00:00",
        "turns": [
            {"role": "user", "content": "turned 29 today. last year sam got me COTA paddock passes for 28. this year riley did a small dinner at home — lily, sam, jake, maya. red velvet cake again, it's tradition now"},
            {"role": "assistant", "content": "Red velvet two years running. How are you feeling compared to last year?"},
            {"role": "user", "content": "night and day. three months ago was my absolute lowest — missing our anniversary, chest tightness, barely sleeping 5.8 hours. therapy with dr choi turned everything around"},
            {"role": "assistant", "content": "The health recovery has been remarkable."},
            {"role": "user", "content": "RHR 66 now, down from 72 at the worst. sleeping 7 hours. a year ago i couldn't have imagined any of this: $65M company, closing on a house next month, planning to propose. 28 was the year everything changed"},
            {"role": "assistant", "content": "What's your wish for 29?"},
            {"role": "user", "content": "balance. i want to be as good a partner and brother and friend as i am a CEO. dr choi says that's the real measure of success. not ARR, not valuation — whether the people closest to you feel loved. working on it"},
            {"role": "assistant", "content": "That's a mature perspective for 29."},
            {"role": "user", "content": "almost losing the people i love will do that. jake got me a 'world's okayest CEO' mug. sam wrote a card that said 'happy birthday to the guy who makes me believe anything is possible.' riley just held my hand. best birthday yet"},
        ],
        "facts_introduced": ["Jordan turned 29, Sept 14 2025", "Birthday: Riley, Lily, Sam, Jake, Maya, red velvet cake", "Dr. Choi on real success: people feeling loved", "Jake: 'world's okayest CEO' mug"],
        "facts_updated": ["Age: 28 -> 29"]
    })

    # V3-11: Fact update — gym location
    sessions.append({
        "session_id": base_id + 10,
        "timestamp": "2025-10-20T07:00:00",
        "turns": [
            {"role": "user", "content": "switched gyms. left gold's on south lamar for lifetime fitness on burnet road. closer to the new house on chicon st and they have better running facilities for marathon training"},
            {"role": "assistant", "content": "Is Jake switching too?"},
            {"role": "user", "content": "no, he's staying at gold's. lives in south austin still so it makes sense for him. we'll do weekend sessions together — saturday mornings probably"},
            {"role": "assistant", "content": "What about the workout schedule? You were doing evenings for a while."},
            {"role": "user", "content": "back to mornings. the 7pm boundary means i actually sleep 7 hours and can wake at 6am again. evenings didn't work — i was too mentally drained after 10 hours of work. and jake couldn't do evenings anyway because of little league coaching at 6:30"},
            {"role": "assistant", "content": "So the gym change and the therapy changes are reinforcing each other."},
            {"role": "user", "content": "exactly. dr choi calls it a 'positive feedback loop.' better sleep -> better mornings -> better workouts -> better mood -> better boundaries -> better sleep. i feel like myself again. also lifetime has a pool which is great for recovery on rest days"},
            {"role": "assistant", "content": "What about the cost difference?"},
            {"role": "user", "content": "lifetime is $75/month versus gold's $35. but the facilities are worth it — pool, sauna, better free weights section. jake says i'm 'going bougie' but he also admits their squat racks are nicer. i told him he's welcome anytime as my guest"},
        ],
        "facts_introduced": ["Gym: Gold's South Lamar -> Lifetime on Burnet", "Lifetime has a pool for recovery", "Lifetime $75/mo vs Gold's $35/mo"],
        "facts_updated": ["Gym changed", "Workout time: mornings -> evenings (June) -> mornings (Oct)"]
    })

    # V3-12: Cross-session — health trajectory
    sessions.append({
        "session_id": base_id + 11,
        "timestamp": "2025-12-20T19:00:00",
        "turns": [
            {"role": "user", "content": "wanted to do a year-end health check. current: RHR 66, sleep 7.0 hours, 7200 steps daily, VO2 max 44, weight 175 lbs"},
            {"role": "assistant", "content": "Let me compare to your earlier data. October 2024 baseline: RHR 64, 7.2hr sleep, 8500 steps. July 2025 crisis point: RHR 72, 5.8hr sleep, 4200 steps. You're recovered, though not quite at your peak October 2024 numbers."},
            {"role": "user", "content": "the trajectory tells the story: healthy baseline -> increasing stress -> crisis in june/july -> therapy and boundaries -> recovery. dr choi called it a 'textbook founder burnout arc'"},
            {"role": "assistant", "content": "The chest tightness is completely gone?"},
            {"role": "user", "content": "gone. dr choi said it was psychosomatic — anxiety manifesting physically. once we addressed the root causes in therapy it disappeared within a month. my actual heart is fine, got an EKG to confirm"},
            {"role": "assistant", "content": "What's the full wellness routine now?"},
            {"role": "user", "content": "therapy biweekly with dr choi, 7pm hard stop every day, morning gym at lifetime on burnet, insight timer meditation, yoga sundays. creatine 5g/day still. training for the february marathon — up to 40 mile weeks. feel better than i have in two years honestly"},
            {"role": "assistant", "content": "Your wellness stack is impressive now."},
            {"role": "user", "content": "it took almost losing everything to build it. riley said 'you went from being your own worst enemy to being your own best friend.' she's going to be such a good therapist. sam noticed too — he said 'you look 5 years younger than july.' i'll take it"},
        ],
        "facts_introduced": ["Dec health: RHR 66, 7hr, 7200 steps, VO2 44, 175lbs", "Chest tightness was psychosomatic", "Got EKG to confirm heart is fine", "Dr. Choi: 'textbook founder burnout arc'", "40 mile weeks for marathon training"],
        "facts_updated": []
    })

    # V3-13: Belief evolution — competition strategy
    sessions.append({
        "session_id": base_id + 12,
        "timestamp": "2025-10-02T18:00:00",
        "turns": [
            {"role": "user", "content": "lost another deal to ecotrace on price. they undercut us by 40% again. tempted to lower our prices"},
            {"role": "assistant", "content": "Last time this came up you were firm about not competing on price. Nina said compete on accuracy and scope 3."},
            {"role": "user", "content": "you're right. i needed that reminder. our win rate is 80% when technical teams do the evaluation. we only lose when procurement departments just look at line items without understanding the accuracy implications"},
            {"role": "assistant", "content": "That's what the TCO calculator is designed to fix right?"},
            {"role": "user", "content": "exactly. rachel and omar are almost done with it. shows that 7% accuracy difference in scope 1 means millions in carbon credit miscalculations over 3 years. at 10 facilities that's roughly $2M in bad data. our $60K annual fee pays for itself 30 times over"},
            {"role": "assistant", "content": "Data quality as the value prop, not just monitoring."},
            {"role": "user", "content": "yes. and ecotrace has zero scope 3. the EPA mandate makes scope 3 required by 2027. companies buying ecotrace today will need to buy something else for scope 3 tomorrow. rachel calls that 'buying a car with no engine.' staying premium. nina was right all along"},
        ],
        "facts_introduced": ["80% win rate on technical evaluation", "7% accuracy gap = $2M over 3 years at 10 facilities", "CarbonSense annual fee pays for itself 30x"],
        "facts_updated": ["Reaffirmed premium pricing"]
    })

    # V3-14: Sam's evolution
    sessions.append({
        "session_id": base_id + 13,
        "timestamp": "2026-01-10T20:00:00",
        "turns": [
            {"role": "user", "content": "sam is writing a real business plan for his fintech idea. carbon credit marketplace for corporate banking. remember when he was just reading 'venture deals' and giving me SAFE term sheet advice?"},
            {"role": "assistant", "content": "That was around August 2024. He's gone from reading about startups to moonlighting sales for CarbonSense to starting his own company."},
            {"role": "user", "content": "exactly. he handled the lone star cement negotiation beautifully, then stepped back gracefully when rachel joined as VP sales. showed real maturity. now he's applying everything he learned watching us"},
            {"role": "assistant", "content": "What does Nina think of his idea?"},
            {"role": "user", "content": "she thinks the carbon credit marketplace is interesting but not right for carbonsense — dev was right about scope creep. as a separate company though, our monitoring feeds data into his marketplace. powerful combo. she might intro him to a fintech-focused fund"},
            {"role": "assistant", "content": "How's Maya about all this?"},
            {"role": "user", "content": "super supportive. she's a nurse at dell seton so she has stable income which helps. sam said 'now i understand why you were checking your savings at 4am.' he gets it. we're going through the same journey 18 months apart"},
            {"role": "assistant", "content": "What advice did you give him?"},
            {"role": "user", "content": "find your nina first. investor quality matters more than check size. also he asked me to be his first advisor which meant a lot. said 'you're the only founder i trust.' full circle from the guy who used to just read me business book summaries"},
        ],
        "facts_introduced": ["Sam writing fintech business plan", "Potential CarbonSense + Sam's marketplace synergy", "Nina may intro Sam to fintech fund", "Sam and Jordan 18 months apart on same journey", "Sam asked Jordan to be first advisor"],
        "facts_updated": []
    })

    # V3-15: Temporal — explicit time references
    sessions.append({
        "session_id": base_id + 14,
        "timestamp": "2025-11-20T20:00:00",
        "turns": [
            {"role": "user", "content": "climate tech summit was last week. biggest talk i've ever given. 500 people. three months ago at series A signing i never imagined we'd be on that stage"},
            {"role": "assistant", "content": "Series A was August. Three months of incredible acceleration."},
            {"role": "user", "content": "it's wild when i think about the timeline. six months ago: demo day, cried in the bathroom. a year ago: meeting nina at epoch coffee for the first time. two years ago: still at dataflux daydreaming about carbon tracking with dev"},
            {"role": "assistant", "content": "And looking forward?"},
            {"role": "user", "content": "next week: housewarming party. february: parents visit, lily's 25th birthday at uchi, full marathon. may: riley's graduation at frank erwin center, then... you know. lady bird lake. sunset. the ring is almost paid off"},
            {"role": "assistant", "content": "That's a beautiful arc from two years ago to what's ahead."},
            {"role": "user", "content": "dr choi asked me to write a letter to my past self. the one who was terrified at dataflux. i wrote 'the terror doesn't go away, you just get better at recognizing it as excitement.' sam's line originally but it became my truth"},
            {"role": "assistant", "content": "Sam has a way with words."},
            {"role": "user", "content": "he does. he texted me this morning: 'two years ago we were eating dollar tacos at torchys debating whether you should quit. now you're speaking at 500-person conferences. i'm proud of you bro.' i may have gotten something in my eye reading that"},
        ],
        "facts_introduced": ["Explicit temporal references spanning 2 years", "Dr. Choi exercise: letter to past self", "Sam's line became Jordan's motto", "Sam's proud text message"],
        "facts_updated": []
    })

    return sessions


def main():
    v2_sessions = build_v2_sessions()
    v3_sessions = build_v3_sessions()

    all_sessions = v2_sessions + v3_sessions
    all_sessions.sort(key=lambda s: s["timestamp"])

    for i, session in enumerate(all_sessions, 1):
        session["session_id"] = i

    total_turns = sum(len(s["turns"]) for s in all_sessions)
    total_facts = sum(len(s.get("facts_introduced", [])) for s in all_sessions)
    total_updates = sum(len(s.get("facts_updated", [])) for s in all_sessions)

    print(f"Total sessions: {len(all_sessions)}")
    print(f"Total turns: {total_turns}")
    print(f"Time range: {all_sessions[0]['timestamp']} to {all_sessions[-1]['timestamp']}")
    print(f"V2-derived sessions: {len(v2_sessions)}")
    print(f"V3-specific sessions: {len(v3_sessions)}")
    print(f"Total facts introduced: {total_facts}")
    print(f"Total facts updated: {total_updates}")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(all_sessions, f, indent=2, ensure_ascii=False)

    print(f"\nWritten to: {OUT_PATH}")


if __name__ == "__main__":
    main()
