"""
A-MEM adapter — Zettelkasten-style dynamic memory indexing.
NeurIPS 2025, superior to SOTA on 6 foundation models.
Requires GitHub clone.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    # A-MEM is typically installed from GitHub, not pip
    # Try various import names
    try:
        import amem
        AMEM_MODULE = amem
    except ImportError:
        try:
            import a_mem
            AMEM_MODULE = a_mem
        except ImportError:
            try:
                import AMEM
                AMEM_MODULE = AMEM
            except ImportError:
                AMEM_MODULE = None

    if AMEM_MODULE is None:
        AVAILABLE = False
        IMPORT_ERROR = "A-MEM not found. Install from GitHub: git clone https://github.com/agiresearch/A-mem"
    else:
        AVAILABLE = True
except Exception as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class AMemAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "A-MEM"

    @property
    def system_version(self) -> str:
        if AMEM_MODULE:
            return getattr(AMEM_MODULE, "__version__", "unknown")
        return "unknown"

    @property
    def architecture(self) -> str:
        return "Zettelkasten dynamic indexing (NeurIPS 2025)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"A-MEM not available: {IMPORT_ERROR}")

        try:
            if hasattr(AMEM_MODULE, "AMEM"):
                self.mem = AMEM_MODULE.AMEM()
            elif hasattr(AMEM_MODULE, "Memory"):
                self.mem = AMEM_MODULE.Memory()
            elif hasattr(AMEM_MODULE, "Agent"):
                self.mem = AMEM_MODULE.Agent()
            else:
                classes = [n for n in dir(AMEM_MODULE)
                          if not n.startswith("_") and isinstance(getattr(AMEM_MODULE, n), type)]
                if classes:
                    self.mem = getattr(AMEM_MODULE, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find A-MEM main class. "
                                     f"Available: {[n for n in dir(AMEM_MODULE) if not n.startswith('_')]}")
        except Exception as e:
            raise RuntimeError(f"A-MEM setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            for turn in session.turns:
                try:
                    if hasattr(self.mem, "add"):
                        self.mem.add(turn["content"])
                    elif hasattr(self.mem, "add_memory"):
                        self.mem.add_memory(turn["content"])
                    ingested += 1
                except Exception as e:
                    errors += 1
                    if errors <= 3:
                        print(f"    A-MEM ingest error: {e}")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            if hasattr(self.mem, "search"):
                raw = self.mem.search(query_text, k=top_k)
            elif hasattr(self.mem, "query"):
                raw = self.mem.query(query_text, top_k=top_k)
            elif hasattr(self.mem, "retrieve"):
                raw = self.mem.retrieve(query_text, k=top_k)
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
