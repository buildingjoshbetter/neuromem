"""
Neuromem Storage Layer
======================

Core data storage using SQLite with WAL mode. Manages the full database schema
and message CRUD operations for the Neuromem 6-layer memory system.

Schema overview:
    messages        - Core message store (content, sender, recipient, timestamps)
    messages_fts    - FTS5 virtual table for full-text search (auto-synced via triggers)
    entity_profiles - L0 Personality Engram (per-entity traits, style, topics)
    fact_timeline   - L5 contradiction tracking (supersedable facts)
    summaries       - L5 consolidated summaries (daily/weekly/monthly/entity)
"""

import json
import sqlite3
from pathlib import Path


# ---------------------------------------------------------------------------
# Schema DDL
# ---------------------------------------------------------------------------

_SCHEMA_SQL = """
-- Core messages table
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
    embedding_separation BLOB DEFAULT NULL
);

-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    content, sender, recipient, category, modality,
    content_rowid='id',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER IF NOT EXISTS messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, content, sender, recipient, category, modality)
    VALUES (new.id, new.content, new.sender, new.recipient, new.category, new.modality);
END;

CREATE TRIGGER IF NOT EXISTS messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, content, sender, recipient, category, modality)
    VALUES ('delete', old.id, old.content, old.sender, old.recipient, old.category, old.modality);
END;

-- Entity profiles (L0 Personality Engram)
CREATE TABLE IF NOT EXISTS entity_profiles (
    entity TEXT PRIMARY KEY,
    message_count INTEGER DEFAULT 0,
    traits TEXT DEFAULT '{}',
    communication_style TEXT DEFAULT '{}',
    topics TEXT DEFAULT '[]',
    relationships TEXT DEFAULT '{}',
    updated_at TEXT
);

-- Fact timeline (L5 contradiction tracking)
CREATE TABLE IF NOT EXISTS fact_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT NOT NULL,
    fact TEXT NOT NULL,
    source_message_id INTEGER,
    timestamp TEXT,
    superseded_by INTEGER,
    entity_scope TEXT DEFAULT '',
    valid_from TEXT DEFAULT '',
    valid_to TEXT DEFAULT '',
    FOREIGN KEY (source_message_id) REFERENCES messages(id)
);

-- Consolidated summaries (L5)
CREATE TABLE IF NOT EXISTS summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period TEXT,
    start_date TEXT,
    end_date TEXT,
    entity TEXT DEFAULT '',
    summary TEXT NOT NULL,
    key_facts TEXT DEFAULT '[]',
    message_ids TEXT DEFAULT '[]',
    created_at TEXT
);

-- Episode boundaries (B1: 6-hour gap heuristic grouping)
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    message_count INTEGER DEFAULT 0,
    summary TEXT DEFAULT ''
);

-- Landmark events (E3: job changes, moves, launches, breakups)
CREATE TABLE IF NOT EXISTS landmark_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_name TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT DEFAULT '',
    related_entities TEXT DEFAULT '[]',
    source_message_id INTEGER,
    FOREIGN KEY (source_message_id) REFERENCES messages(id)
);

-- Causal edges (D2: forward chains and backward cause scanning)
CREATE TABLE IF NOT EXISTS causal_edges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cause_msg_id INTEGER NOT NULL,
    effect_msg_id INTEGER NOT NULL,
    relationship TEXT DEFAULT '',
    confidence REAL DEFAULT 0.0,
    FOREIGN KEY (cause_msg_id) REFERENCES messages(id),
    FOREIGN KEY (effect_msg_id) REFERENCES messages(id)
);

-- Entity relationships (E2: Dunbar hierarchy)
CREATE TABLE IF NOT EXISTS entity_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_a TEXT NOT NULL,
    entity_b TEXT NOT NULL,
    relationship_type TEXT DEFAULT '',
    strength REAL DEFAULT 0.0,
    dunbar_layer TEXT DEFAULT '',
    last_interaction TEXT DEFAULT ''
);
"""


# ---------------------------------------------------------------------------
# Database creation
# ---------------------------------------------------------------------------

def create_db(db_path: str | Path) -> sqlite3.Connection:
    """
    Create (or open) a Neuromem database with the full schema.

    Enables WAL mode for concurrent read/write performance and executes all
    CREATE TABLE / CREATE VIRTUAL TABLE / CREATE TRIGGER statements.

    Args:
        db_path: Filesystem path for the SQLite database file.
                 Use \":memory:\" for an in-memory database.

    Returns:
        An open ``sqlite3.Connection`` with row_factory left at default
        (callers choose their own access pattern).
    """
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(_SCHEMA_SQL)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# Message loading
# ---------------------------------------------------------------------------

