"""
Expansion batch 2 — push from ~474 to 1500+ messages.
More daily life, work noise, cross-references, and subtle details.
"""

import json
from datetime import datetime, timedelta

with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
    messages = json.load(f)

print(f"Starting with {len(messages)} messages")

new = []

def msg(ts, sender, recipient, content, cat="text_message", mod="imessage"):
    new.append({"content": content, "sender": sender, "recipient": recipient,
                 "timestamp": ts, "category": cat, "modality": mod})

def email(ts, sender, recipient, content):
    new.append({"content": content, "sender": sender, "recipient": recipient,
                 "timestamp": ts, "category": "work_email", "modality": "email"})

def ocr(ts, content, mod="ocr_receipt"):
    new.append({"content": content, "sender": "ocr_system", "recipient": "jordan",
                 "timestamp": ts, "category": "ocr", "modality": mod})

def note(ts, content):
    new.append({"content": content, "sender": "jordan", "recipient": "self",
                 "timestamp": ts, "category": "note", "modality": "note"})

def cal(ts, content):
    new.append({"content": content, "sender": "calendar", "recipient": "jordan",
                 "timestamp": ts, "category": "calendar", "modality": "calendar"})

# ============================================================
# More Jordan & Riley daily life (~80 msgs)
# ============================================================

# Morning routines
msg("2024-07-25T07:00:00", "jordan", "riley", "leaving for the 'office' (aka dev's apartment). biscuit had breakfast. love you")
msg("2024-07-25T07:05:00", "riley", "jordan", "love you too. don't forget we have dinner with jessica and matt tonight at 7")
msg("2024-07-25T07:06:00", "jordan", "riley", "right right. where again?")
msg("2024-07-25T07:08:00", "riley", "jordan", "dai due on manor rd. the charcuterie place")
msg("2024-08-18T08:00:00", "jordan", "riley", "biscuit won't eat his breakfast. just staring at the bowl")
msg("2024-08-18T08:05:00", "riley", "jordan", "try adding a little warm water to the kibble. he does that when it's hot out")
msg("2024-08-18T08:15:00", "jordan", "riley", "worked! he inhaled it. you're the dog whisperer")

# Cooking together
msg("2024-09-22T17:00:00", "riley", "jordan", "i'm making your mom's mapo tofu recipe tonight. can you grab silken tofu from MT Supermarket?")
msg("2024-09-22T17:05:00", "jordan", "riley", "on it. need doubanjiang too?")
msg("2024-09-22T17:06:00", "riley", "jordan", "yes and sichuan peppercorns. the ones in the red bag")
msg("2024-11-20T18:00:00", "jordan", "riley", "riley your lemon garlic salmon was so good last week. can you teach me how to make it?")
msg("2024-11-20T18:05:00", "riley", "jordan", "it's literally the easiest thing. salmon, garlic, lemon, butter, 400 degrees for 12 minutes. i'll show you tonight")

# Netflix/entertainment
msg("2024-10-05T21:00:00", "jordan", "riley", "what should we watch? i'm tired of scrolling")
msg("2024-10-05T21:02:00", "riley", "jordan", "that new show 'nobody wants this' looks funny. or we could finally start shogun")
msg("2024-10-05T21:05:00", "jordan", "riley", "shogun. i've heard it's incredible. get the popcorn, i'll set up")
msg("2024-10-15T22:00:00", "jordan", "riley", "ok shogun is a masterpiece. that battle scene. i'm shook")
msg("2024-10-15T22:02:00", "riley", "jordan", "right?? and the love story is so subtle. japanese period dramas are underrated")
msg("2025-02-25T21:00:00", "jordan", "riley", "severance season 3 is out. dev mentioned it today. starting tonight?")
msg("2025-02-25T21:05:00", "riley", "jordan", "YES. i've been waiting months. biscuit is already on the couch ready")

# Weather/seasons in Austin
msg("2024-07-15T14:00:00", "jordan", "riley", "it's 106 degrees. i'm working from home. AC at dev's apartment can't keep up")
msg("2024-07-15T14:05:00", "riley", "jordan", "good call. i made iced tea. also biscuit is laying on the tile floor like a pancake")
msg("2024-12-10T07:00:00", "jordan", "riley", "first freeze warning! cover the plants tonight?")
msg("2024-12-10T07:05:00", "riley", "jordan", "already brought the succulents inside. biscuit is wearing his sweater")
msg("2025-03-20T16:00:00", "jordan", "riley", "bluebonnets are blooming on 360! drive this weekend?")
msg("2025-03-20T16:05:00", "riley", "jordan", "absolutely. and bring biscuit for photos. last year's bluebonnet pics of him were perfect")

# Apartment/house life
msg("2025-01-15T09:00:00", "riley", "jordan", "the upstairs neighbors are stomping again. 2am last night. i couldn't sleep")
msg("2025-01-15T09:05:00", "jordan", "riley", "we should talk to the landlord. or start looking at houses... just saying")
msg("2025-01-15T09:10:00", "riley", "jordan", "houses in austin are so expensive though. can we even afford it?")
msg("2025-01-15T09:15:00", "jordan", "riley", "not right now. maybe after the raise closes. let's revisit in summer")

# Riley's grad school
msg("2025-02-05T19:00:00", "riley", "jordan", "had my first real therapy client today. practicum. she's 19 with severe anxiety. it was intense")
msg("2025-02-05T19:05:00", "jordan", "riley", "how did it go? are you ok?")
msg("2025-02-05T19:10:00", "riley", "jordan", "i think it went well? my supervisor said my rapport was excellent. but emotionally draining. i need to learn better boundaries")
msg("2025-02-05T19:15:00", "jordan", "riley", "ironically that's what my therapist tells me too 😂 we're a pair")
msg("2025-05-10T20:00:00", "riley", "jordan", "got my practicum evaluation. all exceeds expectations! my supervisor wants me for the advanced rotation next year")
msg("2025-05-10T20:05:00", "jordan", "riley", "that's amazing babe. you're going to be an incredible therapist. i'm so proud of you")
msg("2025-09-01T18:00:00", "riley", "jordan", "guess what! got accepted to the adolescent specialization track. only 8 spots and i got one")
msg("2025-09-01T18:05:00", "jordan", "riley", "RILEY!! you've wanted this since undergrad! when does it start?")
msg("2025-09-01T18:10:00", "riley", "jordan", "january. it's a year-long program at dell children's hospital. i'll be doing group therapy with teens")

