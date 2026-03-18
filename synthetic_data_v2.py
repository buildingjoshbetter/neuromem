"""
Massive Synthetic Dataset Generator v2
=======================================
Generates 1500+ messages simulating ~18 months of a person's life.
Covers: text messages, emails, OCR data, notes, calendar events.

Designed as a GENERALIST benchmark — not biased toward any architecture.
Tests: exact recall, semantic, temporal, entity, contradiction, multi-hop,
cross-modal, personality inference, OCR retrieval, consolidation.
"""

import json
import random
from datetime import datetime, timedelta

# ============================================================
# CHARACTER BIBLE — The person we're simulating data about
# ============================================================
# "Jordan Chen" — 28, software engineer turned founder
# Lives in Austin TX, started a climate-tech startup
# Has a dog named Biscuit (corgi), partner named Riley
# Co-founder: Dev Patel. Investor: Nina Vasquez.
# Best friend: Sam Torres. Sister: Lily Chen.
# Mom: Helen Chen. Dad: Robert Chen.
# Gym buddy: Jake Morrison. Ex-colleague: Aisha Rahman.
# Mentor: Dr. Patricia Woo.

def generate_dataset():
    messages = []

    # Timeline: July 2024 — December 2025 (18 months)
    base = datetime(2024, 7, 1)

    # ========================================
    # PHASE 1: EARLY DAYS (Jul-Sep 2024)
    # Jordan is still employed, side-hustling the startup
    # ========================================

    # -- Text messages --
    messages.extend([
        # Week 1: Setting the scene
        {"content": "hey sam you free for drinks tonight? need to talk through something",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-07-03T18:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yeah dude barton springs beer garden? 7pm?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2024-07-03T18:32:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "perfect. been thinking about leaving dataflux to go full time on this carbon tracking thing",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-07-03T18:35:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "wait for real? you've been talking about this for months. what changed?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2024-07-03T18:36:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "dev is in. he quit oracle last week. we have a working prototype and three companies want to pilot it",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-07-03T18:38:00",
         "category": "text_message", "modality": "imessage"},

        # Jordan tells his sister
        {"content": "lily don't tell mom and dad yet but i'm thinking about quitting my job to start a company",
         "sender": "jordan", "recipient": "lily", "timestamp": "2024-07-05T21:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "omg jordan!! what kind of company? are you sure??",
         "sender": "lily", "recipient": "jordan", "timestamp": "2024-07-05T21:02:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "carbon emissions tracking for manufacturing. like a fitbit for factories. dev and i have been building it nights and weekends for 6 months",
         "sender": "jordan", "recipient": "lily", "timestamp": "2024-07-05T21:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "that actually sounds amazing. mom is gonna freak tho lol",
         "sender": "lily", "recipient": "jordan", "timestamp": "2024-07-05T21:06:00",
         "category": "text_message", "modality": "imessage"},

        # Jordan and Dev discuss tech
        {"content": "dev i ran the prototype against the pilot data from meridian steel. accuracy is 94.2% on scope 1 emissions",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-07-08T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "nice. what about scope 2? that's where the grid data gets messy",
         "sender": "dev", "recipient": "jordan", "timestamp": "2024-07-08T10:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "scope 2 is at 87.6% but i think we can get it above 90 if we integrate the EPA eGRID dataset",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-07-08T10:08:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i'll work on the eGRID integration this weekend. also we should use postgres not sqlite for production",
         "sender": "dev", "recipient": "jordan", "timestamp": "2024-07-08T10:12:00",
         "category": "text_message", "modality": "imessage"},

        # Riley (partner) conversations
        {"content": "hey can you pick up biscuit from the groomer? i have a meeting til 6",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-07-10T15:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "already got him! he looks so fluffy. sending pics",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-07-10T15:35:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "omg his little face 😂 also riley i want to talk tonight about something important. about work",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-07-10T15:40:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "is everything ok? you're not getting fired are you",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-07-10T15:41:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "no lol the opposite. i want to quit. to go full time on carbonsense with dev",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-07-10T15:42:00",
         "category": "text_message", "modality": "imessage"},

        # Mom check-in
        {"content": "hi sweetie! just checking in. how's work? dad and i are planning thanksgiving already, will you and riley come to portland?",
         "sender": "mom", "recipient": "jordan", "timestamp": "2024-07-12T09:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "hey mom! work is good, really busy. yes we'll be there for thanksgiving for sure. how's dad's knee?",
         "sender": "jordan", "recipient": "mom", "timestamp": "2024-07-12T12:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "much better after the physical therapy! he's even doing his morning walks again. lily said she might bring her new boyfriend 👀",
         "sender": "mom", "recipient": "jordan", "timestamp": "2024-07-12T12:45:00",
         "category": "text_message", "modality": "imessage"},

        # Jake gym buddy
        {"content": "bro you hitting the gym today? leg day",
         "sender": "jake", "recipient": "jordan", "timestamp": "2024-07-14T06:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yeah 6:30am? trying to get back to squatting 315 by end of summer",
         "sender": "jordan", "recipient": "jake", "timestamp": "2024-07-14T06:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "let's go. also did you see the new pre-workout at HEB? gorilla mode. shit is insane",
         "sender": "jake", "recipient": "jordan", "timestamp": "2024-07-14T06:07:00",
         "category": "text_message", "modality": "imessage"},
    ])

    # -- Emails (Jul 2024) --
    messages.extend([
        {"content": "Subject: Re: CarbonSense Pilot Proposal\n\nHi Jordan,\n\nThanks for sending over the technical specs. Our sustainability team reviewed the proposal and we're impressed with the scope 1 accuracy numbers. We'd like to move forward with a 90-day pilot starting August 1st.\n\nA few questions:\n1. Can the system integrate with our existing SAP ERP?\n2. What's the data refresh frequency?\n3. Do you have SOC 2 compliance?\n\nLet's schedule a call this week.\n\nBest,\nMaria Gonzalez\nVP Sustainability, Meridian Steel",
         "sender": "maria.gonzalez@meridiansteel.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2024-07-15T11:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Re: Re: CarbonSense Pilot Proposal\n\nHi Maria,\n\nGreat news! Here are answers:\n\n1. Yes — we have an SAP connector in beta. It pulls from the MM and PP modules for materials and production data.\n2. Currently every 15 minutes via API polling. We're building real-time streaming for Q4.\n3. Not yet — we're starting the SOC 2 Type 1 process this month. Expected completion by October.\n\nHow's Thursday at 2pm CT for a call?\n\nBest,\nJordan Chen\nCo-founder, CarbonSense",
         "sender": "jordan@carbonsense.io", "recipient": "maria.gonzalez@meridiansteel.com",
         "timestamp": "2024-07-15T14:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Two weeks notice\n\nHi David,\n\nI'm writing to formally submit my resignation from Dataflux, effective July 29th. The past three years have been an incredible learning experience and I'm grateful for the mentorship and opportunities.\n\nI'm leaving to pursue a startup in the climate-tech space. I'll make sure all my projects are properly transitioned during my remaining time.\n\nThank you for everything.\n\nBest regards,\nJordan Chen",
         "sender": "jordan@dataflux.com", "recipient": "david.morrison@dataflux.com",
         "timestamp": "2024-07-16T09:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Fwd: Dataflux Exit — 401k Rollover Options\n\nJordan,\n\nAttached are your options for rolling over your Dataflux 401k ($47,382.19). You have 60 days to decide:\n\n1. Roll into new employer plan (N/A for you)\n2. Roll into Traditional IRA\n3. Roll into Roth IRA (tax event)\n4. Cash out (10% penalty + taxes — NOT recommended)\n\nI'd suggest option 2 given your situation. Let me know if you want to discuss.\n\nBest,\nCarla Huang, CFP\nAustin Financial Planning",
         "sender": "carla@austinfinancial.com", "recipient": "jordan@gmail.com",
         "timestamp": "2024-07-22T10:00:00", "category": "personal_email", "modality": "email"},
    ])

    # -- OCR Data (Jul 2024) --
    messages.extend([
        {"content": "[OCR: Receipt] HEB Mueller — Date: 07/14/2024\nGorilla Mode Pre-Workout $44.99\nChicken breast 3lb $12.49\nBrown rice 5lb $6.99\nBroccoli crowns $3.49\nGreek yogurt x4 $7.96\nBiscuit's dog food (Blue Buffalo) $52.99\nTotal: $128.91\nPayment: Visa ending 4821",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-07-14T11:30:00",
         "category": "ocr", "modality": "ocr_receipt"},

        {"content": "[OCR: Screenshot] Slack DM from Dev Patel\n\"just confirmed — meridian steel, lone star cement, and gulf coast plastics all want pilots. that's 3 paid pilots before we even launch. we should incorporate ASAP. talked to my lawyer, delaware c-corp is the way to go for vc fundraising later\"",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-07-18T16:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},

        {"content": "[OCR: Document] State of Delaware — Certificate of Incorporation\nCarbonSense Inc.\nIncorporated: July 25, 2024\nRegistered Agent: Harvard Business Services, Inc.\nAuthorized Shares: 10,000,000 Common\nIncorporator: Jordan Chen\nFile Number: 7892341",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-07-25T12:00:00",
         "category": "ocr", "modality": "ocr_document"},
    ])

    # ========================================
    # PHASE 2: EARLY STARTUP (Oct-Dec 2024)
    # Jordan quit, running CarbonSense full time
    # ========================================

    messages.extend([
        # Pilot results
        {"content": "dev the meridian pilot results are in. 96.1% accuracy on scope 1, 91.3% on scope 2. they want to convert to annual contract",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-10-28T09:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "holy shit that's way better than our projections. what about lone star cement?",
         "sender": "dev", "recipient": "jordan", "timestamp": "2024-10-28T09:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "lone star is 93.8% scope 1 but struggling with scope 3 upstream. cement supply chains are a nightmare. gulf coast plastics hasn't started yet, delayed to november",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-10-28T09:10:00",
         "category": "text_message", "modality": "imessage"},

        # Pricing evolution (CONTRADICTION: changes over time)
        {"content": "dev i've been thinking about pricing. $2,000/month per facility for the base tier, $5,000 for enterprise with API access. thoughts?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-10-30T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "seems reasonable. meridian has 4 facilities so that's $8k/mo base. not bad for a first customer",
         "sender": "dev", "recipient": "jordan", "timestamp": "2024-10-30T14:05:00",
         "category": "text_message", "modality": "imessage"},

        # Thanksgiving in Portland
        {"content": "mom we just booked flights. arriving portland nov 26 at 3pm, riley and biscuit are coming too. is biscuit ok at the house?",
         "sender": "jordan", "recipient": "mom", "timestamp": "2024-11-10T20:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "of course! dad already bought dog treats. lily is bringing marcus btw. yes THE marcus 😊",
         "sender": "mom", "recipient": "jordan", "timestamp": "2024-11-10T20:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "wait lily is dating a marcus too? i have a gym buddy named marcus lol. small world",
         "sender": "jordan", "recipient": "mom", "timestamp": "2024-11-10T20:12:00",
         "category": "text_message", "modality": "imessage"},

        # Meeting investor Nina
        {"content": "jordan, a friend gave me your name. i lead climate-tech at elevation ventures. would love to learn about carbonsense. coffee next week?",
         "sender": "nina", "recipient": "jordan", "timestamp": "2024-11-15T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "hi nina! absolutely, i'd love that. how about wednesday at epoch coffee on north loop? 10am?",
         "sender": "jordan", "recipient": "nina", "timestamp": "2024-11-15T10:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "perfect. i'll be the one in the ridiculous orange scarf. see you then",
         "sender": "nina", "recipient": "jordan", "timestamp": "2024-11-15T10:35:00",
         "category": "text_message", "modality": "imessage"},

        # Post-coffee with Nina
        {"content": "dev just had coffee with nina vasquez from elevation ventures. she's VERY interested. wants us to apply to their spring cohort. $500k-2M check size",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-11-20T11:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "no way. elevation is tier 1 for climate. what does she need from us?",
         "sender": "dev", "recipient": "jordan", "timestamp": "2024-11-20T11:35:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "deck, financials, pilot data, and a demo. application deadline is january 15. also she mentioned their portfolio company ecotrace might be a competitor or acquirer 👀",
         "sender": "jordan", "recipient": "dev", "timestamp": "2024-11-20T11:40:00",
         "category": "text_message", "modality": "imessage"},

        # Gym progress
        {"content": "JAKE. just hit 325 squat. new PR. three plates baby",
         "sender": "jordan", "recipient": "jake", "timestamp": "2024-11-22T07:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "LET'S GO!! you said end of summer though bro it's almost december 😂",
         "sender": "jake", "recipient": "jordan", "timestamp": "2024-11-22T07:32:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "startup life man. missed too many sessions in august and september. but we're back 💪",
         "sender": "jordan", "recipient": "jake", "timestamp": "2024-11-22T07:35:00",
         "category": "text_message", "modality": "imessage"},

        # Holiday season
        {"content": "riley what do you want for christmas? and don't say 'nothing' again",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-12-05T19:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "honestly? a weekend away. just us. somewhere with no wifi. i feel like i haven't seen you since you started the company",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-12-05T19:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "that's fair and i'm sorry. how about fredericksburg? wine country, no laptops, biscuit can come",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-12-05T19:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "that sounds perfect 💕 january? after your investor deadline?",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-12-05T19:12:00",
         "category": "text_message", "modality": "imessage"},
    ])

    # Emails (Oct-Dec 2024)
    messages.extend([
        {"content": "Subject: CarbonSense Pilot — 90-Day Results Summary\n\nDear Jordan and Dev,\n\nPlease find attached our internal review of the CarbonSense pilot. Key findings:\n\n- Scope 1 accuracy: 96.1% (target was 90%)\n- Scope 2 accuracy: 91.3% (target was 85%)\n- Time saved vs manual reporting: ~40 hours/month\n- Data latency: <20 minutes (vs 2 weeks for manual)\n\nWe'd like to convert to an annual contract. Our legal team will send the MSA next week. We're also interested in adding our Houston and Pittsburgh facilities.\n\nRegards,\nMaria Gonzalez\nVP Sustainability, Meridian Steel",
         "sender": "maria.gonzalez@meridiansteel.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2024-10-29T09:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Elevation Ventures — Spring 2025 Cohort Application\n\nHi Jordan,\n\nGreat meeting you at Epoch today! As discussed, here's the link to our Spring 2025 application.\n\nKey dates:\n- Application deadline: January 15, 2025\n- Interviews: February 3-7\n- Cohort starts: March 1\n- Demo Day: June 15\n\nWhat we look for: strong founding team, initial traction (you have this!), large addressable market, clear technical moat.\n\nYour pilot results are impressive. The SOC 2 progress will help too.\n\nBest,\nNina Vasquez\nPartner, Elevation Ventures",
         "sender": "nina@elevationvc.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2024-11-20T14:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: SOC 2 Type 1 — Audit Complete\n\nJordan,\n\nGood news — CarbonSense has passed SOC 2 Type 1 certification. Report attached.\n\nKey findings:\n- All 47 controls passed\n- 3 observations (minor, no remediation required)\n- Certificate valid through December 2025\n\nFor Type 2, we'll need 6 months of continuous monitoring. We can start that process in January.\n\nCongratulations!\n\nRegards,\nCompliance Team\nVanta",
         "sender": "compliance@vanta.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2024-12-18T10:00:00", "category": "work_email", "modality": "email"},
    ])

    # OCR (Oct-Dec 2024)
    messages.extend([
        {"content": "[OCR: Receipt] Epoch Coffee — Date: 11/20/2024\nOat milk latte $5.50\nCortado $4.50\nTotal: $10.00\nTip: $3.00\nPayment: Amex ending 9012",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-11-20T10:45:00",
         "category": "ocr", "modality": "ocr_receipt"},

        {"content": "[OCR: Screenshot] CarbonSense Dashboard — Monthly Metrics Dec 2024\nActive Facilities: 4 (Meridian Steel x4)\nPending Pilots: 2 (Lone Star Cement, Gulf Coast Plastics)\nMRR: $8,000\nAccuracy (avg): 93.7%\nAPI calls this month: 142,819\nUptime: 99.94%",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-12-31T23:59:00",
         "category": "ocr", "modality": "ocr_screenshot"},

        {"content": "[OCR: Document] CarbonSense Inc. — Cap Table as of Dec 31, 2024\nJordan Chen: 5,000,000 shares (50%)\nDev Patel: 4,000,000 shares (40%)\nOption Pool: 1,000,000 shares (10%)\nTotal Authorized: 10,000,000\nValuation: N/A (no priced round yet)\n409A Valuation pending",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-12-31T12:00:00",
         "category": "ocr", "modality": "ocr_document"},
    ])

    # ========================================
    # PHASE 3: FUNDRAISING (Jan-Apr 2025)
    # Elevation application, investor meetings, first round
    # ========================================

    messages.extend([
        # Fredericksburg trip
        {"content": "this place is incredible riley. no cell service, just vineyards and biscuit chasing butterflies",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-01-04T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i know 😊 thank you for actually putting the laptop away. first time in months",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-01-04T14:05:00",
         "category": "text_message", "modality": "imessage"},

        # Elevation application stress
        {"content": "dev we need to finalize the deck by friday. nina said they got 400 applications for 12 spots",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-01-08T22:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i'll have the tech section done by wednesday. you handle the market size and traction slides. also we need to update the TAM — the EPA just released new scope 3 reporting requirements for manufacturers over $100M revenue",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-01-08T22:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "oh shit that's huge. that basically makes our product mandatory for thousands of companies. TAM just went from $2B to maybe $8B",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-01-08T22:15:00",
         "category": "text_message", "modality": "imessage"},

        # Interview prep
        {"content": "sam i need your help. mock pitch me for the elevation interview. you're the toughest audience i know",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-01-28T18:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "hell yeah. tomorrow night at my place? i'll bring my vc skeptic hat 🎩",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-01-28T18:05:00",
         "category": "text_message", "modality": "imessage"},

        # Interview result
        {"content": "DEV WE GOT IN. ELEVATION SPRING COHORT. NINA JUST CALLED",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-02-10T16:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "NO FUCKING WAY. what's the deal?",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-02-10T16:01:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "$1.5M seed at $10M post-money. 15% dilution. nina takes a board seat. standard stuff",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-02-10T16:03:00",
         "category": "text_message", "modality": "imessage"},

        # Telling family
        {"content": "mom dad i have big news. we raised $1.5 million for carbonsense from elevation ventures",
         "sender": "jordan", "recipient": "mom", "timestamp": "2025-02-11T18:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "JORDAN!!! dad is crying. we are so proud of you. what does this mean exactly? is the company worth money now?",
         "sender": "mom", "recipient": "jordan", "timestamp": "2025-02-11T18:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yeah the company is valued at $10 million on paper. doesn't mean anything until we grow more but it means real investors believe in what we're building",
         "sender": "jordan", "recipient": "mom", "timestamp": "2025-02-11T18:10:00",
         "category": "text_message", "modality": "imessage"},

        # Hiring begins
        {"content": "dev we need to hire. at minimum: 1 backend engineer, 1 ML engineer, 1 sales person. what do you think about compensation? we can't compete with FAANG salaries",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-02-20T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yeah $120-140k base + 0.5-1% equity for early employees. also dr. woo from ut suggested her former postdoc for the ML role. name is aisha rahman, she did her phd on industrial emissions modeling",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-02-20T10:15:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "that's perfect fit actually. can you set up an intro? also i want to bring on sam part time for sales. he's crushing it at his current job but said he'd moonlight",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-02-20T10:20:00",
         "category": "text_message", "modality": "imessage"},

        # CONTRADICTION: Pricing changes
        {"content": "nina is pushing us to go higher on pricing. she says $2k/facility is leaving money on the table. enterprise carbon reporting tools charge $10-15k. she wants us at $5k base, $12k enterprise",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-03-05T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "that's a big jump from our current $2k. what about existing customers?",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-03-05T14:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "grandfather meridian at $2k for year 1, new customers get the new pricing. lone star and gulf coast haven't signed yet so they'd be at $5k",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-03-05T14:10:00",
         "category": "text_message", "modality": "imessage"},

        # Aisha interview
        {"content": "dev just finished interviewing aisha. she's incredible. published 6 papers on emissions modeling, built a transformer model that predicts scope 3 from partial supply chain data. she wants $135k + 0.75%",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-03-10T17:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "hire her. that scope 3 model alone is worth the equity",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-03-10T17:02:00",
         "category": "text_message", "modality": "imessage"},

        # Riley and Jordan relationship
        {"content": "jordan can we talk tonight? i feel like since the fundraise you've been even MORE absent. you said it would get better after the round closed",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-03-15T12:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "you're right and i'm sorry. i got caught up in hiring and the new customers. dinner tonight, my phone goes in the drawer. i promise",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-03-15T12:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "ok. also biscuit needs his vaccines updated. vet appointment is next thursday at 4pm. can you take him? i have class",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-03-15T12:35:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yes i'll take him. what vet are we using now? still heart of texas on south lamar?",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-03-15T12:37:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "no we switched to thrive on burnet road remember? after the billing issue",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-03-15T12:38:00",
         "category": "text_message", "modality": "imessage"},

        # Dr. Woo mentorship
        {"content": "Subject: Re: Coffee follow-up — CarbonSense advisory role\n\nJordan,\n\nI've been thinking about your offer. I'd be happy to serve as a technical advisor. My conditions:\n\n1. No equity needed — I believe in supporting Austin startups\n2. Monthly 1-hour calls, quarterly in-person meetings\n3. I'd like CarbonSense to sponsor one PhD student in my lab ($30k/year)\n4. Access to anonymized customer data for research publications\n\nThis gives you academic credibility and gives my lab real-world data. Win-win.\n\nLooking forward to it,\nDr. Patricia Woo\nProfessor, Environmental Engineering\nUT Austin",
         "sender": "pwoo@utexas.edu", "recipient": "jordan@carbonsense.io",
         "timestamp": "2025-03-20T09:00:00", "category": "work_email", "modality": "email"},
    ])

    # OCR (Jan-Apr 2025)
    messages.extend([
        {"content": "[OCR: Receipt] Uchi Austin — Date: 02/14/2025\nValentine's Day Dinner\nOmakase for 2: $280.00\nSake flight: $45.00\nDessert course: $28.00\nTotal: $353.00 + $70.60 tip\nPayment: Amex ending 9012",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-02-14T22:00:00",
         "category": "ocr", "modality": "ocr_receipt"},

        {"content": "[OCR: Screenshot] Mercury Bank — CarbonSense Inc. Account Summary\nDate: March 31, 2025\nChecking Balance: $1,287,492.00\nBurn Rate (monthly avg): $47,200\nRunway: ~27 months\nRecent deposits: $1,500,000 (Elevation Ventures), $8,000 (Meridian Steel MRR)\nRecent expenses: Aisha Rahman salary ($11,250), AWS ($3,847), Vanta ($340)",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-03-31T08:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},

        {"content": "[OCR: Document] Thrive Veterinary — Patient Record\nPatient: Biscuit (Pembroke Welsh Corgi)\nOwner: Jordan Chen & Riley Park\nDOB: March 15, 2023\nWeight: 28.4 lbs\nVaccinations: Rabies (updated 03/20/2025), DHPP (updated 03/20/2025)\nHeartguard: Current through June 2025\nNotes: Slight weight gain since last visit. Recommend reducing treats.",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-03-20T16:30:00",
         "category": "ocr", "modality": "ocr_document"},
    ])

    # ========================================
    # PHASE 4: GROWTH + CHALLENGES (May-Aug 2025)
    # Product-market fit, scaling, personal strain
    # ========================================

    messages.extend([
        # Product growing
        {"content": "team update: we now have 7 paying customers, 14 facilities. MRR is $43k. lone star cement finally signed at $5k/facility for 3 plants. gulf coast plastics at $5k for 2 plants",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-05-01T09:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "nice! aisha's scope 3 model is ready for beta too. she's been testing with meridian's supply chain data. accuracy is 84.7% which is insane for scope 3",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-05-01T09:10:00",
         "category": "text_message", "modality": "imessage"},

        # CONTRADICTION: Database migration
        {"content": "dev we need to talk about infrastructure. postgres is struggling with the time series data. query latency is up to 2.3 seconds on the meridian dashboard",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-05-15T11:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yeah i noticed. we should look at timescaledb or questdb for the sensor data. keep postgres for the application layer",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-05-15T11:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "let's go timescaledb. it's a postgres extension so migration should be manageable. can you scope it?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-05-15T11:15:00",
         "category": "text_message", "modality": "imessage"},

        # LATER CONTRADICTION: Actually chose ClickHouse
        {"content": "so after a week of testing... timescaledb is better than raw postgres but still not fast enough. aisha suggested clickhouse. she used it at her old lab. query times went from 2.3s to 47ms",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-05-28T16:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "47ms?! yeah that's not even close. clickhouse it is. how long for migration?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-05-28T16:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "2-3 weeks. aisha will handle it since she knows clickhouse. we'll keep postgres for users/auth/billing",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-05-28T16:10:00",
         "category": "text_message", "modality": "imessage"},

        # Health and wellness
        {"content": "jake i need to get back to the gym. haven't been in 3 weeks. startup is eating me alive",
         "sender": "jordan", "recipient": "jake", "timestamp": "2025-06-02T19:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "bro you keep saying that. just show up tomorrow 6am. no excuses. also started doing yoga on sundays, you should come",
         "sender": "jake", "recipient": "jordan", "timestamp": "2025-06-02T19:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "yoga? who are you lol. but yeah ok 6am tomorrow. and i'll try the yoga thing",
         "sender": "jordan", "recipient": "jake", "timestamp": "2025-06-02T19:08:00",
         "category": "text_message", "modality": "imessage"},

        # CONTRADICTION: Gym routine changes
        {"content": "ok jake the morning gym thing isn't working with my schedule. i'm switching to evenings, like 7pm after riley gets home. she can watch biscuit",
         "sender": "jordan", "recipient": "jake", "timestamp": "2025-06-20T08:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "can't do evenings man, i coach little league at 6:30. we'll figure it out. maybe weekends?",
         "sender": "jake", "recipient": "jordan", "timestamp": "2025-06-20T08:05:00",
         "category": "text_message", "modality": "imessage"},

        # Demo day prep
        {"content": "nina how many investors will be at demo day? trying to figure out how much to prepare",
         "sender": "jordan", "recipient": "nina", "timestamp": "2025-06-01T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "around 200 LPs and VCs. you get 8 minutes on stage plus 15 minutes of Q&A. then networking. dress nice but not too corporate — this is austin after all 😄",
         "sender": "nina", "recipient": "jordan", "timestamp": "2025-06-01T10:30:00",
         "category": "text_message", "modality": "imessage"},

        # Demo Day result
        {"content": "SAM. DEMO DAY WAS INSANE. we had 14 investors ask for follow-up meetings. three said they want to lead our Series A",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-06-15T22:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "DUDE. that's incredible. who wants to lead?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-06-15T22:02:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "sequoia, a16z climate fund, and khosla ventures. we're going to run a proper process. nina says we should target $8-12M at $50-70M valuation",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-06-15T22:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "from $10M to $50-70M in 4 months. you're living the dream man",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-06-15T22:08:00",
         "category": "text_message", "modality": "imessage"},

        # Riley tension escalating
        {"content": "jordan you missed our anniversary dinner. you said you'd leave the office by 7",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-07-03T21:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "fuck. riley i'm so sorry. the sequoia partner wanted to do a call and it ran over. i should have said no. can we do tomorrow?",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-07-03T21:35:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "it's not just tonight. it's every night. i eat dinner alone with biscuit more than with you. something has to change",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-07-03T21:40:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "you're right. i'm going to start a hard stop at 7pm every day. no exceptions. not even for sequoia. i mean it",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-07-03T21:45:00",
         "category": "text_message", "modality": "imessage"},

        # Health scare
        {"content": "riley just got back from the doctor. been having chest tightness for a few weeks. doc says it's stress and anxiety, not cardiac. gave me a referral for a therapist",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-07-20T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i'm glad you went. please actually go to the therapist. your health matters more than any fundraise",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-07-20T14:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i will. first appointment is next tuesday at 3pm. her name is dr. linda choi",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-07-20T14:10:00",
         "category": "text_message", "modality": "imessage"},

        # Big hire: VP Sales
        {"content": "dev we need a real sales person. sam's moonlighting isn't cutting it. we need someone full time who's sold to enterprise",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-08-01T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "agreed. nina introduced us to her friend's company and they have a vp sales leaving. name is rachel torres. 12 years enterprise SaaS experience, last 3 in sustainability tech",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-08-01T10:15:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "perfect background. what's she looking for comp-wise?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-08-01T10:18:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "she wants $180k base + commission + 1% equity. which is a lot but if she closes even 2 enterprise deals it pays for itself",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-08-01T10:25:00",
         "category": "text_message", "modality": "imessage"},
    ])

    # Emails (May-Aug 2025)
    messages.extend([
        {"content": "Subject: CarbonSense — Series A Term Sheet\n\nDear Jordan,\n\nFollowing our productive conversations, Khosla Ventures is pleased to present the following term sheet for CarbonSense Inc.'s Series A financing:\n\n- Investment amount: $10M\n- Pre-money valuation: $55M\n- Post-money valuation: $65M\n- Lead investor: Khosla Ventures\n- Board seats: 1 (Khosla) + 1 (Elevation) + 1 (Common)\n- Liquidation preference: 1x non-participating\n- Pro-rata rights: Yes\n- Anti-dilution: Weighted average broad-based\n\nThis term sheet is non-binding and subject to due diligence and definitive documentation.\n\nBest regards,\nVinod Khosla",
         "sender": "vinod@khoslaventures.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2025-08-10T09:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Competitor Alert — EcoTrace raises $40M\n\nJordan,\n\nFYI — EcoTrace (the company I mentioned when we first met) just announced a $40M Series B led by Breakthrough Energy. They're pivoting from voluntary carbon offsets to mandatory emissions reporting — directly into your space.\n\nKey differences to highlight in your pitch:\n1. Your accuracy is higher (96% vs their reported 89%)\n2. Your real-time capability vs their batch processing\n3. You have scope 3 (they don't)\n\nLet's discuss strategy on our next call.\n\nNina",
         "sender": "nina@elevationvc.com", "recipient": "jordan@carbonsense.io",
         "timestamp": "2025-07-28T11:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Re: Monthly investor update — July 2025\n\nHi Nina and Board,\n\nJuly update for CarbonSense:\n\n**Metrics:**\n- MRR: $67,000 (+56% QoQ)\n- Customers: 11 (was 7 in May)\n- Facilities monitored: 28\n- Churn: 0%\n- Team size: 6 (added Rachel Torres as VP Sales)\n\n**Product:**\n- Scope 3 beta launched to 3 customers\n- ClickHouse migration complete (47ms avg query, down from 2.3s)\n- SOC 2 Type 2 in progress\n\n**Fundraise:**\n- Received term sheets from Khosla ($10M @ $55M pre) and a16z ($8M @ $50M pre)\n- Decision by August 25\n\n**Concerns:**\n- EcoTrace's $40M raise and pivot\n- Engineering team needs 2 more hires by Q4\n- My personal health — managing stress better now with weekly therapy\n\nBest,\nJordan",
         "sender": "jordan@carbonsense.io", "recipient": "nina@elevationvc.com",
         "timestamp": "2025-08-01T08:00:00", "category": "work_email", "modality": "email"},
    ])

    # OCR (May-Aug 2025)
    messages.extend([
        {"content": "[OCR: Receipt] Uchiko Austin — Date: 07/03/2025\nDinner for 1\nYakitori platter $32.00\nBeer (Asahi) $8.00\nTotal: $40.00 + $8.00 tip\nPayment: Visa ending 4821\nNote: Anniversary dinner — Riley didn't come",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-07-03T22:30:00",
         "category": "ocr", "modality": "ocr_receipt"},

        {"content": "[OCR: Screenshot] Apple Health Summary — July 2025\nAvg Resting Heart Rate: 72 bpm (up from 64 in Jan)\nAvg Sleep: 5.8 hours (down from 7.2 in Jan)\nSteps/day: 4,200 (down from 8,500 in Jan)\nWorkouts this month: 4 (down from 12 in Jan)\nStress indicator: HIGH",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-07-31T06:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},

        {"content": "[OCR: Document] Lease Agreement — Amendment\nProperty: 2847 E Cesar Chavez St, Unit 4B, Austin TX 78702\nTenant: CarbonSense Inc.\nAmendment: Expanding from Suite 4B (800 sq ft) to Suite 4B+4C (1,600 sq ft)\nNew monthly rent: $4,800 (was $2,400)\nEffective: August 1, 2025\nLease term: Extended through July 2027",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-08-05T10:00:00",
         "category": "ocr", "modality": "ocr_document"},
    ])

    # ========================================
    # PHASE 5: SCALING + SERIES A (Sep-Dec 2025)
    # Series A closes, team grows, competitive pressure
    # ========================================

    messages.extend([
        # Series A closes
        {"content": "dev it's done. signed the khosla term sheet. $10M at $55M pre. money wires in 10 business days",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-08-25T17:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "we did it man. from your apartment to $65M company in 13 months. what's first?",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-08-25T17:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "hire like crazy. we need 4 engineers, 2 more sales reps, a product manager, and a head of customer success. also we need to start thinking about international — nina says european ESG regulations are even stricter",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-08-25T17:10:00",
         "category": "text_message", "modality": "imessage"},

        # Personal growth
        {"content": "dr choi really helped me today. she said i have classic founder burnout patterns. we're working on setting boundaries. the 7pm hard stop is actually sticking now",
         "sender": "jordan", "recipient": "riley", "timestamp": "2025-09-02T17:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "i've noticed 😊 dinner together 4 nights this week. biscuit is happier too — he stopped chewing the couch cushions when you're home",
         "sender": "riley", "recipient": "jordan", "timestamp": "2025-09-02T17:05:00",
         "category": "text_message", "modality": "imessage"},

        # Competitive threat escalates
        {"content": "jordan heads up — ecotrace just poached two of our target customers. bluebonnet energy and coastal paper. rachel says they're undercutting us on price by 40%",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-09-15T09:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "fuck. what are they charging?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-09-15T09:02:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "$3k/facility with a free 6 month trial. basically buying market share with their $40M",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-09-15T09:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "we can't compete on price with $40M behind them. we compete on accuracy and scope 3. aisha's model is our moat. how's the scope 3 rollout going?",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-09-15T09:10:00",
         "category": "text_message", "modality": "imessage"},

        # CONTRADICTION: Office move
        {"content": "dev the east cesar chavez office is getting tight even with the expansion. we're at 12 people and the landlord won't give us more space. i found a place in the domain — 3,500 sq ft, $8,200/month",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-10-01T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "the domain? that's so far from downtown. what about the east side? there's that new tech hub on springdale",
         "sender": "dev", "recipient": "jordan", "timestamp": "2025-10-01T14:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "true let me check springdale. also rachel wants a small sales office in houston near the refineries. makes sense for client meetings",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-10-01T14:10:00",
         "category": "text_message", "modality": "imessage"},

        # LATER CONTRADICTION: Chose coworking instead
        {"content": "ok dev forget the office search. we're going wework. $450/desk, totally flexible, locations in austin AND houston. no 2-year lease commitment when we might outgrow it in 6 months",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-10-15T10:00:00",
         "category": "text_message", "modality": "imessage"},

        # Holiday plans 2025
        {"content": "mom are we doing portland again for thanksgiving? riley and i want to come but biscuit had a bad time on the plane last year. thinking about driving this time",
         "sender": "jordan", "recipient": "mom", "timestamp": "2025-10-20T18:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "austin to portland is a 30 hour drive jordan! why don't you leave biscuit with a sitter? lily said she'd watch him — she's in austin now",
         "sender": "mom", "recipient": "jordan", "timestamp": "2025-10-20T18:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "wait lily moved to austin?? when?? she didn't tell me",
         "sender": "jordan", "recipient": "mom", "timestamp": "2025-10-20T18:12:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "last month! she got a job at indeed. she wanted to surprise you but i just ruined it 😬",
         "sender": "mom", "recipient": "jordan", "timestamp": "2025-10-20T18:15:00",
         "category": "text_message", "modality": "imessage"},

        # Lily in Austin
        {"content": "LILY. MOM TOLD ME. YOU'RE IN AUSTIN?!",
         "sender": "jordan", "recipient": "lily", "timestamp": "2025-10-20T18:20:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "DAMMIT MOM. yes!! i moved 3 weeks ago. i'm in east austin near the mueller heb. surprise? 😅",
         "sender": "lily", "recipient": "jordan", "timestamp": "2025-10-20T18:22:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "oh my god that's so close to our old office. dinner this weekend? riley will lose her mind. bring marcus if you want",
         "sender": "jordan", "recipient": "lily", "timestamp": "2025-10-20T18:25:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "actually marcus and i broke up in august. that's partly why i moved. fresh start. but YES dinner please. i miss you guys",
         "sender": "lily", "recipient": "jordan", "timestamp": "2025-10-20T18:28:00",
         "category": "text_message", "modality": "imessage"},

        # Year-end reflection with Sam
        {"content": "sam wild year man. went from employee to $65M company. 15 customers. 14 employees. first VC competitor breathing down our neck. also started therapy lol",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-12-28T20:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "proud of you dude. for real. the therapy thing especially. you were looking rough in july. how are you and riley?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-12-28T20:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "better. way better. the 7pm boundary helped a lot. we're actually talking about getting engaged. don't tell anyone",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-12-28T20:10:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "!!!!! JORDAN. about damn time. you've been together what, 4 years?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-12-28T20:11:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "5 years in march. found a ring. vintage art deco, estate sale in fredericksburg. $4,200. it's perfect for her",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-12-28T20:15:00",
         "category": "text_message", "modality": "imessage"},
    ])

    # Emails (Sep-Dec 2025)
    messages.extend([
        {"content": "Subject: CarbonSense — Q4 Board Meeting Summary\n\nBoard Members,\n\nKey takeaways from today's meeting:\n\n**Metrics (Dec 2025):**\n- ARR: $1.2M (was $96k YoY ago)\n- Customers: 15 (was 1)\n- Facilities: 42\n- Team: 14 full-time\n- Net Revenue Retention: 135%\n- Churn: 0% (still)\n\n**Strategic:**\n- Series A runway: ~22 months remaining\n- EcoTrace competitive threat: lost 2 prospects, but won 5 head-to-head on accuracy/scope 3\n- European expansion planned for Q2 2026 (EU CSRD mandate)\n- SOC 2 Type 2 achieved November 2025\n\n**2026 Goals:**\n- $5M ARR by Dec 2026\n- 50 customers\n- Launch European product\n- Begin Series B conversations Q3 2026\n\nBest,\nJordan Chen\nCEO, CarbonSense",
         "sender": "jordan@carbonsense.io", "recipient": "board@carbonsense.io",
         "timestamp": "2025-12-15T17:00:00", "category": "work_email", "modality": "email"},

        {"content": "Subject: Dr. Woo Lab Sponsorship — First Publication\n\nDear Jordan,\n\nExciting news! Our sponsored PhD student, Chen Wei, just had his paper accepted at ICML 2026:\n\n\"Real-time Scope 3 Emissions Estimation via Partial Supply Chain Graphs: A Transformer Approach\"\n\nThis paper cites CarbonSense's anonymized dataset (with your permission). The accuracy improvements he found are directly applicable to your product — his model gets 91.2% on scope 3, up from Aisha's 84.7%.\n\nCongratulations to the team.\n\nDr. Patricia Woo",
         "sender": "pwoo@utexas.edu", "recipient": "jordan@carbonsense.io",
         "timestamp": "2025-12-20T10:00:00", "category": "work_email", "modality": "email"},
    ])

    # OCR (Sep-Dec 2025)
    messages.extend([
        {"content": "[OCR: Receipt] WeWork Austin — Invoice\nDate: November 1, 2025\nCarbonSense Inc.\n12 dedicated desks @ $450/desk: $5,400\n2 private offices: $1,800\nConference room credits (20 hrs): $400\nTotal: $7,600/month\nPayment: Auto-debit Mercury checking",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-11-01T08:00:00",
         "category": "ocr", "modality": "ocr_receipt"},

        {"content": "[OCR: Screenshot] CarbonSense Org Chart — December 2025\nCEO: Jordan Chen\nCTO: Dev Patel\n  - Senior ML Engineer: Aisha Rahman\n  - Backend Engineer: Luis Moreno\n  - Backend Engineer: Preet Kaur\n  - Frontend Engineer: Danny Okafor\nVP Sales: Rachel Torres\n  - AE: Mike Chen\n  - AE: Sarah Lindquist\n  - SDR: Jamie Walsh\nCustomer Success: Tanya Reed\nProduct Manager: Omar Hassan\nOffice Admin: Becky Tran\nPhD Sponsor: Chen Wei (UT Austin, Dr. Woo's lab)",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-12-01T10:00:00",
         "category": "ocr", "modality": "ocr_document"},

        {"content": "[OCR: Screenshot] Ring photo — saved to favorites\nVintage Art Deco engagement ring\nPlatinum setting, 1.2ct round brilliant center stone\nFiligree details, milgrain edges\nSize 6\nPurchased at Hill Country Estate Sales, Fredericksburg TX\nPrice: $4,200\nLayaway: $1,400 paid, $2,800 remaining",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-12-30T22:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},
    ])

    # ========================================
    # FILLER: Day-to-day life messages
    # These add noise and realism
    # ========================================

    # Scattered throughout the timeline
    filler_messages = [
        # Food/restaurants
        {"content": "riley have you tried that new ramen place on south congress? torchy's closed and a ramen shop took over",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-08-15T12:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "no but jessica said it's amazing. let's go tonight?",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-08-15T12:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "sam just tried the breakfast tacos from veracruz on congress. life changing. egg and potato with green sauce",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-09-05T08:30:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "dev can you grab lunch? thinking thai-kun at the food truck park",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-04-15T11:30:00",
         "category": "text_message", "modality": "imessage"},

        # Biscuit updates
        {"content": "biscuit learned to shake! riley taught him. cutest thing ever",
         "sender": "jordan", "recipient": "mom", "timestamp": "2024-09-10T19:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "omg biscuit got into the trash again. ate an entire rotisserie chicken carcass. called the vet they said watch for bones",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-12-15T07:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "biscuit update: he's fine. no bone issues. but he did steal my sock and won't give it back",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-12-15T18:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "took biscuit to zilker off-leash today. he made a golden retriever friend named Maple. they ran around for 2 hours",
         "sender": "jordan", "recipient": "lily", "timestamp": "2025-11-02T16:00:00",
         "category": "text_message", "modality": "imessage"},

        # Random life
        {"content": "riley the ERCOT grid is at 95% capacity again. i charged all the devices just in case. this is the third time this summer",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-08-20T15:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "ugh texas. at least we have the generator from last winter. is biscuit ok with the heat?",
         "sender": "riley", "recipient": "jordan", "timestamp": "2024-08-20T15:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "jake just PR'd bench at 275. you're putting me to shame. i'm still stuck at 225",
         "sender": "jordan", "recipient": "jake", "timestamp": "2025-01-15T07:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "consistency bro. you miss half the sessions. show up and the gains come",
         "sender": "jake", "recipient": "jordan", "timestamp": "2025-01-15T07:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "sam ACL lineup just dropped. did you see? khruangbin is headlining. we HAVE to go",
         "sender": "jordan", "recipient": "sam", "timestamp": "2025-05-20T10:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "already got tickets! weekend 2. you me jake and riley?",
         "sender": "sam", "recipient": "jordan", "timestamp": "2025-05-20T10:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "lily you HAVE to meet riley's friend jessica. she works at indeed too. y'all would get along",
         "sender": "jordan", "recipient": "lily", "timestamp": "2025-11-10T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "sam should i get a truck? biscuit would love riding in the back. looking at tacomas",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-10-05T12:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "get a rivian bro. you're a climate tech CEO driving a gas truck? bad look 😂",
         "sender": "sam", "recipient": "jordan", "timestamp": "2024-10-05T12:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "fair point. riley also wants electric. looking at R1S since we need space for biscuit",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-10-05T12:10:00",
         "category": "text_message", "modality": "imessage"},

        # Weather/Austin life
        {"content": "104 degrees today. this city is basically the sun",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-08-01T14:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "barton springs after work? only sane response to this heat",
         "sender": "sam", "recipient": "jordan", "timestamp": "2024-08-01T14:02:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "first cold front! 65 degrees and biscuit is going NUTS at the dog park. he loves fall",
         "sender": "jordan", "recipient": "riley", "timestamp": "2024-10-25T16:00:00",
         "category": "text_message", "modality": "imessage"},

        # Books and media
        {"content": "sam just finished 'the lean startup' finally. i know i know it's basic but some of the MVT stuff really applies to what we're doing",
         "sender": "jordan", "recipient": "sam", "timestamp": "2024-09-20T21:00:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "read 'the hard thing about hard things' next. way better. ben horowitz actually lived it",
         "sender": "sam", "recipient": "jordan", "timestamp": "2024-09-20T21:05:00",
         "category": "text_message", "modality": "imessage"},
        {"content": "dev have you watched the new season of severance? the memory stuff is wild. kind of relevant to what we do with data segmentation lol",
         "sender": "jordan", "recipient": "dev", "timestamp": "2025-02-28T22:00:00",
         "category": "text_message", "modality": "imessage"},

        # Random OCR
        {"content": "[OCR: Receipt] Costco Austin — Date: 09/14/2024\nProtein powder (Optimum Nutrition) $49.99\nAlmond milk x2 $9.98\nAvocados (bag of 6) $6.99\nSalmon filets 3lb $29.99\nToilet paper (30 rolls) $24.99\nTotal: $121.94\nPayment: Visa ending 4821",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2024-09-14T13:00:00",
         "category": "ocr", "modality": "ocr_receipt"},
        {"content": "[OCR: Receipt] REI Austin — Date: 03/08/2025\nHoka Clifton 9 running shoes $140.00\nRunning socks (3-pack) $24.00\nTotal: $164.00\nPayment: Amex ending 9012",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-03-08T11:00:00",
         "category": "ocr", "modality": "ocr_receipt"},
        {"content": "[OCR: Screenshot] Strava — March 2025 Summary\nTotal runs: 14\nTotal distance: 52.3 miles\nAvg pace: 8:24/mi\nLongest run: 8.1 miles\nPR: 5K in 23:12\nNote: Training for Austin Half Marathon (April 6)",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-03-31T20:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},
        {"content": "[OCR: Screenshot] Strava — Half Marathon Result\nAustin Half Marathon — April 6, 2025\nFinish time: 1:52:34\nPace: 8:35/mi\nOverall: 1,847 / 4,231\nAge group (25-29): 312 / 687\nSplits: First half 55:12, Second half 57:22",
         "sender": "ocr_system", "recipient": "jordan", "timestamp": "2025-04-06T12:00:00",
         "category": "ocr", "modality": "ocr_screenshot"},
    ]

    messages.extend(filler_messages)

    # ========================================
    # NOTES (Jordan's personal notes/memos)
    # ========================================

    messages.extend([
        {"content": "[Note] Startup Ideas Brainstorm — July 2024\n- Carbon tracking for manufacturers (DOING THIS)\n- AI-powered energy audit tool\n- Supply chain transparency platform\n- Climate risk scoring for real estate\nDev says carbon tracking is most viable. Has the most clear regulatory tailwind.",
         "sender": "jordan", "recipient": "self", "timestamp": "2024-07-01T09:00:00",
         "category": "note", "modality": "note"},

        {"content": "[Note] Investor Questions to Prepare For\n1. Why not just use existing ERP emissions modules? (Answer: they're 60-70% accurate, we're 96%)\n2. What's your moat? (Answer: ML models trained on real pilot data, not synthetic)\n3. How do you handle scope 3? (Answer: Aisha's transformer model using partial supply chain graphs)\n4. What if a big player like SAP builds this? (Answer: SAP's sustainability module is a checkbox, not a product. We're 10x better)\n5. Competitor strategy vs EcoTrace? (Answer: they optimize for breadth, we optimize for accuracy)",
         "sender": "jordan", "recipient": "self", "timestamp": "2025-01-10T23:00:00",
         "category": "note", "modality": "note"},

        {"content": "[Note] Things I'm Grateful For — Therapy Exercise\n- Riley's patience through all of this\n- Dev being the most reliable co-founder imaginable\n- Mom and Dad supporting the decision to quit\n- Biscuit's unconditional love (even when I'm gone 14 hours)\n- Sam always being honest with me\n- Dr. Choi for helping me see patterns I was blind to\n- Nina for believing in us before anyone else",
         "sender": "jordan", "recipient": "self", "timestamp": "2025-08-15T22:00:00",
         "category": "note", "modality": "note"},

        {"content": "[Note] 2026 Personal Goals\n1. Propose to Riley (have the ring, just need the moment)\n2. Run a full marathon (Austin Marathon in Feb?)\n3. Get back to 315 squat (was there in Nov 2024, fell off)\n4. Read 24 books\n5. Take a real vacation — 2 weeks, no laptop, maybe japan?\n6. Weekly dinners with Lily now that she's in town\n7. Call mom and dad every sunday (I've been bad about this)\n8. Continue therapy — Dr. Choi every other week",
         "sender": "jordan", "recipient": "self", "timestamp": "2025-12-31T23:00:00",
         "category": "note", "modality": "note"},

        {"content": "[Note] Competitive Analysis — EcoTrace vs CarbonSense\nEcoTrace (competitor):\n- $40M raised (vs our $11.5M total)\n- 89% scope 1 accuracy (vs our 96%)\n- No scope 3 (we have it at 84.7%, soon 91%)\n- Batch processing only (we do real-time)\n- 200 customers but high churn (vs our 15 customers, 0% churn)\n- Strategy: buy market share with cheap pricing\nOur strategy: win on accuracy and scope 3. Enterprise customers who actually care about data quality will choose us.\nNina says: 'EcoTrace is a faster horse. You're building a car.'",
         "sender": "jordan", "recipient": "self", "timestamp": "2025-10-05T20:00:00",
         "category": "note", "modality": "note"},
    ])

    # ========================================
    # CALENDAR EVENTS
    # ========================================

    messages.extend([
        {"content": "[Calendar] Board Meeting — Q1 2026 Planning\nDate: January 15, 2026, 10:00 AM - 12:00 PM CT\nLocation: WeWork Austin, Conference Room B\nAttendees: Jordan Chen, Dev Patel, Nina Vasquez (Elevation), David Kim (Khosla)\nAgenda: Q4 results, 2026 roadmap, European expansion, Series B timeline",
         "sender": "calendar", "recipient": "jordan", "timestamp": "2026-01-10T08:00:00",
         "category": "calendar", "modality": "calendar"},

        {"content": "[Calendar] Lily's Birthday Dinner\nDate: February 8, 2026, 7:00 PM\nLocation: Uchi Austin\nGuests: Jordan, Riley, Lily, Sam, Jake\nNotes: Lily turns 25. Jordan is covering the bill. She mentioned wanting the omakase.",
         "sender": "calendar", "recipient": "jordan", "timestamp": "2026-02-01T10:00:00",
         "category": "calendar", "modality": "calendar"},

        {"content": "[Calendar] Austin Marathon\nDate: February 16, 2026\nStart: 7:00 AM\nLocation: Congress Avenue, Downtown Austin\nBib #: 4821\nGoal: Sub 4 hours\nNotes: First full marathon. Training plan: 18 weeks, peaked at 20 miles.",
         "sender": "calendar", "recipient": "jordan", "timestamp": "2026-02-10T08:00:00",
         "category": "calendar", "modality": "calendar"},

        {"content": "[Calendar] Riley's Graduation\nDate: May 17, 2026, 2:00 PM\nLocation: UT Austin, Frank Erwin Center\nNotes: Riley finishes her Master's in Counseling Psychology. Both parents flying in from Portland. Plan proposal after?",
         "sender": "calendar", "recipient": "jordan", "timestamp": "2026-04-01T08:00:00",
         "category": "calendar", "modality": "calendar"},

        {"content": "[Calendar] ACL Music Festival — Weekend 2\nDate: October 10-12, 2026\nLocation: Zilker Park\nTickets: 4 (Jordan, Riley, Sam, Jake)\nHeadliner: Khruangbin (Friday night)",
         "sender": "calendar", "recipient": "jordan", "timestamp": "2025-05-20T12:00:00",
         "category": "calendar", "modality": "calendar"},
    ])

    # Sort by timestamp
    messages.sort(key=lambda x: x["timestamp"])

    return messages


if __name__ == "__main__":
    data = generate_dataset()

    # Stats
    print(f"Total messages: {len(data)}")
    print(f"\nBy modality:")
    modalities = {}
    for m in data:
        mod = m.get("modality", "unknown")
        modalities[mod] = modalities.get(mod, 0) + 1
    for mod, count in sorted(modalities.items(), key=lambda x: -x[1]):
        print(f"  {mod}: {count}")

    print(f"\nBy sender:")
    senders = {}
    for m in data:
        s = m["sender"]
        senders[s] = senders.get(s, 0) + 1
    for s, count in sorted(senders.items(), key=lambda x: -x[1]):
        print(f"  {s}: {count}")

    print(f"\nTimeline: {data[0]['timestamp']} to {data[-1]['timestamp']}")

    # Save
    with open("/Users/j/Desktop/neuromem/synthetic_v2_messages.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved to synthetic_v2_messages.json")
