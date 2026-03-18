"""
Expand the v2 dataset from ~193 to 1500+ messages.
Adds realistic daily life noise, more conversations, more data modalities.
"""

import json
import random
from datetime import datetime, timedelta

with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json") as f:
    messages = json.load(f)

print(f"Starting with {len(messages)} messages")

new_messages = []

# ================================================
# BATCH 1: More text conversations (daily life)
# ================================================

# Jordan and Riley — domestic life (~100 messages)
riley_convos = [
    # Groceries
    ("2024-07-20T17:00:00", "jordan", "riley", "hey can you grab milk and eggs on your way home?"),
    ("2024-07-20T17:05:00", "riley", "jordan", "sure. need anything else? i'm at HEB"),
    ("2024-07-20T17:06:00", "jordan", "riley", "actually yeah get some chicken thighs and that garlic naan we like"),
    ("2024-07-20T17:10:00", "riley", "jordan", "got it. also biscuit is almost out of food. getting blue buffalo?"),
    ("2024-07-20T17:11:00", "jordan", "riley", "yes the chicken and brown rice one. the large bag"),

    # Apartment stuff
    ("2024-08-02T09:00:00", "riley", "jordan", "the AC is making that weird noise again. can you call maintenance?"),
    ("2024-08-02T09:30:00", "jordan", "riley", "called them. they're coming between 2-4. can you be home?"),
    ("2024-08-02T15:00:00", "riley", "jordan", "they fixed it! was a loose fan belt. no charge since we're still under warranty"),
    ("2024-08-05T20:00:00", "jordan", "riley", "the lease renewal came. they want to raise rent from $2,100 to $2,350"),
    ("2024-08-05T20:05:00", "riley", "jordan", "ugh that's $250 more. should we look for a new place?"),
    ("2024-08-05T20:10:00", "jordan", "riley", "maybe not right now with the startup thing. let's just sign for one more year and reassess"),

    # Weekend plans
    ("2024-08-10T10:00:00", "jordan", "riley", "farmers market tomorrow? lady bird lake one"),
    ("2024-08-10T10:05:00", "riley", "jordan", "yes! and can we take biscuit to the dog park after?"),
    ("2024-08-10T10:06:00", "jordan", "riley", "plan. also sam invited us to his place for a BBQ at 4"),
    ("2024-08-10T10:08:00", "riley", "jordan", "fun. i'll make that corn salad everyone likes"),

    # Riley's school
    ("2024-09-01T18:00:00", "riley", "jordan", "first day of the masters program tomorrow. i'm so nervous"),
    ("2024-09-01T18:05:00", "jordan", "riley", "you're going to crush it. counseling psych is literally what you were born to do"),
    ("2024-09-01T18:10:00", "riley", "jordan", "thanks babe. my first practicum client is in october. real people with real problems. scary"),
    ("2024-09-15T21:00:00", "riley", "jordan", "my professor said my case conceptualization was the best in the class 😊"),
    ("2024-09-15T21:02:00", "jordan", "riley", "obviously. you're the most empathetic person i know. they're lucky to have you"),

    # Cooking
    ("2024-10-12T17:00:00", "jordan", "riley", "i'm making that thai basil chicken tonight. the one from the youtube channel"),
    ("2024-10-12T17:05:00", "riley", "jordan", "pad kra pao! yes please. do we have thai basil?"),
    ("2024-10-12T17:06:00", "jordan", "riley", "no need to stop at the asian market on east 7th. can you grab thai basil and fish sauce?"),
    ("2024-11-05T19:00:00", "riley", "jordan", "made your favorite — lemon garlic salmon with roasted brussels sprouts"),
    ("2024-11-05T19:02:00", "jordan", "riley", "YOU'RE THE BEST. running home now. leaving office in 5"),

    # Biscuit adventures
    ("2024-11-15T08:00:00", "riley", "jordan", "biscuit just puked on the rug. again. i think it's the new treats"),
    ("2024-11-15T08:05:00", "jordan", "riley", "which treats? the ones from the farmer's market?"),
    ("2024-11-15T08:06:00", "riley", "jordan", "yeah the sweet potato ones. going back to the milk-bone ones he's been fine on"),
    ("2025-01-20T07:30:00", "riley", "jordan", "biscuit rolled in something dead at the park. he needs a bath ASAP 🤢"),
    ("2025-01-20T07:35:00", "jordan", "riley", "classic corgi move. i'll bathe him when i get home"),
    ("2025-04-10T16:00:00", "jordan", "riley", "biscuit's birthday is march 15 right? we missed it 😬"),
    ("2025-04-10T16:05:00", "riley", "jordan", "yes we did. bad pet parents. let's do a belated party this weekend? invite lily and her friend's dog"),

    # Moving discussion
    ("2025-06-15T20:00:00", "riley", "jordan", "jordan our lease is up in august. with the company doing well should we look at houses?"),
    ("2025-06-15T20:05:00", "jordan", "riley", "i've been thinking about that. we could probably afford a down payment. zillow says east austin has some good ones around $450-550k"),
    ("2025-06-15T20:10:00", "riley", "jordan", "i love east austin. close to your old office, close to lily. let's start looking"),
    ("2025-07-10T12:00:00", "jordan", "riley", "just saw a listing. 3bed 2bath on webberville road. $520k. backyard for biscuit. open house saturday"),
    ("2025-07-10T12:05:00", "riley", "jordan", "omg it's perfect. yes let's go"),
    ("2025-07-25T19:00:00", "riley", "jordan", "we didn't get the webberville house. outbid by $30k cash offer"),
    ("2025-07-25T19:05:00", "jordan", "riley", "ugh. austin housing market is insane. we'll find something. let's keep looking"),
    ("2025-08-30T14:00:00", "jordan", "riley", "RILEY. 4bed 2bath on chicon st. $495k. it's been on market for 3 weeks. no bidding war"),
    ("2025-08-30T14:02:00", "riley", "jordan", "showing tomorrow morning???"),
    ("2025-08-30T14:03:00", "jordan", "riley", "already scheduled. 10am. i have a good feeling about this one"),
    ("2025-09-10T17:00:00", "jordan", "riley", "OFFER ACCEPTED. we're buying a house. $495k, closing october 15"),
    ("2025-09-10T17:01:00", "riley", "jordan", "I'M CRYING. OUR FIRST HOUSE. BISCUIT IS GETTING A YARD"),
]

