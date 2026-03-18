#!/usr/bin/env python3
"""
Deep dive into why single_hop queries fail so badly (21-41% recall).
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from neuromem.engine import NeuromemEngine

with open("locomo_data/data/locomo10.json") as f:
    data = json.load(f)

# Analyze first conversation
conv = data[0]

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
dia_id_to_msg = {m["_dia_id"]: m for m in messages}

# Set up engine
tmp_db = Path(tempfile.mktemp(suffix=".db", prefix=f"locomo_single_"))
engine = NeuromemEngine(db_path=tmp_db)

tmp_json = Path(tempfile.mktemp(suffix=".json", prefix="locomo_msgs_"))
clean_messages = [{k: v for k, v in m.items() if not k.startswith("_")} for m in messages]
with open(tmp_json, "w") as f:
    json.dump(clean_messages, f)

engine.ingest(tmp_json)

# Get all single_hop questions
single_hop_qs = [qa for qa in conv["qa"] if qa["category"] == 1]

print(f"SINGLE-HOP FAILURE DEEP DIVE")
print(f"=" * 80)
print(f"Total single-hop questions: {len(single_hop_qs)}\n")

failed_count = 0
success_count = 0

for i, qa in enumerate(single_hop_qs[:10]):  # First 10
    question = qa["question"]
    evidence_ids = qa.get("evidence", [])
    gold_answer = qa.get("answer", "")

    # Get evidence text
    evidence_text = ""
    evidence_session = None
    if evidence_ids:
        evidence_msg = dia_id_to_msg.get(evidence_ids[0])
        if evidence_msg:
            evidence_text = evidence_msg["content"]
            evidence_session = evidence_msg["_session_num"]

    # Query
    results = engine.search(question, limit=10)

    # Check if found
    found = False
    if evidence_text:
        for r in results:
            if evidence_text in r["content"] or r["content"] in evidence_text:
                found = True
                break

    if found:
        success_count += 1
    else:
        failed_count += 1

    status = "✓ SUCCESS" if found else "✗ FAILED"
    print(f"{status} #{i+1}:")
    print(f"  Q: {question}")
    print(f"  A: {gold_answer}")
    print(f"  Evidence [{evidence_ids[0] if evidence_ids else 'N/A'}] Session {evidence_session}:")
    print(f"    \"{evidence_text[:150]}...\"")
    print(f"  Top-3 retrieved results:")
    for j, r in enumerate(results[:3]):
        print(f"    {j+1}. \"{r['content'][:100]}...\"")
    print()

print(f"\n" + "=" * 80)
print(f"SUMMARY: {success_count} success, {failed_count} failed ({success_count/(success_count+failed_count)*100:.1f}% success rate)")

# Now let's test if the evidence text is even SEARCHABLE
print(f"\n" + "=" * 80)
print(f"DIRECT EVIDENCE SEARCHABILITY TEST")
print(f"=" * 80)
print("Testing if we can find evidence by searching for exact phrases from it...\n")

# Take a failed query and test searching for the exact evidence text
failed_qa = next((qa for qa in single_hop_qs if qa["question"] == "What did Caroline research?"), None)
if failed_qa:
    evidence_id = failed_qa["evidence"][0]
    evidence_msg = dia_id_to_msg[evidence_id]
    evidence_text = evidence_msg["content"]

    print(f"Evidence text: \"{evidence_text}\"")
    print(f"\nTest 1: Search for 'adoption agencies'")
    results = engine.search("adoption agencies", limit=5)
    for j, r in enumerate(results[:5]):
        match = "✓" if evidence_text in r["content"] or r["content"] in evidence_text else " "
        print(f"  {match} {j+1}. \"{r['content'][:100]}...\"")

    print(f"\nTest 2: Search for 'Researching adoption'")
    results = engine.search("Researching adoption", limit=5)
    for j, r in enumerate(results[:5]):
        match = "✓" if evidence_text in r["content"] or r["content"] in evidence_text else " "
        print(f"  {match} {j+1}. \"{r['content'][:100]}...\"")

    print(f"\nTest 3: Search for exact evidence text")
    results = engine.search(evidence_text, limit=5)
    for j, r in enumerate(results[:5]):
        match = "✓" if evidence_text in r["content"] or r["content"] in evidence_text else " "
        print(f"  {match} {j+1}. \"{r['content'][:100]}...\"")

# Cleanup
engine.close()
tmp_db.unlink(missing_ok=True)
for suffix in ["-wal", "-shm"]:
    Path(str(tmp_db) + suffix).unlink(missing_ok=True)
tmp_json.unlink(missing_ok=True)
