"""
Hindsight adapter — Entity tracking + belief evolution.
LongMemEval 91.4% (highest accuracy on standard benchmarks).
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import hindsight
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class HindsightAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Hindsight"

    @property
    def system_version(self) -> str:
        try:
            return getattr(hindsight, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Proprietary agent memory (entity tracking, belief evolution)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Hindsight not available: {IMPORT_ERROR}")

        api_key = os.environ.get("HINDSIGHT_API_KEY", os.environ.get("VECTORIZE_API_KEY"))

        try:
            if hasattr(hindsight, "Hindsight"):
                self.hs = hindsight.Hindsight(api_key=api_key) if api_key else hindsight.Hindsight()
            elif hasattr(hindsight, "Memory"):
                self.hs = hindsight.Memory(api_key=api_key) if api_key else hindsight.Memory()
            elif hasattr(hindsight, "Client"):
                self.hs = hindsight.Client(api_key=api_key) if api_key else hindsight.Client()
            else:
                classes = [n for n in dir(hindsight)
                          if not n.startswith("_") and isinstance(getattr(hindsight, n), type)]
                if classes:
                    cls = getattr(hindsight, classes[0])
                    self.hs = cls(api_key=api_key) if api_key else cls()
                else:
                    raise RuntimeError(f"Cannot find Hindsight main class. "
                                     f"Available: {[n for n in dir(hindsight) if not n.startswith('_')]}")
        except Exception as e:
            raise RuntimeError(f"Hindsight setup failed: {e}")

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
                if hasattr(self.hs, "add_conversation"):
                    self.hs.add_conversation(messages, metadata={
                        "session_id": session.session_id,
                        "timestamp": session.timestamp,
                    })
                elif hasattr(self.hs, "add"):
                    for m in messages:
                        self.hs.add(m["content"], role=m["role"])
                elif hasattr(self.hs, "ingest"):
                    text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
                    self.hs.ingest(text)
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"    Hindsight ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.hs, "search"):
                raw = self.hs.search(query_text, limit=top_k)
            elif hasattr(self.hs, "query"):
                raw = self.hs.query(query_text, top_k=top_k)
            elif hasattr(self.hs, "recall"):
                raw = self.hs.recall(query_text, k=top_k)
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
        if hasattr(self, "hs") and hasattr(self.hs, "close"):
            try:
                self.hs.close()
            except Exception:
                pass
