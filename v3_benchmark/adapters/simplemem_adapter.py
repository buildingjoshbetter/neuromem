"""
SimpleMem adapter — Semantic lossless compression.
+64% performance over Claude-Mem, needs OpenAI key.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import simplemem
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class SimpleMemAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "SimpleMem"

    @property
    def system_version(self) -> str:
        try:
            return getattr(simplemem, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Semantic lossless compression (3-stage pipeline)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"SimpleMem not available: {IMPORT_ERROR}")

        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("SimpleMem requires OPENAI_API_KEY")

        try:
            if hasattr(simplemem, "SimpleMem"):
                self.sm = simplemem.SimpleMem()
            elif hasattr(simplemem, "Memory"):
                self.sm = simplemem.Memory()
            else:
                classes = [n for n in dir(simplemem)
                          if not n.startswith("_") and isinstance(getattr(simplemem, n), type)]
                if classes:
                    self.sm = getattr(simplemem, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find SimpleMem main class")
        except Exception as e:
            raise RuntimeError(f"SimpleMem setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            text = "\n".join(
                f"{'User' if t['role'] == 'user' else 'Assistant'}: {t['content']}"
                for t in session.turns
            )
            try:
                if hasattr(self.sm, "add"):
                    self.sm.add(text)
                elif hasattr(self.sm, "compress"):
                    self.sm.compress(text)
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"    SimpleMem ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.sm, "search"):
                raw = self.sm.search(query_text, limit=top_k)
            elif hasattr(self.sm, "retrieve"):
                raw = self.sm.retrieve(query_text, k=top_k)
            elif hasattr(self.sm, "query"):
                raw = self.sm.query(query_text, top_k=top_k)
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
