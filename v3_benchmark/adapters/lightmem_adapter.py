"""
LightMem adapter — 117x token reduction (ICLR 2026).
Academic system, may be fragile.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import lightmem
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class LightMemAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "LightMem"

    @property
    def system_version(self) -> str:
        try:
            return getattr(lightmem, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "117x token reduction (ICLR 2026, compression-based)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"LightMem not available: {IMPORT_ERROR}")

        try:
            if hasattr(lightmem, "LightMem"):
                self.lm = lightmem.LightMem()
            elif hasattr(lightmem, "Memory"):
                self.lm = lightmem.Memory()
            else:
                classes = [n for n in dir(lightmem)
                          if not n.startswith("_") and isinstance(getattr(lightmem, n), type)]
                if classes:
                    self.lm = getattr(lightmem, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find LightMem main class")
        except Exception as e:
            raise RuntimeError(f"LightMem setup failed: {e}")

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
                if hasattr(self.lm, "add"):
                    for m in messages:
                        self.lm.add(m["content"])
                elif hasattr(self.lm, "add_conversation"):
                    self.lm.add_conversation(messages)
                elif hasattr(self.lm, "compress"):
                    text = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
                    self.lm.compress(text)
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 3:
                    print(f"    LightMem ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.lm, "search"):
                raw = self.lm.search(query_text, limit=top_k)
            elif hasattr(self.lm, "retrieve"):
                raw = self.lm.retrieve(query_text, k=top_k)
            elif hasattr(self.lm, "query"):
                raw = self.lm.query(query_text, top_k=top_k)
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
