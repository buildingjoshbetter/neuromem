"""
Letta (MemGPT) adapter — OS-inspired 3-tier memory hierarchy.
LoCoMo 74.0%, requires Letta server.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    from letta_client import Letta
    AVAILABLE = True
except ImportError as e:
    try:
        from letta import create_client as _cc
        # Wrap old API
        class Letta:
            def __init__(self, **kw):
                self._c = _cc(**kw)
            def __getattr__(self, name):
                return getattr(self._c, name)
        AVAILABLE = True
    except ImportError:
        AVAILABLE = False
        IMPORT_ERROR = str(e)


class LettaAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Letta"

    @property
    def system_version(self) -> str:
        try:
            import letta
            return getattr(letta, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "OS-inspired 3-tier hierarchy (core/recall/archival memory)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Letta not available: {IMPORT_ERROR}")

        try:
            self.client = Letta(base_url="http://localhost:8283")
            # Create a dedicated agent for benchmarking
            self.agent = self.client.agents.create(
                name="v3_benchmark_jordan",
                instructions="You are an AI assistant helping Jordan Chen. "
                             "Remember everything Jordan tells you across conversations.",
            )
            self.agent_id = self.agent.id
        except Exception as e:
            raise RuntimeError(
                f"Letta server connection failed: {e}. "
                f"Start with: letta server"
            )

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            for turn in session.turns:
                if turn["role"] == "user":
                    try:
                        self.client.send_message(
                            agent_id=self.agent_id,
                            message=turn["content"],
                            role="user",
                        )
                        ingested += 1
                    except Exception as e:
                        errors += 1
                        if errors <= 5:
                            print(f"    Letta ingest error: {e}")

            if (session.session_id) % 10 == 0:
                elapsed = time.time() - t0
                print(f"    Session {session.session_id}: {ingested} turns ({elapsed:.0f}s)")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            # Search archival memory
            archival_results = self.client.get_archival_memory(
                agent_id=self.agent_id,
                query=query_text,
                limit=top_k,
            )
        except Exception:
            archival_results = []

        results = []
        for item in archival_results[:top_k]:
            if hasattr(item, "text"):
                content = item.text
            elif isinstance(item, dict):
                content = item.get("text", item.get("content", str(item)))
            else:
                content = str(item)

            results.append(RetrievalResult(
                content=str(content),
                score=0.0,
            ))

        return results

    def teardown(self) -> None:
        if hasattr(self, "client") and hasattr(self, "agent_id"):
            try:
                self.client.delete_agent(self.agent_id)
            except Exception:
                pass
