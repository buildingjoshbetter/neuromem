"""
Cognee adapter — Knowledge graph + LLM extraction.
Had embedding issues in v2.
"""

import os
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import cognee
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class CogneeAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Cognee"

    @property
    def system_version(self) -> str:
        try:
            return getattr(cognee, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Knowledge graph + LLM extraction (multi-hop reasoning)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Cognee not available: {IMPORT_ERROR}")

        if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("Cognee requires ANTHROPIC_API_KEY or OPENAI_API_KEY")

        import asyncio
        self._loop = asyncio.new_event_loop()

        try:
            # Configure cognee
            self._loop.run_until_complete(cognee.prune.prune_data())
            self._loop.run_until_complete(cognee.prune.prune_system(metadata=True))
        except Exception as e:
            print(f"    Cognee prune warning: {e}")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        async def _ingest():
            nonlocal ingested, errors
            for session in sessions:
                text = f"[Session {session.session_id}, {session.timestamp}]\n"
                for turn in session.turns:
                    role = "Jordan" if turn["role"] == "user" else "Assistant"
                    text += f"{role}: {turn['content']}\n"

                try:
                    await cognee.add(text, dataset_name="v3_benchmark")
                    ingested += 1
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"    Cognee add error (session {session.session_id}): {e}")

            # Process all added data
            try:
                await cognee.cognify()
            except Exception as e:
                print(f"    Cognee cognify error: {e}")
                errors += 1

        self._loop.run_until_complete(_ingest())

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        async def _query():
            return await cognee.search(query_text)

        try:
            search_results = self._loop.run_until_complete(_query())
        except Exception:
            return []

        results = []
        if isinstance(search_results, list):
            for item in search_results[:top_k]:
                if isinstance(item, dict):
                    content = item.get("text", item.get("content", str(item)))
                    score = item.get("score", 0.0)
                elif hasattr(item, "text"):
                    content = item.text
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
        if hasattr(self, "_loop"):
            try:
                self._loop.run_until_complete(cognee.prune.prune_data())
            except Exception:
                pass
            self._loop.close()