for ts, sender, recipient, content in riley_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Jordan and Dev — more technical/business (~80 messages)
dev_convos = [
    ("2024-07-22T10:00:00", "jordan", "dev", "dev the LLC docs are ready. delaware c-corp like you said. $500 filing fee"),
    ("2024-07-22T10:05:00", "dev", "jordan", "nice. did you set up the stripe atlas thing?"),
    ("2024-07-22T10:10:00", "jordan", "dev", "yeah stripe atlas handles banking, incorporation, everything. mercury for banking"),
    ("2024-08-01T09:00:00", "dev", "jordan", "first day as full time founders. feels weird not having a boss"),
    ("2024-08-01T09:05:00", "jordan", "dev", "right? i kept checking my email for standup invites lol. anyway let's set up our own rituals. daily standup at 9am?"),
    ("2024-08-01T09:10:00", "dev", "jordan", "9am standup, weekly planning mondays, monthly retrospective. let's be disciplined about this"),
    ("2024-08-15T14:00:00", "jordan", "dev", "the SAP connector is giving me nightmares. their API documentation is from 2019 and half the endpoints are deprecated"),
    ("2024-08-15T14:05:00", "dev", "jordan", "try the odata v4 interface instead. it's newer. also look at the BAPI function modules for real-time data"),
    ("2024-08-15T14:10:00", "jordan", "dev", "ok found it. also we need to handle IDOC messages for the batch data. this is way more complex than i thought"),
    ("2024-09-01T11:00:00", "dev", "jordan", "finally got the eGRID integration working. scope 2 accuracy jumped to 93.4%. we're ready for the lone star pilot"),
    ("2024-09-01T11:05:00", "jordan", "dev", "amazing. let me update the deck. also do we need any cloud infrastructure changes?"),
    ("2024-09-01T11:10:00", "dev", "jordan", "we should move from my personal AWS account to a company account. i'll set up proper IAM and VPC this week"),
    ("2024-09-20T16:00:00", "jordan", "dev", "dev i've been tracking our burn rate. we're spending about $4,200/month total. $2,400 rent for the apartment we use as office, $1,200 AWS, $600 misc"),
    ("2024-09-20T16:05:00", "dev", "jordan", "that's lean. how long can we survive on savings?"),
    ("2024-09-20T16:10:00", "jordan", "dev", "i have about $45k saved plus the 401k rollover ($47k). so maybe 22 months if we're careful. but we need revenue before that"),
    ("2024-10-15T09:00:00", "jordan", "dev", "the gulf coast plastics pilot keeps getting delayed. their IT team is blocking the API access. something about security review"),
    ("2024-10-15T09:10:00", "dev", "jordan", "enterprise sales man. everything takes 3x longer than you think. can you get maria at meridian to make an intro to their security team?"),
    ("2024-12-01T14:00:00", "jordan", "dev", "year end planning: we need to decide on the tech stack for 2025. are we staying with python + fastapi?"),
    ("2024-12-01T14:05:00", "dev", "jordan", "python for ML and data pipelines, but i want to rewrite the API layer in go for performance. the fastapi server is struggling with concurrent connections above 200"),
    ("2024-12-01T14:10:00", "jordan", "dev", "go? is it worth the rewrite? what about rust?"),
    ("2024-12-01T14:15:00", "dev", "jordan", "go is pragmatic. rust is overkill for an API. go gives us 10x concurrency improvement. i can do the rewrite in 3 weeks"),
    ("2025-04-01T09:00:00", "jordan", "dev", "aisha is asking about GPU budget for training the scope 3 model. she needs A100s. cloud GPU costs are insane"),
    ("2025-04-01T09:05:00", "dev", "jordan", "how much?"),
    ("2025-04-01T09:10:00", "jordan", "dev", "she says 2 weeks of A100 time = about $12,000. but the model improvement should be worth it"),
    ("2025-04-01T09:12:00", "dev", "jordan", "let her do it. scope 3 is our moat. invest in the moat"),
    ("2025-05-05T11:00:00", "dev", "jordan", "the go API rewrite is done. benchmarks: 3,200 concurrent connections, avg response time 12ms. the python version was choking at 200 connections with 340ms response"),
    ("2025-05-05T11:05:00", "jordan", "dev", "12ms!! that's insane. nice work. did you keep the python ML pipeline separate?"),
    ("2025-05-05T11:10:00", "dev", "jordan", "yeah python handles all ML inference and data processing. go handles API, auth, billing, webhooks. they communicate via grpc"),
    ("2025-06-28T10:00:00", "jordan", "dev", "nina is asking about our AWS bill. it's $8,700 this month. up from $3,200 in march"),
    ("2025-06-28T10:05:00", "dev", "jordan", "scaling costs. more customers = more data = more compute. we need to look at reserved instances and savings plans. could save 30-40%"),
    ("2025-06-28T10:10:00", "jordan", "dev", "do it. also aisha mentioned we could move some inference to our own GPUs if we get big enough. she says break-even vs cloud is around 20 customers"),
    ("2025-09-20T14:00:00", "jordan", "dev", "dev we need to start the european product. EU CSRD mandate kicks in january 2026. nina says we're already getting inbound from european companies"),
    ("2025-09-20T14:05:00", "dev", "jordan", "how different is CSRD from EPA reporting?"),
    ("2025-09-20T14:10:00", "jordan", "dev", "structurally similar but different metrics, different emission factors, and we need GDPR compliance. aisha says we need a model fine-tuned on european industrial data"),
    ("2025-09-20T14:15:00", "dev", "jordan", "so basically a 3-month project. model fine-tuning, regulatory mapping, GDPR infra, EU data center. should we hire a european engineer?"),
    ("2025-11-01T10:00:00", "jordan", "dev", "update on european product: we're partnering with a german company called KlimaSync. they have the EU regulatory expertise, we have the ML. revenue share model"),
    ("2025-11-01T10:05:00", "dev", "jordan", "smart. better than building regulatory expertise from scratch. what's the split?"),
    ("2025-11-01T10:10:00", "jordan", "dev", "70/30 our favor for the tech, they handle compliance and local sales. nina approved it"),
    ("2025-12-01T16:00:00", "jordan", "dev", "dev end of year reflection: we did it man. from 0 to $1.2M ARR in 17 months. remember when we were coding in my apartment?"),
    ("2025-12-01T16:05:00", "dev", "jordan", "lol your apartment where the AC broke every other week and biscuit kept eating the ethernet cables"),
    ("2025-12-01T16:10:00", "jordan", "dev", "good times. also terrible times. but mostly good times"),
]

for ts, sender, recipient, content in dev_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Jordan and Sam — friendship (~50 messages)
sam_convos = [
    ("2024-07-20T20:00:00", "sam", "jordan", "so you're really doing it? quitting dataflux?"),
    ("2024-07-20T20:05:00", "jordan", "sam", "turned in my notice today. last day is july 29. terrifying and exciting"),
    ("2024-07-20T20:10:00", "sam", "jordan", "proud of you man. you've been talking about this for over a year. it was time"),
    ("2024-08-20T19:00:00", "jordan", "sam", "dude i need to vent. no revenue, no customers yet, and i just paid $3k for legal fees i didn't expect"),
    ("2024-08-20T19:05:00", "sam", "jordan", "deep breaths. you have pilot commitments right? the revenue will come. first 6 months of any startup is pure grind"),
    ("2024-08-20T19:10:00", "jordan", "sam", "you're right. just freaking out a little. riley is being supportive but i can tell she's worried too"),
    ("2024-10-31T21:00:00", "jordan", "sam", "happy halloween! riley and i dressed biscuit as a hot dog. he hated it. sending pics"),
    ("2024-10-31T21:05:00", "sam", "jordan", "LMAO the little legs. that poor dog. also i dressed as ted lasso. nobody got it"),
    ("2025-02-14T20:00:00", "jordan", "sam", "took riley to uchi for valentines. $350 omakase. am i insane?"),
    ("2025-02-14T20:05:00", "sam", "jordan", "you just raised $1.5M. you can afford one nice dinner bro"),
    ("2025-03-15T14:00:00", "sam", "jordan", "are you watching march madness? my bracket is already busted"),
    ("2025-03-15T14:05:00", "jordan", "sam", "didn't even fill one out this year. too busy. what happened to your bracket?"),
    ("2025-03-15T14:10:00", "sam", "jordan", "picked duke to win it all and they lost in the first round. classic"),
    ("2025-05-01T18:00:00", "jordan", "sam", "sam about the moonlighting sales thing. we're going to hire a real VP sales. but i really appreciate what you did for us the last few months"),
    ("2025-05-01T18:05:00", "sam", "jordan", "no worries at all. honestly i learned a ton. makes me want to do my own thing eventually"),
    ("2025-05-01T18:10:00", "jordan", "sam", "you should. you're a natural salesperson. seriously the way you handled the lone star negotiation was chef's kiss"),
    ("2025-08-15T19:00:00", "sam", "jordan", "how's therapy going? still seeing dr choi?"),
    ("2025-08-15T19:05:00", "jordan", "sam", "yeah every other week now. it's honestly been life changing. wish i started years ago"),
    ("2025-08-15T19:10:00", "sam", "jordan", "what kind of stuff do you work on?"),
    ("2025-08-15T19:15:00", "jordan", "sam", "boundaries mainly. i was terrible at separating work from life. also perfectionism. apparently i have extremely high standards that are sometimes unrealistic"),
    ("2025-08-15T19:20:00", "sam", "jordan", "you? unrealistic standards? NEVER 😂 but seriously good for you man"),
    ("2025-10-15T14:00:00", "sam", "jordan", "dude we're closing on the house next week right? you excited?"),
    ("2025-10-15T14:05:00", "jordan", "sam", "SO excited. biscuit is getting a yard. riley is already planning the garden. i just want a grill"),
    ("2025-10-15T14:10:00", "sam", "jordan", "housewarming BBQ is mandatory. i'll bring the brisket"),
    ("2025-11-15T18:00:00", "jordan", "sam", "housewarming is november 22. you, jake, lily, dev, aisha. casual. bring whoever"),
    ("2025-11-15T18:05:00", "sam", "jordan", "wouldn't miss it. also can i bring someone? i'm sort of seeing this girl maya"),
    ("2025-11-15T18:10:00", "jordan", "sam", "SAM. yes obviously bring her. tell me everything. where did you meet?"),
    ("2025-11-15T18:15:00", "sam", "jordan", "bumble lol. she's a nurse at dell seton. really cool. very different from my usual type"),
    ("2025-12-15T19:00:00", "jordan", "sam", "sam i need your honest opinion. is it too soon to propose? we've been together 5 years but i feel like with the house and everything the timing is right"),
    ("2025-12-15T19:05:00", "sam", "jordan", "bro it's not too soon. it's possibly too late. riley has been WAITING. trust me i've talked to her"),
    ("2025-12-15T19:10:00", "jordan", "sam", "wait you talked to her about it?! what did she say?"),
    ("2025-12-15T19:15:00", "sam", "jordan", "i'm not telling you what she said. but you should propose. that's all i'll say 😏"),
]

