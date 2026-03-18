"""
Expansion batch 3 — push from ~694 to 1000+ messages.
More edge cases, multi-hop scenarios, ambiguity, and noise.
"""

import json

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

# ============================================================
# MULTI-HOP REASONING SCENARIOS
# Facts spread across multiple messages that need connecting
# ============================================================

# Multi-hop 1: Dr. Woo → Aisha → Chen Wei → ICML paper → Scope 3 improvement
msg("2025-02-25T10:00:00", "dev", "jordan", "dr woo wants to schedule the first advisory call. she mentioned her student chen wei is starting research on supply chain emissions modeling")
msg("2025-02-25T10:05:00", "jordan", "dev", "perfect timing. that's exactly what aisha will need help with. can you cc aisha on the intro?")
msg("2025-06-01T14:00:00", "aisha", "jordan", "jordan chen wei's synthetic data augmentation technique is incredible. he generated 50,000 training samples from just 2,000 real data points using a VAE approach. our model accuracy jumped from 84.7 to 88.9")
msg("2025-09-01T10:00:00", "aisha", "jordan", "chen wei submitted the paper to ICML! title: 'Real-time Scope 3 Emissions Estimation via Partial Supply Chain Graphs'. he credits carbonsense in the acknowledgments")

# Multi-hop 2: Riley's career → therapy recommendation → Jordan's therapy → better relationship
msg("2024-09-01T19:00:00", "riley", "jordan", "my counseling psych professor dr martinez recommended a book called 'burnout' by emily nagoski. she says founders are especially prone to it")
msg("2025-07-18T20:00:00", "riley", "jordan", "jordan i think you should see a therapist. dr martinez recommended someone — dr linda choi on william cannon. she specializes in high-achiever burnout")
msg("2025-08-05T17:00:00", "jordan", "riley", "you were right about therapy. dr choi is amazing. she helped me understand why i can't stop working — it's tied to how i grew up")
msg("2025-09-20T19:00:00", "jordan", "riley", "therapy update: dr choi says i've made real progress. my boundaries are better. riley you literally saved my health by pushing me to go")

# Multi-hop 3: Sam's financial knowledge → CarbonSense advice → Sam's startup idea
msg("2024-08-10T14:00:00", "sam", "jordan", "dude you need to set up a SAFE for angel investors, not a priced round. YC's standard SAFE is free to use and simpler than a series seed")
msg("2024-08-10T14:05:00", "jordan", "sam", "how do you know about SAFEs? you work in sales not finance")
msg("2024-08-10T14:10:00", "sam", "jordan", "i've been reading 'venture deals' by brad feld. secretly want to start my own thing someday. just absorbing everything")
msg("2025-10-01T20:00:00", "sam", "jordan", "ok i'm serious about the fintech idea. what if there was a carbon credit marketplace built into corporate banking? like, every time a company makes a purchase, it auto-offsets")
msg("2025-10-01T20:05:00", "jordan", "sam", "dude that's actually brilliant. nina just asked us to build a marketplace and we said no. but as a SEPARATE company? there's a play there")

# ============================================================
# AMBIGUITY AND ENTITY DISAMBIGUATION
# Same names, similar contexts, requires precision
# ============================================================

# Two Marcus problem (gym buddy vs lily's ex)
msg("2024-08-05T07:00:00", "jordan", "jake", "jake you know marcus from the gym right? he's been doing those crazy olympic lifts. asked if he could join us")
msg("2024-08-05T07:05:00", "jake", "jordan", "marcus johnson? yeah he's a beast. 225 clean and jerk. sure bring him")
msg("2024-11-29T12:00:00", "jordan", "lily", "lily how's marcus? he seemed nice at thanksgiving. different vibe from gym marcus lol")
msg("2024-11-29T12:05:00", "lily", "jordan", "haha yeah my marcus is more chill. gym marcus sounds intense. marcus and i are good, thinking about moving in together")

# Two Rachel problem (VP Sales vs college friend)
msg("2025-04-20T18:00:00", "riley", "jordan", "rachel from college called. she's coming to austin next month for a conference. dinner?")
msg("2025-04-20T18:05:00", "jordan", "riley", "wait which rachel? not rachel torres from the sales candidate list right?")
msg("2025-04-20T18:10:00", "riley", "jordan", "no lol. rachel kim. from our study group at UO. she's a doctor now in seattle")
msg("2025-04-20T18:15:00", "jordan", "riley", "oh rachel kim! yes of course. let's do dinner at odd duck")

