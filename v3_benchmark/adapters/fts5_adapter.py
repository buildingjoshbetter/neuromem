"""
FTS5 adapter — SQLite full-text search baseline.
No embeddings, no LLM — pure keyword search with BM25 ranking.
"""

import json
import sqlite3
import time
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session


class FTS5Adapter(BaseAdapter):

    def __init__(self):
        self.db_path = None
        self.conn = None

    @property
    def system_name(self) -> str:
        return "FTS5"

    @property
    def system_version(self) -> str:
        return sqlite3.sqlite_version

    @property
    def architecture(self) -> str:
        return "SQLite FTS5 (Porter stemming, BM25 ranking)"

    def setup(self) -> None:
        self.db_path = Path(tempfile.mktemp(suffix=".db"))
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.execute("PRAGMA journal_mode=WAL")

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                role TEXT,
                session_id INTEGER,
                turn_index INTEGER,
                timestamp TEXT
            )
        """)

        self.conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS turns_fts USING fts5(
                content,
                role,
                tokenize='porter unicode61'
            )
        """)

        self.conn.execute("""
            CREATE TRIGGER IF NOT EXISTS turns_ai AFTER INSERT ON turns BEGIN
                INSERT INTO turns_fts(rowid, content, role)
                VALUES (new.id, new.content, new.role);
            END
        """)

        self.conn.commit()

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            for i, turn in enumerate(session.turns):
                try:
                    self.conn.execute(
                        "INSERT INTO turns (content, role, session_id, turn_index, timestamp) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (turn["content"], turn["role"], session.session_id,
                         i, session.timestamp),
                    )
                    ingested += 1
                except Exception:
                    errors += 1

        self.conn.commit()
        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 3),
            "db_size_kb": round(self.db_path.stat().st_size / 1024, 1) if self.db_path.exists() else 0,
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            rows = self.conn.execute("""
                SELECT
                    t.content, t.role, t.session_id, t.turn_index, t.timestamp,
                    turns_fts.rank AS bm25_score
                FROM turns_fts
                JOIN turns t ON t.id = turns_fts.rowid
                WHERE turns_fts MATCH ?
                ORDER BY turns_fts.rank
                LIMIT ?
            """, (query_text, top_k)).fetchall()
        except sqlite3.OperationalError:
            # FTS5 query syntax error — fallback to OR-joined terms
            safe_query = " OR ".join(
                f'"{w}"' for w in query_text.split() if w.strip()
            )
            if not safe_query:
                return []
            try:
                rows = self.conn.execute("""
                    SELECT
                        t.content, t.role, t.session_id, t.turn_index, t.timestamp,
                        turns_fts.rank AS bm25_score
                    FROM turns_fts
                    JOIN turns t ON t.id = turns_fts.rowid
                    WHERE turns_fts MATCH ?
                    ORDER BY turns_fts.rank
                    LIMIT ?
                """, (safe_query, top_k)).fetchall()
            except sqlite3.OperationalError:
                return []

        results = []
        for row in rows:
            results.append(RetrievalResult(
                content=row[0],
                score=abs(row[5]) if row[5] else 0.0,
                metadata={
                    "role": row[1],
                    "session_id": row[2],
                    "turn_index": row[3],
                    "timestamp": row[4],
                },
            ))
        return results

    def teardown(self) -> None:
        if self.conn:
            self.conn.close()
        if self.db_path and self.db_path.exists():
            self.db_path.unlink()

    def get_stats(self) -> dict:
        size = self.db_path.stat().st_size / 1024 if self.db_path and self.db_path.exists() else 0
        count = self.conn.execute("SELECT COUNT(*) FROM turns").fetchone()[0] if self.conn else 0
        return {
            "db_size_kb": round(size, 1),
            "row_count": count,
        }