def load_messages(conn: sqlite3.Connection, messages: list[dict]) -> int:
    """
    Bulk-load messages into the database.

    Clears all existing message data (messages + FTS index) before inserting,
    so the database reflects exactly the provided list afterwards.

    Each dict in *messages* should have at minimum a ``content`` key.
    Optional keys: ``sender``, ``recipient``, ``timestamp``, ``category``,
    ``modality``.

    Args:
        conn:     Open database connection (from :func:`create_db`).
        messages: List of message dicts to insert.

    Returns:
        Number of messages inserted.
    """
    conn.execute("DELETE FROM messages")
    # The DELETE trigger handles FTS cleanup row-by-row, but if the table was
    # freshly created (no rows yet) that is a no-op.  For safety, also rebuild
    # the FTS index after bulk delete.
    try:
        conn.execute("INSERT INTO messages_fts(messages_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass  # FTS table might already be clean

    for msg in messages:
        conn.execute(
            """INSERT INTO messages
               (content, sender, recipient, timestamp, category, modality)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                msg["content"],
                msg.get("sender", ""),
                msg.get("recipient", ""),
                msg.get("timestamp", ""),
                msg.get("category", ""),
                msg.get("modality", ""),
            ),
        )

    conn.commit()
    return len(messages)


def load_messages_from_file(conn: sqlite3.Connection, json_path: str | Path) -> int:
    """
    Load messages from a JSON file into the database.

    The file must contain a JSON array of message objects (same format as
    :func:`load_messages`).

    Args:
        conn:      Open database connection.
        json_path: Path to the JSON file.

    Returns:
        Number of messages inserted.
    """
    path = Path(json_path)
    with open(path, "r", encoding="utf-8") as f:
        messages = json.load(f)

    return load_messages(conn, messages)


# ---------------------------------------------------------------------------
# Message retrieval (CRUD reads)
# ---------------------------------------------------------------------------

def _row_to_dict(row: tuple) -> dict:
    """Convert a raw row tuple to a message dict."""
    return {
        "id": row[0],
        "content": row[1],
        "sender": row[2],
        "recipient": row[3],
        "timestamp": row[4],
        "category": row[5],
        "modality": row[6],
    }


_SELECT_COLS = "id, content, sender, recipient, timestamp, category, modality"


def get_message(conn: sqlite3.Connection, msg_id: int) -> dict | None:
    """
    Retrieve a single message by its primary key.

    Args:
        conn:   Open database connection.
        msg_id: The message ID to look up.

    Returns:
        Message dict, or ``None`` if not found.
    """
    row = conn.execute(
        f"SELECT {_SELECT_COLS} FROM messages WHERE id = ?", (msg_id,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def get_messages_by_sender(conn: sqlite3.Connection, sender: str) -> list[dict]:
    """
    Retrieve all messages from a specific sender, ordered by timestamp.

    Args:
        conn:   Open database connection.
        sender: Sender name to filter on (case-sensitive).

    Returns:
        List of message dicts.
    """
    rows = conn.execute(
        f"SELECT {_SELECT_COLS} FROM messages WHERE sender = ? ORDER BY timestamp",
        (sender,),
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_messages_in_range(
    conn: sqlite3.Connection,
    after: str | None = None,
    before: str | None = None,
) -> list[dict]:
    """
    Retrieve messages within a timestamp range.

    Timestamps are compared as ISO-8601 strings (lexicographic ordering).
    Either bound may be omitted for an open-ended range.

    Args:
        conn:   Open database connection.
        after:  Inclusive lower bound (e.g. ``"2025-01-01"``).
        before: Inclusive upper bound (e.g. ``"2025-12-31"``).

    Returns:
        List of message dicts ordered by timestamp.
    """
    clauses: list[str] = []
    params: list[str] = []

    if after is not None:
        clauses.append("timestamp >= ?")
        params.append(after)
    if before is not None:
        clauses.append("timestamp <= ?")
        params.append(before)

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    rows = conn.execute(
        f"SELECT {_SELECT_COLS} FROM messages{where} ORDER BY timestamp",
        params,
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def get_all_senders(conn: sqlite3.Connection) -> list[str]:
    """
    Get a sorted list of unique sender names in the database.

    Returns:
        Sorted list of sender strings (empty strings excluded).
    """
    rows = conn.execute(
        "SELECT DISTINCT sender FROM messages WHERE sender != '' ORDER BY sender"
    ).fetchall()
    return [r[0] for r in rows]


def get_message_count(conn: sqlite3.Connection) -> int:
    """
    Return the total number of messages in the database.
    """
    row = conn.execute("SELECT COUNT(*) FROM messages").fetchone()
    return row[0] if row else 0