# Mike Chen (employee) vs Jordan's cousin Mike
msg("2025-10-05T12:00:00", "jordan", "dev", "dev mike chen is starting monday right? the new AE on rachel's team")
msg("2025-10-05T12:05:00", "dev", "jordan", "yeah. and lol your cousin is also mike chen right? that's going to be confusing in emails")
msg("2025-10-05T12:10:00", "jordan", "dev", "haha yeah cousin mike is in SF doing AI stuff at anthropic. totally different mike chen")

# ============================================================
# NEGATION AND CORRECTED INFORMATION
# Things that are NOT true — tests if systems handle negation
# ============================================================

msg("2025-01-20T14:00:00", "jordan", "dev", "dev are we going to raise a series A from sequoia?")
msg("2025-01-20T14:05:00", "dev", "jordan", "way too early. let's focus on the elevation seed first. series A is probably a year away")
msg("2025-03-10T10:00:00", "jordan", "sam", "no i'm not hiring sam as a full time employee. he's just doing part time sales consulting until we can afford a real VP sales")
msg("2025-05-20T11:00:00", "dev", "jordan", "should we use kubernetes for deployment?")
msg("2025-05-20T11:05:00", "jordan", "dev", "definitely not. k8s is overkill for our stage. ECS is fine. let's not over-engineer")
msg("2025-07-10T09:00:00", "jordan", "nina", "nina should we acquire ecotrace? someone mentioned they might be open to it")
msg("2025-07-10T09:05:00", "nina", "jordan", "absolutely not. they raised $40M, they're not selling for less than $100M. and we don't need their tech — ours is better. focus on winning, not buying")

# ============================================================
# EMOTIONAL/SENTIMENT DATA
# Tests personality and emotional understanding
# ============================================================

msg("2024-07-29T22:00:00", "jordan", "riley", "last day at dataflux today. walked out of the building and just stood in the parking lot for 10 minutes. three years of my life. weird feeling")
msg("2024-07-29T22:05:00", "riley", "jordan", "it's ok to feel sad about it. you can be excited about the future and still grieve what you're leaving behind")
msg("2024-07-29T22:10:00", "jordan", "riley", "when did you get so wise? oh right, counseling psych student. you practice on me")
msg("2024-07-29T22:12:00", "riley", "jordan", "guilty as charged 😂 but seriously, i'm proud of you. this is brave")

msg("2025-02-10T17:00:00", "jordan", "riley", "riley i'm shaking. we just got into elevation. $1.5M. i can't believe this is real")
msg("2025-02-10T17:02:00", "riley", "jordan", "JORDAN. i'm so proud of you. you worked so hard for this. come home, i'm opening the fancy wine")

msg("2025-07-03T22:00:00", "jordan", "sam", "sam i fucked up. missed my anniversary dinner with riley. again. she's right, i'm never present")
msg("2025-07-03T22:05:00", "sam", "jordan", "jordan you need to fix this. riley is the most patient person alive but even she has limits. the company means nothing if you lose her")
msg("2025-07-03T22:10:00", "jordan", "sam", "i know. starting therapy. for real this time. not just thinking about it")

msg("2025-10-16T23:00:00", "jordan", "sam", "sleeping in our house for the first time tonight. air mattress. no furniture. but sam... this is ours. riley and i own a home")
msg("2025-10-16T23:05:00", "sam", "jordan", "🏠 you've come a long way from that shitty studio apartment in portland")

# ============================================================
# PROCEDURAL/HOW-TO INFORMATION
# Tests for retrieving instructions and processes
# ============================================================

msg("2024-08-05T10:00:00", "jordan", "dev", "dev what's the deploy process? i want to document it")
msg("2024-08-05T10:05:00", "dev", "jordan", "1. push to main branch 2. github actions runs tests 3. if green, builds docker image 4. pushes to ECR 5. updates ECS task definition 6. rolling deploy with zero downtime. takes about 8 minutes end to end")
msg("2025-06-05T14:00:00", "jordan", "rachel", "rachel what's the sales process we should standardize?")
msg("2025-06-05T14:10:00", "rachel", "jordan", "1. SDR qualifies lead (BANT framework) 2. AE does discovery call (30 min) 3. technical demo with dev or aisha (45 min) 4. pilot proposal 5. 90 day pilot 6. annual contract. avg sales cycle: 4.5 months for enterprise")

