"""
ChromaDB adapter — pure vector similarity baseline.
No LLM intelligence, just embeddings + cosine similarity.
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from base_adapter import BaseAdapter, RetrievalResult, Session

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class ChromaDBAdapter(BaseAdapter):

    @property
    def system_name(self) -> str:
        return "ChromaDB"

    @property
    def system_version(self) -> str:
        try:
            return chromadb.__version__
        except Exception:
            return "unknown"

    @property
    def architecture(self) -> str:
        return "Pure vector similarity (all-MiniLM-L6-v2, cosine)"

    def setup(self) -> None:
        if not AVAILABLE:
            raise RuntimeError(f"ChromaDB not available: {IMPORT_ERROR}")

        self.client = chromadb.EphemeralClient()
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.create_collection(
            name="v3_benchmark",
            metadata={"hnsw:space": "cosine"},
        )

    def ingest_sessions(self, sessions: list[Session]) -> dict:
        t0 = time.time()
        ingested = 0
        errors = 0

        for session in sessions:
            for i, turn in enumerate(session.turns):
                doc_id = f"s{session.session_id}_t{i}"
                content = turn["content"]
                role = turn["role"]

                try:
                    embedding = self.embed_model.encode([content]).tolist()
                    self.collection.add(
                        ids=[doc_id],
                        documents=[content],
                        embeddings=embedding,
                        metadatas=[{
                            "session_id": str(session.session_id),
                            "turn_index": i,
                            "role": role,
                            "timestamp": session.timestamp,
                        }],
                    )
                    ingested += 1
                except Exception:
                    errors += 1

        return {
            "ingested": ingested,
            "errors": errors,
            "elapsed_seconds": round(time.time() - t0, 1),
            "collection_count": self.collection.count(),
        }

    def query(self, query_text: str, top_k: int = 10) -> list[RetrievalResult]:
        query_embedding = self.embed_model.encode([query_text]).tolist()

        search_results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        results = []
        if search_results and search_results["documents"]:
            for doc, meta, dist in zip(
                search_results["documents"][0],
                search_results["metadatas"][0],
                search_results["distances"][0],
            ):
                results.append(RetrievalResult(
                    content=doc,
                    score=round(1 - dist, 4),
                    metadata=meta,
                ))

        return results

    def teardown(self) -> None:
        try:
            self.client.delete_collection("v3_benchmark")
        except Exception:
            pass

    def get_stats(self) -> dict:
        return {
            "embedding_model": "all-MiniLM-L6-v2",
            "collection_count": self.collection.count() if hasattr(self, "collection") else 0,
        }