# Gift/holiday stuff
msg("2025-12-20T18:00:00", "jordan", "riley", "what are you getting lily for christmas?")
msg("2025-12-20T18:05:00", "riley", "jordan", "that fancy candle set from jo malone she keeps hinting at. $85. you?")
msg("2025-12-20T18:10:00", "jordan", "riley", "i got mom and dad matching austin 'keep it weird' mugs. and dad a fancy coffee subscription from third coast coffee")
msg("2025-12-20T18:15:00", "riley", "jordan", "cute. also sam texted me about new year's eve. he's hosting at his place. should we go?")
msg("2025-12-20T18:20:00", "jordan", "riley", "definitely. last year we fell asleep at 10pm watching the ball drop with biscuit. we can do better lol")

# ============================================================
# More Dev technical conversations (~60 msgs)
# ============================================================

msg("2024-07-30T09:00:00", "jordan", "dev", "first official day! i set up the carbonsense.io domain and google workspace. your email is dev@carbonsense.io")
msg("2024-07-30T09:05:00", "dev", "jordan", "nice. i set up the github org, terraform for AWS, and a basic CI/CD pipeline with github actions")
msg("2024-07-30T09:10:00", "jordan", "dev", "already? you're a machine. what framework for the frontend?")
msg("2024-07-30T09:15:00", "dev", "jordan", "react 18 with typescript and vite. tailwind for styling. nothing fancy, just get it working")
msg("2024-08-10T23:00:00", "dev", "jordan", "jordan the pilot deployment for meridian is ready. hosted on ECS with an RDS postgres instance. monitoring via cloudwatch")
msg("2024-08-10T23:05:00", "jordan", "dev", "let me review the security setup before we deploy. we're handling industrial data")
msg("2024-08-10T23:10:00", "dev", "jordan", "already set up: VPC with private subnets, encryption at rest (AES-256), TLS 1.3, IAM roles with least privilege. no public endpoints except the API gateway")
msg("2024-08-25T10:00:00", "jordan", "dev", "dev we have a bug. meridian's scope 1 readings are showing negative values for their blast furnace. that's physically impossible")
msg("2024-08-25T10:05:00", "dev", "jordan", "found it. unit conversion error — we're treating their data as metric tons but they report in short tons. 10% difference")
msg("2024-08-25T10:10:00", "jordan", "dev", "classic. we need a unit normalization layer. every customer might report differently")
msg("2024-08-25T10:15:00", "dev", "jordan", "on it. i'll add a configurable unit mapping per facility in the admin panel")
msg("2024-09-15T16:00:00", "jordan", "dev", "dev our AWS bill for august was $1,247. mostly RDS and ECS. is that reasonable?")
msg("2024-09-15T16:05:00", "dev", "jordan", "bit high for one pilot. the RDS instance is overprovisioned. i'll downsize from r5.xlarge to r5.large. should save $200/month")
msg("2024-11-01T09:00:00", "dev", "jordan", "lone star cement pilot starting today. their data format is completely different from meridian. XML instead of JSON")
msg("2024-11-01T09:05:00", "jordan", "dev", "of course it is. enterprise software and XML, name a more iconic duo")
msg("2024-11-01T09:10:00", "dev", "jordan", "i'll build an XML parser. but this is going to happen with every customer. we need a universal data ingestion layer")
msg("2024-11-01T09:15:00", "jordan", "dev", "agreed. add it to the roadmap. for now just get lone star working manually")

# Security incident
msg("2025-05-10T02:00:00", "dev", "jordan", "jordan wake up. we got an alert. someone is port scanning our API endpoints. 45,000 requests in the last hour")
msg("2025-05-10T02:05:00", "jordan", "dev", "shit. is anything compromised?")
msg("2025-05-10T02:10:00", "dev", "jordan", "no. WAF blocked everything. but we should add rate limiting and maybe cloudflare. also the IPs are from a known botnet")
msg("2025-05-10T02:15:00", "jordan", "dev", "ok add cloudflare tomorrow. also we should get a penetration test done before the series A due diligence")
msg("2025-05-12T10:00:00", "dev", "jordan", "cloudflare is up. also set up fail2ban and reduced the rate limit to 100 req/min per API key. pentest scheduled for june")

# Infrastructure discussions
msg("2025-06-15T11:00:00", "dev", "jordan", "the clickhouse migration is going smoother than expected. 80% done. the hardest part is the aggregation queries — clickhouse uses different SQL dialect")
msg("2025-06-15T11:05:00", "jordan", "dev", "any risk to customer dashboards during migration?")
msg("2025-06-15T11:10:00", "dev", "jordan", "no. running both in parallel. once clickhouse is validated, we flip the switch. zero downtime")
msg("2025-07-05T14:00:00", "dev", "jordan", "pentest results are in. 2 medium findings: one XSS in the reporting dashboard (fixed), one API endpoint with excessive data exposure (fixed). no highs or criticals")
msg("2025-07-05T14:05:00", "jordan", "dev", "that's great for khosla due diligence. can you write up the remediation summary?")