# ============================================================
# PREFERENCES AND HABITS
# Personality data that memory systems should capture
# ============================================================

msg("2024-07-20T07:00:00", "jordan", "dev", "dev i need coffee before i can function. epoch coffee on north loop? they have the best oat milk latte in austin")
msg("2024-10-01T07:30:00", "jordan", "sam", "morning routine: wake up 6am, meditate 10 min (headspace app), gym or run, shower, breakfast (usually overnight oats or eggs), work by 8:30")
msg("2025-01-05T12:00:00", "jordan", "riley", "ok i've decided. i'm going vegetarian on weekdays. just weekdays. still eating mom's dumplings on weekends")
msg("2025-01-20T12:00:00", "jordan", "riley", "the weekday vegetarian thing lasted 2 weeks 😂 i caved when jake grilled those brisket tacos")
msg("2025-03-05T08:00:00", "jordan", "jake", "new running shoes: hoka clifton 9. game changer. my knees feel 10 years younger")
msg("2025-08-01T07:00:00", "jordan", "riley", "switched from headspace to insight timer for meditation. free and better guided sessions")
msg("2025-10-20T08:00:00", "jordan", "dev", "dev what podcast are you listening to? i need something for my runs")
msg("2025-10-20T08:05:00", "dev", "jordan", "all-in podcast for business, huberman for health, and acquired for deep dives on companies. also lex fridman but only the ones under 2 hours")
msg("2025-11-01T19:00:00", "jordan", "riley", "riley i think we should get a second dog. biscuit needs a friend. he gets lonely when we're both at work")
msg("2025-11-01T19:05:00", "riley", "jordan", "absolutely not. we just moved. biscuit is already 2 lbs overweight. let's get him back in shape first")
msg("2025-11-01T19:10:00", "jordan", "riley", "fair. but i'm not dropping this topic forever 😄")

# ============================================================
# MORE RANDOM DAILY NOISE (~50 msgs)
# ============================================================

