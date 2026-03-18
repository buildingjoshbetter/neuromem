"""
Zep/Graphiti adapter — Temporal knowledge graph.
LoCoMo 75.1%, requires Neo4j.
"""

import asyncio
import os
import time
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class GraphitiAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "Graphiti"

    @property
    def system_version(self) -> str:
        try:
            import graphiti_core
            return getattr(graphiti_core, "__version__", "unknown")
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Temporal knowledge graph (Neo4j, bi-temporal, RRF hybrid search)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"Graphiti not available: {IMPORT_ERROR}")

        neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
        neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
        neo4j_pass = os.environ.get("NEO4J_PASSWORD", "password")

        if not os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("Graphiti requires OPENAI_API_KEY or ANTHROPIC_API_KEY")

        try:
            self.graphiti = Graphiti(neo4j_uri, neo4j_user, neo4j_pass)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(self.graphiti.build_indices_and_constraints())
            self._loop = loop
        except Exception as e:
            raise RuntimeError(f"Neo4j connection failed: {e}. Is Neo4j running? "
                             f"Try: docker run -d -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j")

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        async def _ingest():
            nonlocal ingested, errors
            for session in sessions:
                # Build episode content from session turns
                episode_text = "\n".join(
                    f"{'Jordan' if t['role'] == 'user' else 'Assistant'}: {t['content']}"
                    for t in session.turns
                )
                try:
                    ts = datetime.fromisoformat(session.timestamp)
                    await self.graphiti.add_episode(
                        name=f"session_{session.session_id}",
                        episode_body=episode_text,
                        source_description="Conversation between Jordan Chen and AI assistant",
                        reference_time=ts,
                        source=EpisodeType.text,
                    )
                    ingested += 1
                except Exception as e:
                    errors += 1
                    if errors <= 5:
                        print(f"    Graphiti ingest error (session {session.session_id}): {e}")

        self._loop.run_until_complete(_ingest())

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        async def _query():
            return await self.graphiti.search(query_text, num_results=top_k)

        search_results = self._loop.run_until_complete(_query())

        results = []
        for item in search_results[:top_k]:
            content = getattr(item, "fact", getattr(item, "content", str(item)))
            score = getattr(item, "score", 0.0)
            meta = {}
            if hasattr(item, "valid_at"):
                meta["valid_at"] = str(item.valid_at)
            if hasattr(item, "invalid_at"):
                meta["invalid_at"] = str(item.invalid_at)
            if hasattr(item, "source_description"):
                meta["source"] = item.source_description

            results.append(RetrievalResult(
                content=str(content),
                score=float(score) if isinstance(score, (int, float)) else 0.0,
                metadata=meta,
            ))

        return results

    def teardown(self) -> None:
        if hasattr(self, "_loop"):
            try:
                self._loop.run_until_complete(self.graphiti.close())
            except Exception:
                pass
            self._loop.close()
