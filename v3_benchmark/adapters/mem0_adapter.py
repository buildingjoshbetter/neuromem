"""
Mem0 adapter — LLM extraction + vector search.
$24M funded, LoCoMo 66.9%.
"""

import os
import time
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    from mem0 import Memory
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class Mem0Adapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Mem0"

    @property
    def system_version(self) -> str:
        try:
            import mem0
            return getattr(mem0, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "LLM extraction + Qdrant vector search (Claude Sonnet 4.5)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Mem0 not available: {IMPORT_ERROR}")

        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY not set")

        self.data_dir = tempfile.mkdtemp(prefix="mem0_v3_")

        config = {
            "llm": {
                "provider": "anthropic",
                "config": {
                    "model": "claude-sonnet-4-5-20250929",
                    "temperature": 0.0,
                    "max_tokens": 2000,
                },
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "all-MiniLM-L6-v2",
                    "model_kwargs": {"device": "cpu"},
                },
            },
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "v3_benchmark",
                    "embedding_model_dims": 384,
                    "path": self.data_dir,
                },
            },
            "version": "v1.1",
        }

        self.memory = Memory.from_config(config)

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            # Build conversation text for the session
            for i, turn in enumerate(session.turns):
                if turn["role"] == "user":
                    content = f"[Session {session.session_id}, {session.timestamp}] User: {turn['content']}"
                else:
                    content = f"[Session {session.session_id}, {session.timestamp}] Assistant: {turn['content']}"

                try:
                    self.memory.add(
                        content,
                        user_id="jordan",
                        metadata={
                            "session_id": session.session_id,
                            "turn_index": i,
                            "role": turn["role"],
                            "timestamp": session.timestamp,
                        },
                    )
                    ingested += 1
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"    Mem0 ingest error: {e}")

            if (session.session_id) % 10 == 0:
                elapsed = time.time() - t0
                print(f"    Session {session.session_id}: {ingested} turns ingested ({elapsed:.0f}s)")

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        search_results = self.memory.search(query_text, user_id="jordan", limit=top_k)

        results = []
        if isinstance(search_results, dict) and "results" in search_results:
            raw = search_results["results"]
        elif isinstance(search_results, list):
            raw = search_results
        else:
            raw = []

        for item in raw[:top_k]:
            if isinstance(item, dict):
                mem_text = item.get("memory", item.get("text", str(item)))
                score = item.get("score", 0.0)
                meta = {k: v for k, v in item.items() if k not in ("memory", "text", "score")}
            else:
                mem_text = str(item)
                score = 0.0
                meta = {}

            results.append(RetrievalResult(
                content=str(mem_text),
                score=float(score) if isinstance(score, (int, float)) else 0.0,
                metadata=meta,
            ))

        return results

    def teardown(self) -> None:
        import shutil
        if hasattr(self, "data_dir") and Path(self.data_dir).exists():
            shutil.rmtree(self.data_dir, ignore_errors=True)