for ts, sender, recipient, content in sam_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Jordan and Mom/Family (~40 messages)
family_convos = [
    ("2024-07-29T18:00:00", "jordan", "mom", "last day at dataflux. packed my desk. feels surreal"),
    ("2024-07-29T18:10:00", "mom", "jordan", "your dad and i are proud of you even if we're nervous. you'll always have a home in portland if you need it ❤️"),
    ("2024-08-15T12:00:00", "mom", "jordan", "jordan i read that article about startup failure rates. 90% fail in the first year??"),
    ("2024-08-15T12:30:00", "jordan", "mom", "mom please stop googling that stuff. we already have paying pilot customers. we're not the typical startup"),
    ("2024-08-15T12:35:00", "mom", "jordan", "ok ok i'll stop. just worried. that's my job. how's biscuit?"),
    ("2024-09-14T10:00:00", "mom", "jordan", "happy birthday sweetie!! 28 years old! we sent a package, should arrive monday"),
    ("2024-09-14T10:05:00", "jordan", "mom", "thanks mom! riley is making me a cake and sam is taking me to the F1 race in october as a bday gift"),
    ("2024-09-14T10:10:00", "mom", "jordan", "F1? is that the car racing thing your dad watches? be careful"),
    ("2024-09-14T10:12:00", "jordan", "mom", "lol we're watching not driving mom. it's at COTA, big racetrack south of austin"),
    ("2024-11-28T12:00:00", "jordan", "mom", "happy thanksgiving! the turkey is amazing. dad outdid himself"),
    ("2024-11-28T12:05:00", "jordan", "lily", "lily your boyfriend marcus is really nice. he and jake would get along — they both do crossfit"),
    ("2024-11-28T12:10:00", "lily", "jordan", "haha right? he's obsessed with crossfit. glad you like him"),
    ("2025-01-01T00:01:00", "jordan", "mom", "happy new year mom and dad! 2025 is going to be our year. i can feel it"),
    ("2025-01-01T00:05:00", "mom", "jordan", "happy new year baby! we're so proud of you. call us this weekend?"),
    ("2025-03-30T15:00:00", "mom", "jordan", "jordan your dad had to have a minor procedure on his knee. nothing serious! arthroscopic. he's home already"),
    ("2025-03-30T15:05:00", "jordan", "mom", "oh no! is he ok? should i fly up?"),
    ("2025-03-30T15:10:00", "mom", "jordan", "no no don't be silly. he's watching TV and eating ice cream. he's fine. the PT says 6 weeks recovery"),
    ("2025-06-20T10:00:00", "jordan", "mom", "mom big news: we raised another $10 million. the company is now worth $65 million. on paper"),
    ("2025-06-20T10:05:00", "mom", "jordan", "I DON'T EVEN KNOW WHAT THAT MEANS BUT I'M SO PROUD. your father is speechless. literally can't talk"),
    ("2025-06-20T10:10:00", "jordan", "mom", "lol it means we have enough money to hire a real team and compete. we're not a tiny startup anymore"),
    ("2025-09-15T18:00:00", "jordan", "mom", "mom riley and i are buying a house! 4 bed 2 bath in east austin. closing in october"),
    ("2025-09-15T18:05:00", "mom", "jordan", "A HOUSE!! my baby is buying a house!! i'm going to cry. does it have a yard for biscuit?"),
    ("2025-09-15T18:10:00", "jordan", "mom", "big backyard. biscuit is going to lose his mind. also there's a guest room for when you and dad visit"),
    ("2025-12-25T09:00:00", "jordan", "mom", "merry christmas mom and dad! we're staying in austin this year since we just moved into the house. come visit us in february? it's still warm here"),
    ("2025-12-25T09:10:00", "mom", "jordan", "merry christmas sweetheart! yes we'd love to visit! february sounds perfect. dad wants to see the new house and meet lily's new friends"),
]

for ts, sender, recipient, content in family_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Jordan and Jake — gym/fitness (~30 messages)
jake_convos = [
    ("2024-08-01T06:00:00", "jake", "jordan", "bro where are you? it's 6am. you said you'd be here"),
    ("2024-08-01T06:05:00", "jordan", "jake", "overslept. sorry man. first week of startup life, sleeping patterns are all messed up"),
    ("2024-08-01T06:06:00", "jake", "jordan", "get your ass here. chest and tris today. no excuses"),
    ("2024-09-10T06:30:00", "jordan", "jake", "bench PR! 235. finally broke through the 225 plateau"),
    ("2024-09-10T06:32:00", "jake", "jordan", "let's go!! what changed? you've been stuck at 225 for months"),
    ("2024-09-10T06:35:00", "jordan", "jake", "added pause reps and close-grip sets. also the creatine is definitely helping"),
    ("2024-10-20T12:00:00", "jordan", "jake", "COTA next weekend for F1! sam got us paddock passes as my bday gift. you in?"),
    ("2024-10-20T12:05:00", "jake", "jordan", "hell yes i'm in. never been to F1 live. what do i wear?"),
    ("2024-10-20T12:10:00", "jordan", "jake", "whatever. it's austin. shorts and a t-shirt. maybe sunscreen"),
    ("2024-10-27T18:00:00", "jordan", "jake", "that was INCREDIBLE. the sound of those engines in person is something else. also max verstappen walked right past us"),
    ("2024-10-27T18:05:00", "jake", "jordan", "i'm still vibrating. also i'm 100% getting a racing sim now"),
    ("2025-02-01T06:30:00", "jake", "jordan", "haven't seen you at the gym in 2 weeks. everything ok?"),
    ("2025-02-01T06:35:00", "jordan", "jake", "elevation investor interviews. been prepping nonstop. back next week i promise"),
    ("2025-04-06T13:00:00", "jake", "jordan", "dude you ran a half marathon?? since when are you a runner?"),
    ("2025-04-06T13:05:00", "jordan", "jake", "since january! added running to the routine. 1:52:34 finish time. not fast but i finished"),
    ("2025-04-06T13:10:00", "jake", "jordan", "that's solid! i could never run that far. my knees would explode"),
    ("2025-07-15T19:00:00", "jake", "jordan", "you look like shit dude. when was the last time you slept 8 hours?"),
    ("2025-07-15T19:05:00", "jordan", "jake", "honestly i can't remember. the fundraise is killing me. also riley and i have been fighting"),
    ("2025-07-15T19:10:00", "jake", "jordan", "take care of yourself man. no company is worth your health. or your relationship"),
    ("2025-07-15T19:12:00", "jordan", "jake", "you sound like riley. and my therapist. and sam. and dev. maybe everyone is right"),
    ("2025-10-20T07:00:00", "jake", "jordan", "6am gym this saturday? just like old times?"),
    ("2025-10-20T07:05:00", "jordan", "jake", "i'm back to mornings! the 7pm hard stop means i sleep better. 6am saturday works"),
    ("2025-11-22T16:00:00", "jake", "jordan", "housewarming was awesome. your house is sick. biscuit loves that yard"),
    ("2025-11-22T16:05:00", "jordan", "jake", "thanks man! glad you came. also maya seems really cool. sam's a lucky guy"),
]

