#!/usr/bin/env python3
"""
Analyze keyword mismatch between queries and evidence.
"""
import json
import re
from pathlib import Path
from collections import Counter

with open("locomo_data/data/locomo10.json") as f:
    data = json.load(f)

def parse_conversations(conv_data: dict) -> dict:
    """Build dia_id -> message map."""
    messages = {}
    conversation = conv_data["conversation"]
    session_keys = sorted(
        [k for k in conversation if k.startswith("session_") and not k.endswith("_date_time")],
        key=lambda k: int(k.split("_")[1]),
    )

    for session_key in session_keys:
        session_num = session_key.split("_")[1]
        turns = conversation[session_key]
        for i, turn in enumerate(turns):
            dia_id = turn.get("dia_id", f"D{session_num}:{i+1}")
            messages[dia_id] = turn["text"]

    return messages

def get_keywords(text):
    """Extract meaningful keywords from text."""
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common stopwords
    stopwords = {
        'i', 'me', 'my', 'we', 'you', 'your', 'he', 'she', 'it', 'they', 'them',
        'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'been', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
        'may', 'might', 'must', 'can', 'of', 'in', 'on', 'at', 'to', 'for', 'from',
        'by', 'with', 'as', 'that', 'this', 'these', 'those', 'what', 'which', 'who',
        'when', 'where', 'why', 'how', 'not', 'so', 'just', 'really', 'very', 'too',
    }
    return {w for w in words if w not in stopwords and len(w) > 2}

# Analyze first conversation
conv = data[0]
dia_id_to_msg = parse_conversations(conv)

print("KEYWORD OVERLAP ANALYSIS")
print("=" * 80)
print("\nAnalyzing single_hop queries (worst category - 21-41% recall)\n")

single_hop_qs = [qa for qa in conv["qa"] if qa["category"] == 1]

overlaps = []
for i, qa in enumerate(single_hop_qs[:15]):
    question = qa["question"]
    evidence_ids = qa.get("evidence", [])

    q_keywords = get_keywords(question)

    for eid in evidence_ids:
        evidence_text = dia_id_to_msg.get(eid, "")
        e_keywords = get_keywords(evidence_text)

        # Calculate overlap
        common = q_keywords & e_keywords
        overlap_pct = len(common) / len(q_keywords) * 100 if q_keywords else 0

        overlaps.append({
            'question': question,
            'evidence': evidence_text[:100],
            'q_keywords': q_keywords,
            'e_keywords': e_keywords,
            'common': common,
            'overlap_pct': overlap_pct
        })

        print(f"Q{i+1}: {question}")
        print(f"  Evidence: {evidence_text[:100]}...")
        print(f"  Query keywords: {sorted(q_keywords)}")
        print(f"  Evidence keywords: {sorted(e_keywords)}")
        print(f"  Common keywords: {sorted(common)}")
        print(f"  Overlap: {overlap_pct:.1f}%")
        print()

avg_overlap = sum(o['overlap_pct'] for o in overlaps) / len(overlaps)
print(f"\n{'='*80}")
print(f"AVERAGE KEYWORD OVERLAP: {avg_overlap:.1f}%")
print(f"{'='*80}")

# Count queries with <30% overlap
low_overlap = [o for o in overlaps if o['overlap_pct'] < 30]
print(f"\nQueries with <30% keyword overlap: {len(low_overlap)}/{len(overlaps)} ({len(low_overlap)/len(overlaps)*100:.1f}%)")

# Show some examples
print(f"\nWorst keyword overlap examples:")
worst = sorted(overlaps, key=lambda x: x['overlap_pct'])[:5]
for o in worst:
    print(f"  {o['overlap_pct']:.1f}% - Q: {o['question']}")
    print(f"         E: {o['evidence']}")
