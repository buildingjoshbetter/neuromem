#!/usr/bin/env python3
"""
Analyze if recall degrades with conversation length.
"""
import json
from pathlib import Path

with open("locomo_data/data/locomo10.json") as f:
    data = json.load(f)

# Load retrieval results
with open("locomo_benchmark/results/neuromem_locomo_retrieval.json") as f:
    results = json.load(f)

print("CONVERSATION LENGTH VS RECALL ANALYSIS")
print("=" * 80)

# Match conversations
for i, conv in enumerate(data):
    sample_id = conv["sample_id"]

    # Count turns
    conversation = conv["conversation"]
    session_keys = [k for k in conversation if k.startswith("session_") and not k.endswith("_date_time")]
    total_turns = sum(len(conversation[k]) for k in session_keys)

    # Get recall from results
    conv_result = next((r for r in results["per_conversation"] if r["conversation"] == sample_id), None)
    if conv_result:
        recall = conv_result["overall_recall_at_k"]
        print(f"{sample_id}: {total_turns:3d} turns → {recall*100:5.1f}% recall")

        # Show category breakdown
        for cat_name, cat_data in conv_result["by_category"].items():
            print(f"  {cat_name:15s}: {cat_data['avg_recall_at_k']*100:5.1f}%")
        print()
