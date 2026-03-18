"""
Memary adapter — Multi-hop reasoning memory.
Less mature, pip install memary.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import memary
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class MemaryAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Memary"

    @property
    def system_version(self) -> str:
        try:
            return getattr(memary, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Multi-hop reasoning memory"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Memary not available: {IMPORT_ERROR}")

        try:
            if hasattr(memary, "Memary"):
                self.mem = memary.Memary()
            elif hasattr(memary, "Memory"):
                self.mem = memary.Memory()
            elif hasattr(memary, "Agent"):
                self.mem = memary.Agent()
            else:
                classes = [n for n in dir(memary)
                          if not n.startswith("_") and isinstance(getattr(memary, n), type)]
                if classes:
                    self.mem = getattr(memary, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find Memary main class")
        except Exception as e:
            raise RuntimeError(f"Memary setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            for turn in session.turns:
                try:
                    if hasattr(self.mem, "add"):
                        self.mem.add(turn["content"])
                    elif hasattr(self.mem, "save"):
                        self.mem.save(turn["content"])
                    ingested += 1
                except Exception as e:
                    errors += 1
                    if errors <= 3:
                        print(f"    Memary ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.mem, "search"):
                raw = self.mem.search(query_text, limit=top_k)
            elif hasattr(self.mem, "query"):
                raw = self.mem.query(query_text, top_k=top_k)
            elif hasattr(self.mem, "recall"):
                raw = self.mem.recall(query_text, k=top_k)
            else:
                return []
        except Exception:
            return []

        results = []
        if isinstance(raw, list):
            for item in raw[:top_k]:
                if isinstance(item, dict):
                    content = item.get("content", item.get("text", str(item)))
                    score = item.get("score", 0.0)
                else:
                    content = str(item)
                    score = 0.0
                results.append(RetrievalResult(
                    content=str(content)[:500],
                    score=float(score) if isinstance(score, (int, float)) else 0.0,
                ))
        return results
