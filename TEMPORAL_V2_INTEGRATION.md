# Temporal V2 Integration Guide
**Quick-start guide for integrating zero-cost temporal reasoning into Neuromem**

---

## Prerequisites

```bash
# Install dependencies
pip install spacy python-dateutil

# Download spaCy model (13MB)
python -m spacy download en_core_web_sm
```

---

## Integration Steps (5 steps, ~30 minutes)

### Step 1: Update Database Schema
**File:** `/Users/j/Desktop/neuromem/neuromem/storage.py`

Add temporal metadata column to messages table:

```python
# In _SCHEMA_SQL, add to messages table:
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    sender TEXT DEFAULT '',
    recipient TEXT DEFAULT '',
    timestamp TEXT DEFAULT '',
    category TEXT DEFAULT '',
    modality TEXT DEFAULT '',
    episode_id INTEGER DEFAULT NULL,
    emotional_valence REAL DEFAULT 0.0,
    embedding_separation BLOB DEFAULT NULL,
    temporal_metadata TEXT DEFAULT '{}'  -- ADD THIS LINE
);
```

### Step 2: Augment Messages During Ingestion
**File:** `/Users/j/Desktop/neuromem/neuromem/storage.py`

Modify `load_messages()` to call temporal augmentation:

```python
# At top of file, add import:
from neuromem.temporal_v2 import augment_message_with_temporal

# In load_messages() function, modify the INSERT loop:
def load_messages(conn: sqlite3.Connection, messages: list[dict]) -> int:
    conn.execute("DELETE FROM messages")

    for msg in messages:
        # NEW: Augment with temporal metadata
        msg = augment_message_with_temporal(msg, use_llm_fallback=False)

        conn.execute(
            """INSERT INTO messages
               (content, sender, recipient, timestamp, category, modality, temporal_metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                msg["content"],
                msg.get("sender", ""),
                msg.get("recipient", ""),
                msg.get("timestamp", ""),
                msg.get("category", ""),
                msg.get("modality", ""),
                msg.get("temporal_metadata", "{}"),  # NEW
            ),
        )

    conn.commit()
    return len(messages)
```

### Step 3: Register SQL Functions
**File:** `/Users/j/Desktop/neuromem/neuromem/engine.py`

Register temporal SQL functions when opening database:

```python
# At top of file, add import:
from neuromem.temporal_v2 import register_temporal_functions

# In NeuromemEngine.open() method, after connecting to DB:
def open(self, rebuild_vectors: bool = True) -> "NeuromemEngine":
    if not self.db_path.exists():
        raise FileNotFoundError(f"Database not found: {self.db_path}")

    self.conn = sqlite3.connect(str(self.db_path))
    self.conn.row_factory = None

    # NEW: Register temporal SQL functions
    try:
        register_temporal_functions(self.conn)
    except Exception:
        pass  # Non-fatal if registration fails

    # ... rest of open() method
```

### Step 4: Augment Vector Embeddings
**File:** `/Users/j/Desktop/neuromem/neuromem/vector_search.py`

Modify `build_vectors()` to augment content before embedding:

```python
# At top of file, add import:
import json

# In build_vectors() function:
def build_vectors(conn: sqlite3.Connection) -> int:
    """Build Model2Vec embeddings with temporal augmentation."""
    model = Model2Vec.from_pretrained("potion-base-8M")

    cursor = conn.execute(
        "SELECT id, content, timestamp, temporal_metadata FROM messages"
    )

    for row in cursor.fetchall():
        msg_id, content, timestamp, temporal_json = row

        # NEW: Augment content with resolved temporal info
        augmented_content = content

        if temporal_json and temporal_json != '{}':
            try:
                metadata = json.loads(temporal_json)
                if metadata.get("has_temporal"):
                    refs = metadata.get("temporal_refs", [])[:3]  # Top 3 refs
                    if refs:
                        temporal_context = " [TEMPORAL: "
                        temporal_context += ", ".join(
                            f"{r['original']}={r['resolved'][:10]}"  # Date only
                            for r in refs
                        )
                        temporal_context += "]"
                        augmented_content += temporal_context
            except Exception:
                pass  # Fall back to raw content on error

        # Embed augmented content
        embedding = model.encode(augmented_content)

        conn.execute(
            "INSERT INTO vec_messages (rowid, embedding) VALUES (?, vec_f32(?))",
            (msg_id, embedding.tobytes()),
        )

    conn.commit()
    return cursor.rowcount
```

