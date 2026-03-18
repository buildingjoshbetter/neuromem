#!/usr/bin/env python3
"""
Analyze LoCoMo retrieval failures in detail to understand why recall is only 54.6%.
"""
import json
import sys
import tempfile
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from neuromem.engine import NeuromemEngine

# Load LoCoMo data
with open("locomo_data/data/locomo10.json") as f:
    data = json.load(f)

# Analyze first conversation in detail
conv = data[0]
sample_id = conv["sample_id"]
qa_pairs = conv["qa"]

print(f"=" * 80)
print(f"ANALYZING CONVERSATION: {sample_id}")
print(f"=" * 80)

# Parse conversation
def parse_conversations(conv_data: dict) -> list[dict]:
    messages = []
    conversation = conv_data["conversation"]
    speaker_a = conversation["speaker_a"]
    speaker_b = conversation["speaker_b"]

    session_keys = sorted(
        [k for k in conversation if k.startswith("session_") and not k.endswith("_date_time")],
        key=lambda k: int(k.split("_")[1]),
    )

    for session_key in session_keys:
        session_num = session_key.split("_")[1]
        datetime_key = f"{session_key}_date_time"
        session_dt = conversation.get(datetime_key, "")
        turns = conversation[session_key]

        for i, turn in enumerate(turns):
            speaker = turn["speaker"]
            recipient = speaker_b if speaker == speaker_a else speaker_a
            dia_id = turn.get("dia_id", f"D{session_num}:{i+1}")

            messages.append({
                "content": turn["text"],
                "sender": speaker,
                "recipient": recipient,
                "timestamp": session_dt,
                "category": f"session_{session_num}",
                "modality": "conversation",
                "_dia_id": dia_id,
                "_session_num": int(session_num),
            })

    return messages

messages = parse_conversations(conv)
print(f"\nTotal turns: {len(messages)}")
print(f"Sessions: {len([m for m in messages if m['_dia_id'].endswith(':1')])}")

# Build dia_id -> message map
dia_id_to_msg = {m["_dia_id"]: m for m in messages}

# Create engine
tmp_db = Path(tempfile.mktemp(suffix=".db", prefix=f"locomo_analysis_"))
engine = NeuromemEngine(db_path=tmp_db)

# Ingest
tmp_json = Path(tempfile.mktemp(suffix=".json", prefix="locomo_msgs_"))
clean_messages = [{k: v for k, v in m.items() if not k.startswith("_")} for m in messages]
with open(tmp_json, "w") as f:
    json.dump(clean_messages, f)

print(f"\nIngesting into Neuromem...")
engine.ingest(tmp_json)

# Analyze failures by category
cat_names = {1: "single_hop", 2: "multi_hop", 3: "temporal", 4: "open_domain", 5: "adversarial"}

failures_by_category = defaultdict(list)
successes_by_category = defaultdict(list)

for qa in qa_pairs:
    cat = qa["category"]
    if cat == 5:  # Skip adversarial
        continue

    question = qa["question"]
    evidence_ids = qa.get("evidence", [])
    gold_answer = qa.get("answer", "")

    # Query
    results = engine.search(question, limit=10)
    retrieved_contents = [r["content"] for r in results]

    # Check evidence recall
    evidence_found = 0
    missing_evidence = []
    for eid in evidence_ids:
        evidence_msg = dia_id_to_msg.get(eid)
        if evidence_msg:
            evidence_text = evidence_msg["content"]
            found = any(evidence_text in rc or rc in evidence_text for rc in retrieved_contents)
            if found:
                evidence_found += 1
            else:
                missing_evidence.append({
                    "dia_id": eid,
                    "text": evidence_text[:200],
                    "session": evidence_msg["_session_num"]
                })

    recall = evidence_found / len(evidence_ids) if evidence_ids else 0.0

    failure_info = {
        "question": question,
        "answer": gold_answer,
        "evidence_ids": evidence_ids,
        "recall": recall,
        "found": evidence_found,
        "total": len(evidence_ids),
        "missing": missing_evidence,
        "top_result": results[0]["content"][:200] if results else "",
    }

    if recall < 1.0:
        failures_by_category[cat].append(failure_info)
    else:
        successes_by_category[cat].append(failure_info)

# Print analysis
print(f"\n" + "=" * 80)
print(f"FAILURE ANALYSIS BY CATEGORY")
print(f"=" * 80)

for cat_id in [1, 2, 3, 4]:
    cat_name = cat_names[cat_id]
    failures = failures_by_category[cat_id]
    successes = successes_by_category[cat_id]
    total = len(failures) + len(successes)

    if total == 0:
        continue

    print(f"\n{'='*80}")
    print(f"{cat_name.upper()}: {len(failures)} failures / {total} total ({len(failures)/total*100:.1f}% fail rate)")
    print(f"{'='*80}")

    # Show first 3 failures
    for i, fail in enumerate(failures[:3]):
        print(f"\nFAILURE {i+1}:")
        print(f"  Q: {fail['question']}")
        print(f"  Gold answer: {fail['answer']}")
        print(f"  Evidence recall: {fail['found']}/{fail['total']} ({fail['recall']*100:.0f}%)")
        print(f"  Missing evidence:")
        for miss in fail['missing']:
            print(f"    - [{miss['dia_id']}] Session {miss['session']}: {miss['text']}")
        print(f"  Top retrieved result:")
        print(f"    {fail['top_result']}")

    # Show 1 success for comparison
    if successes:
        succ = successes[0]
        print(f"\nSUCCESS EXAMPLE (for comparison):")
        print(f"  Q: {succ['question']}")
        print(f"  Gold answer: {succ['answer']}")
        print(f"  Evidence recall: {succ['found']}/{succ['total']} (100%)")

# Analyze evidence length patterns
print(f"\n" + "=" * 80)
print(f"EVIDENCE LENGTH ANALYSIS")
print(f"=" * 80)

all_evidence_lengths = []
failed_evidence_lengths = []

for qa in qa_pairs:
    if qa["category"] == 5:
        continue
    evidence_ids = qa.get("evidence", [])
    for eid in evidence_ids:
        msg = dia_id_to_msg.get(eid)
        if msg:
            length = len(msg["content"])
            all_evidence_lengths.append(length)

# Get lengths of specifically failed retrievals
for cat_id, failures in failures_by_category.items():
    for fail in failures:
        for miss in fail['missing']:
            msg = dia_id_to_msg.get(miss['dia_id'])
            if msg:
                failed_evidence_lengths.append(len(msg['content']))

print(f"\nAll evidence turns:")
print(f"  Count: {len(all_evidence_lengths)}")
print(f"  Avg length: {sum(all_evidence_lengths)/len(all_evidence_lengths):.1f} chars")
print(f"  Min: {min(all_evidence_lengths)}, Max: {max(all_evidence_lengths)}")

print(f"\nFailed-to-retrieve evidence turns:")
print(f"  Count: {len(failed_evidence_lengths)}")
if failed_evidence_lengths:
    print(f"  Avg length: {sum(failed_evidence_lengths)/len(failed_evidence_lengths):.1f} chars")
    print(f"  Min: {min(failed_evidence_lengths)}, Max: {max(failed_evidence_lengths)}")

# Cleanup
engine.close()
tmp_db.unlink(missing_ok=True)
for suffix in ["-wal", "-shm"]:
    Path(str(tmp_db) + suffix).unlink(missing_ok=True)
tmp_json.unlink(missing_ok=True)

print(f"\n" + "=" * 80)
