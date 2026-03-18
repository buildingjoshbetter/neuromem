"""
Neuromem M2: Your First Search Engine
SQLite + FTS5 keyword search — no AI, no embeddings, just full-text search.

This is the first piece of actual Neuromem code.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).parent / "neuromem_fts5.db"
DATA_PATH = Path(__file__).parent / "synthetic_v2_messages.json"


def create_db(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Create SQLite database with FTS5 virtual table."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")

    # Core messages table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            sender TEXT,
            recipient TEXT,
            timestamp TEXT,
            category TEXT,
            modality TEXT
        )
    """)

    # FTS5 virtual table for full-text search
    # tokenize='porter unicode61' gives us stemming (running -> run) + unicode support
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
            content,
            sender,
            recipient,
            category,
            modality,
            content_rowid='id',
            tokenize='porter unicode61'
        )
    """)

    # Triggers to keep FTS5 in sync with messages table
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
            INSERT INTO messages_fts(rowid, content, sender, recipient, category, modality)
            VALUES (new.id, new.content, new.sender, new.recipient, new.category, new.modality);
        END
    """)

    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
            INSERT INTO messages_fts(messages_fts, rowid, content, sender, recipient, category, modality)
            VALUES ('delete', old.id, old.content, old.sender, old.recipient, old.category, old.modality);
        END
    """)

    conn.commit()
    return conn


def load_messages(conn: sqlite3.Connection, data_path: Path = DATA_PATH) -> int:
    """Load synthetic messages into the database. Returns count loaded."""
    with open(data_path) as f:
        messages = json.load(f)

    conn.execute("DELETE FROM messages")
    conn.execute("DELETE FROM messages_fts")

    for msg in messages:
        conn.execute(
            "INSERT INTO messages (content, sender, recipient, timestamp, category, modality) VALUES (?, ?, ?, ?, ?, ?)",
            (msg["content"], msg.get("sender", ""), msg.get("recipient", ""),
             msg.get("timestamp", ""), msg.get("category", ""), msg.get("modality", ""))
        )

    conn.commit()
    return len(messages)


def search(conn: sqlite3.Connection, query: str, limit: int = 10) -> list[dict]:
    """
    Search messages using FTS5.
    Returns ranked results with BM25 relevance scores.
    """
    try:
        rows = conn.execute("""
            SELECT
                m.id, m.content, m.sender, m.recipient, m.timestamp,
                m.category, m.modality,
                messages_fts.rank AS bm25_score
            FROM messages_fts
            JOIN messages m ON m.id = messages_fts.rowid
            WHERE messages_fts MATCH ?
            ORDER BY messages_fts.rank
            LIMIT ?
        """, (query, limit)).fetchall()
    except sqlite3.OperationalError:
        # FTS5 query syntax error — try quoting each word
        safe_query = " OR ".join(f'"{w}"' for w in query.split() if w.strip())
        if not safe_query:
            return []
        try:
            rows = conn.execute("""
                SELECT
                    m.id, m.content, m.sender, m.recipient, m.timestamp,
                    m.category, m.modality,
                    messages_fts.rank AS bm25_score
                FROM messages_fts
                JOIN messages m ON m.id = messages_fts.rowid
                WHERE messages_fts MATCH ?
                ORDER BY messages_fts.rank
                LIMIT ?
            """, (safe_query, limit)).fetchall()
        except sqlite3.OperationalError:
            return []

    results = []
    for row in rows:
        results.append({
            "id": row[0],
            "content": row[1],
            "sender": row[2],
            "recipient": row[3],
            "timestamp": row[4],
            "category": row[5],
            "modality": row[6],
            "bm25_score": row[7],
        })
    return results


def search_with_time_filter(conn: sqlite3.Connection, query: str,
                            after: str = None, before: str = None,
                            limit: int = 10) -> list[dict]:
    """
    Search with optional timestamp filtering.
    This is a preview of what makes FTS5 + SQL powerful —
    none of the benchmarked systems can do temporal filtering.
    """
    results = search(conn, query, limit=100)  # Get more, then filter

    if after or before:
        filtered = []
        for r in results:
            ts = r.get("timestamp", "")
            if after and ts < after:
                continue
            if before and ts > before:
                continue
            filtered.append(r)
        results = filtered

    return results[:limit]


def search_by_sender(conn: sqlite3.Connection, query: str, sender: str,
                     limit: int = 10) -> list[dict]:
    """
    Search within a specific sender's messages.
    This is a preview of L4 Salience Guard — per-entity filtering.
    """
    try:
        rows = conn.execute("""
            SELECT
                m.id, m.content, m.sender, m.recipient, m.timestamp,
                m.category, m.modality,
                messages_fts.rank AS bm25_score
            FROM messages_fts
            JOIN messages m ON m.id = messages_fts.rowid
            WHERE messages_fts MATCH ? AND m.sender = ?
            ORDER BY messages_fts.rank
            LIMIT ?
        """, (query, sender, limit)).fetchall()
    except sqlite3.OperationalError:
        return []

    return [
        {
            "id": row[0], "content": row[1], "sender": row[2],
            "recipient": row[3], "timestamp": row[4], "category": row[5],
            "modality": row[6], "bm25_score": row[7],
        }
        for row in rows
    ]


if __name__ == "__main__":
    import time

    print("=" * 60)
    print("NEUROMEM M2: SQLite + FTS5 Search Engine")
    print("=" * 60)

    # Create and load
    if DB_PATH.exists():
        DB_PATH.unlink()

    t0 = time.time()
    conn = create_db()
    count = load_messages(conn)
    load_time = time.time() - t0
    print(f"\nLoaded {count} messages in {load_time:.3f}s")
    print(f"Database size: {DB_PATH.stat().st_size / 1024:.1f} KB")

    # Demo queries
    demos = [
        "Jordan's dog",
        "CarbonSense funding seed round",
        "scope 1 accuracy Meridian",
        "networking problems",  # FTS5 should MISS this (semantic)
        "ECONNREFUSED",          # FTS5 should HIT this (keyword)
        "What happened after Demo Day",
    ]

    print(f"\n{'=' * 60}")
    print("DEMO QUERIES")
    print(f"{'=' * 60}")

    for q in demos:
        t0 = time.time()
        results = search(conn, q, limit=3)
        elapsed = time.time() - t0
        print(f"\nQ: {q}")
        print(f"  Results: {len(results)} ({elapsed*1000:.1f}ms)")
        for i, r in enumerate(results):
            preview = r["content"][:120].replace("\n", " ")
            print(f"  [{i+1}] ({r['sender']}) {preview}...")

    # Time-filtered search demo
    print(f"\n{'=' * 60}")
    print("TEMPORAL SEARCH DEMO (FTS5 + SQL timestamp filtering)")
    print(f"{'=' * 60}")

    t0 = time.time()
    results = search_with_time_filter(
        conn, "Demo Day investor",
        after="2025-06-15", before="2025-07-15",
        limit=5
    )
    elapsed = time.time() - t0
    print(f"\nQ: 'Demo Day investor' (June 15 - July 15, 2025)")
    print(f"  Results: {len(results)} ({elapsed*1000:.1f}ms)")
    for i, r in enumerate(results):
        preview = r["content"][:120].replace("\n", " ")
        print(f"  [{i+1}] {r['timestamp'][:10]} ({r['sender']}) {preview}...")

    conn.close()
    print(f"\n{'=' * 60}")
    print("M2 engine ready. Run benchmark_v2_fts5.py for full 60-query test.")
    print(f"{'=' * 60}")