# Product roadmap debates
msg("2025-08-20T10:00:00", "jordan", "dev", "nina wants us to build a carbon credit marketplace. buy and sell credits through our platform. thoughts?")
msg("2025-08-20T10:05:00", "dev", "jordan", "scope creep alert. we're a monitoring platform, not a marketplace. that's a whole different business")
msg("2025-08-20T10:10:00", "jordan", "dev", "you're right. i'll push back. we should stay focused on monitoring and accuracy. that's what customers pay for")
msg("2025-08-20T10:15:00", "dev", "jordan", "exactly. ecotrace tried to be everything and their accuracy suffered. focus is our advantage")
msg("2025-11-05T09:00:00", "dev", "jordan", "jordan we need to decide on the AI model upgrade path. openai just released gpt-5. should we integrate it for the natural language reporting feature?")
msg("2025-11-05T09:05:00", "jordan", "dev", "what does aisha think? she's our ML expert")
msg("2025-11-05T09:10:00", "dev", "jordan", "she says use claude for NL reporting (better at structured output) but keep our custom models for the actual emissions prediction. mixing LLM hype with real ML is dangerous")
msg("2025-11-05T09:15:00", "jordan", "dev", "agree with aisha. our scope models are purpose-built. LLMs for the reporting layer only")

# Hiring discussions
msg("2025-09-25T14:00:00", "jordan", "dev", "dev we have 89 applicants for the 2 engineering roles. how should we filter?")
msg("2025-09-25T14:05:00", "dev", "jordan", "take-home project: build a simple data pipeline that reads CSV emissions data, validates it, and outputs a summary. 4 hour time limit")
msg("2025-09-25T14:10:00", "jordan", "dev", "good. tests for data engineering instinct not leetcode trivia. also require a README explaining their design decisions")
msg("2025-10-10T16:00:00", "dev", "jordan", "top 3 candidates: luis moreno (ex-stripe, strong go), preet kaur (ex-datadog, great with monitoring), and someone named danny okafor who's frontend but his take-home was the cleanest code i've ever seen")
msg("2025-10-10T16:05:00", "jordan", "dev", "hire all three. we have the budget and we need the help. luis and preet on backend, danny on frontend")
msg("2025-10-10T16:10:00", "dev", "jordan", "agreed. i'll make offers today. $130k base + 0.3% each. start dates in november")

# ============================================================
# More Sam conversations (friendship, life advice) (~40 msgs)
# ============================================================

msg("2024-07-25T20:00:00", "jordan", "sam", "dude first week of startup life. i'm simultaneously terrified and the happiest i've ever been")
msg("2024-07-25T20:05:00", "sam", "jordan", "that's exactly how it should feel. the terror keeps you sharp")
msg("2024-09-14T19:00:00", "sam", "jordan", "happy birthday bro! 28. old man territory. how does it feel?")
msg("2024-09-14T19:05:00", "jordan", "sam", "like 27 but with more gray hairs and less sleep. riley made an incredible cake though. red velvet")
msg("2024-09-14T19:10:00", "sam", "jordan", "she's a keeper. also your COTA tickets are booked. paddock passes. happy birthday 🎂")
msg("2024-09-14T19:15:00", "jordan", "sam", "SAM. paddock passes?! those are like $200 each!! you didn't have to do that")
msg("2024-09-14T19:20:00", "sam", "jordan", "shut up and say thank you. also jake is coming. bro day at the races")
msg("2024-11-02T19:00:00", "sam", "jordan", "how was thanksgiving in portland? did your mom interrogate riley about marriage again?")
msg("2024-11-02T19:05:00", "jordan", "sam", "obviously. 'when are you giving me grandchildren?' literally before the turkey was carved")
msg("2024-11-02T19:10:00", "sam", "jordan", "lmao. classic helen chen. how'd riley handle it?")
msg("2024-11-02T19:15:00", "jordan", "sam", "like a pro. just smiled and said 'we're enjoying the journey'. she's better at this than me")
msg("2025-04-06T14:00:00", "jordan", "sam", "just finished the half marathon!! 1:52:34. not fast but i didn't die")
msg("2025-04-06T14:05:00", "sam", "jordan", "dude!! 1:52 is solid for a first half. i could barely run a mile in high school")
msg("2025-04-06T14:10:00", "jordan", "sam", "the last 3 miles were pure suffering. but riley was at the finish line with biscuit and a sign that said 'run faster, biscuit is hungry'")
msg("2025-04-06T14:15:00", "sam", "jordan", "😂😂😂 that's amazing. you're running the full marathon next right?")
msg("2025-04-06T14:20:00", "jordan", "sam", "that's the plan. austin marathon in february 2026. 18 week training plan starts in october")
msg("2025-06-20T12:00:00", "sam", "jordan", "bro you need to take a vacation. you look exhausted every time i see you")
msg("2025-06-20T12:05:00", "jordan", "sam", "i know. riley keeps saying the same thing. maybe after the fundraise")
msg("2025-06-20T12:10:00", "sam", "jordan", "you always say 'after X'. after the launch. after the pilot. after the fundraise. there's always another X")
msg("2025-06-20T12:15:00", "jordan", "sam", "damn. that's... accurate. ok i'll plan something. japan maybe? riley has always wanted to go")
msg("2025-06-20T12:20:00", "sam", "jordan", "japan would be INCREDIBLE. i'll send you my restaurant recs. my cousin lived in tokyo for 3 years")
msg("2025-09-20T14:00:00", "sam", "jordan", "question: you said you were done moonlighting sales for carbonsense. but would you be interested in doing strategy consulting? like helping with the european expansion?")
msg("2025-09-20T14:05:00", "jordan", "sam", "wait are you saying you want to leave your job?")
msg("2025-09-20T14:10:00", "sam", "jordan", "not yet. but the startup bug bit me. i'm thinking about my own thing. maybe in the fintech space")
msg("2025-09-20T14:15:00", "jordan", "sam", "dude YES. you would be incredible as a founder. let's talk about it over beers. i have so much advice (mostly what NOT to do)")

# ============================================================
# More Jake gym conversations (~25 msgs)
# ============================================================