for ts, sender, recipient, content in jake_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Aisha work conversations (~30 messages)
aisha_convos = [
    ("2025-03-15T09:00:00", "jordan", "aisha", "welcome to the team aisha! first day. dev will get you set up with access to everything"),
    ("2025-03-15T09:05:00", "aisha", "jordan", "thanks jordan! excited to be here. i already have ideas for improving the scope 3 model"),
    ("2025-03-15T09:10:00", "jordan", "aisha", "love the energy. let's save them for your first 1:1 on friday. for now just get settled and review the codebase"),
    ("2025-04-05T14:00:00", "aisha", "jordan", "jordan i finished the initial scope 3 model benchmark. current accuracy is 84.7% on meridian's supply chain. i think i can get it to 90+ with graph attention networks"),
    ("2025-04-05T14:05:00", "jordan", "aisha", "90+?! that would be best in class. how much GPU time do you need?"),
    ("2025-04-05T14:10:00", "aisha", "jordan", "about 2 weeks on A100s. roughly $12k in cloud compute. the model architecture uses partial supply chain graphs — we don't need complete data to make accurate predictions"),
    ("2025-05-20T16:00:00", "aisha", "jordan", "scope 3 model v2 results: 88.9% accuracy on meridian, 91.2% on lone star, 86.4% on gulf coast. weighted avg: 89.1%"),
    ("2025-05-20T16:05:00", "jordan", "aisha", "incredible. that's a 4.4 point improvement. the graph attention approach is working. can you write up a blog post about the methodology? good for marketing"),
    ("2025-05-20T16:10:00", "aisha", "jordan", "sure. also dr. woo's student chen wei has been helping with the training data augmentation. his synthetic data generation technique added 15% more training samples"),
    ("2025-08-10T10:00:00", "aisha", "jordan", "jordan i need to talk to you about something. i got an offer from google's climate AI team. $280k total comp"),
    ("2025-08-10T10:05:00", "jordan", "aisha", "oh. that's... a lot. what are you thinking?"),
    ("2025-08-10T10:10:00", "aisha", "jordan", "i love what we're building here. i don't want to leave. but i'd be lying if i said the money doesn't matter. i have student loans"),
    ("2025-08-10T10:15:00", "jordan", "aisha", "let me talk to dev and nina. we'll figure something out. you're the most important person on the team after dev"),
    ("2025-08-12T09:00:00", "jordan", "aisha", "ok here's our counter: $160k base (up from $135k), 1.25% equity (up from 0.75%), and we'll cover $30k of your student loans. the equity is worth a lot more now at a $65M valuation"),
    ("2025-08-12T09:05:00", "aisha", "jordan", "that's really generous jordan. the student loan thing especially. i'm staying. tell google thanks but no thanks"),
    ("2025-08-12T09:10:00", "jordan", "aisha", "YES. you're the best. now let's make that equity worth $650M 😎"),
    ("2025-10-05T11:00:00", "aisha", "jordan", "the european scope 3 model is trained. accuracy: 87.3% on the KlimaSync test data. need to tune for german industrial categories but it's a strong start"),
    ("2025-11-15T14:00:00", "aisha", "jordan", "chen wei's paper got accepted to ICML! his scope 3 improvements are directly usable in our model. we should cite carbonsense in the acknowledgments"),
]

for ts, sender, recipient, content in aisha_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Nina investor conversations (~25 messages)
nina_convos = [
    ("2025-03-01T10:00:00", "nina", "jordan", "jordan how's the cohort going? first week done. any issues?"),
    ("2025-03-01T10:05:00", "jordan", "nina", "amazing. the other companies in the cohort are impressive. learned a lot from the product-market fit workshop"),
    ("2025-04-15T09:00:00", "nina", "jordan", "your monthly metrics are strong. 7 customers, $43k MRR. the scope 3 beta is a differentiator. keep pushing"),
    ("2025-04-15T09:05:00", "jordan", "nina", "thanks nina. the EPa scope 3 mandate is driving massive inbound. we can barely keep up with demos"),
    ("2025-06-10T14:00:00", "nina", "jordan", "demo day prep: your pitch needs work. too much tech, not enough story. lead with the problem, not the solution"),
    ("2025-06-10T14:05:00", "jordan", "nina", "you're right. i tend to geek out on the ML stuff. i'll restructure tonight"),
    ("2025-06-10T14:10:00", "nina", "jordan", "also practice the 'why now' slide. the EPA mandate is your best friend. make it visceral — these companies HAVE to comply or face penalties"),
    ("2025-07-01T11:00:00", "nina", "jordan", "three firms want to lead. good position to be in. my advice: khosla or a16z. both have strong climate portfolios"),
    ("2025-07-01T11:05:00", "jordan", "nina", "leaning khosla. vinod actually understands the science. the a16z partner kept asking about 'AI agents' and 'autonomous emissions' which isn't really what we do"),
    ("2025-07-01T11:10:00", "nina", "jordan", "good instinct. khosla is the right pick. their operating partners will be more helpful too"),
    ("2025-09-01T10:00:00", "nina", "jordan", "series A closed! $10M from khosla. you've come a long way from that first coffee at epoch. i'm proud of you jordan"),
    ("2025-09-01T10:05:00", "jordan", "nina", "couldn't have done it without you nina. literally. you took a bet on two guys with a prototype. i won't forget that"),
    ("2025-10-15T14:00:00", "nina", "jordan", "jordan the ecotrace competition is heating up. my recommendation: don't compete on price. compete on accuracy and scope 3. that's your moat"),
    ("2025-10-15T14:05:00", "jordan", "nina", "agreed. our 0% churn tells the story. customers who try our accuracy don't leave. ecotrace is buying growth, we're earning it"),
]

for ts, sender, recipient, content in nina_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Lily conversations (~20 messages)
lily_convos = [
    ("2024-08-01T20:00:00", "lily", "jordan", "so you really quit? mom is being dramatic about it btw"),
    ("2024-08-01T20:05:00", "jordan", "lily", "yeah she sent me an article about startup failure rates. classic helen chen move"),
    ("2024-08-01T20:10:00", "lily", "jordan", "LOL she did the same to me when i changed my major from pre-med to marketing. she'll come around"),
    ("2024-12-25T11:00:00", "lily", "jordan", "merry christmas big bro! love the book you sent. how did you know i wanted 'atomic habits'?"),
    ("2024-12-25T11:05:00", "jordan", "lily", "riley told me. merry christmas! hows marcus?"),
    ("2024-12-25T11:10:00", "lily", "jordan", "he's good! we're at his parents in dallas. his mom makes insane tamales"),
    ("2025-08-20T19:00:00", "lily", "jordan", "jordan i need advice. marcus and i broke up. he wanted to move to seattle for a job and i didn't want to do long distance"),
    ("2025-08-20T19:05:00", "jordan", "lily", "oh lily i'm sorry. that's a tough situation. are you ok?"),
    ("2025-08-20T19:10:00", "lily", "jordan", "sad but also relieved? we weren't great together the last few months. anyway i'm thinking about moving. maybe somewhere new"),
    ("2025-08-20T19:15:00", "jordan", "lily", "move to austin!! we're here, riley is here, you'd love it. and indeed has an office here"),
    ("2025-08-20T19:20:00", "lily", "jordan", "actually... indeed does have austin jobs. let me look into it 👀"),
    ("2025-11-05T18:00:00", "lily", "jordan", "bro i found the BEST taco truck in austin. el primo on east 12th. better than veracruz don't @ me"),
    ("2025-11-05T18:05:00", "jordan", "lily", "better than veracruz?! those are fighting words. prove it. lunch tomorrow?"),
    ("2025-11-30T14:00:00", "lily", "jordan", "jordan i got promoted!! marketing manager at indeed! my boss said she was impressed with my campaign analytics"),
    ("2025-11-30T14:05:00", "jordan", "lily", "LILY!! congratulations!! dinner is on me. anywhere you want"),
]