msg("2024-07-18T12:00:00", "jordan", "riley", "traffic on 35 is insane. gonna be 30 min late. sorry")
msg("2024-07-18T12:05:00", "riley", "jordan", "take mopac instead. 35 is always a nightmare during lunch")
msg("2024-08-12T20:00:00", "jordan", "sam", "just started watching the bear on hulu. have you seen it?")
msg("2024-08-12T20:05:00", "sam", "jordan", "YES. carmy is so stressful to watch but you can't look away. season 2 is even better")
msg("2024-09-30T08:00:00", "riley", "jordan", "biscuit's paw is swollen. he was limping this morning. making a vet appointment")
msg("2024-09-30T12:00:00", "riley", "jordan", "vet said it's a bee sting. gave him benadryl. he's fine now. dramatic dog")
msg("2024-10-15T19:00:00", "jordan", "jake", "jake what gym are we at now? golds on lamar?")
msg("2024-10-15T19:05:00", "jake", "jordan", "yeah golds on south lamar. $35/month. can't beat it")
msg("2024-11-05T07:00:00", "jordan", "riley", "daylight savings sucks. it's dark at 5:30pm. biscuit doesn't understand why his walk is in the dark")
msg("2024-12-20T18:00:00", "jordan", "sam", "sam what's the best streaming deal right now? we're paying for netflix, hulu, and disney+ separately")
msg("2024-12-20T18:05:00", "sam", "jordan", "disney bundle. hulu + disney+ for $15/month. ditch netflix honestly, everything good is on hulu now")
msg("2025-01-10T07:00:00", "jordan", "riley", "it's 28 degrees in austin. 28. this is not what i signed up for")
msg("2025-01-10T07:05:00", "riley", "jordan", "biscuit refused to go outside. he stood at the door, looked at the cold, and walked back to bed")
msg("2025-02-01T12:00:00", "jordan", "dev", "dev there's a tech happy hour tonight at lazarus brewing. austin tech council. want to go?")
msg("2025-02-01T12:05:00", "dev", "jordan", "sure. free beer? i'm in. also good for networking. we need to find engineers")
msg("2025-03-14T12:00:00", "jordan", "riley", "happy pi day! made you a reservation at pie society on east 7th. all the pie you can eat")
msg("2025-03-14T12:05:00", "riley", "jordan", "you are the biggest nerd and i love you for it 🥧")
msg("2025-04-20T08:00:00", "jordan", "sam", "brutal allergies today. cedar season in austin is no joke. my eyes are on fire")
msg("2025-04-20T08:05:00", "sam", "jordan", "cedar fever is a rite of passage. you're not a real austinite until you've suffered through it. take zyrtec")
msg("2025-05-30T09:00:00", "jordan", "riley", "memorial day weekend plans? i was thinking float the guadalupe river")
msg("2025-05-30T09:05:00", "riley", "jordan", "YES. can we bring biscuit? he loved the water at barton springs")
msg("2025-05-30T09:10:00", "jordan", "riley", "corgis and rivers... could be interesting. he's basically a submarine with legs. let's try it")
msg("2025-07-04T11:00:00", "jordan", "lily", "lily first 4th of july in austin! you coming to the auditorium shores fireworks?")
msg("2025-07-04T11:05:00", "lily", "jordan", "can i bring my roommate? she doesn't know anyone in austin yet")
msg("2025-07-04T11:10:00", "jordan", "lily", "of course! the more the merrier. sam is bringing a cooler")
msg("2025-08-20T19:00:00", "jordan", "riley", "power went out again. ERCOT is the worst utility operator in america and it's not even close")
msg("2025-08-20T19:05:00", "riley", "jordan", "generator is running. biscuit is unphased. he's sleeping through it")
msg("2025-09-05T12:00:00", "jordan", "lily", "lily did you end up asking ben to coffee?")
msg("2025-09-05T12:05:00", "lily", "jordan", "NO i chickened out. what if he says no? we have to work together every day")
msg("2025-09-05T12:10:00", "jordan", "lily", "lily chen. you moved cities after a breakup. you can ask a boy to coffee. DO IT")
msg("2025-11-10T20:00:00", "jordan", "sam", "sam we just got the house internet set up. google fiber 2 gig. working from home is actually possible now")
msg("2025-11-10T20:05:00", "sam", "jordan", "2 gig?! i'm coming to YOUR house to work. my apartment has 100mbps and it drops twice a day")
msg("2025-12-10T18:00:00", "jordan", "riley", "riley i saw a puppy at the shelter today. accidentally. i wasn't looking. golden retriever mix. 4 months old")
msg("2025-12-10T18:05:00", "riley", "jordan", "jordan chen. no. we talked about this. biscuit first. he needs to lose 2 pounds")
msg("2025-12-10T18:10:00", "jordan", "riley", "you're right you're right. but the puppy had a little bandana...")
msg("2025-12-10T18:12:00", "riley", "jordan", "NO. ask me again in spring. MAYBE")

# ============================================================
# MORE OCR (shopping, health, tech)
# ============================================================

ocr("2024-08-12T14:00:00", "[OCR: Receipt] Amazon.com Order\nDate: 08/12/2024\nStanding desk (FlexiSpot E7) $549.99\nMonitor arm (AmazonBasics) $32.99\nUSB-C dock (CalDigit) $179.99\nTotal: $762.97\nPayment: Visa ending 4821\nShip to: 1847 E Riverside Dr Apt 4A, Austin TX 78741")

ocr("2024-10-27T20:00:00", "[OCR: Receipt] Whataburger — COTA Location\nDate: 10/27/2024\n3x Honey BBQ Chicken Strip Sandwich $29.97\n3x Lg Drink $8.97\n1x Apple Pie $2.99\nTotal: $41.93\nPayment: Visa ending 4821\nNote: Post-F1 celebration meal", "ocr_receipt")

ocr("2025-02-14T23:00:00", "[OCR: Receipt] Uchi Austin — Valentine's Day 2025\n2x Omakase Chef's Tasting $280.00\nSake flight (Dassai) $45.00\nDessert (mochi ice cream) $28.00\nSubtotal: $353.00\nTax: $29.00\nTip: $70.60 (20%)\nTotal: $452.60\nPayment: Amex ending 9012")