msg("2024-07-28T06:30:00", "jake", "jordan", "bro your deadlift form was off yesterday. you're rounding your lower back. gonna hurt yourself")
msg("2024-07-28T06:35:00", "jordan", "jake", "yeah i felt it today. thanks for the callout. i'll drop the weight and fix the form")
msg("2024-08-20T07:00:00", "jordan", "jake", "jake what supplements are you taking? your recovery seems insane")
msg("2024-08-20T07:05:00", "jake", "jordan", "creatine monohydrate (5g/day), whey protein, fish oil, vitamin D, and magnesium before bed. nothing fancy")
msg("2024-08-20T07:10:00", "jordan", "jake", "i should start creatine. everyone says it's the one supplement that actually works")
msg("2024-08-20T07:12:00", "jake", "jordan", "it is. just drink more water. you'll gain 3-5 lbs of water weight in the first week. don't freak out")
msg("2024-11-10T07:00:00", "jake", "jordan", "dude i signed up for a spartan race in april. you should do it with me")
msg("2024-11-10T07:05:00", "jordan", "jake", "spartan race? those mud obstacle things? how far?")
msg("2024-11-10T07:10:00", "jake", "jordan", "5k with 20 obstacles. it's called the 'sprint'. not that bad. mostly grip strength and cardio")
msg("2024-11-10T07:15:00", "jordan", "jake", "tempting but i think i'm going to train for a half marathon instead. want to try running")
msg("2025-03-01T06:00:00", "jake", "jordan", "you've been running a lot. are you still lifting? don't become a cardio bro 😂")
msg("2025-03-01T06:05:00", "jordan", "jake", "3 days lifting, 3 days running, 1 rest. trying to be well-rounded. also yoga on sundays now")
msg("2025-03-01T06:10:00", "jake", "jordan", "yoga is legit. my flexibility improved so much. also helps with squat depth")
msg("2025-06-05T07:00:00", "jake", "jordan", "haven't seen you in 3 weeks. startup eating you alive again?")
msg("2025-06-05T07:05:00", "jordan", "jake", "yeah the demo day prep is insane. after june 15 i'll be back. i promise this time")
msg("2025-06-05T07:10:00", "jake", "jordan", "you said that in february too. just saying")
msg("2025-06-05T07:12:00", "jordan", "jake", "fair. but this time there's no next thing. series A stuff is dev and nina's job. i can actually breathe")
msg("2025-11-01T07:00:00", "jake", "jordan", "gym this saturday at the new lifetime fitness on burnet?")
msg("2025-11-01T07:05:00", "jordan", "jake", "you switched from golds? what happened?")
msg("2025-11-01T07:10:00", "jake", "jordan", "lifetime has a pool and basketball courts. way nicer. also my coaching clients prefer it")
msg("2025-11-01T07:12:00", "jordan", "jake", "wait you have coaching clients? since when?")
msg("2025-11-01T07:15:00", "jake", "jordan", "started personal training on the side! 4 clients so far. $60/session. it's fun and decent money")
msg("2025-11-01T07:18:00", "jordan", "jake", "jake that's awesome! you've always been great at coaching. remember when you fixed my squat form in like 5 minutes?")

# ============================================================
# More Lily (~25 msgs)
# ============================================================

msg("2025-10-25T12:00:00", "lily", "jordan", "jordan can you help me pick a couch? i know nothing about furniture. my apartment is empty")
msg("2025-10-25T12:05:00", "jordan", "lily", "YES. article has great mid-century modern stuff. what's your budget?")
msg("2025-10-25T12:10:00", "lily", "jordan", "like $800? is that enough for a not-terrible couch?")
msg("2025-10-25T12:15:00", "jordan", "lily", "tight but doable. check IKEA for the KIVIK. riley and i had one in our first apartment. surprisingly comfortable")
msg("2025-11-20T19:00:00", "lily", "jordan", "update: got the KIVIK in dark gray. it's perfect. also got a bookshelf from facebook marketplace for $40")
msg("2025-11-20T19:05:00", "jordan", "lily", "nice! you're settling in. how's indeed going?")
msg("2025-11-20T19:10:00", "lily", "jordan", "really good actually. my team is great. we're working on employer branding campaigns. totally different from my portland job")
msg("2025-12-05T20:00:00", "lily", "jordan", "jordan can riley and i have a girls night? i don't have many friends here yet and she's the coolest person i know")
msg("2025-12-05T20:05:00", "jordan", "lily", "she would love that. she's been wanting to take you to this wine bar on east 6th. i'll watch biscuit")
msg("2025-12-05T20:10:00", "lily", "jordan", "perfect! also is it weird that i don't miss marcus at all? i thought breakups were supposed to hurt more")
msg("2025-12-05T20:15:00", "jordan", "lily", "sometimes not missing someone IS the answer. it means it was the right decision")
msg("2025-12-15T14:00:00", "lily", "jordan", "there's this guy at work... don't tell mom")
msg("2025-12-15T14:05:00", "jordan", "lily", "LILY. tell me everything. what's his name?")
msg("2025-12-15T14:10:00", "lily", "jordan", "his name is ben. he's a UX designer. we've been having lunch together every day for 2 weeks. he doesn't know i like him yet")
msg("2025-12-15T14:15:00", "jordan", "lily", "just ask him to coffee. life is too short. also 2 weeks of daily lunch means he definitely likes you too")

# ============================================================
# More work emails (~30)
# ============================================================

email("2024-08-05T09:00:00", "jordan@carbonsense.io", "dev@carbonsense.io",
      "Subject: CarbonSense — First Sprint Plan\n\nDev,\n\nSprint 1 (Aug 5-19):\n- [ ] Deploy pilot environment for Meridian Steel\n- [ ] SAP connector beta (MM + PP modules)\n- [ ] Set up monitoring (CloudWatch alerts)\n- [ ] Unit conversion layer\n- [ ] Customer admin dashboard v1\n\nLet's knock this out.\n\nJordan")

