"""
MemMachine adapter — Hybrid episodic/personal/procedural memory.
LoCoMo 84.9% (highest among systems with published pip packages).
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import memmachine
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class MemMachineAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "MemMachine"

    @property
    def system_version(self) -> str:
        try:
            return getattr(memmachine, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Hybrid episodic/personal/procedural memory"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"MemMachine not available: {IMPORT_ERROR}")

        try:
            # Try common API patterns
            if hasattr(memmachine, "MemMachine"):
                self.mm = memmachine.MemMachine()
            elif hasattr(memmachine, "Memory"):
                self.mm = memmachine.Memory()
            elif hasattr(memmachine, "create_memory"):
                self.mm = memmachine.create_memory()
            else:
                # Inspect module to find the main class
                classes = [name for name in dir(memmachine)
                          if not name.startswith("_") and isinstance(getattr(memmachine, name), type)]
                if classes:
                    cls = getattr(memmachine, classes[0])
                    self.mm = cls()
                else:
                    raise RuntimeError(f"Cannot find MemMachine main class. "
                                     f"Available: {dir(memmachine)}")
        except Exception as e:
            raise RuntimeError(f"MemMachine setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            messages = []
            for turn in session.turns:
                messages.append({
                    "role": turn["role"],
                    "content": turn["content"],
                })

            try:
                if hasattr(self.mm, "add"):
                    for msg in messages:
                        self.mm.add(msg["content"], metadata={
                            "role": msg["role"],
                            "session_id": session.session_id,
                            "timestamp": session.timestamp,
                        })
                elif hasattr(self.mm, "add_conversation"):
                    self.mm.add_conversation(messages, metadata={
                        "session_id": session.session_id,
                        "timestamp": session.timestamp,
                    })
                elif hasattr(self.mm, "ingest"):
                    text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
                    self.mm.ingest(text)
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"    MemMachine ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.mm, "search"):
                raw = self.mm.search(query_text, limit=top_k)
            elif hasattr(self.mm, "query"):
                raw = self.mm.query(query_text, top_k=top_k)
            elif hasattr(self.mm, "recall"):
                raw = self.mm.recall(query_text, k=top_k)
            else:
                return []
        except Exception:
            return []

        results = []
        if isinstance(raw, list):
            for item in raw[:top_k]:
                if isinstance(item, dict):
                    content = item.get("content", item.get("text", item.get("memory", str(item))))
                    score = item.get("score", item.get("relevance", 0.0))
                elif hasattr(item, "content"):
                    content = item.content
                    score = getattr(item, "score", 0.0)
                else:
                    content = str(item)
                    score = 0.0
                results.append(RetrievalResult(
                    content=str(content)[:500],
                    score=float(score) if isinstance(score, (int, float)) else 0.0,
                ))

        return results

    def teardown(self) -> None:
        if hasattr(self, "mm") and hasattr(self.mm, "close"):
            try:
                self.mm.close()
            except Exception:
                pass