ocr("2025-05-01T10:00:00", "[OCR: Screenshot] Slack — #general channel\nJordan: Team — we hit $43K MRR! 🎉 That's 7 paying customers across 14 facilities. Thank you all for the incredible work.\nDev: 🚀🚀🚀\nAisha: Scope 3 beta ready for 3 of them!\nRachel: Pipeline has never looked better. Let's get to $100K by Demo Day.\nJordan: I love this team.", "ocr_screenshot")

ocr("2025-07-20T15:00:00", "[OCR: Document] Dr. Linda Choi, PhD — Clinical Psychology\nPatient: Jordan Chen\nDate: July 20, 2025\nDiagnosis: Adjustment Disorder with Anxiety (F43.22)\nTreatment: Cognitive Behavioral Therapy (CBT)\nFrequency: Biweekly\nInsurance: Aetna PPO\nCopay: $30\nNotes: Patient presents with work-related anxiety, sleep disruption, and relationship strain. High-functioning. Motivated for change.", "ocr_document")

ocr("2025-10-15T15:00:00", "[OCR: Document] Closing Statement — 2847 Chicon St\nBuyer: Jordan Chen & Riley Park\nProperty: 2847 Chicon St, Austin TX 78702\nPurchase Price: $495,000.00\nDown Payment (20%): $99,000.00\nLoan Amount: $396,000.00\nInterest Rate: 5.875% (30-year fixed)\nMonthly P&I: $2,343.00\nProperty Tax (est.): $583/month\nInsurance: $100/month\nTotal Monthly: $3,026.00\nClosing Costs: $12,847.00\nTotal Due at Closing: $111,847.00", "ocr_document")

ocr("2025-12-25T10:00:00", "[OCR: Receipt] Third Coast Coffee — Gift Subscription\nDate: 12/20/2025\nRecipient: Robert Chen (Dad)\n12-month subscription: Single Origin\nFrequency: Monthly (1 lb bag)\nPrice: $216.00 ($18/month)\nFirst shipment: January 2026\nPayment: Visa ending 4821", "ocr_receipt")

# ============================================================
# MORE NOTES
# ============================================================

note("2025-02-10T22:00:00", "[Note] Post-Elevation acceptance thoughts\nI just cried in the car for 20 minutes. Not sad crying — pure relief.\nDev and I started this in my apartment 7 months ago.\nWe've been living on savings and hope.\nNow we have $1.5M and real investors who believe in us.\n\nThings I need to remember:\n- Stay humble. This is the beginning, not the end.\n- Don't let the money change our culture. We're still scrappy.\n- Call mom more often. She worries.\n- Kiss Riley more. She's been so patient.\n- Pet Biscuit. He doesn't understand any of this but he's always happy to see me.")

note("2025-07-03T23:00:00", "[Note] Anniversary disaster\nMissed our 5th anniversary dinner for a Sequoia call.\nRiley was right — I prioritize work over everything.\nThis has to stop. Not 'I'll try to do better' — it has to STOP.\nTomorrow: finding a therapist. Riley's professor recommended Dr. Linda Choi.\nI refuse to lose the best person in my life because I can't manage my time.")

note("2025-12-28T22:00:00", "[Note] End of year letter to future self\nDear 2027 Jordan,\nIf you're reading this, remember:\n1. You almost burned out in 2025. Don't do it again.\n2. Riley is more important than any deal. Always.\n3. Biscuit doesn't care about ARR. Pet him.\n4. Therapy works. Keep going.\n5. Your team is everything. Dev, Aisha, Rachel — protect them.\n6. The goal was never money. It was impact. 42 facilities are emitting less because of you.\n7. Call your mom.\n\nLove, 2025 Jordan\n\nP.S. If you haven't proposed yet, WHAT ARE YOU WAITING FOR?")

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

senders = {}
for m in messages:
    s = m["sender"]
    senders[s] = senders.get(s, 0) + 1
print(f"\nUnique senders: {len(senders)}")
print(f"Timeline: {messages[0]['timestamp']} to {messages[-1]['timestamp']}")

# Compute some stats
timestamps = [m["timestamp"] for m in messages]
months = set(t[:7] for t in timestamps)
print(f"Months covered: {len(months)} ({min(months)} to {max(months)})")

with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json", "w") as f:
    json.dump(messages, f, indent=2)
print(f"\nSaved to synthetic_v2_messages.json")
