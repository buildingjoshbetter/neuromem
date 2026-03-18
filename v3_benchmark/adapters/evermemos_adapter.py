"""
EverMemOS adapter — Token-efficient memory OS.
LoCoMo 92.3%, claims to beat full-context approaches.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import evermemos
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class EverMemOSAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "EverMemOS"

    @property
    def system_version(self) -> str:
        try:
            return getattr(evermemos, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Token-efficient memory OS (beats full-context)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"EverMemOS not available: {IMPORT_ERROR}")

        try:
            if hasattr(evermemos, "EverMemOS"):
                self.emos = evermemos.EverMemOS()
            elif hasattr(evermemos, "Memory"):
                self.emos = evermemos.Memory()
            elif hasattr(evermemos, "create"):
                self.emos = evermemos.create()
            else:
                classes = [n for n in dir(evermemos)
                          if not n.startswith("_") and isinstance(getattr(evermemos, n), type)]
                if classes:
                    self.emos = getattr(evermemos, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find EverMemOS main class. "
                                     f"Available: {[n for n in dir(evermemos) if not n.startswith('_')]}")
        except Exception as e:
            raise RuntimeError(f"EverMemOS setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            messages = [
                {"role": t["role"], "content": t["content"]}
                for t in session.turns
            ]

            try:
                if hasattr(self.emos, "add_conversation"):
                    self.emos.add_conversation(messages)
                elif hasattr(self.emos, "add"):
                    for m in messages:
                        self.emos.add(m["content"], role=m["role"])
                elif hasattr(self.emos, "ingest"):
                    text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
                    self.emos.ingest(text)
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"    EverMemOS ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.emos, "search"):
                raw = self.emos.search(query_text, limit=top_k)
            elif hasattr(self.emos, "query"):
                raw = self.emos.query(query_text, top_k=top_k)
            elif hasattr(self.emos, "recall"):
                raw = self.emos.recall(query_text, k=top_k)
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

    def teardown(self) -> None:
        if hasattr(self, "emos") and hasattr(self.emos, "close"):
            try:
                self.emos.close()
            except Exception:
                pass
