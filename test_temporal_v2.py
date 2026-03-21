"""
Test script for temporal_v2 zero-cost temporal reasoning.

Usage:
    python test_temporal_v2.py
"""

from datetime import datetime
from neuromem.temporal_v2 import (
    resolve_temporal_expressions,
    compute_temporal_features,
    augment_message_with_temporal,
)

# Test cases covering various temporal expression types
TEST_CASES = [
    {
        "content": "I quit my job last year and started a new one in January 2025.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["last year", "January 2025"],
    },
    {
        "content": "We're meeting next Tuesday to discuss the project.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["next Tuesday"],
    },
    {
        "content": "Three months ago I moved to Austin, and two weeks from now I'm starting a new role.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["Three months ago", "two weeks from now"],
    },
    {
        "content": "Last summer we went to Greece, and this winter we're planning a ski trip.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["Last summer", "this winter"],
    },
    {
        "content": "The demo is scheduled for June 15, 2026.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["June 15, 2026"],
    },
    {
        "content": "Yesterday I had a meeting, and tomorrow I'm flying to SF.",
        "timestamp": "2026-03-21T10:00:00",
        "expected_refs": ["Yesterday", "tomorrow"],
    },
    {
        "content": "Last Friday we closed the deal, and next Monday we start implementation.",
        "timestamp": "2026-03-21T10:00:00",  # Saturday
        "expected_refs": ["Last Friday", "next Monday"],
    },
]


def test_temporal_resolution():
    """Test temporal expression resolution."""
    print("=" * 80)
    print("TEMPORAL V2 RESOLUTION TEST")
    print("=" * 80)

    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        content = test_case["content"]
        timestamp = test_case["timestamp"]
        expected = test_case["expected_refs"]

        print(f"\nTest {i}/{len(TEST_CASES)}")
        print(f"Content: {content}")
        print(f"Session date: {timestamp}")

        session_date = datetime.fromisoformat(timestamp)
        resolved = resolve_temporal_expressions(content, session_date)

        print(f"\nResolved {len(resolved)} temporal references:")
        for ref in resolved:
            print(f"  - '{ref['original']}' → {ref['resolved_date'].strftime('%Y-%m-%d')}")
            print(f"    Type: {ref['type']}, Granularity: {ref['granularity']}, Confidence: {ref['confidence']:.2f}")

        # Check if we found expected references
        found = [ref['original'] for ref in resolved]
        missing = [e for e in expected if not any(e.lower() in f.lower() for f in found)]

        if missing:
            print(f"  ⚠️  Missing expected references: {missing}")
            failed += 1
        else:
            print(f"  ✅ All expected references found")
            passed += 1

    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{len(TEST_CASES)} passed, {failed}/{len(TEST_CASES)} failed")
    print("=" * 80)


def test_feature_computation():
    """Test temporal feature computation."""
    print("\n" + "=" * 80)
    print("TEMPORAL FEATURE COMPUTATION TEST")
    print("=" * 80)

    test_message = {
        "content": "Last year I quit my job. Next month I'm starting at a new company. Yesterday we had the offer call.",
        "timestamp": "2026-03-21T10:00:00",
        "sender": "Jordan",
        "recipient": "Caroline",
    }

    print(f"\nTest Message:")
    print(f"  {test_message['content']}")
    print(f"  Session: {test_message['timestamp']}")

    session_date = datetime.fromisoformat(test_message['timestamp'])
    resolved_refs = resolve_temporal_expressions(test_message['content'], session_date)

    features = compute_temporal_features(test_message, resolved_refs)

    print(f"\nComputed Features:")
    print(f"  Has temporal: {features['has_temporal']}")
    print(f"  Time scope: {features['time_scope']}")
    print(f"  Date range: {features['earliest_date']} → {features['latest_date']}")
    print(f"  Is planning: {features['is_planning']}")
    print(f"  Is narrative: {features['is_narrative']}")
    print(f"  Avg confidence: {features['avg_confidence']:.2f}")
    print(f"  Temporal refs: {len(features['temporal_refs'])}")


def test_message_augmentation():
    """Test full message augmentation pipeline."""
    print("\n" + "=" * 80)
    print("MESSAGE AUGMENTATION TEST")
    print("=" * 80)

    test_message = {
        "content": "Three months ago we launched the beta. Next week we're releasing v1.0.",
        "timestamp": "2026-03-21T10:00:00",
        "sender": "Jordan",
        "recipient": "Caroline",
        "category": "conv_1",
        "modality": "text",
    }

    print(f"\nOriginal Message:")
    for k, v in test_message.items():
        print(f"  {k}: {v}")

    augmented = augment_message_with_temporal(test_message)

    print(f"\nAugmented Message (with temporal_metadata):")
    import json
    metadata = json.loads(augmented['temporal_metadata'])
    print(json.dumps(metadata, indent=2))


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "=" * 80)
    print("EDGE CASE TEST")
    print("=" * 80)

    edge_cases = [
        # No temporal references
        {
            "content": "This is a message with no dates at all.",
            "timestamp": "2026-03-21T10:00:00",
        },
        # Missing timestamp
        {
            "content": "Last year we did something.",
            "timestamp": "",
        },
        # Very long message
        {
            "content": "word " * 1000 + "last year",
            "timestamp": "2026-03-21T10:00:00",
        },
        # Special characters
        {
            "content": "We met on 2025-06-15 (remember? 😊) and tomorrow we're meeting again!",
            "timestamp": "2026-03-21T10:00:00",
        },
    ]

    for i, msg in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}:")
        print(f"  Content: {msg['content'][:100]}...")
        print(f"  Timestamp: {msg['timestamp']}")

        try:
            augmented = augment_message_with_temporal(msg)
            import json
            metadata = json.loads(augmented['temporal_metadata'])
            print(f"  Result: {metadata.get('has_temporal', False)} temporal refs found")
            if metadata.get('has_temporal'):
                print(f"  Refs: {len(metadata.get('temporal_refs', []))}")
        except Exception as e:
            print(f"  ❌ Error: {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("NEUROMEM TEMPORAL V2 - ZERO-COST TEMPORAL REASONING")
    print("Test Suite")
    print("=" * 80)

    try:
        test_temporal_resolution()
        test_feature_computation()
        test_message_augmentation()
        test_edge_cases()

        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETE")
        print("=" * 80)
        print("\nNext steps:")
        print("  1. Install dependencies: pip install spacy python-dateutil")
        print("  2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("  3. Integrate into storage.py: call augment_message_with_temporal() during load_messages()")
        print("  4. Register SQL functions: call register_temporal_functions(conn) in engine.py")
        print("  5. Update vector_search.py: augment content before embedding")
        print("  6. Benchmark on LoCoMo Category 2 (temporal questions)")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