for ts, sender, recipient, content in lily_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# ================================================
# BATCH 2: More emails (~60)
# ================================================

more_emails = [
    # Customer emails
    {"content": "Subject: CarbonSense Integration Request\n\nHi Jordan,\n\nWe're Palisade Manufacturing, a mid-size aluminum producer in Houston. We heard about CarbonSense from Maria Gonzalez at Meridian Steel.\n\nWe have 6 facilities and are facing EPA scope 1 reporting requirements. Our current process is manual Excel spreadsheets taking ~60 hours/month.\n\nCan we schedule a demo?\n\nRegards,\nTom Sullivan\nCFO, Palisade Manufacturing",
     "sender": "tom.sullivan@palisademfg.com", "recipient": "jordan@carbonsense.io",
     "timestamp": "2025-04-20T09:00:00", "category": "work_email", "modality": "email"},

    {"content": "Subject: Quarterly Business Review — Lone Star Cement\n\nJordan & Team,\n\nAttached are our QBR findings for Q2 2025:\n\n- Scope 1 accuracy: 95.2% (up from 93.8% at pilot)\n- Scope 2 accuracy: 92.1%\n- Time savings: 55 hours/month (up from 40 at pilot)\n- ROI: 340% annualized\n- NPS: 82\n\nWe'd like to discuss adding scope 3 tracking and expanding to our Oklahoma facilities.\n\nBest,\nCarlos Jimenez\nSustainability Director, Lone Star Cement",
     "sender": "carlos.jimenez@lonestacement.com", "recipient": "jordan@carbonsense.io",
     "timestamp": "2025-07-15T10:00:00", "category": "work_email", "modality": "email"},

    # Recruiting emails
    {"content": "Subject: Full Stack Engineer — CarbonSense\n\nHi Jordan,\n\nI saw your job posting on Hacker News. I'm a full stack engineer with 5 years experience (React + Go). Currently at Stripe.\n\nWhat drew me to CarbonSense is the climate mission. I've been looking for a way to use my skills for environmental impact.\n\nAttaching my resume and GitHub.\n\nBest,\nDanny Okafor",
     "sender": "danny.okafor@gmail.com", "recipient": "hiring@carbonsense.io",
     "timestamp": "2025-05-10T14:00:00", "category": "work_email", "modality": "email"},

    # Legal/admin emails
    {"content": "Subject: CarbonSense Inc. — Trademark Registration Complete\n\nDear Jordan,\n\nThe USPTO has approved your trademark registration for:\n- Mark: CARBONSENSE\n- Registration Number: 7,234,891\n- Class: IC 042 (Software as a Service)\n- Filing Date: November 15, 2024\n- Registration Date: April 22, 2025\n\nThis registration is valid for 10 years, renewable.\n\nRegards,\nJennifer Liu, Esq.\nAustin IP Law Group",
     "sender": "jliu@austiniplaw.com", "recipient": "jordan@carbonsense.io",
     "timestamp": "2025-04-22T10:00:00", "category": "work_email", "modality": "email"},

    # Personal emails
    {"content": "Subject: Portland High School Class of 2016 — 10 Year Reunion!\n\nHi Jordan!\n\nCan you believe it's been 10 years? We're organizing the Lincoln High class of 2016 reunion!\n\nDate: August 15, 2026\nLocation: McMenamins Kennedy School\nTickets: $75/person (includes dinner + open bar)\n\nRSVP by June 1st.\n\nHope to see you there!\nReunion Committee",
     "sender": "reunion@lincolnhigh2016.org", "recipient": "jordan@gmail.com",
     "timestamp": "2025-11-20T12:00:00", "category": "personal_email", "modality": "email"},

    {"content": "Subject: Your Mortgage Pre-Approval — Approved!\n\nDear Jordan Chen and Riley Park,\n\nCongratulations! You have been pre-approved for a mortgage loan:\n\n- Loan Amount: Up to $550,000\n- Type: 30-year fixed\n- Rate: 5.875% (as of 08/15/2025)\n- Monthly Payment (est.): $3,254 (at $500k)\n- Down Payment: 20% required\n- Pre-approval valid through: November 15, 2025\n\nPlease note this is based on:\n- Combined income: $295,000/year\n- Credit scores: Jordan 782, Riley 768\n- DTI ratio: 28%\n\nBest regards,\nMark Thompson\nLoan Officer, Austin Community Credit Union",
     "sender": "mthompson@austincu.com", "recipient": "jordan@gmail.com",
     "timestamp": "2025-08-20T09:00:00", "category": "personal_email", "modality": "email"},

    {"content": "Subject: Re: Japanese Restaurant Recommendations\n\nJordan,\n\nHere are my recs for your Japan trip (when you eventually go!):\n\nTokyo:\n- Tsuta (Michelin star ramen)\n- Sukiyabashi Jiro (if you can get in — book 3 months ahead)\n- Shibuya Nonbei Yokocho (tiny bar alley, amazing)\n\nKyoto:\n- Kikunoi (kaiseki, mind-blowing)\n- Nishiki Market (street food heaven)\n\nOsaka:\n- Dotombori for street food\n- Kushikatsu Daruma (deep fried everything)\n\nBook ryokans early! Traditional inns fill up fast.\n\nSam",
     "sender": "sam.torres@gmail.com", "recipient": "jordan@gmail.com",
     "timestamp": "2025-12-20T14:00:00", "category": "personal_email", "modality": "email"},

    # Investor update emails
    {"content": "Subject: Monthly Investor Update — September 2025\n\nHi Board & Investors,\n\nSeptember update:\n\n**Metrics:**\n- MRR: $82,000 (+22% MoM)\n- ARR run rate: $984,000\n- Customers: 13\n- Facilities: 36\n- Net Revenue Retention: 142%\n- Monthly burn: $95,000\n- Runway: 24 months\n\n**Highlights:**\n- Closed 2 new enterprise customers (Palisade Manufacturing, Texas Instruments)\n- Scope 3 model accuracy reached 89.1%\n- Retained Aisha Rahman (countered Google offer)\n- WeWork Houston satellite office opened for Rachel's sales team\n\n**Lowlights:**\n- Lost 2 prospects to EcoTrace on price\n- Engineering hiring slower than expected (2 open roles)\n- Need to start SOC 2 Type 2 renewal process\n\n**Personal:**\n- Bought a house! Closing October 15\n- Health is better — therapy helping, back in the gym\n- Planning to propose to Riley (keep this confidential 😄)\n\nBest,\nJordan",
     "sender": "jordan@carbonsense.io", "recipient": "investors@carbonsense.io",
     "timestamp": "2025-10-01T08:00:00", "category": "work_email", "modality": "email"},

    {"content": "Subject: CarbonSense — Press Feature in TechCrunch\n\nTeam,\n\nWe got featured in TechCrunch! Article title: \"CarbonSense raises $10M to bring real-time emissions tracking to manufacturers\"\n\nKey quotes they used:\n- \"96% accuracy on scope 1 emissions\" (from our press release)\n- \"The only platform offering real-time scope 3 estimation\" (Nina's quote)\n- \"Zero customer churn since launch\" (Maria from Meridian confirmed)\n\nThe article also mentions EcoTrace as a competitor but positions us favorably.\n\nGreat coverage for the team!\n\nJordan",
     "sender": "jordan@carbonsense.io", "recipient": "team@carbonsense.io",
     "timestamp": "2025-09-05T16:00:00", "category": "work_email", "modality": "email"},

    # Conference/event emails
    {"content": "Subject: Speaker Invitation — Climate Tech Summit 2025\n\nDear Jordan,\n\nWe'd like to invite you to speak at the Climate Tech Summit in San Francisco, November 14-15, 2025.\n\nProposed session: \"Real-time Emissions Monitoring: From Prototype to Production\"\nFormat: 30-minute keynote + 15-minute Q&A\nAudience: ~500 climate tech professionals\n\nWe'll cover travel and accommodation. Honorarium: $2,500.\n\nPlease confirm by September 15.\n\nBest,\nClimate Tech Summit Committee",
     "sender": "speakers@climatetechsummit.com", "recipient": "jordan@carbonsense.io",
     "timestamp": "2025-09-01T12:00:00", "category": "work_email", "modality": "email"},
]

