"""
LangMem adapter — LangChain's memory SDK.
LoCoMo 58.1%, semantic extraction.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    from langmem import create_memory_manager
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class LangMemAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "LangMem"

    @property
    def system_version(self) -> str:
        try:
            import langmem
            return getattr(langmem, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "LLM extraction + InMemoryStore (LangChain)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"LangMem not available: {IMPORT_ERROR}")

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        try:
            from langgraph.store.memory import InMemoryStore
        except ImportError:
            raise RuntimeError("langgraph not available: pip install langgraph")

        self.store = InMemoryStore()
        self.manager = create_memory_manager(
            "anthropic:claude-sonnet-4-5-20250929",
            instructions="Extract key facts, preferences, and events about the user Jordan Chen.",
            enable_inserts=True,
            enable_updates=True,
        )
        self.namespace = ("jordan", "memories")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            # Build LangChain message format
            messages = []
            for turn in session.turns:
                if turn["role"] == "user":
                    messages.append({"role": "user", "content": turn["content"]})
                else:
                    messages.append({"role": "assistant", "content": turn["content"]})

            try:
                # Extract memories from the conversation
                result = self.manager.invoke(
                    {"messages": messages},
                    config={"configurable": {"langgraph_store": self.store,
                                             "user_id": "jordan"}},
                )
                ingested += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"    LangMem ingest error (session {session.session_id}): {e}")

            if (session.session_id) % 10 == 0:
                elapsed = time.time() - t0
                print(f"    Session {session.session_id}: {ingested} sessions ingested ({elapsed:.0f}s)")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        try:
            memories = self.store.search(self.namespace, query=query_text, limit=top_k)
        except Exception:
            # Fallback: try listing all memories
            try:
                memories = list(self.store.list(self.namespace))
            except Exception:
                return []

        results = []
        for mem in memories[:top_k]:
            if hasattr(mem, "value"):
                content = str(mem.value)
                score = getattr(mem, "score", 0.0)
            elif isinstance(mem, dict):
                content = str(mem.get("value", mem.get("content", str(mem))))
                score = mem.get("score", 0.0)
            else:
                content = str(mem)
                score = 0.0

            results.append(RetrievalResult(
                content=content,
                score=float(score) if isinstance(score, (int, float)) else 0.0,
            ))

        return results

    def teardown(self) -> None:
        pass