email("2024-10-01T10:00:00", "jordan@carbonsense.io", "team@carbonsense.io",
      "Subject: Monthly Investor Update — September 2024\n\nHi (just me and Dev right now lol),\n\nSeptember recap:\n- Meridian pilot running 60 days. Scope 1: 95.3% accuracy\n- Lone Star Cement pilot starts Nov 1\n- Gulf Coast Plastics delayed (IT security review)\n- Burn rate: $4,200/month\n- Cash remaining: ~$38,000 (personal savings)\n- Key risk: running out of cash before revenue materializes\n\nWe need the pilots to convert by Q1 2025.\n\nJordan")

email("2025-01-20T11:00:00", "jordan@carbonsense.io", "dev@carbonsense.io",
      "Subject: Elevation Application — Submitted!\n\nDev,\n\nJust submitted the Elevation application. 43 pages total:\n- Pitch deck: 18 slides\n- Financial model: 3 scenarios (conservative, base, aggressive)\n- Pilot data: Meridian 90-day results + Lone Star 60-day results\n- Technical architecture doc\n- Team bios\n\nNow we wait. Interviews Feb 3-7 if we make the cut.\n\nFingers crossed.\n\nJordan")

email("2025-06-01T09:00:00", "jordan@carbonsense.io", "team@carbonsense.io",
      "Subject: Demo Day Prep — Two Weeks Out\n\nTeam,\n\nDemo Day is June 15. Here's the plan:\n\n**Pitch:** Jordan (8 minutes)\n**Demo:** Dev live-demos the dashboard (3 minutes)\n**Available for Q&A:** Everyone\n\nKey messages:\n1. 96% scope 1 accuracy (best in class)\n2. Only platform with real-time scope 3\n3. 0% churn across all customers\n4. $43K MRR and growing 15% month-over-month\n\nDress code: Smart casual. This is Austin, not NYC.\n\nLet's do this.\n\nJordan")

email("2025-10-15T17:00:00", "jordan@carbonsense.io", "team@carbonsense.io",
      "Subject: We Bought a House! 🏠\n\nTeam,\n\nNon-work announcement: Riley and I closed on a house today! 2847 Chicon St in East Austin.\n\nHousewarming party TBD but you're all invited.\n\nAlso, this means I finally have a proper home office. No more working from the couch.\n\nJordan\n\nP.S. Biscuit has a yard now. He's already dug 3 holes.")

email("2025-11-15T09:00:00", "jordan@carbonsense.io", "team@carbonsense.io",
      "Subject: Climate Tech Summit Recap\n\nTeam,\n\nJust got back from the Climate Tech Summit in SF. Key takeaways:\n\n1. EU CSRD is driving massive demand — every European manufacturer will need emissions monitoring by 2027\n2. Our scope 3 capability is genuinely unique — nobody else has it\n3. Met 3 potential customers (BMW Munich, Unilever Rotterdam, ArcelorMittal Luxembourg)\n4. EcoTrace was there — their booth was fancy but their demo crashed twice 😬\n5. A journalist from Bloomberg wants to feature us in a climate tech piece\n\nThe KlimaSync partnership is perfectly timed.\n\nJordan")

email("2025-12-01T08:00:00", "nina@elevationvc.com", "jordan@carbonsense.io",
      "Subject: Series B Timing\n\nJordan,\n\nBased on your growth trajectory, I think we should start Series B conversations in Q2 2026. You'll be at ~$3M ARR by then, which puts you in a strong position.\n\nTarget: $25-40M raise at $200-300M valuation.\n\nKey milestones to hit first:\n1. $5M ARR by Dec 2026\n2. European revenue (at least 3 EU customers)\n3. 50+ total customers\n4. Scope 3 accuracy above 92%\n\nStart building relationships with growth-stage investors now. Happy to make intros.\n\nNina")

# ============================================================
# More OCR data (~50)
# ============================================================

# Monthly receipts (creating spending pattern)
ocr("2024-07-28T13:00:00", "[OCR: Receipt] Torchy's Tacos — 07/28/2024\n2x Trailer Park (trashy) $9.98\nQueso $4.50\n2x Mexican Coke $5.98\nTotal: $20.46\nPayment: Visa ending 4821")
ocr("2024-08-22T12:00:00", "[OCR: Receipt] Thai-Kun Food Truck — 08/22/2024\nPad thai $12.00\nThai iced tea $4.00\nTotal: $16.00\nPayment: Cash")
ocr("2024-09-05T08:00:00", "[OCR: Receipt] Veracruz All Natural — 09/05/2024\nMigas taco $4.50\nEgg & potato taco $3.50\n2x green sauce $0.00\nTotal: $8.00\nPayment: Visa ending 4821")
ocr("2024-10-12T19:00:00", "[OCR: Receipt] MT Supermarket — 10/12/2024\nSilken tofu $2.49\nDoubanjiang paste $5.99\nSichuan peppercorns $3.99\nThai basil $1.99\nFish sauce (Three Crabs) $4.99\nJasmine rice 10lb $12.99\nTotal: $32.44\nPayment: Visa ending 4821")
ocr("2024-11-22T18:00:00", "[OCR: Receipt] Costco Gas — 11/22/2024\n12.847 gallons regular\nPrice: $2.89/gal\nTotal: $37.13\nPayment: Visa ending 4821\nVehicle: 2020 Honda Civic")
ocr("2025-01-10T14:00:00", "[OCR: Receipt] Boot Campaign Hill Country Run\nDate: 01/10/2025\nRegistration: Austin Half Marathon (April 6)\nDivision: Men 25-29\nFee: $95.00\nShirt size: Medium\nPayment: Amex ending 9012")
ocr("2025-05-15T20:00:00", "[OCR: Receipt] Apple Store Domain — 05/15/2025\nMacBook Pro 14\" M4 Pro: $2,499.00\nAppleCare+ (3yr): $299.00\nUSB-C hub: $49.00\nTotal: $2,847.00\nPayment: CarbonSense Amex\nNote: Company laptop — Dev approved")
ocr("2025-06-01T11:00:00", "[OCR: Receipt] Academy Sports — 06/01/2025\nHoka Bondi 8 (running shoes): $165.00\nRunning shorts x2: $49.98\nCompression socks: $19.99\nTotal: $234.97\nPayment: Amex ending 9012")
ocr("2025-09-10T16:00:00", "[OCR: Receipt] Austin Community Credit Union\nDate: 09/10/2025\nCashier's Check: $99,000.00\nPurpose: Down payment — 2847 Chicon St\nAccount: Joint Savings ending 7734\nRemaining balance: $24,847.00")
ocr("2025-10-15T12:00:00", "[OCR: Receipt] Sherwin-Williams — 10/15/2025\nExtraWhite (5 gal) x3: $269.85\nRoycroft Bottle Green (1 gal) x2: $65.98\nPaint roller kit: $24.99\nDrop cloths x4: $31.96\nPainter's tape (3 rolls): $17.97\nTotal: $410.75\nPayment: Visa ending 4821\nNote: House painting supplies")
ocr("2025-11-20T10:00:00", "[OCR: Receipt] Rivian Service Center Austin\nDate: 11/20/2025\nService: R1S Annual Maintenance\nOdometer: 8,247 miles\nTire rotation: included\nCabin air filter: included\nSoftware update: 2025.46.2\nTotal: $0.00 (covered under warranty)\nNext service: May 2026 or 15,000 miles")