new_messages.extend(more_emails)

# ================================================
# BATCH 3: More OCR data (~80)
# ================================================

more_ocr = [
    # Monthly expenses OCR
    {"content": "[OCR: Receipt] Whole Foods Austin — Date: 08/03/2024\nOrganic chicken $14.99\nKale bunch $3.99\nAvocados x4 $5.96\nOat milk (Oatly) $5.49\nProtein bars (KIND) x2 $7.98\nBiscuit treats (Blue Buffalo) $12.99\nTotal: $51.40\nPayment: Visa ending 4821",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-08-03T12:00:00",
     "category": "ocr", "modality": "ocr_receipt"},

    {"content": "[OCR: Receipt] Starbucks Reserve — Date: 09/01/2024\nLatte $6.50\nCroissant $4.00\nTotal: $10.50\nTip: $2.00\nPayment: Amex ending 9012\nNote: Meeting with Sam about quitting",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-09-01T09:30:00",
     "category": "ocr", "modality": "ocr_receipt"},

    {"content": "[OCR: Receipt] COTA — Circuit of the Americas\nDate: 10/27/2024\nGeneral Admission x3: $450.00\nPaddock passes x3 (upgrade): $600.00\nParking: $40.00\nTotal: $1,090.00\nPayment: Visa ending 4821\nNote: Sam's birthday gift to Jordan",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-10-27T08:00:00",
     "category": "ocr", "modality": "ocr_receipt"},

    {"content": "[OCR: Receipt] Home Depot Austin — Date: 10/20/2025\nWeber Spirit II E-310 Gas Grill: $449.00\nPropane tank: $49.99\nGrill cover: $39.99\nGrill tools set: $29.99\nTotal: $568.97\nPayment: Visa ending 4821\nNote: New house grill setup",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-10-20T14:00:00",
     "category": "ocr", "modality": "ocr_receipt"},

    {"content": "[OCR: Receipt] Veterinary Emergency Clinic of Austin\nDate: 12/15/2024\nEmergency exam — Biscuit (Corgi): $250.00\nX-ray (abdomen): $380.00\nFluid therapy: $120.00\nMedication (anti-nausea): $45.00\nTotal: $795.00\nPayment: Amex ending 9012\nDiagnosis: Foreign body ingestion (chicken bone). No surgery needed. Monitor 48 hours.",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-12-15T22:00:00",
     "category": "ocr", "modality": "ocr_receipt"},

    # Financial OCR
    {"content": "[OCR: Screenshot] Mercury Bank — CarbonSense Inc.\nDate: June 30, 2025\nChecking: $1,104,287.00\nBurn rate (3-month avg): $68,400/month\nRunway: ~16 months\nMRR deposits: $67,000\nPayroll (June): $52,300\nAWS: $8,700\nWeWork: $7,600\nMisc: $4,100",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-06-30T08:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    {"content": "[OCR: Screenshot] Mercury Bank — CarbonSense Inc.\nDate: September 30, 2025\nChecking: $10,847,292.00 (includes Series A deposit)\nBurn rate (3-month avg): $95,000/month\nRunway: ~24 months\nMRR deposits: $82,000\nPayroll (Sep): $78,500\nAWS: $11,200\nWeWork: $7,600\nWeWork Houston: $3,600\nMisc: $5,800",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-09-30T08:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    {"content": "[OCR: Document] Jordan Chen — Personal Finance Summary 2025\nSalary (CarbonSense): $120,000/year\nRiley's stipend (UT): $28,000/year\nCombined gross: $148,000\nMortgage payment: $3,254/month\nCar payment (Rivian R1S): $892/month\nStudent loans (Riley): $340/month\nInsurance (health): $680/month\n401k contribution: $23,000/year\nSavings rate: ~15%",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-12-31T10:00:00",
     "category": "ocr", "modality": "ocr_document"},

    # Health/fitness OCR
    {"content": "[OCR: Screenshot] Apple Health — October 2024\nAvg Resting Heart Rate: 64 bpm\nAvg Sleep: 7.2 hours\nSteps/day: 8,500\nWorkouts: 12 (8 gym, 4 runs)\nVO2 Max estimate: 42 ml/kg/min\nWeight: 178 lbs\nNote: Best health metrics in months",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-10-31T06:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    {"content": "[OCR: Screenshot] Apple Health — December 2025\nAvg Resting Heart Rate: 66 bpm\nAvg Sleep: 7.0 hours\nSteps/day: 7,200\nWorkouts: 10 (6 gym, 3 runs, 1 yoga)\nVO2 Max estimate: 44 ml/kg/min\nWeight: 175 lbs\nNote: Recovery trend — better than July crisis. Therapy + boundaries working.",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-12-31T06:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    # App screenshots
    {"content": "[OCR: Screenshot] Robinhood Portfolio — December 31, 2024\nTotal value: $12,847\nHoldings: VOO (S&P 500) $8,200, QCLN (Clean Energy ETF) $3,100, TSLA $1,547\nYear return: +14.2%\n401k (Traditional IRA): $52,419",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-12-31T20:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    {"content": "[OCR: Screenshot] Zillow — Saved Listing\n2847 Chicon St, Austin TX 78702\n4 bed / 2 bath / 1,850 sq ft\nLot: 0.18 acres\nBuilt: 1962, renovated 2021\nListing price: $495,000\nEstimated monthly: $3,254 (20% down, 5.875%)\nSchool district: Austin ISD\nWalk score: 82\nBike score: 91\nDays on market: 21",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-08-30T10:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    # Biscuit's records
    {"content": "[OCR: Document] Thrive Veterinary — Annual Exam\nPatient: Biscuit (Pembroke Welsh Corgi)\nDate: September 15, 2025\nWeight: 30.1 lbs (goal: 28 lbs)\nHeart: Normal\nTeeth: Grade 1 tartar buildup — recommend dental cleaning\nNotes: Biscuit is overweight. Owner reports increased treat consumption since moving to house with large yard (neighbors also giving treats). Recommended: reduce to 1 cup food 2x/day, limit treats to 2/day.",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-09-15T15:00:00",
     "category": "ocr", "modality": "ocr_document"},

    # Work dashboard OCR
    {"content": "[OCR: Screenshot] CarbonSense Dashboard — September 2025\nActive Customers: 13\nActive Facilities: 36\nMRR: $82,000\nScope 1 Avg Accuracy: 95.8%\nScope 2 Avg Accuracy: 92.7%\nScope 3 Avg Accuracy: 89.1% (beta, 5 customers)\nAPI uptime: 99.97%\nAvg query time: 47ms (ClickHouse)\nData points processed today: 2,847,291",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-09-30T17:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    {"content": "[OCR: Screenshot] LinkedIn — CarbonSense Company Page Stats\nFollowers: 2,847 (up 340% YoY)\nJob applicants this month: 89\nTechCrunch article views: 45,200\nMost popular post: Jordan's thread on scope 3 methodology (12K impressions)\nEmployee count: 14",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-10-01T09:00:00",
     "category": "ocr", "modality": "ocr_screenshot"},

    # House inspection OCR
    {"content": "[OCR: Document] Home Inspection Report — 2847 Chicon St\nInspector: Mike Reeves, Austin Home Inspections\nDate: September 5, 2025\n\nMajor findings:\n- Roof: Good condition, ~5 years remaining life\n- Foundation: Minor crack in garage slab (cosmetic, not structural)\n- HVAC: 3-year-old Trane unit, well maintained\n- Plumbing: Copper pipes, good pressure\n- Electrical: 200 amp panel, up to code\n\nMinor findings:\n- Kitchen faucet drips\n- Two windows need resealing\n- Fence gate latch broken\n\nOverall: PASS — recommended for purchase",
     "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-09-05T14:00:00",
     "category": "ocr", "modality": "ocr_document"},
]

new_messages.extend(more_ocr)

# ================================================
# BATCH 4: More notes/memos (~30)
# ================================================

more_notes = [
    {"content": "[Note] First week as a founder — reflections\nJuly 29, 2024\n- Terrifying but liberating\n- No safety net feels both scary and motivating\n- Dev and I work well together — complementary skills (me: product/biz, him: engineering)\n- Need to establish routines or I'll burn out\n- Riley is being incredibly supportive\n- Biggest fear: what if we fail and I wasted my savings?",
     "sender": "jordan", "recipient": "self", "timestamp": "2024-07-29T23:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] Meeting notes — Nina Vasquez (Elevation VC)\nNov 20, 2024 at Epoch Coffee\n- She's been in climate VC for 8 years\n- Portfolio includes EcoTrace (potential competitor/acquirer)\n- Impressed by our pilot accuracy numbers\n- She says our TAM is bigger than we think — scope 3 mandates coming\n- Application deadline Jan 15. Need: deck, financials, pilot data, demo\n- She mentioned she writes $500K-2M checks\n- Vibe: genuine, not just pattern-matching. Actually understands the science",
     "sender": "jordan", "recipient": "self", "timestamp": "2024-11-20T12:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] Therapy session notes — Dr. Choi #1\nJuly 22, 2025\n- Identified: I have difficulty delegating. I try to do everything myself\n- Pattern: work expands to fill all available time. No boundaries = no personal life\n- Homework: implement 7pm hard stop for 2 weeks. Track compliance\n- Discussion about anxiety symptoms: chest tightness is classic stress response\n- Next session: August 5",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-07-22T16:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] Therapy session notes — Dr. Choi #5\nSeptember 16, 2025\n- 7pm boundary is working! 80% compliance\n- Riley reports feeling more connected\n- Explored: why do I tie self-worth to company performance?\n- Insight: growing up with immigrant parents, achievement = love. Need to decouple\n- Started mindfulness meditation (Headspace app, 10 min/morning)\n- RHR down from 72 to 68. Sleep up from 5.8 to 6.5 hours\n- Next session: September 30",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-09-16T16:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] CarbonSense Tech Stack — December 2025\nBackend:\n- Go (API layer, auth, billing, webhooks) — rewritten from Python May 2025\n- Python (ML inference, data processing pipelines)\n- gRPC between Go and Python services\n\nDatabases:\n- PostgreSQL (users, auth, billing, application data)\n- ClickHouse (time series sensor data, emissions data) — migrated from Postgres May 2025\n- Redis (caching, rate limiting)\n\nML:\n- Scope 1 model: XGBoost + custom features (96.1% accuracy)\n- Scope 2 model: ensemble (XGBoost + linear) + eGRID data (92.7%)\n- Scope 3 model: Graph Attention Network on partial supply chain graphs (89.1%)\n- All models served via FastAPI + uvicorn\n\nInfra:\n- AWS (us-east-1 primary, eu-west-1 for European expansion)\n- ECS for containers, S3 for data lake\n- CloudFront CDN\n- Datadog monitoring\n\nFrontend:\n- React 18 + TypeScript\n- Vite\n- TailwindCSS\n- D3.js for emissions visualizations",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-12-15T10:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] House renovation ideas — 2847 Chicon St\n- Paint: warm white walls, dark green accent wall in living room\n- Kitchen: the backsplash is dated. subway tile replacement?\n- Guest room: set up for mom and dad visits\n- Backyard: dog run area for biscuit, raised garden beds for riley, grill station\n- Office: convert 4th bedroom to home office. standing desk, good monitor\n- Budget: $15,000 max. Prioritize backyard since that's why we bought this house",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-10-18T21:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] Books Read 2025\n1. The Hard Thing About Hard Things — Ben Horowitz ⭐⭐⭐⭐⭐\n2. Zero to One — Peter Thiel ⭐⭐⭐⭐\n3. Measure What Matters — John Doerr ⭐⭐⭐\n4. The Lean Startup — Eric Ries ⭐⭐⭐ (basic but useful)\n5. Thinking, Fast and Slow — Kahneman ⭐⭐⭐⭐⭐\n6. The Body Keeps the Score — Van der Kolk ⭐⭐⭐⭐ (Dr. Choi recommended)\n7. Atomic Habits — James Clear ⭐⭐⭐⭐\n8. How to Win Friends and Influence People — Carnegie ⭐⭐⭐\n9. The Innovator's Dilemma — Christensen ⭐⭐⭐⭐\n10. Drawdown — Paul Hawken ⭐⭐⭐⭐⭐ (essential for climate tech founders)\nGoal was 20 books. Only hit 10. Better than 0.",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-12-31T21:00:00",
     "category": "note", "modality": "note"},

    {"content": "[Note] Proposal plan\n- Ring: Vintage art deco, $4,200, Fredericksburg estate sale. Platinum, 1.2ct\n- When: After Riley's graduation (May 17, 2026)\n- Where: Lady Bird Lake at sunset. Our first date spot.\n- Who knows: Sam, Lily. NOT parents yet (mom can't keep a secret)\n- Backup plan: if weather is bad, the rooftop at Hotel San José\n- Speech: keep it short. Tell her she's my home. The house is just walls without her.\n- Photographer: Sam will hide and take photos (he's actually good with a camera)",
     "sender": "jordan", "recipient": "self", "timestamp": "2025-12-31T23:30:00",
     "category": "note", "modality": "note"},
]

new_messages.extend(more_notes)

# ================================================
# BATCH 5: Calendar events (~20)
# ================================================

more_calendar = [
    {"content": "[Calendar] Dataflux Last Day\nDate: July 29, 2024\nNotes: 3 years at the company. Exit interview at 2pm. Turn in laptop and badge.",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2024-07-28T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] CarbonSense Board Meeting — Q3\nDate: October 1, 2025, 2:00 PM\nLocation: WeWork Austin, Conference Room A\nAttendees: Jordan, Dev, Nina (Elevation), Priya Mehta (Khosla designee)\nAgenda: Series A deployment, EcoTrace response, European expansion",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-09-25T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] COTA F1 Grand Prix\nDate: October 27, 2024\nTickets: 3 (Jordan, Sam, Jake)\nPaddock passes (Sam's birthday gift)\nMeet at COTA parking lot at 8am",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2024-10-25T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Biscuit — Vet Appointment\nDate: March 20, 2025, 4:00 PM\nLocation: Thrive Veterinary, Burnet Road\nType: Annual vaccines (Rabies + DHPP)\nNotes: Riley can't go — Jordan taking him",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-03-18T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Climate Tech Summit — San Francisco\nDate: November 14-15, 2025\nLocation: Moscone Center\nRole: Keynote Speaker\nSession: 'Real-time Emissions Monitoring: From Prototype to Production'\nFlight: AA 1247, Nov 13 AUS→SFO, 2:15pm\nHotel: Marriott Union Square (2 nights)\nReturn: AA 982, Nov 15 SFO→AUS, 6:00pm",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-11-01T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] House Closing — 2847 Chicon St\nDate: October 15, 2025, 10:00 AM\nLocation: Capital Title, 1221 S Congress Ave\nBring: ID, cashier's check ($99,000 down payment), proof of insurance\nAttendees: Jordan, Riley, Mark Thompson (lender), Sarah Kim (realtor)",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-10-10T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Housewarming Party\nDate: November 22, 2025, 4:00 PM\nLocation: 2847 Chicon St (our new house!)\nGuests: Sam (+Maya), Jake, Lily, Dev, Aisha, Rachel\nJordan: grill duty\nSam: brisket\nRiley: sides and drinks\nLily: dessert",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-11-15T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Dr. Choi — Therapy\nRecurring: Every other Tuesday, 3:00 PM\nLocation: 4301 W William Cannon Dr, Suite 200\nStarted: July 22, 2025\nInsurance: Aetna, $30 copay",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-07-20T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Parents Visit Austin\nDate: February 15-22, 2026\nArrival: Alaska Airlines, 2:15 PM\nStaying at: our house (guest room)\nPlanned activities: show them the office, dinner at Uchi, Zilker Park, meet Lily",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2026-01-05T08:00:00",
     "category": "calendar", "modality": "calendar"},

    {"content": "[Calendar] Portland High School Reunion\nDate: August 15, 2026\nLocation: McMenamins Kennedy School, Portland OR\nTickets: 2 (Jordan + Riley)\nNotes: 10 year reunion. Class of 2016.",
     "sender": "calendar", "recipient": "jordan", "timestamp": "2025-12-01T08:00:00",
     "category": "calendar", "modality": "calendar"},
]

new_messages.extend(more_calendar)

# ================================================
# BATCH 6: Rachel (VP Sales) conversations (~20)
# ================================================

rachel_convos = [
    ("2025-08-15T09:00:00", "rachel", "jordan", "jordan first week done. i've mapped out 40 target accounts. focusing on manufacturing companies above $500M revenue with EPA reporting requirements"),
    ("2025-08-15T09:05:00", "jordan", "rachel", "amazing rachel. that's exactly the ICP. how's the pipeline looking?"),
    ("2025-08-15T09:10:00", "rachel", "jordan", "3 demos scheduled next week. texas instruments, dow chemical austin facility, and a surprise — boeing's sustainability team reached out after the techcrunch article"),
    ("2025-09-01T14:00:00", "rachel", "jordan", "closed texas instruments! $5k/facility x 4 facilities = $20k MRR. 2 year contract"),
    ("2025-09-01T14:05:00", "jordan", "rachel", "RACHEL. $20k MRR in your first month?? you're already paying for yourself"),
    ("2025-09-01T14:10:00", "rachel", "jordan", "this product sells itself honestly. the accuracy numbers close the deal. i just have to get us in the room"),
    ("2025-10-01T10:00:00", "rachel", "jordan", "bad news. lost the boeing deal to ecotrace. they came in at $2k/facility. we were at $5k"),
    ("2025-10-01T10:05:00", "jordan", "rachel", "ugh. did they even evaluate accuracy?"),
    ("2025-10-01T10:10:00", "rachel", "jordan", "no. procurement made the decision. sustainability team wanted us but couldn't justify 2.5x price to finance"),
    ("2025-10-01T10:15:00", "jordan", "rachel", "this is going to keep happening. we need a 'total cost of ownership' calculator. show that our accuracy saves them money on carbon credits and compliance risk"),
    ("2025-10-01T10:20:00", "rachel", "jordan", "brilliant. i'll work with omar on that. also we should get case studies from meridian and lone star. real ROI numbers"),
    ("2025-11-10T11:00:00", "rachel", "jordan", "the houston satellite office is working great. had 3 in-person meetings this week. gulf coast refinery companies prefer face-to-face"),
    ("2025-11-10T11:05:00", "jordan", "rachel", "good call on the houston office. what's the pipeline looking like for Q1?"),
    ("2025-11-10T11:10:00", "rachel", "jordan", "pipeline: $380k in qualified opportunities. if we close 40% that's $152k new ARR. i think we can hit 50% with the scope 3 differentiator"),
    ("2025-12-10T09:00:00", "rachel", "jordan", "jordan the KlimaSync partnership is getting inbound from europe. got 5 demo requests from german manufacturers this week alone"),
    ("2025-12-10T09:05:00", "jordan", "rachel", "EU CSRD mandate is driving demand exactly like nina predicted. can you prioritize the european pipeline?"),
]

for ts, sender, recipient, content in rachel_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# ================================================
# BATCH 7: Dr. Woo (mentor) conversations (~10)
# ================================================

drwoo_convos = [
    ("2025-04-15T14:00:00", "jordan", "dr_woo", "dr woo, quick question. aisha wants to publish a paper on our scope 3 methodology. any concerns about IP?"),
    ("2025-04-15T14:30:00", "dr_woo", "jordan", "great question. publish the methodology, keep the training data and specific model weights proprietary. that's standard practice. the publication actually strengthens your IP position"),
    ("2025-06-10T10:00:00", "jordan", "dr_woo", "dr woo your advice on demo day was gold. 'lead with the problem, not the solution' — same thing nina said. i restructured the whole pitch"),
    ("2025-06-10T10:30:00", "dr_woo", "jordan", "scientists and engineers always want to show their work. investors want to see the impact. you're learning the difference 😊"),
    ("2025-09-01T11:00:00", "jordan", "dr_woo", "series A closed! $10M from khosla. thank you for introducing us to aisha. she's been transformative"),
    ("2025-09-01T11:30:00", "dr_woo", "jordan", "congratulations jordan. well deserved. now the real work begins — scaling is harder than building. don't forget that"),
    ("2025-12-20T15:00:00", "jordan", "dr_woo", "chen wei's ICML paper is incredible. the scope 3 improvements are directly usable. thank you for the sponsorship partnership"),
    ("2025-12-20T15:30:00", "dr_woo", "jordan", "chen wei did the work. but yes, the partnership model works beautifully. i have another student starting in january who could work on European emission factors"),
]

for ts, sender, recipient, content in drwoo_convos:
    new_messages.append({
        "content": content,
        "sender": sender, "recipient": recipient,
        "timestamp": ts, "category": "text_message", "modality": "imessage"
    })

# Combine all
messages.extend(new_messages)
messages.sort(key=lambda x: x["timestamp"])

# Stats
print(f"\nFinal dataset: {len(messages)} messages")
print(f"\nBy modality:")
modalities = {}
for m in messages:
    mod = m.get("modality", "unknown")
    modalities[mod] = modalities.get(mod, 0) + 1
for mod, count in sorted(modalities.items(), key=lambda x: -x[1]):
    print(f"  {mod}: {count}")

print(f"\nBy category:")
categories = {}
for m in messages:
    cat = m["category"]
    categories[cat] = categories.get(cat, 0) + 1
for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

print(f"\nBy sender (top 15):")
senders = {}
for m in messages:
    s = m["sender"]
    senders[s] = senders.get(s, 0) + 1
for s, count in sorted(senders.items(), key=lambda x: -x[1])[:15]:
    print(f"  {s}: {count}")

print(f"\nTimeline: {messages[0]['timestamp']} to {messages[-1]['timestamp']}")

# Save
with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json", "w") as f:
    json.dump(messages, f, indent=2)
print(f"\nSaved to synthetic_v2_messages.json")
