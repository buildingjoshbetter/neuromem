"""
Base adapter interface for v3 benchmark.
All memory systems must implement this interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalResult:
    """A single result from a memory system's retrieval."""
    content: str
    score: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class Session:
    """A conversation session to ingest."""
    session_id: int
    timestamp: str
    turns: list[dict]  # [{"role": "user"/"assistant", "content": "..."}]
    facts_introduced: list[str] = field(default_factory=list)
    facts_updated: list[str] = field(default_factory=list)


class BaseAdapter(ABC):
    """Abstract interface for all memory system adapters."""

    @property
    @abstractmethod
    def system_name(self) -> str:
        """Human-readable system name (e.g., 'Mem0', 'ChromaDB')."""
        ...

    @property
    @abstractmethod
    def system_version(self) -> str:
        """Version string of the system being tested."""
        ...

    @property
    def architecture(self) -> str:
        """Short description of the system's architecture."""
        return "Unknown"

    @abstractmethod
    def setup(self) -> None:
        """
        Initialize the system. Called once before ingestion.
        Should handle all setup: creating DBs, loading models, etc.
        Raise RuntimeError if setup fails (e.g., missing dependency).
        """
        ...

    @abstractmethod
    def ingest_sessions(self, sessions: list[Session]) -> dict:
        """
        Ingest all conversation sessions into the memory system.

        Args:
            sessions: List of Session objects to ingest.

        Returns:
            dict with at least:
                - "ingested": int (number of sessions/turns ingested)
                - "errors": int (number of failures)
                - "elapsed_seconds": float
        """
        ...

    @abstractmethod
    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        """
        Query the memory system and return ranked results.

        Args:
            query_text: The natural language query.
            top_k: Maximum number of results to return.

        Returns:
            List of RetrievalResult, ranked by relevance (best first).
        """
        ...

    def teardown(self) -> None:
        """Clean up resources. Called after all queries are done."""
        pass

    def get_stats(self) -> dict:
        """Return system-specific stats (memory usage, DB size, etc.)."""
        return {}