# Dashboard/app OCR
ocr("2025-04-30T08:00:00", "[OCR: Screenshot] CarbonSense Dashboard — April 2025\nActive Customers: 7\nActive Facilities: 14\nMRR: $43,000\nScope 1 Accuracy: 95.5%\nScope 2 Accuracy: 92.0%\nScope 3 Beta: 84.7% (3 customers)\nUptime: 99.96%\nAvg query time: 2.3s (PostgreSQL — needs optimization)", "ocr_screenshot")

ocr("2025-08-31T08:00:00", "[OCR: Screenshot] CarbonSense Pipeline — August 2025\nQualified Opportunities:\n- Palisade Manufacturing (6 facilities, $30k/yr) — Negotiation\n- Texas Instruments (4 facilities, $20k/yr) — CLOSED WON\n- Boeing Austin (2 facilities, $10k/yr) — Lost to EcoTrace\n- Dow Chemical (8 facilities, $40k/yr) — Discovery\n- 3M Austin (3 facilities, $15k/yr) — Demo scheduled\nTotal pipeline value: $115k ARR", "ocr_screenshot")

ocr("2025-11-30T08:00:00", "[OCR: Screenshot] GitHub — CarbonSense/carbonsense-api\nStars: 0 (private repo)\nContributors: 6 (dev, jordan, aisha, luis, preet, danny)\nLanguages: Go 45%, Python 35%, TypeScript 15%, SQL 5%\nOpen PRs: 3\nOpen issues: 12\nLast commit: 2 hours ago (danny: 'fix: dashboard chart tooltip alignment')", "ocr_screenshot")

ocr("2025-12-15T12:00:00", "[OCR: Screenshot] Strava — Year in Review 2025\nTotal runs: 127\nTotal distance: 482 miles\nAvg pace: 8:18/mi\nLongest run: 13.1 miles (half marathon)\nBest 5K: 22:48 (October PR)\nTotal elevation gain: 8,847 ft\nMost active month: March (52.3 miles)\nLeast active month: July (12.1 miles)\nStreak: 14 days (October)", "ocr_screenshot")

# Financial documents
ocr("2025-06-30T12:00:00", "[OCR: Document] CarbonSense Inc. — Cap Table (Post Seed)\nJordan Chen: 4,250,000 shares (42.5%)\nDev Patel: 3,400,000 shares (34.0%)\nElevation Ventures: 1,500,000 shares (15.0%)\nOption Pool: 850,000 shares (8.5%)\n  - Aisha Rahman: 75,000 (0.75%)\n  - Options reserved: 775,000 (7.75%)\nTotal: 10,000,000 shares\n409A valuation: $1.50/share", "ocr_document")

ocr("2025-12-31T12:00:00", "[OCR: Document] CarbonSense Inc. — Cap Table (Post Series A)\nJordan Chen: 4,250,000 shares (33.1%)\nDev Patel: 3,400,000 shares (26.5%)\nElevation Ventures: 1,500,000 shares (11.7%)\nKhosla Ventures: 2,307,692 shares (18.0%)\nOption Pool: 1,392,308 shares (10.8%)\n  - Aisha Rahman: 125,000 (0.97%)\n  - Rachel Torres: 128,205 (1.0%)\n  - Luis Moreno: 38,461 (0.3%)\n  - Preet Kaur: 38,461 (0.3%)\n  - Danny Okafor: 38,461 (0.3%)\n  - Reserved: 1,023,720 (7.98%)\nTotal: 12,850,000 shares\n409A valuation: $5.06/share", "ocr_document")

# ============================================================
# More notes (~15)
# ============================================================

note("2024-08-01T22:00:00", "[Note] CarbonSense Name Origin\nWe almost called it 'EmissionIQ' but it sounded too corporate. 'CarbonSense' was Riley's idea. She said 'it should sound like common sense for carbon.' Brilliant. That's going in the origin story.")

note("2024-09-30T23:00:00", "[Note] First 60 days — lessons learned\n1. Enterprise sales takes 3x longer than expected\n2. Every customer has different data formats\n3. Unit conversion is a bigger problem than the ML\n4. Dev is incredible but we both need to specialize (me: biz, him: eng)\n5. Personal savings burn rate: $3,200/month (rent $1,050 my share, food $400, car $250, insurance $300, misc $1,200)\n6. I'm sleeping 5-6 hours. Need to fix this.")

