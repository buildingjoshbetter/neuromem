"""
OpenMemory adapter — Cognitive memory engine with 5 memory types.
Claims ~95% recall, 338 QPS.
"""

import asyncio
import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    # Try various package names
    try:
        import openmemory
        OM_MODULE = openmemory
    except ImportError:
        try:
            from openmemory import client as OM_MODULE
        except ImportError:
            try:
                import openmemory_py as OM_MODULE
            except ImportError:
                OM_MODULE = None

    if OM_MODULE is None:
        AVAILABLE = False
        IMPORT_ERROR = "OpenMemory not found. Try: pip install openmemory-py"
    else:
        AVAILABLE = True
except Exception as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class OpenMemoryAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "OpenMemory"

    @property
    def system_version(self) -> str:
        if OM_MODULE:
            return getattr(OM_MODULE, "__version__", "unknown")
        return "unknown"

    @property
    def architecture(self) -> str:
        return "Cognitive engine (semantic, episodic, procedural, emotional, reflective)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"OpenMemory not available: {IMPORT_ERROR}")

        self._loop = asyncio.new_event_loop()

        try:
            if hasattr(OM_MODULE, "Memory"):
                self.om = OM_MODULE.Memory()
            elif hasattr(OM_MODULE, "OpenMemory"):
                self.om = OM_MODULE.OpenMemory()
            elif hasattr(OM_MODULE, "Client"):
                self.om = OM_MODULE.Client()
            else:
                classes = [n for n in dir(OM_MODULE)
                          if not n.startswith("_") and isinstance(getattr(OM_MODULE, n), type)]
                if classes:
                    self.om = getattr(OM_MODULE, classes[0])()
                else:
                    raise RuntimeError(f"Cannot find OpenMemory main class. "
                                     f"Available: {[n for n in dir(OM_MODULE) if not n.startswith('_')]}")
        except Exception as e:
            raise RuntimeError(f"OpenMemory setup failed: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        async def _ingest():
            nonlocal ingested, errors
            for session in sessions:
                for turn in session.turns:
                    try:
                        await self.om.add(
                            turn["content"],
                            user_id="jordan",
                            metadata={
                                "role": turn["role"],
                                "session_id": session.session_id,
                                "timestamp": session.timestamp,
                            },
                        )
                        ingested += 1
                    except Exception as e:
                        errors += 1
                        if errors <= 3:
                            print(f"    OpenMemory ingest error: {e}")

        self._loop.run_until_complete(_ingest())

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        async def _query():
            return await self.om.search(query_text, user_id="jordan", limit=top_k)

        try:
            raw = self._loop.run_until_complete(_query())
        except Exception:
            return []

        results = []
        if isinstance(raw, list):
            for item in raw[:top_k]:
                if isinstance(item, dict):
                    content = item.get("content", item.get("text", item.get("memory", str(item))))
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
        if hasattr(self, "_loop"):
            self._loop.close()
