"""
Neuromem adapter — 6-layer memory system (FTS5 + vector + consolidation pipeline).

All local computation, no LLM API calls.
Layers: L0 Personality Engram, L2 Episodic (FTS5), L3 Semantic (Model2Vec + RRF),
        L4 Salience Guard, L5 Consolidation + Predictive Coding.
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Ensure neuromem package and v3_benchmark are importable
_PROJECT_ROOT = Path(__file__).parent.parent.parent  # /Users/j/Desktop/neuromem
sys.path.insert(0, str(_PROJECT_ROOT))
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_adapter import BaseAdapter, RetrievalResult, Session
from neuromem.engine import NeuromemEngine


class NeuromemAdapter(BaseAdapter):

    def __init__(self):
        self.engine: NeuromemEngine | None = None
        self._tmp_db: Path | None = None
        self._tmp_json: Path | None = None

    @property
    def system_name(self) -> str:
        return "Neuromem"

    @property
    def system_version(self) -> str:
        return "1.0.0"

    @property
    def architecture(self) -> str:
        return "6-layer memory (FTS5 + Model2Vec RRF + personality + salience + consolidation)"

    def setup(self) -> None:
        self._tmp_db = Path(tempfile.mktemp(suffix=".db", prefix="neuromem_bench_"))
        self.engine = NeuromemEngine(db_path=self._tmp_db)

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()

        # Convert session turns to flat message format for Neuromem's storage layer.
        # Neuromem expects: [{content, sender, recipient, timestamp, category, modality}]
        messages = []
        for session in sessions:
            for i, turn in enumerate(session.turns):
                # Create a timestamp offset per turn so temporal reasoning works
                # within a session (e.g. turn 0 at :00, turn 1 at :05, etc.)
                ts = session.timestamp
                if i > 0:
                    # Offset by i minutes within the session
                    # Simple approach: append minute offset to ISO timestamp
                    base = ts.replace("T", " ").split(":")[0]  # "2024-07-01 09"
                    hour_min = ts.split("T")[1] if "T" in ts else "00:00:00"
                    parts = hour_min.split(":")
                    minutes = int(parts[1]) + (i * 2)  # 2-minute gaps between turns
                    hours = int(parts[0]) + minutes // 60
                    minutes = minutes % 60
                    ts = f"{ts.split('T')[0]}T{hours:02d}:{minutes:02d}:00"

                sender = "jordan" if turn["role"] == "user" else "assistant"
                recipient = "assistant" if turn["role"] == "user" else "jordan"

                messages.append({
                    "content": turn["content"],
                    "sender": sender,
                    "recipient": recipient,
                    "timestamp": ts,
                    "category": f"session_{session.session_id}",
                    "modality": "conversation",
                })

        # Write to temp JSON for Neuromem's ingest pipeline
        self._tmp_json = Path(tempfile.mktemp(suffix=".json", prefix="neuromem_data_"))
        with open(self._tmp_json, "w") as f:
            json.dump(messages, f)

        # Run full ingestion pipeline (all 6 layers)
        ingest_stats = self.engine.ingest(self._tmp_json)

        elapsed = time.time() - t0
        return {
            "ingested": len(messages),
            "errors": 0,
            "elapsed_seconds": round(elapsed, 3),
            "neuromem_stats": ingest_stats,
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        raw_results = self.engine.search(query_text, limit=top_k)

        results = []
        for r in raw_results:
            score = r.get("score", 0)
            # Normalize negative BM25 scores
            if isinstance(score, (int, float)) and score < 0:
                score = abs(score)

            results.append(RetrievalResult(
                content=r.get("content", ""),
                score=float(score),
                metadata={
                    "sender": r.get("sender", ""),
                    "recipient": r.get("recipient", ""),
                    "timestamp": r.get("timestamp", ""),
                    "category": r.get("category", ""),
                    "source": r.get("source", ""),
                    "message_id": r.get("id", 0),
                },
            ))

        return results

    def teardown(self) -> None:
        if self.engine:
            self.engine.close()
        # Clean up temp files
        for p in [self._tmp_db, self._tmp_json]:
            if p and p.exists():
                p.unlink()
        # Also clean up WAL/SHM files
        if self._tmp_db:
            for suffix in ["-wal", "-shm"]:
                wal = Path(str(self._tmp_db) + suffix)
                if wal.exists():
                    wal.unlink()

    def get_stats(self) -> dict:
        if self.engine:
            stats = self.engine.get_stats()
            stats["layers"] = stats.get("capabilities", {})
            return stats
        return {}