note("2024-12-31T23:00:00", "[Note] 2024 Year in Review\n- Quit Dataflux (July 29)\n- Incorporated CarbonSense (July 25)\n- Completed Meridian Steel pilot (96.1% accuracy!)\n- Started Lone Star Cement pilot\n- Revenue: $8,000 MRR by December\n- Hit 325 squat PR\n- Biscuit ate a rotisserie chicken carcass and survived\n- Watched Shogun with Riley — best show ever\n- F1 at COTA with Sam and Jake — incredible\n- Biggest fear: running out of money\n- Biggest joy: building something with Dev")

note("2025-06-15T23:00:00", "[Note] Demo Day reflection\n- 8 minute pitch went well. Nina said it was the best of the cohort\n- Dev's live demo was flawless (thank god)\n- 14 investors asked for follow-ups\n- Three want to lead Series A (Sequoia, a16z, Khosla)\n- I cried in the bathroom after. Not sad crying. Relief crying.\n- Called mom and dad from the parking lot. Dad said 'I always knew you could do it'\n- This is real. This is actually happening.")

note("2025-09-10T23:00:00", "[Note] House buying checklist — DONE\n✅ Pre-approval ($550k, ACCU)\n✅ Found house (2847 Chicon St, $495k)\n✅ Home inspection (passed, minor issues)\n✅ Appraisal ($510k — $15k above purchase price 🎉)\n✅ Down payment ($99k cashier's check)\n✅ Homeowner's insurance (State Farm, $1,200/yr)\n✅ Close (October 15)\nMove-in: October 16\nFirst task: set up Biscuit's yard fence")

note("2025-10-16T22:00:00", "[Note] First night in our house\nSlept on an air mattress because the moving truck comes tomorrow. Biscuit ran around the empty house for 20 minutes. Riley and I sat on the back porch and drank champagne. No furniture, no TV, just us and the stars. She said 'this feels like home already.' I almost proposed right there but the ring is still on layaway. Soon.")

note("2025-11-14T22:00:00", "[Note] Climate Tech Summit — talk notes\nAudience: ~500 people. Biggest stage I've ever spoken on.\nTalk: 'Real-time Emissions Monitoring: From Prototype to Production'\nKey points:\n1. Started in my apartment, now 14 people and $1.2M ARR\n2. Accuracy is everything — manufacturing companies need >95%\n3. Scope 3 is the frontier — our graph attention network approach\n4. Live demo: showed real-time emissions for Meridian Steel\nQ&A highlights:\n- Bloomberg journalist asked about European expansion (good press)\n- EcoTrace CEO was in the audience (awkward)\n- Someone from BMW asked about German compliance (!!)\nFeedback: multiple people said it was the best talk of the conference")

# ============================================================
# More calendar events (~15)
# ============================================================

cal("2024-09-14T00:00:00", "[Calendar] Jordan's 28th Birthday\nDate: September 14, 2024\nPlans: Riley making red velvet cake, dinner at home\nGift from Sam: COTA F1 paddock passes")

cal("2024-10-26T08:00:00", "[Calendar] F1 US Grand Prix — COTA\nDate: October 27, 2024\nTickets: 3 (Jordan, Sam, Jake)\nMeet at COTA parking lot at 8am\nPaddock access: 10am-2pm")

cal("2024-11-26T08:00:00", "[Calendar] Thanksgiving — Portland\nDate: November 28, 2024\nFlight: Nov 26, 3pm arrival\nStaying at: Parents' house\nRiley + Biscuit coming\nLily + Marcus also attending")

cal("2025-01-03T08:00:00", "[Calendar] Fredericksburg Weekend — Riley's Christmas Gift\nDate: January 3-5, 2025\nAccommodation: Hye Meadow Winery Cottage\nNo laptops. No wifi.\nBiscuit friendly.")

cal("2025-02-03T08:00:00", "[Calendar] Elevation Ventures — Interview\nDate: February 5, 2025, 2:00 PM CT\nFormat: Video call (Zoom)\nInterviewers: Nina Vasquez + 2 other partners\nPitch: 10 minutes + 20 min Q&A\nPrepare: Pilot data, financial model, competitive landscape")

cal("2025-03-20T08:00:00", "[Calendar] Aisha Rahman — First Day\nDate: March 15, 2025\nSetup: Dev handles access (GitHub, AWS, Slack)\nOnboarding doc: /docs/onboarding.md\nFirst 1:1 with Jordan: Friday March 21")

cal("2025-04-06T06:00:00", "[Calendar] Austin Half Marathon\nDate: April 6, 2025, 7:00 AM\nStart: Congress Ave Bridge\nBib #: 3847\nGoal: Sub 2 hours\nRiley + Biscuit at finish line")

cal("2025-06-14T08:00:00", "[Calendar] Elevation Ventures — Demo Day\nDate: June 15, 2025, 1:00 PM\nLocation: Line Hotel, Austin\nFormat: 8-min pitch + 15-min Q&A\n~200 investors in audience\nDress: Smart casual\nJordan pitches, Dev does live demo")

cal("2025-07-03T08:00:00", "[Calendar] Jordan & Riley Anniversary\nDate: July 3, 2025 — 5 year anniversary\nReservation: Uchiko, 7:30 PM\n⚠️ DO NOT SCHEDULE CALLS AFTER 5PM")

cal("2025-08-25T08:00:00", "[Calendar] Series A Signing\nDate: August 25, 2025\nKhosla Ventures — $10M\nDocuSign ceremony at 4pm\nCelebration dinner: Uchi with Dev, Nina, and team")

# ============================================================
# More misc conversations for noise/realism (~30 msgs)
# ============================================================