### Step 5: Enhance Temporal Search
**File:** `/Users/j/Desktop/neuromem/neuromem/temporal.py`

Update `detect_temporal_intent()` to check metadata:

```python
# Add at top of detect_temporal_intent():
def detect_temporal_intent(query: str, conn: sqlite3.Connection = None) -> dict:
    """
    Analyze a query to detect temporal constraints.

    New: Can optionally accept a connection to check message temporal metadata
    for better date resolution hints.
    """
    result = {
        "has_temporal": False,
        "after": None,
        "before": None,
        "sort_by_time": False,
        "is_trajectory": False,
        "reference_date": None,
    }

    q = query.strip()
    ql = q.lower()

    # NEW: If we have a connection, we can check temporal metadata
    # for intelligent date suggestions
    if conn:
        try:
            # Find messages with temporal metadata matching query keywords
            import json
            rows = conn.execute("""
                SELECT temporal_metadata FROM messages
                WHERE temporal_metadata != '{}'
                LIMIT 100
            """).fetchall()

            # Extract common date ranges from metadata to suggest bounds
            all_dates = []
            for (metadata_json,) in rows:
                metadata = json.loads(metadata_json)
                if metadata.get('has_temporal'):
                    refs = metadata.get('temporal_refs', [])
                    for ref in refs:
                        all_dates.append(ref['resolved'])

            # Use median date as reference if we found any
            if all_dates:
                all_dates.sort()
                result['reference_date'] = all_dates[len(all_dates) // 2]
        except Exception:
            pass  # Non-fatal, continue with regex-based detection

    # ... rest of existing detect_temporal_intent() logic
```

---

## Testing the Integration

### 1. Run Unit Tests
```bash
cd /Users/j/Desktop/neuromem
python test_temporal_v2.py
```

Expected output:
- 7/7 test cases pass
- Feature computation shows correct metadata
- Edge cases handled gracefully

### 2. Test on Small Dataset
```python
from neuromem import NeuromemEngine

# Create test engine
engine = NeuromemEngine("test_temporal.db")

# Ingest test data
test_messages = [
    {
        "content": "Last year I quit my job and moved to Austin.",
        "timestamp": "2026-03-21T10:00:00",
        "sender": "Jordan",
        "recipient": "Caroline",
    },
    {
        "content": "Next month we're launching the beta.",
        "timestamp": "2026-03-21T11:00:00",
        "sender": "Caroline",
        "recipient": "Jordan",
    },
]

import json
with open("test_messages.json", "w") as f:
    json.dump(test_messages, f)

stats = engine.ingest("test_messages.json")
print(stats)

# Test search
results = engine.search("What happened last year?")
print(results)
```

### 3. Validate Temporal Metadata
```python
import sqlite3
conn = sqlite3.connect("test_temporal.db")

# Check temporal metadata was stored
rows = conn.execute("""
    SELECT content, temporal_metadata
    FROM messages
    WHERE temporal_metadata != '{}'
""").fetchall()

for content, metadata_json in rows:
    import json
    metadata = json.loads(metadata_json)
    print(f"Content: {content[:50]}...")
    print(f"Temporal refs: {len(metadata.get('temporal_refs', []))}")
    print(f"Time scope: {metadata.get('time_scope', 'unknown')}")
    print()
```

### 4. Test SQL Functions
```python
import sqlite3
from neuromem.temporal_v2 import register_temporal_functions

conn = sqlite3.connect("test_temporal.db")
register_temporal_functions(conn)

# Test days_between
result = conn.execute("""
    SELECT days_between('2026-01-01', '2026-03-21')
""").fetchone()
print(f"Days between: {result[0]}")  # Should be ~79

# Test extract_quarter
result = conn.execute("""
    SELECT extract_quarter(timestamp), COUNT(*)
    FROM messages
    GROUP BY extract_quarter(timestamp)
""").fetchall()
print(f"Messages by quarter: {result}")
```

---

## Validation Checklist

After integration, verify:

- [ ] Messages have `temporal_metadata` column populated
- [ ] Temporal references are resolved (check JSON contains `resolved` dates)
- [ ] SQL functions work (`SELECT days_between('2026-01-01', '2026-03-21')`)
- [ ] Vector embeddings include temporal augmentation (check db size increased slightly)
- [ ] Search still works for non-temporal queries
- [ ] Temporal queries return better results (test "What happened last year?")
- [ ] Ingestion time increased by < 100ms per message
- [ ] No API calls made (check network traffic)

---

## Benchmarking on LoCoMo

Run Category 2 (temporal questions) before and after:

```bash
cd /Users/j/Desktop/neuromem

# Before integration
python run_locomo_benchmark.py --category 2 --output before_temporal_v2.json

# After integration
python run_locomo_benchmark.py --category 2 --output after_temporal_v2.json

# Compare
python compare_benchmark_results.py before_temporal_v2.json after_temporal_v2.json
```

Expected improvement: **+2-4% accuracy** on Category 2 (temporal questions)

---

## Troubleshooting

### spaCy model not found
```bash
python -m spacy download en_core_web_sm
```

### Temporal metadata not populating
Check that `augment_message_with_temporal()` is called in `load_messages()`:
```python
# Add debug print:
msg = augment_message_with_temporal(msg)
print(f"Augmented: {msg.get('temporal_metadata', 'MISSING')[:100]}")
```

### SQL functions not working
Verify registration:
```python
# In engine.py open() method:
register_temporal_functions(self.conn)
print("Temporal SQL functions registered")
```

### Vector search not using augmented content
Check `build_vectors()` logs augmented content:
```python
# Add debug print in vector_search.py:
print(f"Original: {content[:50]}")
print(f"Augmented: {augmented_content[:50]}")
```

### GPU box LLM fallback not working
- Check GPU box is accessible: `curl http://192.168.1.182:11434/api/version`
- Verify Qwen model loaded: `curl http://192.168.1.182:11434/api/tags`
- Set longer timeout: `extract_temporal_with_llm(..., timeout=10)`

---

## Performance Tuning

### Reduce Ingestion Latency
```python
# In storage.py, batch augmentation:
def load_messages(conn, messages):
    # Augment in parallel
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:
        messages = list(pool.map(augment_message_with_temporal, messages))

    # ... rest of ingestion
```

### Disable LLM Fallback
```python
# For faster ingestion, disable Qwen fallback:
msg = augment_message_with_temporal(msg, use_llm_fallback=False)
```

### Optimize spaCy Processing
```python
# Use spaCy's pipe() for batch processing:
from neuromem.temporal_v2 import nlp

if nlp:
    docs = list(nlp.pipe([m['content'] for m in messages], batch_size=50))
    # ... process docs in parallel
```

---

## Next Steps

1. **Run integration tests** (test_temporal_v2.py)
2. **Integrate into storage.py** (5 minutes)
3. **Register SQL functions** (2 minutes)
4. **Update vector embeddings** (5 minutes)
5. **Benchmark on LoCoMo** (10 minutes)
6. **Measure performance delta** (latency, accuracy)

**Total integration time:** ~30 minutes

**Expected gains:**
- +2-4% accuracy on temporal queries
- +50ms ingestion per message (local CPU)
- 0ms query latency (all work done at ingest)
- $0.00/month cost

---

## Code Review Checklist

Before committing:

- [ ] All imports at top of file
- [ ] Error handling with try/except around optional features
- [ ] Graceful degradation if spaCy/dateutil not installed
- [ ] No breaking changes to existing API
- [ ] Temporal metadata stored as JSON (SQLite TEXT column)
- [ ] SQL functions handle NULL values gracefully
- [ ] Vector augmentation is optional (doesn't break if metadata missing)
- [ ] Tests pass (test_temporal_v2.py)
- [ ] Documentation updated (this file)

---

## Rollback Plan

If integration causes issues:

1. **Revert storage.py changes:**
   ```python
   # Remove augment_message_with_temporal() call
   # Keep temporal_metadata column (won't break anything)
   ```

2. **Revert engine.py changes:**
   ```python
   # Remove register_temporal_functions() call
   ```

3. **Revert vector_search.py changes:**
   ```python
   # Use raw content instead of augmented_content
   ```

4. **Rebuild vectors:**
   ```bash
   python -c "from neuromem import NeuromemEngine; e = NeuromemEngine('neuromem.db'); e.open(rebuild_vectors=True)"
   ```

System will work as before, temporal_v2 simply won't be active.