# Group chat references
msg("2025-05-25T15:00:00", "jordan", "sam", "ACL weekend 2 confirmed? me riley you and jake? we need a group chat")
msg("2025-05-25T15:05:00", "sam", "jordan", "group chat created: 'ACL Squad'. added you riley and jake. let's figure out logistics")
msg("2025-10-05T14:00:00", "jordan", "sam", "bro ACL was amazing. khruangbin absolutely destroyed. also riley and maya are now best friends apparently")
msg("2025-10-05T14:05:00", "sam", "jordan", "right?! they exchanged numbers and already have brunch planned. also jake was so funny at the tycho set")

# Random life moments
msg("2024-08-30T22:00:00", "jordan", "riley", "can't sleep. keep thinking about what happens if we fail. we have maybe 18 months of savings")
msg("2024-08-30T22:05:00", "riley", "jordan", "come here. put the phone down. we're going to be fine. worst case you get another engineering job. you're incredibly talented")
msg("2024-08-30T22:10:00", "jordan", "riley", "you're right. thanks for being my person. i don't say it enough")
msg("2024-08-30T22:12:00", "riley", "jordan", "you don't need to say it. i know. now sleep. biscuit is already snoring")

msg("2025-02-14T21:00:00", "jordan", "riley", "best valentines dinner ever. the omakase at uchi was insane. 14 courses")
msg("2025-02-14T21:05:00", "riley", "jordan", "the uni course. i'm still thinking about it. also you looked really handsome tonight ❤️")

msg("2025-03-01T14:00:00", "jordan", "dev", "dev random question: what's your favorite book about startups? nina asked me for a reading list")
msg("2025-03-01T14:05:00", "dev", "jordan", "the mom test by rob fitzpatrick. changed how i think about customer interviews. also 'high growth handbook' by elad gil")

msg("2025-07-04T10:00:00", "jordan", "sam", "happy 4th! going to the fireworks at auditorium shores tonight?")
msg("2025-07-04T10:05:00", "sam", "jordan", "yeah! bringing a cooler. meet at 7? grab a spot by the water")
msg("2025-07-04T10:10:00", "jordan", "sam", "perfect. bringing riley, biscuit, and sparklers. biscuit might hate the fireworks though")
msg("2025-07-04T22:00:00", "jordan", "sam", "biscuit LOVED the fireworks. just sat there watching. what a weird dog")

msg("2025-08-05T07:00:00", "jordan", "riley", "morning. i made coffee and fed biscuit. heading to the gym then office. therapy at 3")
msg("2025-08-05T07:05:00", "riley", "jordan", "thanks babe. have a good day. therapy is important — proud of you for going")

msg("2025-11-28T10:00:00", "jordan", "mom", "happy thanksgiving mom! we're doing a small one here at the house this year. lily is coming. we FaceTimed dad earlier")
msg("2025-11-28T10:05:00", "mom", "jordan", "happy thanksgiving sweetie! we miss you. february can't come soon enough. lily sent me photos of your house — it's beautiful!")

msg("2025-12-31T23:55:00", "jordan", "riley", "2025. what a year. new company. new investors. new house. new understanding of myself. and through all of it, you")
msg("2025-12-31T23:57:00", "riley", "jordan", "i love you jordan. 2026 is going to be even better. i can feel it")
msg("2025-12-31T23:58:00", "jordan", "riley", "i love you too. more than you know. 💕")

# ============================================================
# Random professional contacts (~15 msgs)
# ============================================================

msg("2025-04-25T10:00:00", "jordan", "rachel", "rachel when you start, first priority is the pipeline spreadsheet. we have 40 target accounts identified but no tracking")
msg("2025-09-05T14:00:00", "jordan", "aisha", "aisha the techcrunch article mentioned your scope 3 work. your linkedin is about to blow up")
msg("2025-09-05T14:05:00", "aisha", "jordan", "haha already got 12 connection requests from recruiters. don't worry, i'm not going anywhere 😊")
msg("2025-10-20T11:00:00", "jordan", "rachel", "rachel the TCO calculator you built is brilliant. meridian showed it to their CFO and he immediately approved 2 more facilities")
msg("2025-10-20T11:05:00", "rachel", "jordan", "YES! that's the power of speaking the CFO's language. ROI, not features")
msg("2025-12-20T09:00:00", "jordan", "dev", "end of year team awards. who gets what?")
msg("2025-12-20T09:05:00", "dev", "jordan", "aisha: 'moat builder' award. rachel: 'closer of the year'. danny: 'best code quality'. luis and preet: 'infrastructure heroes'")
msg("2025-12-20T09:10:00", "jordan", "dev", "love it. you get the 'rock' award. because you're literally the foundation of everything")
msg("2025-12-20T09:15:00", "dev", "jordan", "stop i'm blushing. also omar (product) should get something. his roadmap discipline saved us from scope creep at least 3 times")

# Combine and save
messages.extend(new)
messages.sort(key=lambda x: x["timestamp"])

print(f"\nFinal dataset: {len(messages)} messages")

modalities = {}
for m in messages:
    mod = m.get("modality", "unknown")
    modalities[mod] = modalities.get(mod, 0) + 1
print(f"\nBy modality:")
for mod, count in sorted(modalities.items(), key=lambda x: -x[1]):
    print(f"  {mod}: {count}")

categories = {}
for m in messages:
    cat = m["category"]
    categories[cat] = categories.get(cat, 0) + 1
print(f"\nBy category:")
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

senders = {}
for m in messages:
    s = m["sender"]
    senders[s] = senders.get(s, 0) + 1
print(f"\nBy sender (top 15):")
for s, count in sorted(senders.items(), key=lambda x: -x[1])[:15]:
    print(f"  {s}: {count}")

print(f"\nTimeline: {messages[0]['timestamp']} to {messages[-1]['timestamp']}")

with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json", "w") as f:
    json.dump(messages, f, indent=2)
print(f"\nSaved to synthetic_v2_messages.json")
